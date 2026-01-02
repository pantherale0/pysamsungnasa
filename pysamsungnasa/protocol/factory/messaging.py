"""Message factory for NASA protocol."""

from __future__ import annotations

from dataclasses import dataclass

from typing import ClassVar, Optional, Any
import struct
from abc import ABC

from ..enum import SamsungEnum


@dataclass
class SendMessage:
    """Base class that represents all sent NASA messages."""

    MESSAGE_ID: int  # pylint: disable=invalid-name
    PAYLOAD: bytes  # pylint: disable=invalid-name


class BaseMessage(ABC):
    """Base class for all NASA protocol messages."""

    MESSAGE_ID: ClassVar[Optional[int]] = None
    MESSAGE_NAME: ClassVar[Optional[str]] = None
    MESSAGE_ENUM: ClassVar[Optional[type[SamsungEnum]]] = None
    ENUM_DEFAULT: ClassVar[Optional[Any]] = None
    UNIT_OF_MEASUREMENT: ClassVar[Optional[str]] = None

    def __init__(self, value: Any, options: Optional[list[str]] = None):
        self.VALUE = value  # pylint: disable=invalid-name
        self.OPTIONS = options  # pylint: disable=invalid-name

    @property
    def is_fsv_message(self) -> bool:
        """Return True if this message is an FSV configuration message."""
        if self.MESSAGE_NAME is None:
            return False
        assert self.__doc__ is not None
        return "FSV" in (self.MESSAGE_NAME.upper() or self.__doc__.upper())

    @property
    def as_dict(self) -> dict:
        """Return the message as a dictionary."""
        return {
            "message_id": self.MESSAGE_ID,
            "message_name": self.MESSAGE_NAME,
            "unit_of_measurement": self.UNIT_OF_MEASUREMENT,
            "value": self.VALUE,
            "is_fsv_message": self.is_fsv_message,
        }

    @classmethod
    def parse_payload(cls, payload: bytes) -> "BaseMessage":
        """Parse the payload into a message instance."""
        raise NotImplementedError("parse_payload must be implemented in subclasses.")


class BoolMessage(BaseMessage):
    """Parser for boolean messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> "BoolMessage":
        """Parse the payload into a boolean value."""
        return cls(value=bool(payload[0]))


class StrMessage(BaseMessage):
    """Parser for str messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> "StrMessage":
        """Parse the payload into a string value."""
        return cls(value=payload.decode("utf-8") if payload else None)


class RawMessage(BaseMessage):
    """Parser for raw messages."""

    MESSAGE_NAME = "UNKNOWN"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "RawMessage":
        """Parse the payload into a raw hex string."""
        return cls(value=payload.hex() if payload else None)


class FloatMessage(BaseMessage):
    """Parser for a float message."""

    ARITHMETIC: ClassVar[float] = 0
    SIGNED: ClassVar[bool] = True

    @classmethod
    def parse_payload(cls, payload: bytes) -> "FloatMessage":
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

        return cls(value=parsed_value)


class EnumMessage(BaseMessage):
    """Parser for enum messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> "EnumMessage":
        """Parse the payload into an enum value."""
        if cls.MESSAGE_ENUM is None:
            raise ValueError(f"{cls.__name__} does not have a MESSAGE_ENUM defined.")
        if not isinstance(cls.MESSAGE_ENUM, type) or not issubclass(cls.MESSAGE_ENUM, SamsungEnum):
            raise TypeError(f"{cls.__name__}.MESSAGE_ENUM must be a SamsungEnum subclass.")
        if cls.MESSAGE_ENUM.has_value(payload[0]):
            return cls(
                value=cls.MESSAGE_ENUM(payload[0]),
                options=[option.name for option in cls.MESSAGE_ENUM],
            )
        else:
            return cls(
                value=cls.ENUM_DEFAULT,
                options=[option.name for option in cls.MESSAGE_ENUM],
            )


class IntegerMessage(BaseMessage):
    """Parser for a basic integer message."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> "IntegerMessage":
        """Parse the payload into an integer value."""
        # Basic integer is the hex as an int
        parsed_value: Optional[int] = None
        if payload:
            parsed_value = int(payload.hex(), 16)
        return cls(value=parsed_value)


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
