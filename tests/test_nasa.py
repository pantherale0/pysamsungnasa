"""Tests for nasa.py module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pysamsungnasa.nasa import SamsungNasa
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.enum import DataType, AddressClass


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
