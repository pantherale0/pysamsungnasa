"""Pytest configuration and fixtures."""

import sys
import pytest
from unittest.mock import MagicMock

# Mock aiotelnet since it requires Python 3.13+
sys.modules['aiotelnet'] = MagicMock()


@pytest.fixture(autouse=True)
def reset_parser_state():
    """Reset parser state between tests to ensure isolation."""
    yield
    # Cleanup after each test if needed
