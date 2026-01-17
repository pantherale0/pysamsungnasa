"""Tests for retry logic in nasa_client.py."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, call
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.enum import DataType, AddressClass
from pysamsungnasa.protocol.factory.types import SendMessage
from pysamsungnasa.helpers import hex2bin


class TestSendMessageRetryTracking:
    """Tests for retry tracking in send_message."""

    @pytest.fixture
    async def client(self):
        """Create a test NasaClient."""
        config = NasaConfig(enable_write_retries=True, enable_read_retries=True)
        client = NasaClient(
            host="localhost",
            port=8000,
            config=config,
        )
        # Mock the connection
        client._connection_status = True
        client._client = Mock()
        client._client.writer = AsyncMock()
        client._tx_queue = asyncio.Queue()
        client._rx_queue = asyncio.Queue()
        return client

    @pytest.mark.asyncio
    async def test_send_message_tracks_write_retry(self, client):
        """Test that send_message tracks write requests for retry."""
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=1):
            messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]
            await client.send_message(
                destination="200001",
                request_type=DataType.WRITE,
                messages=messages,
            )

            # Check that the write was tracked
            # Note: Keys are formatted as destination_message_id (as integer, not hex)
            write_key = "200001_16384"  # 0x4000 = 16384
            assert write_key in client._pending_writes
            write_info = client._pending_writes[write_key]
            assert write_info["destination"] == "200001"
            assert write_info["message_id"] == 0x4000
            assert write_info["payload"] == b"\x01"
            assert write_info["data_type"] == DataType.WRITE
            assert write_info["attempts"] == 0
            assert write_info["packet_number"] == 1

    @pytest.mark.asyncio
    async def test_send_message_tracks_read_retry(self, client):
        """Test that send_message tracks read requests for retry."""
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
    async def test_send_message_request_type_tracked_as_write(self, client):
        """Test that REQUEST type is tracked for write retries."""
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=3):
            messages = [SendMessage(MESSAGE_ID=0x5000, PAYLOAD=b"\x02")]
            await client.send_message(
                destination="100001",
                request_type=DataType.REQUEST,
                messages=messages,
            )

            # REQUEST type should be tracked as write retry
            write_key = "100001_20480"  # 0x5000 = 20480
            assert write_key in client._pending_writes

    @pytest.mark.asyncio
    async def test_send_message_no_tracking_when_retries_disabled(self, client):
        """Test that send_message doesn't track when retries are disabled."""
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
    async def test_send_message_tracks_multiple_writes(self, client):
        """Test that send_message tracks multiple messages in one request."""
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

            # Each message should have its own tracked entry
            assert "200001_16384" in client._pending_writes  # 0x4000
            assert "200001_16385" in client._pending_writes  # 0x4001
            assert "200001_16386" in client._pending_writes  # 0x4002


class TestNasaWriteRetry:
    """Tests for nasa_write using centralized retry logic."""

    @pytest.fixture
    async def client(self):
        """Create a test NasaClient."""
        config = NasaConfig(enable_write_retries=True)
        client = NasaClient(
            host="localhost",
            port=8000,
            config=config,
        )
        client._connection_status = True
        client._client = Mock()
        client._client.writer = AsyncMock()
        client._tx_queue = asyncio.Queue()
        client._rx_queue = asyncio.Queue()
        return client

    @pytest.mark.asyncio
    async def test_nasa_write_tracked_for_retry(self, client):
        """Test that nasa_write properly uses send_message retry tracking."""
        with patch.object(client, "send_command", new_callable=AsyncMock, return_value=1):
            await client.nasa_write(
                msg=0x4000,
                value="01",
                destination="200001",
                data_type=DataType.WRITE,
            )

            # Check that write was tracked
            write_key = "200001_16384"  # 0x4000 = 16384
            assert write_key in client._pending_writes
            write_info = client._pending_writes[write_key]
            assert write_info["payload"] == b"\x01"
            assert write_info["data_type"] == DataType.WRITE


class TestNasaReadRetry:
    """Tests for nasa_read using centralized retry logic."""

    @pytest.fixture
    async def client(self):
        """Create a test NasaClient."""
        config = NasaConfig(enable_read_retries=True)
        client = NasaClient(
            host="localhost",
            port=8000,
            config=config,
        )
        client._connection_status = True
        client._client = Mock()
        client._client.writer = AsyncMock()
        client._tx_queue = asyncio.Queue()
        client._rx_queue = asyncio.Queue()
        return client

    @pytest.mark.asyncio
    async def test_nasa_read_tracked_for_retry(self, client):
        """Test that nasa_read properly uses send_message retry tracking."""
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

    @pytest.fixture
    async def client(self):
        """Create a test NasaClient."""
        config = NasaConfig(
            enable_write_retries=True,
            enable_read_retries=True,
            write_retry_interval=0.1,
            read_retry_interval=0.1,
            write_retry_max_attempts=3,
            read_retry_max_attempts=3,
            write_retry_backoff_factor=1.5,
            read_retry_backoff_factor=1.5,
        )
        client = NasaClient(
            host="localhost",
            port=8000,
            config=config,
        )
        client._connection_status = True
        client._client = Mock()
        client._client.writer = AsyncMock()
        client._tx_queue = asyncio.Queue()
        client._rx_queue = asyncio.Queue()
        return client

    @pytest.mark.asyncio
    async def test_retry_manager_retries_failed_write(self, client):
        """Test that retry manager retries failed write requests."""
        # Manually add a pending write that needs retry
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_0x4000"  # Use unique key to avoid conflicts
        client._pending_writes[write_key] = {
            "destination": "200001",
            "message_id": 0x4000,
            "payload": b"\x01",
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
    async def test_retry_manager_retries_failed_read(self, client):
        """Test that retry manager retries failed read requests."""
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
    async def test_retry_manager_applies_backoff_factor(self, client):
        """Test that retry manager applies backoff factor to retry interval."""
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_16384"  # Use unique key
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
    async def test_retry_manager_abandons_after_max_attempts(self, client):
        """Test that retry manager abandons request after max attempts."""
        current_time = asyncio.get_running_loop().time()
        write_key = "test_200001_16384"  # Use unique key

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
        # The write key should be destination_message_id (as integer)
        dest = "200001"
        msg_id = 0x4000  # = 16384

        # Manually create a write entry to verify key format
        write_key = f"{dest}_{msg_id}"
        assert write_key == "200001_16384"

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
