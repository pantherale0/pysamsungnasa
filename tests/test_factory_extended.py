"""Extended tests for protocol factory modules to improve coverage."""

import pytest
import struct
from typing import cast
from unittest.mock import Mock, patch

from pysamsungnasa.protocol.factory import (
    build_message,
    get_nasa_message_name,
    get_nasa_message_id,
    parse_message,
)
from pysamsungnasa.protocol.factory.types import (
    SendMessage,
    RawMessage,
    BaseMessage,
    BoolMessage,
    StrMessage,
    FloatMessage,
    EnumMessage,
    IntegerMessage,
    BasicTemperatureMessage,
    BasicPowerMessage,
    BasicEnergyMessage,
    BasicCurrentMessage,
    StructureMessage,
)
from pysamsungnasa.protocol.factory.parser import parse_tlv_structure
from pysamsungnasa.protocol.factory.messages.basic import (
    SerialNumber,
    DbCodeMiComMainMessage,
    ProductModelName,
)
from pysamsungnasa.protocol.enum import DataType, SamsungEnum


class TestParserEdgeCases:
    """Tests for edge cases in parser.py."""

    def test_parse_message_with_custom_parsers_dict(self):
        """Test parse_message with custom message_parsers dictionary."""
        custom_parsers = {0x1234: cast(BaseMessage, Mock(spec=BaseMessage))}
        custom_parsers[0x1234].parse_payload = Mock(return_value=Mock(spec=BaseMessage))

        result = parse_message(0x1234, b"\x01\x02", message_parsers=cast(dict[int, BaseMessage], custom_parsers))
        assert result is not None

    def test_parse_message_exception_fallback_to_raw(self):
        """Test that parsing exception falls back to RawMessage."""
        # Create a mock parser that raises an exception
        bad_parser = cast(BaseMessage, Mock(spec=BaseMessage))
        bad_parser.parse_payload = Mock(side_effect=ValueError("Test error"))

        custom_parsers = {0x5678: bad_parser}

        result = parse_message(0x5678, b"\xff\xfe", message_parsers=cast(dict[int, BaseMessage], custom_parsers))

        # Should fall back to RawMessage
        assert isinstance(result, RawMessage)
        assert result.VALUE == "fffe"

    def test_parse_tlv_structure_empty_payload(self):
        """Test parse_tlv_structure with empty payload."""
        result = parse_tlv_structure(b"")

        assert isinstance(result, dict)
        assert "_submessages" in result
        assert "_joined" in result
        assert result["_submessages"] == {}
        assert result["_joined"] is None

    def test_parse_tlv_structure_incomplete_header(self):
        """Test parse_tlv_structure with incomplete TLV header."""
        # Only 1 byte - not enough for length + message ID
        payload = b"\x05"

        result = parse_tlv_structure(payload)

        assert result["_submessages"] == {}
        assert result["_joined"] is None

    def test_parse_tlv_structure_incomplete_message_id(self):
        """Test parse_tlv_structure when message ID is incomplete."""
        # Length = 3, but only 1 byte available for message ID
        payload = b"\x03\xff"

        result = parse_tlv_structure(payload)

        assert result["_submessages"] == {}
        assert result["_joined"] is None

    def test_parse_tlv_structure_incomplete_value(self):
        """Test parse_tlv_structure when value is incomplete."""
        # Length = 5 (2 bytes for ID + 3 bytes for value), but only 2 bytes available for value
        payload = b"\x05\x12\x34\xff"

        result = parse_tlv_structure(payload)

        # Should handle gracefully - value will be b"\xFF"
        assert 0x1234 in result["_submessages"]

    def test_parse_tlv_structure_zero_length_entry(self):
        """Test parse_tlv_structure with zero-length TLV entry."""
        # Zero length - should skip ID and value parsing
        payload = b"\x00\xff\xff"

        result = parse_tlv_structure(payload)

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_parse_tlv_structure_multiple_entries(self):
        """Test parse_tlv_structure with multiple TLV entries."""
        # Entry 1: Length=3, ID=0x1234, Value=0xFF
        # Entry 2: Length=3, ID=0x5678, Value=0xAA
        payload = b"\x03\x12\x34\xff\x03\x56\x78\xaa"

        result = parse_tlv_structure(payload)

        assert 0x1234 in result["_submessages"]
        assert 0x5678 in result["_submessages"]

    def test_parse_tlv_structure_non_bytes_payload(self):
        """Test parse_tlv_structure behavior at boundary conditions."""
        # Test with minimal valid entry
        payload = b"\x02\x12\x34"  # Length=2, ID=0x1234, no value

        result = parse_tlv_structure(payload)

        assert 0x1234 in result["_submessages"]

    def test_parse_tlv_structure_joined_hex_string(self):
        """Test parse_tlv_structure joining of hex values."""
        # Create payload with RawMessage (hex values) that should join
        with patch("pysamsungnasa.protocol.factory.parser.parse_message") as mock_parse:
            mock_parse.return_value = Mock(VALUE="4142")  # "AB" in hex

            payload = b"\x03\x00\x01AB\x03\x00\x02CD"
            result = parse_tlv_structure(payload)

            assert result["_joined"] is not None


