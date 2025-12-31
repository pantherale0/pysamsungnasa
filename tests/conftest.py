"""Pytest configuration and fixtures."""

import sys
from unittest.mock import MagicMock

# Mock aiotelnet since it requires Python 3.13+
sys.modules['aiotelnet'] = MagicMock()
