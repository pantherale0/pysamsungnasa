"""Pytest configuration and fixtures."""

import sys
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, Mock
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.config import NasaConfig

# Mock aiotelnet since it requires Python 3.13+
sys.modules["aiotelnet"] = MagicMock()


@pytest.fixture(autouse=True)
def reset_parser_state():
    """Reset parser state between tests to ensure isolation."""
    yield
    # Cleanup after each test if needed


@pytest.fixture
async def nasa_client():
    """Create a basic test NasaClient with retry enabled."""
    config = NasaConfig(enable_write_retries=True, enable_read_retries=True)
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


@pytest.fixture
async def nasa_client_write_only():
    """Create a NasaClient with only write retries enabled."""
    config = NasaConfig(enable_write_retries=True, enable_read_retries=False)
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


@pytest.fixture
async def nasa_client_read_only():
    """Create a NasaClient with only read retries enabled."""
    config = NasaConfig(enable_write_retries=False, enable_read_retries=True)
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
