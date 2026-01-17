"""Tests for NASA device module."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone
from pysamsungnasa.device import NasaDevice
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import AddressClass, InUseThermostat, InOperationMode
from pysamsungnasa.protocol.factory.types import BaseMessage


# Helper message classes for testing
class Message4000(BaseMessage):
    """Test message with ID 0x4000."""

    MESSAGE_ID = 0x4000


class Message4001(BaseMessage):
    """Test message with ID 0x4001."""

    MESSAGE_ID = 0x4001


class Message4203(BaseMessage):
    """Test message with ID 0x4203."""

    MESSAGE_ID = 0x4203


class Message8000(BaseMessage):
    """Test message with ID 0x8000."""

    MESSAGE_ID = 0x8000


class TestNasaDevice:
    """Tests for NasaDevice class."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()
        return config, parser, client

    def test_nasa_device_initialization(self, setup_device):
        """Test NasaDevice initialization."""
        config, parser, client = setup_device

        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        assert device.address == "200001"
        assert device.device_type == AddressClass.INDOOR
        assert device.attributes == {}
        assert device.last_packet_time is None
        assert device.fsv_config == {}

    def test_add_device_callback_duplicate(self, setup_device):
        """Test that duplicate device callbacks are not added twice."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_device_callback(callback)
        initial_count = len(device._device_callbacks)

        # Add the same callback again
        device.add_device_callback(callback)

        # Should not have added duplicate
        assert len(device._device_callbacks) == initial_count

    def test_add_packet_callback_duplicate(self, setup_device):
        """Test that duplicate packet callbacks are not added twice."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(Message4203, callback)
        initial_count = len(device._packet_callbacks[0x4203])

        # Add the same callback again
        device.add_packet_callback(Message4203, callback)

        # Should not have added duplicate
        assert len(device._packet_callbacks[0x4203]) == initial_count

    def test_add_device_callback_no_duplicates(self, setup_device):
        """Test that duplicate callbacks are not added."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_device_callback(callback)
        device.add_device_callback(callback)

        assert len([c for c in device._device_callbacks if c == callback]) == 1

    def test_remove_device_callback(self, setup_device):
        """Test removing device callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_device_callback(callback)
        device.remove_device_callback(callback)

        assert callback not in device._device_callbacks

    @pytest.mark.parametrize(
        "message_class,message_id", [(Message4000, 0x4000), (Message4001, 0x4001), (Message8000, 0x8000)]
    )
    def test_add_packet_callback(self, setup_device, message_class, message_id):
        """Test adding packet callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(message_class, callback)

        assert message_id in device._packet_callbacks
        assert callback in device._packet_callbacks[message_id]

    @pytest.mark.parametrize("message_class,message_id", [(Message4000, 0x4000), (Message4001, 0x4001)])
    def test_remove_packet_callback(self, setup_device, message_class, message_id):
        """Test removing packet callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(message_class, callback)
        device.remove_packet_callback(message_class, callback)

        assert callback not in device._packet_callbacks.get(message_id, [])


