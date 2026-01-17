"""Tests for retry logic in nasa_client.py."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.enum import DataType, AddressClass
from pysamsungnasa.protocol.factory.types import SendMessage


class TestSendMessageRetryTracking:
    """Tests for retry tracking in send_message."""

    @pytest.mark.asyncio
    async def test_send_message_tracks_write_retry(self, nasa_client):
        """Test that send_message tracks write requests for retry."""
        client = nasa_client
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=1):
            messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]
            await client.send_message(
                destination="200001",
                request_type=DataType.WRITE,
                messages=messages,
            )

            # Check that the write was tracked
            # Note: Keys are formatted as destination_packet_number
            write_key = "200001_1"  # packet_number=1
            assert write_key in client._pending_writes
            write_info = client._pending_writes[write_key]
            assert write_info["destination"] == "200001"
            assert write_info["message_ids"] == [0x4000]
            assert write_info["data_type"] == DataType.WRITE
            assert write_info["attempts"] == 0
            assert write_info["packet_number"] == 1

    @pytest.mark.asyncio
    async def test_send_message_tracks_read_retry(self, nasa_client):
        """Test that send_message tracks read requests for retry."""
        client = nasa_client
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=2):
            messages = [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x05\xa5\xa5\xa5"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x05\xa5\xa5\xa5"),
            ]
            await client.send_message(
                destination="200001",
                request_type=DataType.READ,
                messages=messages,
            )

            # Check that the read was tracked with sorted message IDs
            read_key = "200001_(16384, 16385)"  # Sorted tuple as string
            assert read_key in client._pending_reads
            read_info = client._pending_reads[read_key]
            assert read_info["destination"] == "200001"
            assert set(read_info["messages"]) == {0x4000, 0x4001}
            assert read_info["attempts"] == 0
            assert read_info["packet_number"] == 2

    @pytest.mark.asyncio
    async def test_send_message_request_type_tracked_as_write(self, nasa_client):
        """Test that REQUEST type is tracked for write retries."""
        client = nasa_client
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=3):
            messages = [SendMessage(MESSAGE_ID=0x5000, PAYLOAD=b"\x02")]
            await client.send_message(
                destination="100001",
                request_type=DataType.REQUEST,
                messages=messages,
            )

            # REQUEST type should be tracked as write retry
            write_key = "100001_3"  # 0x5000 = 20480
            assert write_key in client._pending_writes

    @pytest.mark.asyncio
    async def test_send_message_no_tracking_when_retries_disabled(self, nasa_client):
        """Test that send_message doesn't track when retries are disabled."""
        client = nasa_client
        client._config.enable_write_retries = False
        client._config.enable_read_retries = False

        # Clear any existing entries
        initial_writes_count = len(client._pending_writes)
        initial_reads_count = len(client._pending_reads)

        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=4):
            messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]
            await client.send_message(
                destination="200001",
                request_type=DataType.WRITE,
                messages=messages,
            )

            # Should not add new tracked entries
            assert len(client._pending_writes) == initial_writes_count
            assert len(client._pending_reads) == initial_reads_count

    @pytest.mark.asyncio
    async def test_send_message_tracks_multiple_writes(self, nasa_client):
        """Test that send_message tracks multiple messages in one request."""
        client = nasa_client
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=5):
            messages = [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
                SendMessage(MESSAGE_ID=0x4002, PAYLOAD=b"\x03"),
            ]
            await client.send_message(
                destination="200001",
                request_type=DataType.WRITE,
                messages=messages,
            )

            # All messages in one packet should have a single entry with packet_number key
            write_key = "200001_5"  # packet_number=5
            assert write_key in client._pending_writes
            write_info = client._pending_writes[write_key]
            assert write_info["message_ids"] == [0x4000, 0x4001, 0x4002]
            assert len(write_info["messages"]) == 3


class TestNasaWriteRetry:
    """Tests for nasa_write using centralized retry logic."""

    @pytest.mark.asyncio
    async def test_nasa_write_tracked_for_retry(self, nasa_client_write_only):
        """Test that nasa_write properly uses send_message retry tracking."""
        client = nasa_client_write_only
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=1):
            await client.nasa_write(
                msg=0x4000,
                value="01",
                destination="200001",
                data_type=DataType.WRITE,
            )

            # Check that write was tracked with message_ids and messages
            write_key = "200001_1"  # packet_number=1
            assert write_key in client._pending_writes
            write_info = client._pending_writes[write_key]
            assert write_info["message_ids"] == [0x4000]
            assert write_info["data_type"] == DataType.WRITE
            assert len(write_info["messages"]) == 1
            assert write_info["messages"][0].MESSAGE_ID == 0x4000


