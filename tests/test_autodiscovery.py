"""Tests for autodiscovery module."""

import pytest
from unittest.mock import AsyncMock
from pysamsungnasa.autodiscovery import request_network_address, nasa_poke


class TestAutodiscovery:
    """Tests for autodiscovery functions."""

    @pytest.mark.asyncio
    async def test_request_network_address(self):
        """Test request_network_address function."""
        mock_client = AsyncMock()
        
        await request_network_address(mock_client)
        
        # Verify send_command was called
        assert mock_client.send_command.called

    @pytest.mark.asyncio
    async def test_nasa_poke(self):
        """Test nasa_poke function."""
        mock_nasa_client = AsyncMock()
        
        await nasa_poke(mock_nasa_client)
        
        # Verify send_message was called
        assert mock_nasa_client.send_message.called