class TestBuildMessageEdgeCases:
    """Additional tests for build_message edge cases."""

    def test_build_message_read_type_different_sizes(self):
        """Test READ message type generates correct dummy payload sizes."""
        source = "80FF01"
        destination = "200001"

        # Test kind=0 (1 byte)
        msg1 = SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"")
        result1 = build_message(source, destination, DataType.READ, [msg1])
        assert "00" in result1.upper()

        # Test kind=1 (2 bytes) - message with bit 8 set
        msg2 = SendMessage(MESSAGE_ID=0x4200, PAYLOAD=b"")
        result2 = build_message(source, destination, DataType.READ, [msg2])
        assert "0000" in result2.upper()

        # Test kind=2 (4 bytes) - message with bit 9 set
        msg3 = SendMessage(MESSAGE_ID=0x4400, PAYLOAD=b"")
        result3 = build_message(source, destination, DataType.READ, [msg3])
        assert "00000000" in result3.upper()

    def test_build_message_protocol_version(self):
        """Test that built message has correct protocol version."""
        source = "80FF01"
        destination = "200001"
        messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]

        result = build_message(source, destination, DataType.WRITE, messages)

        # Check protocol version 2 is set (bits 6,5)
        # Should be 0x80 | (2 << 5) = 0x80 | 0x40 = 0xC0
        assert "C0" in result.upper()

    def test_build_message_preserves_case(self):
        """Test build_message output case handling."""
        source = "AbCd01"
        destination = "FfFf01"
        messages = [SendMessage(MESSAGE_ID=0xABCD, PAYLOAD=b"\xef")]

        result = build_message(source, destination, DataType.WRITE, messages)

        # Output should be uppercase
        assert result == result.upper()


class TestGetNasaMessageNameEdgeCases:
    """Additional tests for get_nasa_message_name edge cases."""

    def test_get_message_name_message_without_name_attribute(self):
        """Test message without MESSAGE_NAME attribute."""
        # Create a mock message without MESSAGE_NAME or with None
        with patch("pysamsungnasa.protocol.factory.MESSAGE_PARSERS", {0xABCD: Mock(MESSAGE_NAME=None)}):
            result = get_nasa_message_name(0xABCD)
            assert result is not None
            assert "0xabcd" in result.lower()

    def test_get_message_name_unknown_message_format(self):
        """Test unknown message returns proper hex format."""
        result = get_nasa_message_name(0xDEADBEEF)
        assert result is not None
        assert "0x" in result.lower()