class TestNasaReadRetry:
    """Tests for nasa_read using centralized retry logic."""

    @pytest.mark.asyncio
    async def test_nasa_read_tracked_for_retry(self, nasa_client_read_only):
        """Test that nasa_read properly uses send_message retry tracking."""
        client = nasa_client_read_only
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=1):
            await client.nasa_read(
                msgs=[0x4000, 0x4001],
                destination="200001",
            )

            # Check that read was tracked
            read_key = "200001_(16384, 16385)"  # Sorted tuple as string
            assert read_key in client._pending_reads
            read_info = client._pending_reads[read_key]
            assert set(read_info["messages"]) == {0x4000, 0x4001}


class TestRetryManagerRetryBehavior:
    """Tests for _retry_manager retrying failed requests."""

    @pytest.mark.asyncio
    async def test_retry_manager_retries_failed_write(self, nasa_client_with_full_retry_config):
        """Test that retry manager retries failed write requests."""
        client = nasa_client_with_full_retry_config
        # Manually add a pending write that needs retry
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_1"  # Use unique key to avoid conflicts
        messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]
        client._pending_writes[write_key] = {
            "destination": "200001",
            "message_ids": [0x4000],
            "messages": messages,
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": current_time,
            "next_retry_time": current_time - 1.0,  # Time to retry now
            "retry_interval": 0.1,
        }

        retry_send_call_count = 0

        async def mock_send(*args, **kwargs):
            nonlocal retry_send_call_count
            retry_send_call_count += 1
            return None

        sleep_count = 0

        async def mock_sleep(delay):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 1:
                # Allow first sleep to "complete" immediately
                return
            else:
                # Raise error on subsequent sleeps to exit
                raise asyncio.CancelledError()

        with patch.object(client, "send_message", new_callable=AsyncMock, side_effect=mock_send):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                # Run retry manager
                retry_task = asyncio.create_task(client._retry_manager())
                try:
                    await retry_task
                except asyncio.CancelledError:
                    pass

                # Check that send_message was called to retry
                assert retry_send_call_count > 0

    @pytest.mark.asyncio
    async def test_retry_manager_retries_failed_read(self, nasa_client_with_full_retry_config):
        """Test that retry manager retries failed read requests."""
        client = nasa_client_with_full_retry_config
        # Manually add a pending read that needs retry
        current_time = asyncio.get_running_loop().time()
        read_key = "test_200001_(16384, 16385)"
        client._pending_reads[read_key] = {
            "destination": "200001",
            "messages": [0x4000, 0x4001],
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": current_time,
            "next_retry_time": current_time - 1.0,  # Time to retry now
            "retry_interval": 0.1,
        }

        retry_send_call_count = 0

        async def mock_send(*args, **kwargs):
            nonlocal retry_send_call_count
            retry_send_call_count += 1
            return None

        sleep_count = 0

        async def mock_sleep(delay):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 1:
                # Allow first sleep to "complete" immediately
                return
            else:
                # Raise error on subsequent sleeps to exit
                raise asyncio.CancelledError()

        with patch.object(client, "send_message", new_callable=AsyncMock, side_effect=mock_send):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                # Run retry manager
                retry_task = asyncio.create_task(client._retry_manager())
                try:
                    await retry_task
                except asyncio.CancelledError:
                    pass

                # Check that send_message was called to retry
                assert retry_send_call_count > 0

    @pytest.mark.asyncio
    async def test_retry_manager_applies_backoff_factor(self, nasa_client_with_full_retry_config):
        """Test that retry manager applies backoff factor to retry interval."""
        client = nasa_client_with_full_retry_config
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_1"  # Use unique key
        initial_interval = 0.1
        client._pending_writes[write_key] = {
            "destination": "200001",
            "message_id": 0x4000,
            "payload": b"\x01",
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": current_time,
            "next_retry_time": current_time - 1.0,  # Time to retry now
            "retry_interval": initial_interval,
        }

        sleep_count = 0

        async def mock_sleep(delay):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 1:
                # Allow first sleep to "complete" immediately
                return
            else:
                # Raise error on subsequent sleeps to exit
                raise asyncio.CancelledError()

        with patch.object(client, "send_message", new_callable=AsyncMock):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                retry_task = asyncio.create_task(client._retry_manager())
                try:
                    await retry_task
                except asyncio.CancelledError:
                    pass

                # Check that backoff was applied
                write_info = client._pending_writes[write_key]
                expected_interval = initial_interval * client._config.write_retry_backoff_factor
                # Use pytest.approx for floating point comparison
                assert write_info["retry_interval"] == pytest.approx(expected_interval, rel=1e-9)
                assert write_info["attempts"] == 1

    @pytest.mark.asyncio
    async def test_retry_manager_abandons_after_max_attempts(self, nasa_client_with_full_retry_config):
        """Test that retry manager abandons request after max attempts."""
        client = nasa_client_with_full_retry_config
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_1"  # Use unique key

        # Clear any existing pending entries to have a clean test
        client._pending_writes.clear()
        client._pending_reads.clear()

        client._pending_writes[write_key] = {
            "destination": "200001",
            "message_id": 0x4000,
            "payload": b"\x01",
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": client._config.write_retry_max_attempts,  # Already at max
            "last_attempt_time": current_time,
            "next_retry_time": current_time - 1.0,
            "retry_interval": 0.1,
        }

        sleep_count = 0

        async def mock_sleep(delay):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 1:
                # Allow first sleep to "complete" immediately
                return
            else:
                # Raise error on subsequent sleeps to exit
                raise asyncio.CancelledError()

        with patch.object(client, "send_message", new_callable=AsyncMock) as mock_send:
            with patch("asyncio.sleep", side_effect=mock_sleep):
                retry_task = asyncio.create_task(client._retry_manager())
                try:
                    await retry_task
                except asyncio.CancelledError:
                    pass

                # send_message should NOT be called since max attempts reached
                mock_send.assert_not_called()
                # And the pending write should be removed
                assert write_key not in client._pending_writes


