"""Message factory for NASA protocol."""

from __future__ import annotations

from dataclasses import dataclass

from typing import final, ClassVar, Optional, Any
import struct
from abc import ABC
from enum import Enum


@dataclass
class SendMessage:
    """Base class that represents all sent NASA messages."""

    MESSAGE_ID: int
    PAYLOAD: bytes


class BaseMessage(ABC):
    """Base class for all NASA protocol messages."""

    MESSAGE_ID: ClassVar[Optional[int]] = None
    MESSAGE_NAME: ClassVar[Optional[str]] = None
    MESSAGE_ENUM: ClassVar[Optional[type[Enum]]] = None
    UNIT_OF_MEASUREMENT: ClassVar[Optional[str]] = None

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
            "uom": cls.UNIT_OF_MEASUREMENT,
            "value": bool(payload[0]),
        }


class StrMessage(BaseMessage):
    """Parser for str messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into a string value."""
        return {
            "message": cls.MESSAGE_NAME,
            "uom": cls.UNIT_OF_MEASUREMENT,
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
            "uom": cls.UNIT_OF_MEASUREMENT,
            "value": payload.hex() if payload else None,
        }


class FloatMessage(BaseMessage):
    """Parser for a float message."""

    ARITHMETIC: ClassVar[float] = 0
    SIGNED: ClassVar[bool] = True

    @classmethod
    def parse_payload(cls, payload: bytes) -> dict:
        """Parse the payload into a float value."""
        parsed_value: float | None = None
        if payload:
            raw_int_value: int
            payload_len = len(payload)
            try:
                # Determine format string based on length and signedness
                if payload_len == 1:
                    # 1-byte values are typically handled by EnumMessage/BoolMessage,
                    # but handle here defensively if needed. Assume signed if not specified.
                    fmt = ">b" if cls.SIGNED else ">B"
                elif payload_len == 2:
                    fmt = ">h" if cls.SIGNED else ">H"
                elif payload_len == 4:
                    fmt = ">l" if cls.SIGNED else ">L"
                else:
                    raise ValueError(
                        f"Unsupported payload length for {cls.__name__}: {payload_len} bytes. "
                        f"Expected 1, 2, or 4. Payload: {payload.hex()}"
                    )
                raw_int_value = struct.unpack(fmt, payload)[0]
                parsed_value = float(raw_int_value) * cls.ARITHMETIC
            except struct.error as e:
                raise ValueError(f"Error unpacking payload for {cls.__name__}: {e}. Payload: {payload.hex()}") from e
            except ValueError as e:
                raise ValueError(f"Error processing payload for {cls.__name__}: {e}") from e

        return {
            "message": cls.MESSAGE_NAME,
            "uom": cls.UNIT_OF_MEASUREMENT,
            "value": parsed_value,
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
            "uom": cls.UNIT_OF_MEASUREMENT,
            "value": cls.MESSAGE_ENUM(payload[0]) if payload else None,
            "options": {option.name: option.value for option in cls.MESSAGE_ENUM},
        }


class BasicTemperatureMessage(FloatMessage):
    """Parser for basic temperature messages."""

    ARITHMETIC = 0.1
    UNIT_OF_MEASUREMENT = "C"


class BasicPowerMessage(FloatMessage):
    """Parser for basic power messages (kW)."""

    ARITHMETIC = 0.1
    UNIT_OF_MEASUREMENT = "kW"


class BasicEnergyMessage(FloatMessage):
    """Parser for basic energy messages (kWh)."""

    ARITHMETIC = 0.1
    UNIT_OF_MEASUREMENT = "kWh"


class BasicCurrentMessage(FloatMessage):
    """Parser for basic current messages (A)."""

    ARITHMETIC = 0.1
    UNIT_OF_MEASUREMENT = "A"
