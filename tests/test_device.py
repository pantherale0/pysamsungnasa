"""Tests for NASA device module."""

import pytest
from unittest.mock import Mock, AsyncMock
from pysamsungnasa.device import NasaDevice, IndoorNasaDevice, OutdoorNasaDevice
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import AddressClass
from pysamsungnasa.protocol.factory.messaging import BaseMessage


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

    def test_add_device_callback(self, setup_device):
        """Test adding device callback."""
        config, parser, client = setup_device
        device = NasaDevice(
            address="200001", device_type=AddressClass.INDOOR, packet_parser=parser, config=config, client=client
        )

        callback = Mock()
        device.add_device_callback(callback)

        assert callback in device._device_callbacks

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