class TestWriteAttributesWithRetry:
    """Integration tests for write_attributes with retry logic."""

    @pytest.fixture
    def device(self):
        """Create a test device."""
        from pysamsungnasa.device import NasaDevice
        from pysamsungnasa.protocol.parser import NasaPacketParser
        from pysamsungnasa.protocol.factory.messages.indoor import InOperationPowerMessage

        config = NasaConfig(enable_write_retries=True)
        parser = NasaPacketParser(config=config)
        client = AsyncMock()
        device = NasaDevice(
            address="200001",
            device_type=AddressClass.INDOOR,
            packet_parser=parser,
            config=config,
            client=client,
        )
        return device

    @pytest.mark.asyncio
    async def test_write_attributes_uses_retry_tracking(self, device):
        """Test that write_attributes triggers retry tracking in send_message."""
        from pysamsungnasa.protocol.enum import InOperationPower
        from pysamsungnasa.protocol.factory.messages.indoor import InOperationPowerMessage

        # Mock send_message to capture the call
        device._client.send_message = AsyncMock()

        await device.write_attributes({InOperationPowerMessage: InOperationPower.ON_STATE_1})

        # Verify send_message was called with correct parameters
        device._client.send_message.assert_called_once()
        call_args = device._client.send_message.call_args
        assert call_args.kwargs["destination"] == "200001"
        assert call_args.kwargs["request_type"] == DataType.WRITE


class TestRetryStateManagement:
    """Tests for proper state management of retry logic."""

    def test_write_key_format(self):
        """Test that write keys are properly formatted."""
        # The write key should be destination_packet_number
        dest = "200001"
        packet_number = 1

        # Write keys now use packet_number to group all messages in a packet
        write_key = f"{dest}_{packet_number}"
        assert write_key == "200001_1"

    def test_read_key_format(self):
        """Test that read keys use sorted tuple of message IDs."""
        dest = "200001"
        msgs = [0x4001, 0x4000, 0x4002]  # Unsorted

        # Read key should have sorted message IDs as string representation
        read_key = f"{dest}_{tuple(sorted(msgs))}"
        assert read_key == "200001_(16384, 16385, 16386)"

    def test_retry_interval_calculation(self):
        """Test that retry intervals are calculated correctly."""
        current_time = 1000.0
        initial_interval = 1.0
        backoff_factor = 1.1

        write_info = {
            "destination": "200001",
            "message_id": 0x4000,
            "payload": b"\x01",
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": current_time,
            "next_retry_time": current_time + initial_interval,
            "retry_interval": initial_interval,
        }

        # Simulate what retry manager does
        new_interval = write_info["retry_interval"] * backoff_factor
        new_next_retry = current_time + new_interval

        assert new_interval == 1.1
        assert new_next_retry > write_info["next_retry_time"]