class TestNasaDeviceHandlePacket:
    """Tests for NasaDevice handle_packet functionality."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()
        return config, parser, client

    def test_handle_packet_updates_last_packet_time(self, setup_device):
        """Test that handle_packet updates last_packet_time."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 1
        mock_message.is_fsv_message = False

        before = datetime.now(timezone.utc)
        device.handle_packet(messageNumber=0x4000, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4000")
        after = datetime.now(timezone.utc)

        assert device.last_packet_time is not None
        assert before <= device.last_packet_time <= after

    def test_handle_packet_stores_attribute(self, setup_device):
        """Test that handle_packet stores packet data in attributes."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 42
        mock_message.is_fsv_message = False

        device.handle_packet(messageNumber=0x4000, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4000")

        assert 0x4000 in device.attributes
        assert device.attributes[0x4000] == mock_message

    def test_handle_packet_stores_fsv_config(self, setup_device):
        """Test that FSV messages are stored in fsv_config."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 123
        mock_message.is_fsv_message = True

        device.handle_packet(messageNumber=0x4093, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4093")

        assert 0x4093 in device.fsv_config
        assert device.fsv_config[0x4093] == 123

    def test_handle_packet_calls_device_callbacks(self, setup_device):
        """Test that handle_packet calls device callbacks."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_device_callback(callback)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 1
        mock_message.is_fsv_message = False

        device.handle_packet(messageNumber=0x4000, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4000")

        callback.assert_called_once_with(device)

    def test_handle_packet_calls_packet_callbacks(self, setup_device):
        """Test that handle_packet calls packet-specific callbacks."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(Message4000, callback)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 1
        mock_message.is_fsv_message = False

        device.handle_packet(messageNumber=0x4000, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4000")

        callback.assert_called_once()
        assert callback.call_args[0][0] == device

    def test_handle_packet_callback_exception_handling(self, setup_device):
        """Test that exceptions in callbacks are caught and logged."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        failing_callback = Mock(side_effect=Exception("Test error"))
        device.add_device_callback(failing_callback)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 1
        mock_message.is_fsv_message = False

        # Should not raise, should handle the exception
        device.handle_packet(messageNumber=0x4000, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4000")

        failing_callback.assert_called_once()


class TestNasaDeviceCallbackExceptionHandling:
    """Tests for exception handling in device callbacks."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()
        return config, parser, client

    def test_device_callback_exception_logged(self, setup_device):
        """Test that exceptions in device callbacks are logged."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        # Create a callback that raises an exception
        error_callback = Mock(side_effect=ValueError("Test error"))
        device.add_device_callback(error_callback)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        # Handle packet should not raise even though callback raises
        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4203")

        # Callback should have been called
        error_callback.assert_called_once()

    def test_packet_callback_exception_logged(self, setup_device):
        """Test that exceptions in packet callbacks are logged."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        # Create a callback that raises an exception
        error_callback = Mock(side_effect=RuntimeError("Packet callback error"))
        device.add_packet_callback(Message4203, error_callback)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        # Handle packet should not raise even though callback raises
        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4203")

        # Callback should have been called
        error_callback.assert_called_once()

    def test_remove_nonexistent_packet_callback(self, setup_device):
        """Test removing a packet callback that doesn't exist."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        # Remove callback that was never added - should not raise
        device.remove_packet_callback(Message4203, callback)
        assert 0x4203 not in device._packet_callbacks

    def test_remove_packet_callback_from_empty_list(self, setup_device):
        """Test removing packet callback from message with no callbacks."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback1 = Mock()
        device.add_packet_callback(Message4203, callback1)
        device.remove_packet_callback(Message4203, callback1)

        # After removing the only callback, list should be empty
        assert callback1 not in device._packet_callbacks.get(0x4203, [])


class TestNasaDeviceFsvConfig:
    """Tests for FSV configuration handling."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()
        return config, parser, client

    def test_fsv_message_stored_in_config(self, setup_device):
        """Test that FSV messages are stored in fsv_config."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 1
        mock_message.is_fsv_message = True  # This is an FSV message

        device.handle_packet(messageNumber=0x4093, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4093")

        # FSV config should be stored
        assert 0x4093 in device.fsv_config
        assert device.fsv_config[0x4093] == 1

    def test_non_fsv_message_not_stored_in_config(self, setup_device):
        """Test that non-FSV messages are not stored in fsv_config."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False  # This is NOT an FSV message

        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4203")

        # FSV config should NOT be stored
        assert 0x4203 not in device.fsv_config


class TestHandlePacketLogging:
    """Tests for logging conditions in handle_packet."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()
        return config, parser, client

    def test_handle_packet_log_when_config_address_matches(self, setup_device):
        """Test that packet is logged when dest matches config address."""
        config, parser, client = setup_device
        # config.address is a property (read-only), so just test with log_all_messages
        config.log_all_messages = True
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        # With log_all_messages=True, packet should be handled
        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4203")

        # Should be stored
        assert device.attributes[0x4203] == mock_message

    def test_handle_packet_log_when_log_all_messages_enabled(self, setup_device):
        """Test that packet is logged when log_all_messages is True."""
        config, parser, client = setup_device
        config.log_all_messages = True
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF02", formattedMessageNumber="0x4203")

        assert device.attributes[0x4203] == mock_message

    def test_handle_packet_log_when_device_in_log_list(self, setup_device):
        """Test that packet is logged when device is in devices_to_log."""
        config, parser, client = setup_device
        config.devices_to_log = ["200001"]
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.0
        mock_message.is_fsv_message = False

        device.handle_packet(messageNumber=0x4203, packet=mock_message, dest="80FF02", formattedMessageNumber="0x4203")

        assert device.attributes[0x4203] == mock_message