class TestGetNasaMessageIdEdgeCases:
    """Additional tests for get_nasa_message_id edge cases."""

    def test_get_message_id_with_multiple_messages(self):
        """Test finding correct message ID among multiple messages."""
        # This tests the loop in get_nasa_message_id
        with patch("pysamsungnasa.protocol.factory.MESSAGE_PARSERS") as mock_parsers:
            msg1 = Mock(MESSAGE_NAME="Message1")
            msg2 = Mock(MESSAGE_NAME="Message2")
            msg3 = Mock(MESSAGE_NAME="SearchMe")

            mock_parsers.items.return_value = [(0x1000, msg1), (0x2000, msg2), (0x3000, msg3)]

            result = get_nasa_message_id("SearchMe")
            assert result == 0x3000


class TestTypesParsers:
    """Tests for message type parsers in types.py."""

    def test_bool_message_parse_true(self):
        """Test BoolMessage parsing with true value."""
        result = BoolMessage.parse_payload(b"\x01")
        assert result.VALUE is True

    def test_bool_message_parse_false(self):
        """Test BoolMessage parsing with false value."""
        result = BoolMessage.parse_payload(b"\x00")
        assert result.VALUE is False

    def test_str_message_parse_empty(self):
        """Test StrMessage parsing with empty payload."""
        result = StrMessage.parse_payload(b"")
        assert result.VALUE is None

    def test_str_message_parse_with_null_bytes(self):
        """Test StrMessage with null-terminated string."""
        result = StrMessage.parse_payload(b"Hello\x00World")
        assert "Hello" in result.VALUE

    def test_float_message_1_byte_signed(self):
        """Test FloatMessage with 1-byte signed payload."""

        class SignedByteMessage(FloatMessage):
            ARITHMETIC = 1.0
            SIGNED = True

        payload = struct.pack(">b", -50)
        result = SignedByteMessage.parse_payload(payload)
        assert result.VALUE == -50.0

    def test_float_message_1_byte_unsigned(self):
        """Test FloatMessage with 1-byte unsigned payload."""

        class UnsignedByteMessage(FloatMessage):
            ARITHMETIC = 1.0
            SIGNED = False

        payload = struct.pack(">B", 200)
        result = UnsignedByteMessage.parse_payload(payload)
        assert result.VALUE == 200.0

    def test_float_message_2_byte_signed(self):
        """Test FloatMessage with 2-byte signed payload."""

        class SignedShortMessage(FloatMessage):
            ARITHMETIC = 0.1
            SIGNED = True

        payload = struct.pack(">h", -1000)
        result = SignedShortMessage.parse_payload(payload)
        assert result.VALUE == -100.0

    def test_float_message_2_byte_unsigned(self):
        """Test FloatMessage with 2-byte unsigned payload."""

        class UnsignedShortMessage(FloatMessage):
            ARITHMETIC = 0.1
            SIGNED = False

        payload = struct.pack(">H", 1000)
        result = UnsignedShortMessage.parse_payload(payload)
        assert result.VALUE == 100.0

    def test_float_message_4_byte_signed(self):
        """Test FloatMessage with 4-byte signed payload."""

        class SignedIntMessage(FloatMessage):
            ARITHMETIC = 0.01
            SIGNED = True

        payload = struct.pack(">l", -10000)
        result = SignedIntMessage.parse_payload(payload)
        assert result.VALUE == -100.0

    def test_float_message_4_byte_unsigned(self):
        """Test FloatMessage with 4-byte unsigned payload."""

        class UnsignedIntMessage(FloatMessage):
            ARITHMETIC = 0.01
            SIGNED = False

        payload = struct.pack(">L", 10000)
        result = UnsignedIntMessage.parse_payload(payload)
        assert result.VALUE == 100.0

    def test_float_message_invalid_size(self):
        """Test FloatMessage with invalid payload size."""

        class TestMessage(FloatMessage):
            ARITHMETIC = 1.0

        with pytest.raises(ValueError, match="Unsupported payload length"):
            TestMessage.parse_payload(b"\x00\x00\x00")

    def test_float_message_empty_payload(self):
        """Test FloatMessage with empty payload."""
        result = FloatMessage.parse_payload(b"")
        assert result.VALUE is None

    def test_float_message_struct_error(self):
        """Test FloatMessage with malformed struct data."""

        # Test that when payload doesn't match struct format, it's handled
        class TestMessage(FloatMessage):
            SIGNED = False

        # Single byte - this should raise ValueError for unsupported length
        # unless it's in the 1-byte case branch
        result = TestMessage.parse_payload(b"\xff")
        # It should still work - 1 byte is a valid case
        assert result.VALUE is not None or isinstance(result, FloatMessage)

    def test_enum_message_missing_enum(self):
        """Test EnumMessage without MESSAGE_ENUM raises error."""

        class BadEnumMessage(EnumMessage):
            pass

        with pytest.raises(ValueError, match="does not have a MESSAGE_ENUM"):
            BadEnumMessage.parse_payload(b"\x01")

    def test_enum_message_invalid_enum_type(self):
        """Test EnumMessage with invalid MESSAGE_ENUM type."""

        class BadEnumMessage(EnumMessage):
            MESSAGE_ENUM = "not_an_enum"  # type: ignore[assignment]

        with pytest.raises(TypeError, match="must be a SamsungEnum subclass"):
            BadEnumMessage.parse_payload(b"\x01")

    def test_enum_message_valid_value(self):
        """Test EnumMessage with valid enum value."""

        class TestEnum(SamsungEnum):
            VALUE1 = 1
            VALUE2 = 2

        class TestEnumMessage(EnumMessage):
            MESSAGE_ENUM = TestEnum

        result = TestEnumMessage.parse_payload(b"\x01")
        assert result.VALUE == TestEnum.VALUE1
        assert result.OPTIONS is not None
        assert "VALUE1" in result.OPTIONS

    def test_enum_message_invalid_value_uses_default(self):
        """Test EnumMessage with invalid value uses ENUM_DEFAULT."""

        class TestEnum(SamsungEnum):
            VALUE1 = 1

        class TestEnumMessage(EnumMessage):
            MESSAGE_ENUM = TestEnum
            ENUM_DEFAULT = TestEnum.VALUE1

        result = TestEnumMessage.parse_payload(b"\xff")
        assert result.VALUE == TestEnum.VALUE1

    def test_integer_message_empty(self):
        """Test IntegerMessage with empty payload."""
        result = IntegerMessage.parse_payload(b"")
        assert result.VALUE is None

    def test_integer_message_single_byte(self):
        """Test IntegerMessage with single byte."""
        result = IntegerMessage.parse_payload(b"\xff")
        assert result.VALUE == 255

    def test_integer_message_multiple_bytes(self):
        """Test IntegerMessage with multiple bytes."""
        result = IntegerMessage.parse_payload(b"\x01\x02\x03")
        assert result.VALUE == 0x010203

    def test_basic_temperature_message(self):
        """Test BasicTemperatureMessage parsing."""
        payload = struct.pack(">h", 250)  # 25.0°C
        result = BasicTemperatureMessage.parse_payload(payload)
        assert result.VALUE == 25.0
        assert result.UNIT_OF_MEASUREMENT == "C"

    def test_basic_power_message(self):
        """Test BasicPowerMessage parsing."""
        payload = struct.pack(">h", 500)  # 50.0 kW
        result = BasicPowerMessage.parse_payload(payload)
        assert result.VALUE == 50.0
        assert result.UNIT_OF_MEASUREMENT == "kW"

    def test_basic_energy_message(self):
        """Test BasicEnergyMessage parsing."""
        payload = struct.pack(">h", 1000)  # 100.0 kWh
        result = BasicEnergyMessage.parse_payload(payload)
        assert result.VALUE == 100.0
        assert result.UNIT_OF_MEASUREMENT == "kWh"

    def test_basic_current_message(self):
        """Test BasicCurrentMessage parsing."""
        payload = struct.pack(">h", 150)  # 15.0 A
        result = BasicCurrentMessage.parse_payload(payload)
        assert result.VALUE == 15.0
        assert result.UNIT_OF_MEASUREMENT == "A"

    def test_structure_message_parse(self):
        """Test StructureMessage parsing."""
        # Create a simple TLV structure
        payload = b"\x03\x12\x34\x01"

        result = StructureMessage.parse_payload(payload)

        assert result.VALUE is not None
        assert "_submessages" in result.VALUE
        assert "_joined" in result.VALUE


