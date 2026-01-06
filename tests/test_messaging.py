"""Tests for messaging module."""

import pytest
import struct
from pysamsungnasa.protocol.factory.types import (
    SendMessage,
    BaseMessage,
    BoolMessage,
    StrMessage,
    RawMessage,
    FloatMessage,
    EnumMessage,
    IntegerMessage,
)
from pysamsungnasa.protocol.enum import SamsungEnum


class TestSendMessage:
    """Tests for SendMessage class."""

    def test_send_message_creation(self):
        """Test SendMessage creation."""
        msg = SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01\x02")
        assert msg.MESSAGE_ID == 0x4000
        assert msg.PAYLOAD == b"\x01\x02"


class TestBaseMessage:
    """Tests for BaseMessage class."""

    def test_base_message_creation(self):
        """Test BaseMessage creation with value."""
        msg = BaseMessage(value=42)
        assert msg.VALUE == 42
        assert msg.OPTIONS is None

    def test_base_message_with_options(self):
        """Test BaseMessage creation with options."""
        msg = BaseMessage(value=10, options=["opt1", "opt2"])
        assert msg.VALUE == 10
        assert msg.OPTIONS == ["opt1", "opt2"]

    def test_base_message_as_dict(self):
        """Test as_dict property."""
        msg = BaseMessage(value=100)
        msg.MESSAGE_ID = 0x4000
        msg.MESSAGE_NAME = "TEST_MESSAGE"
        msg.UNIT_OF_MEASUREMENT = "°C"

        result = msg.as_dict

        assert result["message_id"] == 0x4000
        assert result["message_name"] == "TEST_MESSAGE"
        assert result["unit_of_measurement"] == "°C"
        assert result["value"] == 100

    def test_is_fsv_message_with_fsv_in_name(self):
        """Test is_fsv_message property when FSV in name."""
        msg = BaseMessage(value=1)
        msg.MESSAGE_NAME = "FSV_TEST_MESSAGE"
        assert msg.is_fsv_message is True

    def test_is_fsv_message_without_fsv(self):
        """Test is_fsv_message property when FSV not in name."""
        msg = BaseMessage(value=1)
        msg.MESSAGE_NAME = "REGULAR_MESSAGE"
        assert msg.is_fsv_message is False

    def test_parse_payload_not_implemented(self):
        """Test that parse_payload raises NotImplementedError in base class."""
        with pytest.raises(NotImplementedError):
            BaseMessage.parse_payload(b"\x01")


class TestBoolMessage:
    """Tests for BoolMessage class."""

    def test_bool_message_parse_true(self):
        """Test parsing True value."""
        msg = BoolMessage.parse_payload(b"\x01")
        assert msg.VALUE is True

    def test_bool_message_parse_false(self):
        """Test parsing False value."""
        msg = BoolMessage.parse_payload(b"\x00")
        assert msg.VALUE is False


class TestStrMessage:
    """Tests for StrMessage class."""

    def test_str_message_parse(self):
        """Test parsing string value."""
        payload = "Hello".encode("utf-8")
        msg = StrMessage.parse_payload(payload)
        assert msg.VALUE == "Hello"

    def test_str_message_parse_empty(self):
        """Test parsing empty string."""
        msg = StrMessage.parse_payload(b"")
        assert msg.VALUE is None


class TestRawMessage:
    """Tests for RawMessage class."""

    def test_raw_message_parse(self):
        """Test parsing raw bytes."""
        payload = b"\x01\x02\x03\x04"
        msg = RawMessage.parse_payload(payload)
        assert msg.VALUE == "01020304"
        assert msg.MESSAGE_NAME == "UNKNOWN"

    def test_raw_message_parse_empty(self):
        """Test parsing empty raw bytes."""
        msg = RawMessage.parse_payload(b"")
        assert msg.VALUE is None


class TestFloatMessage:
    """Tests for FloatMessage class."""

    def test_float_message_parse_unsigned(self):
        """Test parsing unsigned float."""

        class TestFloatMsg(FloatMessage):
            ARITHMETIC = 0.1
            SIGNED = False

        payload = struct.pack(">H", 123)  # 2-byte unsigned
        msg = TestFloatMsg.parse_payload(payload)
        assert msg.VALUE == 12.3

    def test_float_message_parse_signed(self):
        """Test parsing signed float."""

        class TestFloatMsg(FloatMessage):
            ARITHMETIC = 0.1
            SIGNED = True

        payload = struct.pack(">h", -123)  # 2-byte signed
        msg = TestFloatMsg.parse_payload(payload)
        assert msg.VALUE == -12.3

    def test_float_message_parse_empty(self):
        """Test parsing empty float payload."""

        class TestFloatMsg(FloatMessage):
            ARITHMETIC = 10.0

        msg = TestFloatMsg.parse_payload(b"")
        assert msg.VALUE is None

    def test_float_message_parse_1_byte(self):
        """Test parsing 1-byte float."""

        class TestFloatMsg(FloatMessage):
            ARITHMETIC = 1.0
            SIGNED = False

        payload = b"\x0a"  # 1 byte
        msg = TestFloatMsg.parse_payload(payload)
        assert msg.VALUE == 10.0

    def test_float_message_parse_4_bytes(self):
        """Test parsing 4-byte float."""

        class TestFloatMsg(FloatMessage):
            ARITHMETIC = 0.01
            SIGNED = False

        payload = struct.pack(">I", 12345)  # 4-byte unsigned
        msg = TestFloatMsg.parse_payload(payload)
        assert msg.VALUE == 123.45


class TestEnumMessage:
    """Tests for EnumMessage class."""

    def test_enum_message_parse(self):
        """Test parsing enum value."""

        # Create a test enum
        class TestEnum(SamsungEnum):
            VALUE1 = 1
            VALUE2 = 2

        class TestEnumMsg(EnumMessage):
            MESSAGE_ENUM = TestEnum
            ENUM_DEFAULT = TestEnum.VALUE1

        payload = b"\x02"
        msg = TestEnumMsg.parse_payload(payload)
        assert msg.VALUE == TestEnum.VALUE2

    def test_enum_message_parse_with_default(self):
        """Test parsing enum with default value for unknown."""

        class TestEnum(SamsungEnum):
            VALUE1 = 1
            VALUE2 = 2

        class TestEnumMsg(EnumMessage):
            MESSAGE_ENUM = TestEnum
            ENUM_DEFAULT = TestEnum.VALUE1

        payload = b"\xff"  # Unknown value
        msg = TestEnumMsg.parse_payload(payload)
        assert msg.VALUE == TestEnum.VALUE1

    def test_enum_message_parse_raises_exception_no_enum(self):
        """Test that parse_payload raises ValueError if MESSAGE_ENUM is None."""

        class TestEnumMsg(EnumMessage):
            MESSAGE_ENUM = None
            ENUM_DEFAULT = None

        with pytest.raises(ValueError):
            TestEnumMsg.parse_payload(b"\x01")


class TestIntegerMessage:
    """Tests for IntegerMessage class."""

    def test_integer_message_parse(self):
        """Test parsing integer value."""
        payload = b"\x00\x00\x30\x39"  # Hex for 12345
        msg = IntegerMessage.parse_payload(payload)
        assert msg.VALUE == 12345

    def test_integer_message_parse_empty(self):
        """Test parsing empty integer payload."""
        msg = IntegerMessage.parse_payload(b"")
        assert msg.VALUE is None

    def test_integer_message_parse_single_byte(self):
        """Test parsing single byte integer value."""
        payload = b"\x64"  # Hex for 100
        msg = IntegerMessage.parse_payload(payload)
        assert msg.VALUE == 100
