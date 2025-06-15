"""Message factory for NASA protocol."""

from typing import final
from abc import ABC
from enum import Enum

from ..enum import InOperationMode, InFanModeReal


class BaseMessage(ABC):
    """Base class for all NASA protocol messages."""

    def __init__(self, message_number: int, payload: bytes, description: str):
        self.message_number = message_number
        self.payload = payload
        self.value = None
        self.description = description

    @final
    def to_dict(self) -> dict:
        """Convert the parsed message into a dictionary."""
        return {
            "message_number": self.message_number,
            "description": self.description,
            "value": self.value.name if isinstance(self.value, Enum) else self.value,
        }


class InOperationModeMessage(BaseMessage):
    """Parser for message 0x4001 (Indoor Operation Mode)."""

    def __init__(self, message_number, payload, description):
        super().__init__(message_number, payload, description)
        self.value = InOperationMode(self.payload[0])


class InFanModeRealMessage(BaseMessage):
    """Parser for message 0x4007 (Indoor Fan Mode Real)."""

    def __init__(self, message_number, payload, description):
        super().__init__(message_number, payload, description)
        self.value = InFanModeReal(self.payload[0])


class BoolMessage(BaseMessage):
    """Parser for boolean messages."""

    def __init__(self, message_number, payload, description):
        super().__init__(message_number, payload, description)
        self.value = bool(self.payload[0])