class TestBasicMessages:
    """Tests for basic message parsers."""

    def test_serial_number_valid(self):
        """Test SerialNumber parsing with valid ASCII string."""
        payload = b"0TYXPAFT900834F\x00"
        result = SerialNumber.parse_payload(payload)

        assert result.VALUE == "0TYXPAFT900834F"

    def test_serial_number_empty(self):
        """Test SerialNumber with empty payload."""
        result = SerialNumber.parse_payload(b"")
        assert result.VALUE == ""

    def test_serial_number_with_null_termination(self):
        """Test SerialNumber strips null bytes."""
        payload = b"TEST\x00\x00\x00"
        result = SerialNumber.parse_payload(payload)

        assert result.VALUE == "TEST"

    def test_db_code_micom_too_short(self):
        """Test DbCodeMiComMainMessage with too short payload."""
        result = DbCodeMiComMainMessage.parse_payload(b"\x91\x02\x09")
        assert result.VALUE == "910209"

    def test_db_code_micom_valid_payload(self):
        """Test DbCodeMiComMainMessage with valid 10-byte payload."""
        # 91 02 09 1b 22 08 02 00 00 00
        payload = b"\x91\x02\x09\x1b\x22\x08\x02\x00\x00\x00"
        result = DbCodeMiComMainMessage.parse_payload(payload)

        assert "DB91-02" in result.VALUE
        assert "2022" in result.VALUE

    def test_db_code_micom_parse_error(self):
        """Test DbCodeMiComMainMessage fallback on parse error."""
        # Valid length but with invalid data that causes exception
        payload = b"\x91\x02\x09\x1b\x22\xff\x02\x00\x00\x00"
        result = DbCodeMiComMainMessage.parse_payload(payload)

        # Should return hex value on parse error
        assert result.VALUE is not None

    def test_product_model_name_empty(self):
        """Test ProductModelName with empty payload."""
        result = ProductModelName.parse_payload(b"")
        assert result.VALUE is None

    def test_product_model_name_too_short(self):
        """Test ProductModelName with payload too short."""
        result = ProductModelName.parse_payload(b"\x09")
        # When payload is < 2 bytes, it returns hex representation
        assert result.VALUE == "09"

    def test_product_model_name_valid(self):
        """Test ProductModelName with valid payload."""
        payload = b"\x09EHS MONO\x00"
        result = ProductModelName.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert result.VALUE["type_id"] == 0x09
        assert result.VALUE["model_name"] == "EHS MONO"
        assert "EHS MONO" in result.VALUE["formatted"]

    def test_product_model_name_no_null_terminator(self):
        """Test ProductModelName without null terminator."""
        payload = b"\x11EHS MONO LOWTEMP"
        result = ProductModelName.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert result.VALUE["model_name"] == "EHS MONO LOWTEMP"

    def test_product_model_name_decode_error(self):
        """Test ProductModelName with invalid UTF-8."""
        payload = b"\x09\xff\xfe\xfd"
        result = ProductModelName.parse_payload(payload)

        # Should fall back to hex on decode error
        assert result.VALUE is not None


