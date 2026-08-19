"""Message factory for NASA protocol."""

from __future__ import annotations

import logging
import struct
from abc import ABC
from dataclasses import dataclass
from typing import Any, ClassVar

from ..enum import SamsungEnum

_LOGGER = logging.getLogger(__name__)


def nasa_payload_size(message_id: int | None) -> int | None:
    """Return the payload size encoded in a NASA message number.

    Bits 9-10 of the 16-bit message ID (bits 1-2 of the high byte) select:
    0 = ENUM (1 byte), 1 = VAR (2 bytes), 2 = LVAR (4 bytes), 3 = STR/struct.
    """
    if message_id is None:
        return None
    kind = ((message_id >> 8) & 0x06) >> 1
    if kind == 0:
        return 1
    if kind == 1:
        return 2
    if kind == 2:
        return 4
    return None


@dataclass
class SendMessage:
    """Base class that represents all sent NASA messages."""

    MESSAGE_ID: int  # pylint: disable=invalid-name
    PAYLOAD: bytes  # pylint: disable=invalid-name


class BaseMessage(ABC):
    """Base class for all NASA protocol messages."""

    MESSAGE_ID: ClassVar[int | None] = None
    MESSAGE_NAME: ClassVar[str | None] = None
    MESSAGE_ENUM: ClassVar[type[SamsungEnum] | None] = None
    ENUM_DEFAULT: ClassVar[SamsungEnum | None] = None
    UNIT_OF_MEASUREMENT: ClassVar[str | None] = None

    def __init__(self, value: Any, raw_payload: bytes = b"", options: list[str] | None = None):
        self.VALUE = value  # pylint: disable=invalid-name
        self.RAW_PAYLOAD = raw_payload  # pylint: disable=invalid-name
        self.OPTIONS = options  # pylint: disable=invalid-name

    @property
    def is_fsv_message(self) -> bool:
        """Return True if this message is an FSV configuration message."""
        if self.MESSAGE_NAME is None:
            return False
        return "FSV" in (self.MESSAGE_NAME.upper() or self.__doc__.upper() if self.__doc__ else "")

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
    def parse_payload(cls, payload: bytes) -> BaseMessage:
        """Parse the payload into a message instance."""
        raise NotImplementedError("parse_payload must be implemented in subclasses.")

    @classmethod
    def to_bytes(cls, value: Any) -> bytes:
        """Convert a value into bytes for sending."""
        raise NotImplementedError("to_bytes must be implemented in subclasses.")


class RawMessage(BaseMessage):
    """Parser for raw messages."""

    MESSAGE_NAME = "UNKNOWN"

    @classmethod
    def parse_payload(cls, payload: bytes) -> RawMessage:
        """Parse the payload into a raw hex string."""
        return cls(value=payload.hex() if payload else None, raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: Any) -> bytes:
        """Convert a hex string value into bytes."""
        raise NotImplementedError("RawMessage does not support to_bytes conversion.")


class BoolMessage(BaseMessage):
    """Parser for boolean messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> BoolMessage:
        """Parse the payload into a boolean value."""
        return cls(value=bool(payload[0]), raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: bool) -> bytes:
        """Convert a boolean value into bytes."""
        return b"\x01" if value else b"\x00"


class StrMessage(BaseMessage):
    """Parser for str messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> StrMessage:
        """Parse the payload into a string value."""
        return cls(value=payload.decode("utf-8") if payload else None, raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: str) -> bytes:
        """Convert a string value into bytes."""
        raise NotImplementedError("StrMessage does not support to_bytes conversion.")


class FloatMessage(BaseMessage):
    """Parser for a float message."""

    ARITHMETIC: ClassVar[float] = 0
    SIGNED: ClassVar[bool] = True
    PAYLOAD_SIZE: ClassVar[int | None] = None  # None = auto-detect, 1/2/4 = force size
    # NASA often uses all-bits-set as "not available" on VAR/LVAR sensors
    NULL_UINT_MAX: ClassVar[bool] = True

    @classmethod
    def _resolve_payload_size(cls, int_value: int | None = None) -> int:
        """Return the byte length to encode, preferring protocol size over value range."""
        if cls.PAYLOAD_SIZE is not None:
            return cls.PAYLOAD_SIZE
        derived = nasa_payload_size(cls.MESSAGE_ID)
        if derived is not None:
            return derived
        if int_value is None:
            return 2
        # Auto-detect based on value range only when the message has no NASA type.
        if (cls.SIGNED and -128 <= int_value <= 127) or (not cls.SIGNED and 0 <= int_value <= 255):
            return 1
        if (cls.SIGNED and -32768 <= int_value <= 32767) or (not cls.SIGNED and 0 <= int_value <= 65535):
            return 2
        return 4

    @classmethod
    def _is_null_payload(cls, payload: bytes) -> bool:
        """Return True when payload is the protocol unavailable sentinel."""
        if not cls.NULL_UINT_MAX or not payload:
            return False
        return payload == b"\xff" * len(payload) and len(payload) in (2, 4)

    @classmethod
    def parse_payload(cls, payload: bytes) -> FloatMessage:
        """Parse the payload into a float value."""
        parsed_value: float | None = None
        if payload:
            if cls._is_null_payload(payload):
                return cls(value=None, raw_payload=payload)
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

        return cls(value=parsed_value, raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: float | None) -> bytes:
        """Convert a float value into bytes."""
        if value is None:
            if not cls.NULL_UINT_MAX:
                raise ValueError(f"None is not supported for {cls.__name__} (NULL_UINT_MAX is False).")
            return b"\xff" * cls._resolve_payload_size()

        if cls.ARITHMETIC == 0:
            raise ValueError(f"ARITHMETIC cannot be zero for {cls.__name__}.")
        int_value = int(value / cls.ARITHMETIC)
        payload_size = cls._resolve_payload_size(int_value)

        # Pack with determined size
        if payload_size == 1:
            fmt = ">b" if cls.SIGNED else ">B"
        elif payload_size == 2:
            fmt = ">h" if cls.SIGNED else ">H"
        elif payload_size == 4:
            fmt = ">l" if cls.SIGNED else ">L"
        else:
            raise ValueError(f"Unsupported PAYLOAD_SIZE {payload_size} for {cls.__name__}.")

        try:
            return struct.pack(fmt, int_value)
        except struct.error as e:
            raise ValueError(f"Value {value} does not fit in a {payload_size}-byte payload for {cls.__name__}.") from e


