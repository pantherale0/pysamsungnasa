"""Tests for nasa.py module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pysamsungnasa.nasa import SamsungNasa
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.enum import DataType, AddressClass
from pysamsungnasa.helpers import hex2bin


class TestSamsungNasa:
    """Tests for SamsungNasa class."""

    def test_samsung_nasa_initialization(self):
        """Test SamsungNasa initialization."""
        with patch("pysamsungnasa.nasa.NasaClient"):
            nasa = SamsungNasa(
                host="192.168.1.100", port=8888, config={}, new_device_event_handler=None, disconnect_event_handler=None
            )

            assert nasa.config is not None
            assert isinstance(nasa.config, NasaConfig)
            assert nasa.devices == {}

    def test_add_device_indoor(self):
        """Test adding an indoor device."""
        with patch("pysamsungnasa.nasa.NasaClient"):
            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8888,
                config={},
            )

            device = nasa._add_device("200001")

            assert "200001" in nasa.devices
            assert device is not None
            assert device.device_type == AddressClass.INDOOR

    def test_add_device_outdoor(self):
        """Test adding an outdoor device."""
        with patch("pysamsungnasa.nasa.NasaClient"):
            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8888,
                config={},
            )

            device = nasa._add_device("100001")

            assert "100001" in nasa.devices
            assert device is not None
            assert device.device_type == AddressClass.OUTDOOR

    @pytest.mark.asyncio
    async def test_add_device_from_config(self):
        """Test adding devices from config."""
        with patch("pysamsungnasa.nasa.NasaClient"):
            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8888,
                config={"device_addresses": ["200001", "100001"]},
            )

            assert "200001" in nasa.devices
            assert "100001" in nasa.devices

            indoor_device = nasa.devices["200001"]
            outdoor_device = nasa.devices["100001"]
            assert indoor_device.device_type == AddressClass.INDOOR
            assert outdoor_device.device_type == AddressClass.OUTDOOR

            # Test that packets from each device are processed correctly
            # Indoor device packet: source=200001, dest=80FF01, response with message 0x4000 (power=on)
            indoor_packet = "200001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
            await nasa.parser.parse_packet(hex2bin(indoor_packet))

            # Verify indoor device received the packet (attribute 0x4000 should be present)
            assert 0x4000 in indoor_device.attributes
            assert outdoor_device.attributes == {}  # Outdoor device should not have received it

            # Outdoor device packet: source=100001, dest=80FF01, response with message 0x4000 (power=on)
            outdoor_packet = "100001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
            await nasa.parser.parse_packet(hex2bin(outdoor_packet))

            # Verify outdoor device received the packet
            assert 0x4000 in outdoor_device.attributes
            # Indoor device should still only have the one attribute from before
            assert len(indoor_device.attributes) == 1

    @pytest.mark.asyncio
    async def test_start(self):
        """Test start method."""
        with patch("pysamsungnasa.nasa.NasaClient") as mock_client_class:
            mock_client_instance = Mock()
            # Set up async methods that need to be awaited
            mock_client_instance.connect = AsyncMock()
            mock_client_instance.disconnect = AsyncMock()
            # Set up non-async methods
            mock_client_instance.set_receive_event_handler = Mock()
            mock_client_instance._mark_read_received = Mock()
            mock_client_class.return_value = mock_client_instance

            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8888,
                config={},
            )

            await nasa.start()
            mock_client_instance.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stop method."""
        with patch("pysamsungnasa.nasa.NasaClient") as mock_client_class:
            mock_client_instance = Mock()
            # Set up async methods that need to be awaited
            mock_client_instance.connect = AsyncMock()
            mock_client_instance.disconnect = AsyncMock()
            # Set up non-async methods
            mock_client_instance.set_receive_event_handler = Mock()
            mock_client_instance._mark_read_received = Mock()
            mock_client_class.return_value = mock_client_instance

            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8888,
                config={},
            )

            await nasa.stop()
            mock_client_instance.disconnect.assert_called_once()