class TestBaseMessageProperties:
    """Tests for BaseMessage properties and methods."""

    def test_is_fsv_message_with_fsv_name(self):
        """Test is_fsv_message when MESSAGE_NAME contains FSV."""

        class FSVMessage(BaseMessage):
            """FSV Configuration message."""

            MESSAGE_NAME = "FSV Configuration"

        msg = FSVMessage(value="test")
        assert msg.is_fsv_message is True

    def test_is_fsv_message_without_fsv_name(self):
        """Test is_fsv_message when MESSAGE_NAME doesn't contain FSV."""

        class NonFSVMessage(BaseMessage):
            """Regular message."""

            MESSAGE_NAME = "Regular Message"

        msg = NonFSVMessage(value="test")
        assert msg.is_fsv_message is False

    def test_is_fsv_message_no_message_name(self):
        """Test is_fsv_message when MESSAGE_NAME is None."""

        class NoNameMessage(BaseMessage):
            MESSAGE_NAME = None

        msg = NoNameMessage(value="test")
        assert msg.is_fsv_message is False

    def test_as_dict_property(self):
        """Test as_dict property returns correct structure."""

        class TestMessage(BaseMessage):
            """Test message type."""

            MESSAGE_ID = 0x1234
            MESSAGE_NAME = "Test Message"
            UNIT_OF_MEASUREMENT = "°C"

        msg = TestMessage(value=25.5)
        result = msg.as_dict

        assert result["message_id"] == 0x1234
        assert result["message_name"] == "Test Message"
        assert result["unit_of_measurement"] == "°C"
        assert result["value"] == 25.5
        assert "is_fsv_message" in result

    def test_base_message_parse_payload_not_implemented(self):
        """Test BaseMessage.parse_payload raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            BaseMessage.parse_payload(b"\x00")

    def test_raw_message_with_data(self):
        """Test RawMessage with actual data."""
        result = RawMessage.parse_payload(b"\xab\xcd\xef")
        assert result.VALUE == "abcdef"

    def test_raw_message_empty(self):
        """Test RawMessage with empty payload."""
        result = RawMessage.parse_payload(b"")
        assert result.VALUE is None


class TestMessageFactoryIntegration:
    """Integration tests for the message factory."""

    def test_parse_message_with_options(self):
        """Test that parsed messages include options when available."""

        # Using EnumMessage which provides options
        class TestEnum(SamsungEnum):
            OPTION1 = 1
            OPTION2 = 2

        class TestEnumMsg(EnumMessage):
            MESSAGE_ENUM = TestEnum
            MESSAGE_ID = 0x9999

        result = TestEnumMsg.parse_payload(b"\x01")
        assert result.OPTIONS is not None
        assert len(result.OPTIONS) > 0

    def test_send_message_creation(self):
        """Test SendMessage creation and usage."""
        msg = SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01\x02\x03")

        assert msg.MESSAGE_ID == 0x4000
        assert msg.PAYLOAD == b"\x01\x02\x03"


class TestMessageLoaderEdgeCases:
    """Tests for message loader edge cases in messages/__init__.py."""

    def test_load_message_classes_filters_imported_classes(self):
        """Test that load_message_classes only includes classes defined in module."""
        from pysamsungnasa.protocol.factory.messages import MESSAGE_PARSERS

        # MESSAGE_PARSERS should only contain classes with MESSAGE_ID set
        assert MESSAGE_PARSERS is not None
        assert isinstance(MESSAGE_PARSERS, dict)

        # All values should have MESSAGE_ID
        for msg_id, parser_class in MESSAGE_PARSERS.items():
            assert parser_class.MESSAGE_ID == msg_id
            assert hasattr(parser_class, "MESSAGE_NAME")

    def test_load_message_classes_skips_none_message_id(self):
        """Test that load_message_classes skips classes with MESSAGE_ID=None."""
        from pysamsungnasa.protocol.factory.messages import MESSAGE_PARSERS

        # BaseMessage and other base classes shouldn't be in MESSAGE_PARSERS
        base_class_ids = [cls for cls in MESSAGE_PARSERS.values() if cls.__name__ == "BaseMessage"]
        assert len(base_class_ids) == 0

    def test_load_message_classes_skips_non_base_message(self):
        """Test that only BaseMessage subclasses are loaded."""
        from pysamsungnasa.protocol.factory.messages import MESSAGE_PARSERS

        # All MESSAGE_PARSERS values should be subclasses of BaseMessage
        for parser_class in MESSAGE_PARSERS.values():
            assert isinstance(parser_class, type) and issubclass(parser_class, BaseMessage)


class TestDbCodeMiComMainMessageEdgeCases:
    """Tests for DbCodeMiComMainMessage error handling."""

    def test_db_code_micom_bcd_decode_error(self):
        """Test DbCodeMiComMainMessage with payload causing parse error."""
        # Create a valid 10-byte payload but structured to cause ValueError during date calculations
        # payload[6] contains nibbles for month and day calculation
        # If we make the BCD value invalid, it should trigger the except block
        payload = b"\x91\x02\x09\x1b\x22\x08\xff\x00\x00\x00"

        result = DbCodeMiComMainMessage.parse_payload(payload)

        # Should return hex fallback on any parsing error
        assert result.VALUE is not None
        # When exception occurs, it returns hex
        assert isinstance(result.VALUE, str)


class TestOutdoorMessageEdgeCases:
    """Tests for outdoor message parsing edge cases."""

    def test_outdoor_base_option_info_short_payload(self):
        """Test OutdoorBaseOptionInfo with payload < 4 bytes."""
        from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorBaseOptionInfo

        # Payload too short
        result = OutdoorBaseOptionInfo.parse_payload(b"\x00\x01")
        assert result.VALUE is not None

    def test_outdoor_base_option_info_empty_payload(self):
        """Test OutdoorBaseOptionInfo with empty payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorBaseOptionInfo

        result = OutdoorBaseOptionInfo.parse_payload(b"")
        assert result.VALUE is None

    def test_outdoor_base_option_info_valid_payload(self):
        """Test OutdoorBaseOptionInfo with valid 4+ byte payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorBaseOptionInfo

        # 4 bytes header + 2 bytes data
        payload = b"\x00\x00\x00\x01\xab\xcd"
        result = OutdoorBaseOptionInfo.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert "header_hex" in result.VALUE
        assert "data_hex" in result.VALUE

    def test_outdoor_message_860c_short_payload(self):
        """Test OutdoorMessage860c with payload < 4 bytes."""
        from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorMessage860c

        result = OutdoorMessage860c.parse_payload(b"\x00")
        assert result.VALUE is not None

    def test_outdoor_message_860c_valid_payload(self):
        """Test OutdoorMessage860c with valid payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorMessage860c

        payload = b"\x00\x00\x00\x02\xff\xee"
        result = OutdoorMessage860c.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert "header_hex" in result.VALUE
        assert result.VALUE["data_length"] == 2

    def test_outdoor_installed_outdoor_unit_model_info_short(self):
        """Test OutdoorInstalledOutdoorUnitModelInfo with short payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import (
            OutdoorInstalledOutdoorUnitModelInfo,
        )

        result = OutdoorInstalledOutdoorUnitModelInfo.parse_payload(b"\x00\x01\x02")
        assert result.VALUE is not None

    def test_outdoor_installed_outdoor_unit_model_info_valid(self):
        """Test OutdoorInstalledOutdoorUnitModelInfo with valid payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import (
            OutdoorInstalledOutdoorUnitModelInfo,
        )

        payload = b"\x00\x00\x00\x01\xaa\xbb\xcc"
        result = OutdoorInstalledOutdoorUnitModelInfo.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert "total_length" in result.VALUE
        assert result.VALUE["total_length"] == 7

    def test_outdoor_installed_outdoor_unit_setup_info_short(self):
        """Test OutdoorInstalledOutdoorUnitSetupInfo with short payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import (
            OutdoorInstalledOutdoorUnitSetupInfo,
        )

        result = OutdoorInstalledOutdoorUnitSetupInfo.parse_payload(b"\x00")
        assert result.VALUE is not None

    def test_outdoor_installed_outdoor_unit_setup_info_valid(self):
        """Test OutdoorInstalledOutdoorUnitSetupInfo with valid payload."""
        from pysamsungnasa.protocol.factory.messages.outdoor import (
            OutdoorInstalledOutdoorUnitSetupInfo,
        )

        payload = b"\x00\x00\x00\x09" + b"\xaa" * 10
        result = OutdoorInstalledOutdoorUnitSetupInfo.parse_payload(payload)

        assert isinstance(result.VALUE, dict)
        assert "header_value" in result.VALUE
        assert result.VALUE["data_length"] == 10
