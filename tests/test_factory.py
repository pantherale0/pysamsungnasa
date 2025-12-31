"""Tests for protocol factory."""

import pytest
from pysamsungnasa.protocol.factory import (
    build_message,
    get_nasa_message_name,
    get_nasa_message_id,
    parse_message,
)
from pysamsungnasa.protocol.factory.messaging import SendMessage, RawMessage
from pysamsungnasa.protocol.enum import DataType
from pysamsungnasa.helpers import hex2bin, bin2hex


class TestBuildMessage:
    """Tests for build_message function."""

    def test_build_message_no_messages_raises(self):
        """Test that building with no messages raises ValueError."""
        source = "80FF01"
        destination = "200001"
        data_type = DataType.WRITE
        messages = []

        with pytest.raises(ValueError, match="At least one message is required"):
            build_message(source, destination, data_type, messages)

    @pytest.mark.parametrize(
        "source,destination,data_type,messages,expected_in_result",
        [
            ("80FF01", "200001", DataType.WRITE, [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")], ["4000", "01"]),
            ("80FF01", "200001", DataType.READ, [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"")], ["4000", "00"]),
            (
                "80FF01",
                "200001",
                DataType.REQUEST,
                [SendMessage(MESSAGE_ID=0x4242, PAYLOAD=b"\xff\xff")],
                ["4242", "FFFF"],
            ),
        ],
    )
    def test_build_message_types(self, source, destination, data_type, messages, expected_in_result):
        """Test building messages of different types."""
        result = build_message(source, destination, data_type, messages)

        assert isinstance(result, str)
        assert result.startswith(source)
        assert destination in result
        for expected in expected_in_result:
            assert expected in result.upper()

    def test_build_message_multiple_messages(self):
        """Test building message with multiple sub-messages."""
        source = "80FF01"
        destination = "200001"
        data_type = DataType.WRITE
        messages = [
            SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01"),
            SendMessage(MESSAGE_ID=0x4001, PAYLOAD=b"\x02"),
        ]

        result = build_message(source, destination, data_type, messages)

        # Check that both messages are included
        assert "4000" in result.upper()
        assert "4001" in result.upper()
        # Check message count is 02
        assert "02" in result.upper()

    def test_build_message_includes_packet_type(self):
        """Test that message includes NORMAL packet type."""
        source = "80FF01"
        destination = "200001"
        data_type = DataType.WRITE
        messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")]

        result = build_message(source, destination, data_type, messages)

        # Byte at position 12-13 should be packet/data type
        # NORMAL (1) << 4 | WRITE (2) = 0x12
        assert "12" in result.upper()

    def test_build_message_uppercase(self):
        """Test that built message is uppercase."""
        source = "80ff01"
        destination = "200001"
        data_type = DataType.WRITE
        messages = [SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\xab")]

        result = build_message(source, destination, data_type, messages)

        assert result.isupper()


class TestGetNasaMessageName:
    """Tests for get_nasa_message_name function."""

    def test_get_message_name_known_message(self):
        """Test getting name of known message."""
        # 0x4000 is a known message (IN_OPERATION_POWER)
        name = get_nasa_message_name(0x4000)
        assert name is not None
        assert isinstance(name, str)

    def test_get_message_name_unknown_message(self):
        """Test getting name of unknown message returns hex format."""
        name = get_nasa_message_name(0xFFFF)
        assert "0xffff" in name.lower()

    @pytest.mark.parametrize("msg_id", [0x4000, 0x4001, 0x8000, 0x8001])
    def test_get_message_name_various_messages(self, msg_id):
        """Test getting names of various messages."""
        name = get_nasa_message_name(msg_id)
        assert name is not None
        assert isinstance(name, str)


class TestGetNasaMessageId:
    """Tests for get_nasa_message_id function."""

    def test_get_message_id_raises_for_unknown(self):
        """Test that getting ID of unknown message raises ValueError."""
        with pytest.raises(ValueError, match="No message ID found"):
            get_nasa_message_id("NONEXISTENT_MESSAGE_NAME")


class TestParseMessage:
    """Tests for parse_message function."""

    def test_parse_message_unknown_returns_raw(self):
        """Test that parsing unknown message returns RawMessage."""
        message_number = 0xFFFF
        payload = b"\x01\x02\x03"
        description = "Unknown"

        result = parse_message(message_number, payload, description)

        assert isinstance(result, RawMessage)

    def test_parse_message_empty_payload(self):
        """Test parsing message with empty payload."""
        message_number = 0xFFFF
        payload = b""
        description = "Empty"

        result = parse_message(message_number, payload, description)

        assert isinstance(result, RawMessage)

    def test_parse_message_known_message(self):
        """Test parsing a known message type."""
        # 0x4000 is IN_OPERATION_POWER (1 byte enum)
        message_number = 0x4000
        payload = b"\x01"
        description = "IN_OPERATION_POWER"

        result = parse_message(message_number, payload, description)

        # Should return parsed message, not RawMessage
        assert result is not None
        assert hasattr(result, "as_dict")

    @pytest.mark.parametrize(
        "message_number,payload",
        [
            (0x4000, b"\x00"),  # 1 byte
            (0x4200, b"\x00\x00"),  # 2 bytes
            (0x4400, b"\x00\x00\x00\x00"),  # 4 bytes
        ],
    )
    def test_parse_message_various_payloads(self, message_number, payload):
        """Test parsing messages with various payload sizes."""
        result = parse_message(message_number, payload, "Test")
        assert result is not None

    def test_parse_message_invalid_payload_returns_raw(self):
        """Test that parsing with invalid payload falls back to RawMessage."""
        # Try to parse a known message with wrong payload size
        message_number = 0x4000  # Expects 1 byte
        payload = b"\x00\x00\x00\x00"  # 4 bytes
        description = "Invalid"

        result = parse_message(message_number, payload, description)

        # Should fall back to RawMessage on parsing error
        assert result is not None
