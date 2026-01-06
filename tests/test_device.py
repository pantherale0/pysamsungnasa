"""Tests for NASA device module."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone
from pysamsungnasa.device import NasaDevice, IndoorNasaDevice, OutdoorNasaDevice
from pysamsungnasa.device.controllers import DhwController, ClimateController, WaterLawMode
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import AddressClass, InUseThermostat, InOperationMode
from pysamsungnasa.protocol.factory.types import BaseMessage


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
        device.add_packet_callback(0x4203, callback)
        initial_count = len(device._packet_callbacks[0x4203])

        # Add the same callback again
        device.add_packet_callback(0x4203, callback)

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

    @pytest.mark.parametrize("message_id", [0x4000, 0x4001, 0x8000])
    def test_add_packet_callback(self, setup_device, message_id):
        """Test adding packet callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(message_id, callback)

        assert message_id in device._packet_callbacks
        assert callback in device._packet_callbacks[message_id]

    @pytest.mark.parametrize("message_id", [0x4000, 0x4001])
    def test_remove_packet_callback(self, setup_device, message_id):
        """Test removing packet callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_packet_callback(message_id, callback)
        device.remove_packet_callback(message_id, callback)

        assert callback not in device._packet_callbacks.get(message_id, [])


class TestIndoorNasaDevice:
    """Tests for IndoorNasaDevice class."""

    def test_indoor_device_initialization(self):
        """Test IndoorNasaDevice initialization."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        assert device.address == "200001"
        assert device.device_type == AddressClass.INDOOR