class EnumMessage(BaseMessage):
    """Parser for enum messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> EnumMessage:
        """Parse the payload into an enum value."""
        if cls.MESSAGE_ENUM is None:
            raise ValueError(f"{cls.__name__} does not have a MESSAGE_ENUM defined.")
        if not isinstance(cls.MESSAGE_ENUM, type) or not issubclass(cls.MESSAGE_ENUM, SamsungEnum):
            raise TypeError(f"{cls.__name__}.MESSAGE_ENUM must be a SamsungEnum subclass.")

        enum_cls = cls.MESSAGE_ENUM  # Type narrowing for the checker
        if enum_cls.has_value(payload[0]):
            return cls(
                value=enum_cls._value2member_map_[payload[0]],  # type: ignore[attr-defined]
                options=[option.name for option in enum_cls],
                raw_payload=payload,
            )
        else:
            return cls(
                value=cls.ENUM_DEFAULT,
                options=[option.name for option in enum_cls],
                raw_payload=payload,
            )

    @classmethod
    def to_bytes(cls, value: SamsungEnum) -> bytes:
        """Convert an enum value into bytes."""
        return bytes([value.value])


class IntegerMessage(BaseMessage):
    """Parser for a basic integer message."""

    # NASA often uses 0xFFFF / 0xFFFFFFFF as "not available" on unused channels
    NULL_UINT_MAX: ClassVar[bool] = True

    @classmethod
    def _is_null_payload(cls, payload: bytes) -> bool:
        """Return True when payload is the protocol unavailable sentinel."""
        if not cls.NULL_UINT_MAX or not payload:
            return False
        return payload == b"\xff" * len(payload) and len(payload) in (2, 4)

    @classmethod
    def parse_payload(cls, payload: bytes) -> IntegerMessage:
        """Parse the payload into an integer value."""
        parsed_value: int | None = None
        if payload:
            if cls._is_null_payload(payload):
                return cls(value=None, raw_payload=payload)
            parsed_value = int(payload.hex(), 16)
        return cls(value=parsed_value, raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: float | None) -> bytes:
        """Convert an integer value into bytes."""
        if value is None:
            if not cls.NULL_UINT_MAX:
                raise ValueError(f"None is not supported for {cls.__name__} (NULL_UINT_MAX is False).")
            return b"\xff" * (nasa_payload_size(cls.MESSAGE_ID) or 2)
        # Determine the minimum number of bytes needed to represent the integer
        if isinstance(value, float):
            value = int(value)
        if value < 0:
            raise ValueError("IntegerMessage only supports non-negative integers.")
        protocol_size = nasa_payload_size(cls.MESSAGE_ID)
        byte_length = protocol_size if protocol_size is not None else ((value.bit_length() + 7) // 8 or 1)
        try:
            return value.to_bytes(byte_length, byteorder="big")
        except OverflowError as e:
            raise ValueError(f"Value {value} does not fit in a {byte_length}-byte payload for {cls.__name__}.") from e


class BasicTemperatureMessage(FloatMessage):
    """Parser for basic temperature messages."""

    ARITHMETIC = 0.1
    UNIT_OF_MEASUREMENT = "C"
    # NASA temperature variables are VAR (2-byte), including values that fit in one byte.
    PAYLOAD_SIZE = 2


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


class StructureMessage(BaseMessage):
    """Parser for structure messages containing nested sub-messages."""

    @classmethod
    def parse_payload(cls, payload: bytes) -> StructureMessage:
        """Parse the payload into a structure message with nested sub-messages.

        When payload is bytes, parse TLV-encoded sub-messages and attempt to join them
        into a single string representation when possible. The implementor is responsible
        for properly defining how the struct message is parsed through this method.

        Args:
            payload: Bytes (raw TLV data)

        Returns:
            StructureMessage instance with parsed VALUE
        """
        from .parser import parse_tlv_structure

        return cls(value=parse_tlv_structure(payload), raw_payload=payload)

    @classmethod
    def to_bytes(cls, value: Any) -> bytes:
        """Convert a structure value into bytes."""
        raise NotImplementedError("StructureMessage does not support to_bytes conversion.")
