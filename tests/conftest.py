"""Pytest configuration and fixtures."""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from pysamsungnasa.config import NasaConfig
from pysamsungnasa.nasa_client import NasaClient

# Mock aiotelnet since it requires Python 3.13+
sys.modules["aiotelnet"] = MagicMock()


def _configure_connected_client(client: NasaClient) -> NasaClient:
    """Mark a NasaClient as connected with a usable writer mock."""
    client.writer = AsyncMock()
    # is_closing() is synchronous on real writers; AsyncMock would make it a coroutine
    # and break is_connected (coroutines are truthy).
    client.writer.is_closing = Mock(return_value=False)
    client.reader = AsyncMock()
    client._is_connected = True
    client._tx_queue = asyncio.Queue()
    client._rx_queue = asyncio.Queue()
    return client


@pytest.fixture(autouse=True)
def reset_parser_state():
    """Reset parser state between tests to ensure isolation."""
    yield
    # Cleanup after each test if needed


@pytest.fixture
async def nasa_client():
    """Create a basic test NasaClient with retry enabled."""
    config = NasaConfig(enable_write_retries=True, enable_read_retries=True, device_path="socket://localhost:8000")
    return _configure_connected_client(NasaClient(config=config))


@pytest.fixture
async def nasa_client_with_full_retry_config():
    """Create a NasaClient with full retry configuration."""
    config = NasaConfig(
        enable_write_retries=True,
        enable_read_retries=True,
        write_retry_interval=0.1,
        read_retry_interval=0.1,
        write_retry_max_attempts=3,
        read_retry_max_attempts=3,
        write_retry_backoff_factor=1.5,
        read_retry_backoff_factor=1.5,
        device_path="socket://localhost:8000",
    )
    return _configure_connected_client(NasaClient(config=config))


@pytest.fixture
async def nasa_client_write_only():
    """Create a NasaClient with only write retries enabled."""
    config = NasaConfig(enable_write_retries=True, enable_read_retries=False, device_path="socket://localhost:8000")
    return _configure_connected_client(NasaClient(config=config))


@pytest.fixture
async def nasa_client_read_only():
    """Create a NasaClient with only read retries enabled."""
    config = NasaConfig(enable_write_retries=False, enable_read_retries=True, device_path="socket://localhost:8000")
    return _configure_connected_client(NasaClient(config=config))
