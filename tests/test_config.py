"""Tests for NasaConfig."""

import pytest
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import Address


class TestNasaConfig:
    """Tests for NasaConfig dataclass."""

    def test_config_default_initialization(self):
        """Test NasaConfig with default values."""
        config = NasaConfig()
        assert config.client_address == 1
        assert config.device_dump_only is False
        assert config.device_pnp is False
        assert config.device_addresses == []
        assert config.max_buffer_size == 262144
        assert config.log_all_messages is False
        assert config.devices_to_log == []
        assert config.log_buffer_messages is False
        assert config.enable_read_retries is True
        assert config.read_retry_max_attempts == 3
        assert config.read_retry_interval == 1.0
        assert config.read_retry_backoff_factor == 1.1

    def test_config_custom_initialization(self):
        """Test NasaConfig with custom values."""
        config = NasaConfig(
            client_address=5,
            device_dump_only=True,
            device_pnp=True,
            device_addresses=["200001", "100000"],
            max_buffer_size=512000,
            log_all_messages=True,
            devices_to_log=["200001"],
            log_buffer_messages=True,
            enable_read_retries=False,
            read_retry_max_attempts=5,
            read_retry_interval=2.0,
            read_retry_backoff_factor=1.5,
        )
        assert config.client_address == 5
        assert config.device_dump_only is True
        assert config.device_pnp is True
        assert config.device_addresses == ["200001", "100000"]
        assert config.max_buffer_size == 512000
        assert config.log_all_messages is True
        assert config.devices_to_log == ["200001"]
        assert config.log_buffer_messages is True
        assert config.enable_read_retries is False
        assert config.read_retry_max_attempts == 5
        assert config.read_retry_interval == 2.0
        assert config.read_retry_backoff_factor == 1.5

    def test_config_address_property(self):
        """Test the address property."""
        config = NasaConfig(client_address=1)
        address = config.address
        assert isinstance(address, Address)
        assert address.class_id == 0x80
        assert address.channel == 0xFF
        assert address.address == 1

    def test_config_address_property_various_values(self):
        """Test address property with various client addresses."""
        test_cases = [1, 5, 10, 255]
        for client_addr in test_cases:
            config = NasaConfig(client_address=client_addr)
            address = config.address
            assert address.class_id == 0x80
            assert address.channel == 0xFF
            assert address.address == client_addr

    def test_config_address_string_representation(self):
        """Test that address property returns correct string representation."""
        config = NasaConfig(client_address=1)
        assert str(config.address) == "80FF01"

    def test_config_partial_initialization(self):
        """Test NasaConfig with only some custom values."""
        config = NasaConfig(
            client_address=3,
            log_all_messages=True,
            read_retry_max_attempts=10,
        )
        assert config.client_address == 3
        assert config.log_all_messages is True
        assert config.read_retry_max_attempts == 10
        # Check defaults for non-specified values
        assert config.device_dump_only is False
        assert config.device_pnp is False
        assert config.device_addresses == []

    def test_config_device_addresses_list(self):
        """Test device_addresses as a list."""
        addresses = ["200001", "200002", "100000"]
        config = NasaConfig(device_addresses=addresses)
        assert config.device_addresses == addresses
        assert len(config.device_addresses) == 3

    def test_config_devices_to_log_list(self):
        """Test devices_to_log as a list."""
        devices = ["200001", "200002"]
        config = NasaConfig(devices_to_log=devices)
        assert config.devices_to_log == devices
        assert len(config.devices_to_log) == 2

    def test_config_retry_settings(self):
        """Test retry-related settings."""
        config = NasaConfig(
            enable_read_retries=True,
            read_retry_max_attempts=5,
            read_retry_interval=2.5,
            read_retry_backoff_factor=2.0,
        )
        assert config.enable_read_retries is True
        assert config.read_retry_max_attempts == 5
        assert config.read_retry_interval == 2.5
        assert config.read_retry_backoff_factor == 2.0

    def test_config_buffer_settings(self):
        """Test buffer-related settings."""
        config = NasaConfig(max_buffer_size=1024000, log_buffer_messages=True)
        assert config.max_buffer_size == 1024000
        assert config.log_buffer_messages is True