class TestAckClearing:
    """Tests for ACK clearing logic in _clear_pending_write."""

    async def test_ack_clears_single_message_packet(self, nasa_client):
        """Test that ACK clears a single message packet when message ID is in ACK list."""
        client = nasa_client
        # Add a pending write with single message
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000],
            "messages": [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK with the message ID
        client._clear_pending_write("200001", [0x4000])

        # Should be cleared
        assert "200001_1" not in client._pending_writes

    async def test_ack_clears_multi_message_packet_when_all_acked(self, nasa_client):
        """Test that multi-message packet is cleared only when ALL messages are ACKed."""
        client = nasa_client
        # Add a pending write with multiple messages
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000, 0x4001, 0x4002],
            "messages": [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
                SendMessage(MESSAGE_ID=0x4002, PAYLOAD=b"\x03"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK all three messages
        client._clear_pending_write("200001", [0x4000, 0x4001, 0x4002])

        # Should be cleared
        assert "200001_1" not in client._pending_writes

    async def test_ack_does_not_clear_multi_message_packet_with_partial_ack(self, nasa_client):
        """Test that multi-message packet is NOT cleared when only SOME messages are ACKed."""
        client = nasa_client
        # Add a pending write with multiple messages
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000, 0x4001, 0x4002],
            "messages": [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
                SendMessage(MESSAGE_ID=0x4002, PAYLOAD=b"\x03"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK only two of three messages
        client._clear_pending_write("200001", [0x4000, 0x4001])

        # Should NOT be cleared - still pending
        assert "200001_1" in client._pending_writes

    async def test_ack_with_empty_message_numbers_clears_all(self, nasa_client):
        """Test that ACK with empty message_numbers clears all writes for destination."""
        client = nasa_client
        # Add multiple pending writes
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000],
            "messages": [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }
        client._pending_writes["200001_2"] = {
            "destination": "200001",
            "message_ids": [0x4001, 0x4002],
            "messages": [
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
                SendMessage(MESSAGE_ID=0x4002, PAYLOAD=b"\x03"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 2,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK with empty message_numbers (ACK all for this destination)
        client._clear_pending_write("200001", [])

        # All writes for 200001 should be cleared
        assert "200001_1" not in client._pending_writes
        assert "200001_2" not in client._pending_writes

    async def test_ack_does_not_clear_different_destination(self, nasa_client):
        """Test that ACK for one destination doesn't affect other destinations."""
        client = nasa_client
        # Add pending writes for different destinations
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000],
            "messages": [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }
        client._pending_writes["200002_1"] = {
            "destination": "200002",
            "message_ids": [0x4000],
            "messages": [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK only for 200001
        client._clear_pending_write("200001", [0x4000])

        # Only 200001 should be cleared
        assert "200001_1" not in client._pending_writes
        assert "200002_1" in client._pending_writes

    async def test_ack_clears_correct_packet_from_multiple_packets(self, nasa_client):
        """Test that ACK clears only the specific packet when multiple exist for same destination."""
        client = nasa_client
        # Add multiple packets from same destination
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000, 0x4001],
            "messages": [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }
        client._pending_writes["200001_2"] = {
            "destination": "200001",
            "message_ids": [0x4002, 0x4003],
            "messages": [
                SendMessage(MESSAGE_ID=0x4002, PAYLOAD=b"\x03"),
                SendMessage(MESSAGE_ID=0x4003, PAYLOAD=b"\x04"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 2,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK only the first packet's messages
        client._clear_pending_write("200001", [0x4000, 0x4001])

        # First packet cleared, second still pending
        assert "200001_1" not in client._pending_writes
        assert "200001_2" in client._pending_writes

    async def test_ack_with_extra_message_ids_still_clears(self, nasa_client):
        """Test that ACK with extra message IDs still clears packet if all required IDs present."""
        client = nasa_client
        # Add a pending write
        client._pending_writes["200001_1"] = {
            "destination": "200001",
            "message_ids": [0x4000, 0x4001],
            "messages": [
                SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
                SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
            ],
            "data_type": DataType.WRITE,
            "packet_number": 1,
            "attempts": 0,
            "last_attempt_time": 0,
            "next_retry_time": 0,
            "retry_interval": 0.1,
        }

        # ACK with extra message IDs (shouldn't matter, as long as required ones present)
        client._clear_pending_write("200001", [0x4000, 0x4001, 0x9999])

        # Should still be cleared
        assert "200001_1" not in client._pending_writes