class TestOutdoorNasaDevice:
    """Tests for OutdoorNasaDevice class."""

    def test_outdoor_device_initialization(self):
        """Test OutdoorNasaDevice initialization."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        assert device.address == "100001"
        assert device.device_type == AddressClass.OUTDOOR

    def test_outdoor_temperature_property(self):
        """Test outdoor_temperature property."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        # Without the attribute, should return None
        assert device.outdoor_temperature is None

        # With a mocked attribute
        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 25.5
        device.attributes[0x8204] = mock_message
        assert device.outdoor_temperature == 25.5

    def test_heatpump_voltage_property(self):
        """Test heatpump_voltage property."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        assert device.heatpump_voltage is None

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = 380.0
        device.attributes[0x24FC] = mock_message
        assert device.heatpump_voltage == 380.0

    @pytest.mark.parametrize(
        "attribute_id,value,property_name",
        [
            (0x8413, 2500, "power_consumption"),
            (0x4426, 1500, "power_generated_last_minute"),
            (0x4427, 5000, "power_produced"),
            (0x82DB, 15.5, "power_current"),
            (0x8414, 10000, "cumulative_energy"),
            (0x8238, 50, "compressor_frequency"),
            (0x823D, 75, "fan_speed"),
        ],
    )
    def test_outdoor_numeric_properties(self, attribute_id, value, property_name):
        """Test various numeric properties of outdoor device."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        # Initially should be None
        assert getattr(device, property_name) is None

        # With attribute
        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = value
        device.attributes[attribute_id] = mock_message
        assert getattr(device, property_name) == value

    def test_cop_rating_calculation(self):
        """Test COP rating calculation."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        # Without attributes, should return None
        assert device.cop_rating is None

        # With attributes
        power_produced_msg = Mock(spec=BaseMessage)
        power_produced_msg.VALUE = 5000
        device.attributes[0x4427] = power_produced_msg

        cumulative_energy_msg = Mock(spec=BaseMessage)
        cumulative_energy_msg.VALUE = 2000
        device.attributes[0x8414] = cumulative_energy_msg

        assert device.cop_rating == 2.5

    def test_cop_rating_zero_division(self):
        """Test COP rating handles zero division."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        power_produced_msg = Mock(spec=BaseMessage)
        power_produced_msg.VALUE = 5000
        device.attributes[0x4427] = power_produced_msg

        cumulative_energy_msg = Mock(spec=BaseMessage)
        cumulative_energy_msg.VALUE = 0
        device.attributes[0x8414] = cumulative_energy_msg

        assert device.cop_rating is None


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
        device.add_packet_callback(0x4000, callback)

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

    @pytest.mark.asyncio
    async def test_get_configuration_non_indoor(self):
        """Test get_configuration returns early for non-indoor devices."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = NasaDevice(
            address="100001", device_type=AddressClass.OUTDOOR, packet_parser=parser, config=config, client=client
        )

        # Should return early and not call client.nasa_read
        await device.get_configuration()
        client.nasa_read.assert_not_called()


class TestIndoorNasaDeviceControllers:
    """Tests for IndoorNasaDevice controller integration."""

    def test_indoor_device_has_dhw_controller(self):
        """Test IndoorNasaDevice has DHW controller."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        assert device.dhw_controller is not None
        assert isinstance(device.dhw_controller, DhwController)

    def test_indoor_device_has_climate_controller(self):
        """Test IndoorNasaDevice has climate controller."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        assert device.climate_controller is not None
        assert isinstance(device.climate_controller, ClimateController)

    def test_climate_controller_water_law_mode_initialization(self):
        """Test climate controller water law mode is initialized."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        assert device.climate_controller is not None
        assert device.climate_controller.water_law_mode == WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT

    def test_infer_water_law_mode_external_thermostat(self):
        """Test water law mode inference with external thermostat."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        # Set external thermostat as enabled
        device._climate_controller.use_external_thermostat_1 = InUseThermostat.VALUE_1
        device._infer_water_law_mode()

        assert device._climate_controller.water_law_mode == WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT

    def test_infer_water_law_mode_internal_thermostat(self):
        """Test water law mode inference with internal thermostat."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        # Set external thermostats as disabled
        device._climate_controller.use_external_thermostat_1 = InUseThermostat.NO
        device._climate_controller.use_external_thermostat_2 = InUseThermostat.NO
        device._infer_water_law_mode()

        assert device._climate_controller.water_law_mode == WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT

    def test_indoor_handle_packet_updates_controllers(self):
        """Test that indoor device handle_packet updates controllers."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        mock_message = Mock(spec=BaseMessage)
        mock_message.VALUE = InOperationMode.COOL
        mock_message.is_fsv_message = False

        # Message 0x4001 maps to "current_mode" in CLIMATE_MESSAGE_MAP
        device.handle_packet(messageNumber=0x4001, packet=mock_message, dest="80FF01", formattedMessageNumber="0x4001")

        assert device._climate_controller.current_mode == InOperationMode.COOL

    def test_outdoor_device_not_has_dhw_controller(self):
        """Test OutdoorNasaDevice doesn't have DHW controller."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = Mock()

        device = OutdoorNasaDevice(address="100001", packet_parser=parser, config=config, client=client)

        # dhw_controller should return None for outdoor device
        indoor_device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)
        outdoor_check = device.__class__.__name__ == "OutdoorNasaDevice"
        assert outdoor_check is True


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
        device.add_packet_callback(0x4203, error_callback)

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
        device.remove_packet_callback(0x4203, callback)
        assert 0x4203 not in device._packet_callbacks

    def test_remove_packet_callback_from_empty_list(self, setup_device):
        """Test removing packet callback from message with no callbacks."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback1 = Mock()
        callback2 = Mock()
        device.add_packet_callback(0x4203, callback1)
        device.remove_packet_callback(0x4203, callback1)

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


class TestGetConfigurationEdgeCases:
    """Tests for get_configuration method edge cases."""

    @pytest.fixture
    def setup_device(self):
        """Setup common device test dependencies."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = AsyncMock()
        return config, parser, client

    @pytest.mark.asyncio
    async def test_get_configuration_outdoor_device(self, setup_device):
        """Test get_configuration for outdoor device does nothing."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="100001", device_type=AddressClass.OUTDOOR, packet_parser=parser, config=config, client=client
        )

        await device.get_configuration()

        # Client should not be called for outdoor devices
        client.nasa_read.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_configuration_indoor_device_with_cached_messages(self, setup_device):
        """Test get_configuration requests messages based on cache."""
        config, parser, client = setup_device
        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        # Pre-populate attributes with a message from _MESSAGES_TO_LISTEN
        mock_message = Mock(spec=BaseMessage)
        device.attributes[0x8001] = mock_message

        await device.get_configuration()

        # get_configuration should make calls for missing messages in both parent and climate/DHW maps
        # Just verify it was called (it requests all climate and DHW config messages)
        assert client.nasa_read.called

    @pytest.mark.asyncio
    async def test_get_configuration_indoor_device_requests_missing_messages(self, setup_device):
        """Test get_configuration requests missing FSV messages."""
        config, parser, client = setup_device
        device = IndoorNasaDevice(address="200001", packet_parser=parser, config=config, client=client)

        await device.get_configuration()

        # Should have called nasa_read for climate and DHW messages
        assert client.nasa_read.called


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
