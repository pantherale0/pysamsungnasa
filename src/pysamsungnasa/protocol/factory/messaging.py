"""Message factory for NASA protocol."""

from __future__ import annotations

from typing import final, ClassVar, Optional, Any
from abc import ABC
from enum import Enum


class BaseMessage(ABC):
    """Base class for all NASA protocol messages."""

    MESSAGE_ID: ClassVar[Optional[int]] = None
    MESSAGE_NAME: ClassVar[Optional[str]] = None
    MESSAGE_ENUM: ClassVar[Optional[type[Enum]]] = None

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into a usable format."""
        return {}


class BoolMessage(BaseMessage):
    """Parser for boolean messages."""

    @classmethod
    def parse_payload(cls, payload: bytes):
        """Parse the payload into a boolean value."""
        return {
            "message": cls.MESSAGE_NAME,
            "value": bool(payload[0]),
        }


class StrMessage(BaseMessage):
    """Parser for str messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into a string value."""
        return {
            "message": cls.MESSAGE_NAME,
            "value": payload.decode("utf-8") if payload else None,
        }


class RawMessage(BaseMessage):
    """Parser for raw messages."""

    MESSAGE_NAME = "UNKNOWN"

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into a raw hex string."""
        return {
            "message": cls.MESSAGE_NAME,
            "value": payload.hex() if payload else None,
        }


class EnumMessage(BaseMessage):
    """Parser for enum messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into an enum value."""
        if cls.MESSAGE_ENUM is None:
            raise ValueError(f"{cls.__name__} does not have a MESSAGE_ENUM defined.")
        return {
            "message": cls.MESSAGE_NAME,
            "value": cls.MESSAGE_ENUM(payload[0]) if payload else None,
        }
