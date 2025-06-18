"""Outdoor unit messages."""

from ..messaging import EnumMessage
from ...enum import OutdoorOperationStatus


class OutdoorOperationStatusMessage(EnumMessage):
    """Parser for message 0x8001 (Outdoor Operation Status)."""

    MESSAGE_ID = 0x8001
    MESSAGE_NAME = "Outdoor Operation Status"
    MESSAGE_ENUM = OutdoorOperationStatus
