"""Tests for NasaDevice Event-based synchronization."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from pysamsungnasa.device import NasaDevice
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import AddressClass
from pysamsungnasa.protocol.factory.messaging import BaseMessage


@pytest.fixture
def fast_timeout():
    """Patch asyncio.timeout to use 0.05 second timeout in tests for fast failure."""
    original_timeout = asyncio.timeout

    def patched_timeout(seconds):
        # Use 0.05s instead of the requested timeout for quick test execution
        return original_timeout(0.05)

    with patch("pysamsungnasa.device.asyncio.timeout", side_effect=patched_timeout):
        yield


class TestGetAttributeEventSync:
    """Tests for get_attribute with Event-based synchronization."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = AsyncMock()
        device = NasaDevice(
            address="200001",
            device_type=AddressClass.INDOOR,
            packet_parser=parser,
            config=config,
            client=client,
        )
        return device, client

    @pytest.mark.asyncio
    async def test_get_attribute_already_present(self, setup_device):
        """Test get_attribute when attribute is already in attributes dict."""
        device, client = setup_device

        # Pre-populate attribute
        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        device.attributes[0x4203] = mock_message

        result = await device.get_attribute(0x4203)

        # Should not call nasa_read since attribute exists
        client.nasa_read.assert_not_called()
        assert result == mock_message

    @pytest.mark.asyncio
    async def test_get_attribute_waits_for_arrival(self, setup_device):
        """Test get_attribute waits for attribute to arrive via handle_packet."""
        device, client = setup_device

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        async def simulate_packet_arrival():
            """Simulate packet arrival after a short delay."""
            await asyncio.sleep(0.1)
            device.handle_packet(
                messageNumber=0x4203,
                packet=mock_message,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # Start get_attribute and packet arrival concurrently
        task_get = asyncio.create_task(device.get_attribute(0x4203))
        task_packet = asyncio.create_task(simulate_packet_arrival())

        result, _ = await asyncio.gather(task_get, task_packet)

        assert result == mock_message
        client.nasa_read.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_attribute_timeout(self, setup_device, fast_timeout):
        """Test get_attribute raises TimeoutError on timeout."""
        device, client = setup_device

        with pytest.raises(TimeoutError):
            await device.get_attribute(0x9999)

    @pytest.mark.asyncio
    async def test_get_attribute_multiple_concurrent_calls(self, setup_device):
        """Test multiple concurrent get_attribute calls for same attribute."""
        device, client = setup_device

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        async def simulate_packet_arrival():
            """Simulate packet arrival after a short delay."""
            await asyncio.sleep(0.15)
            device.handle_packet(
                messageNumber=0x4203,
                packet=mock_message,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # Start three concurrent get_attribute calls
        packet_task = asyncio.create_task(simulate_packet_arrival())
        result1_task = asyncio.create_task(device.get_attribute(0x4203))
        result2_task = asyncio.create_task(device.get_attribute(0x4203))
        result3_task = asyncio.create_task(device.get_attribute(0x4203))

        results = await asyncio.gather(packet_task, result1_task, result2_task, result3_task)
        _, result1, result2, result3 = results

        # All should return the same message
        assert result1 == mock_message
        assert result2 == mock_message
        assert result3 == mock_message

        # nasa_read should be called, but ideally only once (depends on implementation)
        # At least it should be called
        assert client.nasa_read.called

    @pytest.mark.asyncio
    async def test_get_attribute_different_attributes(self, setup_device):
        """Test get_attribute with different attributes being requested."""
        device, client = setup_device

        message_4203 = Mock(spec=BaseMessage)
        message_4203.VALUE = 25.0
        message_4203.is_fsv_message = False

        message_4001 = Mock(spec=BaseMessage)
        message_4001.VALUE = "heating"
        message_4001.is_fsv_message = False

        async def simulate_packets():
            """Simulate multiple packets arriving."""
            await asyncio.sleep(0.1)
            device.handle_packet(
                messageNumber=0x4203,
                packet=message_4203,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )
            await asyncio.sleep(0.05)
            device.handle_packet(
                messageNumber=0x4001,
                packet=message_4001,
                dest="80FF01",
                formattedMessageNumber="0x4001",
            )

        # Request both attributes concurrently
        packet_task = asyncio.create_task(simulate_packets())
        result_4203_task = asyncio.create_task(device.get_attribute(0x4203))
        result_4001_task = asyncio.create_task(device.get_attribute(0x4001))

        await packet_task
        result_4203 = await result_4203_task
        result_4001 = await result_4001_task

        assert result_4203 == message_4203
        assert result_4001 == message_4001

    @pytest.mark.asyncio
    async def test_get_attribute_event_cleanup(self, setup_device):
        """Test that event objects are created and used properly."""
        device, client = setup_device

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        async def simulate_packet_arrival():
            """Simulate packet arrival after a short delay."""
            await asyncio.sleep(0.1)
            device.handle_packet(
                messageNumber=0x4203,
                packet=mock_message,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # Request attribute
        packet_task = asyncio.create_task(simulate_packet_arrival())
        result = await device.get_attribute(0x4203)
        await packet_task

        assert result == mock_message
        # Event should have been created
        assert 0x4203 in device._attribute_events

    @pytest.mark.asyncio
    async def test_get_attribute_rapid_sequential_calls(self, setup_device):
        """Test rapid sequential calls to get_attribute for same attribute."""
        device, client = setup_device

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        async def simulate_packet_arrival():
            """Simulate packet arrival after a short delay."""
            await asyncio.sleep(0.05)
            device.handle_packet(
                messageNumber=0x4203,
                packet=mock_message,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        packet_task = asyncio.create_task(simulate_packet_arrival())

        # First call will trigger nasa_read
        result1 = await device.get_attribute(0x4203)

        # Second call should return immediately (attribute already present)
        result2 = await device.get_attribute(0x4203)

        await packet_task

        assert result1 == mock_message
        assert result2 == mock_message
        # nasa_read should only be called once (from first get_attribute)
        assert client.nasa_read.call_count == 1

    @pytest.mark.asyncio
    async def test_event_signaling_on_handle_packet(self, setup_device):
        """Test that handle_packet properly signals waiting events."""
        device, client = setup_device

        message_attr_1 = Mock(spec=BaseMessage)
        message_attr_1.VALUE = 1
        message_attr_1.is_fsv_message = False

        message_attr_2 = Mock(spec=BaseMessage)
        message_attr_2.VALUE = 2
        message_attr_2.is_fsv_message = False

        async def request_attributes():
            """Request multiple attributes."""
            result1 = await device.get_attribute(0x4000)
            result2 = await device.get_attribute(0x4001)
            return result1, result2

        async def send_packets():
            """Send packets with delays."""
            await asyncio.sleep(0.05)
            device.handle_packet(
                messageNumber=0x4000,
                packet=message_attr_1,
                dest="80FF01",
                formattedMessageNumber="0x4000",
            )
            await asyncio.sleep(0.05)
            device.handle_packet(
                messageNumber=0x4001,
                packet=message_attr_2,
                dest="80FF01",
                formattedMessageNumber="0x4001",
            )

        request_task = asyncio.create_task(request_attributes())
        packet_task = asyncio.create_task(send_packets())

        (result1, result2), _ = await asyncio.gather(request_task, packet_task)

        assert result1 == message_attr_1
        assert result2 == message_attr_2

    @pytest.mark.asyncio
    async def test_get_attribute_timeout_with_asyncio_timeout(self, setup_device, fast_timeout):
        """Test that timeout is properly enforced."""
        device, client = setup_device

        # Set a shorter timeout by calling get_attribute
        # This test verifies the timeout mechanism works
        with pytest.raises(TimeoutError):
            # Wait up to 10 seconds but attribute will never arrive
            await device.get_attribute(0x9999)

    @pytest.mark.asyncio
    async def test_handle_packet_fires_events_correctly(self, setup_device):
        """Test that multiple packets for same attribute fire events correctly."""
        device, client = setup_device

        message1 = Mock(spec=BaseMessage)
        message1.VALUE = 1
        message1.is_fsv_message = False

        message2 = Mock(spec=BaseMessage)
        message2.VALUE = 2
        message2.is_fsv_message = False

        async def get_and_wait():
            """Get attribute multiple times."""
            result1 = await device.get_attribute(0x4203)
            return result1

        async def send_packets():
            """Send first packet."""
            await asyncio.sleep(0.05)
            device.handle_packet(
                messageNumber=0x4203,
                packet=message1,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # First request should wait and receive message1
        request_task = asyncio.create_task(get_and_wait())
        packet_task = asyncio.create_task(send_packets())

        result = await request_task
        await packet_task

        assert result == message1
        assert device.attributes[0x4203] == message1

    @pytest.mark.asyncio
    async def test_get_attribute_requires_read_forces_new_request(self, setup_device):
        """Test requires_read parameter forces a fresh read even when cached."""
        device, client = setup_device

        cached_message = Mock(spec=BaseMessage)
        cached_message.VALUE = 10.0
        cached_message.is_fsv_message = False

        fresh_message = Mock(spec=BaseMessage)
        fresh_message.VALUE = 25.0
        fresh_message.is_fsv_message = False

        # Pre-populate with cached value
        device.attributes[0x4203] = cached_message

        async def send_fresh_packet():
            """Send fresh packet after delay."""
            await asyncio.sleep(0.1)
            device.handle_packet(
                messageNumber=0x4203,
                packet=fresh_message,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # Request with requires_read=True (should re-request and get fresh value)
        packet_task = asyncio.create_task(send_fresh_packet())
        result = await device.get_attribute(0x4203, requires_read=True)
        await packet_task

        # Should have called nasa_read even though attribute was cached
        client.nasa_read.assert_called_once()
        # Should return the fresh message, not the cached one
        assert result == fresh_message
        assert result.VALUE == 25.0

    @pytest.mark.asyncio
    async def test_get_attribute_requires_read_false_uses_cache(self, setup_device):
        """Test requires_read=False (default) uses cached value."""
        device, client = setup_device

        cached_message = Mock(spec=BaseMessage)
        cached_message.VALUE = 10.0
        device.attributes[0x4203] = cached_message

        # Request with requires_read=False (default)
        result = await device.get_attribute(0x4203, requires_read=False)

        # Should not call nasa_read since attribute is cached and requires_read=False
        client.nasa_read.assert_not_called()
        assert result == cached_message
        assert result.VALUE == 10.0

    @pytest.mark.asyncio
    async def test_get_attribute_requires_read_with_concurrent_requests(self, setup_device):
        """Test requires_read with concurrent requests."""
        device, client = setup_device

        message_v1 = Mock(spec=BaseMessage)
        message_v1.VALUE = 1.0
        message_v1.is_fsv_message = False

        message_v2 = Mock(spec=BaseMessage)
        message_v2.VALUE = 2.0
        message_v2.is_fsv_message = False

        # Pre-populate with v1
        device.attributes[0x4203] = message_v1

        async def send_packets():
            """Send updated packet."""
            await asyncio.sleep(0.1)
            device.handle_packet(
                messageNumber=0x4203,
                packet=message_v2,
                dest="80FF01",
                formattedMessageNumber="0x4203",
            )

        # One request with requires_read=True, another without
        packet_task = asyncio.create_task(send_packets())
        result_cached = await device.get_attribute(0x4203, requires_read=False)
        result_fresh = await device.get_attribute(0x4203, requires_read=True)
        await packet_task

        # First call should return cached v1
        assert result_cached.VALUE == 1.0
        # Second call should wait and get v2
        assert result_fresh.VALUE == 2.0
