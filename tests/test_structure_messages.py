"""Tests for structure-based message parsing."""

import pytest
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import hex2bin
import struct

EHS_MONO_TYPE_09 = "09454853204d4f4e4f00"
EHS_MONO_LOW_TEMP_TYPE_11 = "11454853204D4F4E4F204C4F5754454D5000"


class TestStructureMessages:
    """Tests for complex structure-based message parsing."""

    @pytest.mark.parametrize(
        "message_id,payload,expected",
        [
            (
                0x061A,
                EHS_MONO_TYPE_09,
                {
                    "type_id": 9,
                    "model_name": "EHS MONO",
                    "formatted": "EHS MONO (type: 0x09)",
                },
            ),
            (
                0x061A,
                EHS_MONO_LOW_TEMP_TYPE_11,
                {
                    "type_id": 17,
                    "model_name": "EHS MONO LOWTEMP",
                    "formatted": "EHS MONO LOWTEMP (type: 0x11)",
                },
            ),
        ],
    )
    async def test_parse_structure_message_single_submessage(self, message_id: int, payload: str, expected: str | dict):
        """Test parsing structure message with a single sub-message."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)

        # Track parsed packets
        parsed_packets = []

        def callback(**kwargs):
            parsed_packets.append(kwargs)

        parser.add_device_handler("200001", callback)
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += struct.pack(">H", message_id).hex()  # Add message ID
        packet_hex += payload  # Add structure data

        packet_data = hex2bin(packet_hex)

        await parser.parse_packet(packet_data)

        # Verify structure message was parsed
        assert len(parsed_packets) >= 1
        structure_msg = parsed_packets[0]
        assert "packet" in structure_msg
        parsed_packet = structure_msg["packet"]

        # Check message ID and value match expected
        assert message_id == parsed_packet.MESSAGE_ID
        assert isinstance(parsed_packet.VALUE, dict)
        value_dict = parsed_packet.VALUE
        assert isinstance(value_dict, dict)  # Type assertion for type checker
        assert expected["formatted"] == value_dict["formatted"]
        assert expected["type_id"] == value_dict["type_id"]
        assert expected["model_name"] == value_dict["model_name"]

    async def test_parse_db_code_micom_main_message(self):
        """Test parsing DB Code MiCom Main Message (0x0608)."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)

        parsed_packets = []

        def callback(**kwargs):
            parsed_packets.append(kwargs)

        parser.add_device_handler("200001", callback)

        # DB Code MiCom Main Message: 9102103b220614090909
        # Expected: DB91-02 (103B) 2022.05.16 090909
        message_id = 0x0608
        payload = "9102103b220614090909"

        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += struct.pack(">H", message_id).hex()
        packet_hex += payload

        await parser.parse_packet(hex2bin(packet_hex))

        assert len(parsed_packets) >= 1
        parsed_packet = parsed_packets[0]["packet"]

        assert message_id == parsed_packet.MESSAGE_ID
        assert "DB91-02" in parsed_packet.VALUE
        assert "2022.05.16" in parsed_packet.VALUE
        assert "090909" in parsed_packet.VALUE

    async def test_parse_serial_number_message(self):
        """Test parsing Serial Number Message (0x0607)."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)

        parsed_packets = []

        def callback(**kwargs):
            parsed_packets.append(kwargs)

        parser.add_device_handler("200001", callback)

        # Serial number example
        message_id = 0x0607
        serial = b"ABC123XYZ\x00"

        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += struct.pack(">H", message_id).hex()
        packet_hex += serial.hex()

        await parser.parse_packet(hex2bin(packet_hex))

        assert len(parsed_packets) >= 1
        parsed_packet = parsed_packets[0]["packet"]

        assert message_id == parsed_packet.MESSAGE_ID
        assert "ABC123XYZ" == parsed_packet.VALUE

    @pytest.mark.parametrize(
        "message_id,payload,expected_contains",
        [
            (0x061A, EHS_MONO_TYPE_09, "EHS MONO"),
            (0x061A, EHS_MONO_LOW_TEMP_TYPE_11, "EHS MONO LOWTEMP"),
        ],
    )
    async def test_parse_product_model_name_message(self, message_id: int, payload: str, expected_contains: str):
        """Test parsing Product Model Name Message (0x061A)."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)

        parsed_packets = []

        def callback(**kwargs):
            parsed_packets.append(kwargs)

        parser.add_device_handler("200001", callback)

        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += struct.pack(">H", message_id).hex()
        packet_hex += payload

        await parser.parse_packet(hex2bin(packet_hex))

        assert len(parsed_packets) >= 1
        parsed_packet = parsed_packets[0]["packet"]

        assert message_id == parsed_packet.MESSAGE_ID
        assert isinstance(parsed_packet.VALUE, dict)
        assert expected_contains == parsed_packet.VALUE["model_name"]

    def test_parse_product_model_name_invalid_payload(self):
        """Test parsing Product Model Name with invalid payload."""
        from pysamsungnasa.protocol.factory.messages.basic import ProductModelName

        # Invalid payload (too short)
        payload = b"\x05"
        msg = ProductModelName.parse_payload(payload)
        assert msg.VALUE == payload.hex()

        # Invalid ASCII string
        payload = b"\x09\xff\xff\xff"
        msg = ProductModelName.parse_payload(payload)
        assert msg.VALUE == payload.hex()

    @pytest.mark.parametrize(
        "payload_hex,expected_percent,expected_raw,expected_status",
        [
            ("3201", 50, 306, "VALID"),  # 50% (306 decimal)
            ("3c01", 60, 316, "VALID"),  # 60% (316 decimal)
            ("6401", 100, 356, "VALID"),  # 100% (356 decimal)
            ("9601", 150, 406, "VALID"),  # 150% (406 decimal)
            ("0000", None, 0, "NOT_INITIALIZED"),  # Uninitialized
        ],
    )
    def test_outdoor_compressor_frc_parse_valid_values(self, payload_hex: str, expected_percent, expected_raw: int, expected_status: str):
        """Test parsing valid FRC frequency ratio values."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        payload = bytes.fromhex(payload_hex)
        msg = InOutdoorCompressorFrequencyRateControlMessage.parse_payload(payload)

        assert isinstance(msg.VALUE, dict)
        value_dict = msg.VALUE
        assert value_dict["frequency_ratio_percent"] == expected_percent
        assert value_dict["raw_value"] == expected_raw
        assert value_dict["status"] == expected_status

        if expected_status == "VALID":
            assert value_dict["is_valid_increment"] is True
            assert value_dict["nearest_valid_value"] is None
        else:
            assert value_dict["is_valid_increment"] is False

    def test_outdoor_compressor_frc_parse_invalid_increment(self):
        """Test parsing invalid FRC increment (not in 10-unit steps)."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        # 302 decimal (46%) - invalid, should suggest 306 (50%)
        payload = bytes.fromhex("2e01")
        msg = InOutdoorCompressorFrequencyRateControlMessage.parse_payload(payload)

        assert isinstance(msg.VALUE, dict)
        value_dict = msg.VALUE
        assert value_dict["raw_value"] == 302
        assert value_dict["frequency_ratio_percent"] == 46
        assert value_dict["status"] == "INVALID_INCREMENT"
        assert value_dict["is_valid_increment"] is False
        assert value_dict["nearest_valid_value"] == 306
        assert value_dict["nearest_valid_percent"] == 50
        assert "WARNING" in value_dict["formatted"]

    def test_outdoor_compressor_frc_parse_empty_payload(self):
        """Test parsing empty payload."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        payload = b""
        msg = InOutdoorCompressorFrequencyRateControlMessage.parse_payload(payload)
        assert msg.VALUE is None

    def test_outdoor_compressor_frc_to_bytes_valid_percentage(self):
        """Test converting valid frequency ratio percentages to bytes."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        test_cases = [
            (50, "3201"),   # 306 decimal
            (60, "3c01"),   # 316 decimal
            (100, "6401"),  # 356 decimal
            (150, "9601"),  # 406 decimal
        ]

        for percent, expected_hex in test_cases:
            payload = InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"frequency_ratio_percent": percent})
            assert payload.hex() == expected_hex

    def test_outdoor_compressor_frc_to_bytes_raw_value(self):
        """Test converting raw value directly to bytes."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        test_cases = [
            (306, "3201"),   # 50%
            (356, "6401"),   # 100%
            (406, "9601"),   # 150%
        ]

        for raw_value, expected_hex in test_cases:
            payload = InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"raw_value": raw_value})
            assert payload.hex() == expected_hex

    def test_outdoor_compressor_frc_to_bytes_invalid_increment(self):
        """Test that invalid increments raise ValueError with helpful suggestion."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        # 311 is not a valid increment
        with pytest.raises(ValueError) as exc_info:
            InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"frequency_ratio_percent": 55})

        error_msg = str(exc_info.value)
        assert "Invalid frequency ratio value" in error_msg
        assert "Nearest valid value" in error_msg

    def test_outdoor_compressor_frc_to_bytes_raw_value_invalid(self):
        """Test that invalid raw values raise ValueError."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        # 311 decimal is not in VALID_INCREMENTS
        with pytest.raises(ValueError) as exc_info:
            InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"raw_value": 311})

        assert "Invalid frequency ratio value" in str(exc_info.value)

    def test_outdoor_compressor_frc_to_bytes_missing_parameter(self):
        """Test that missing required parameter raises ValueError."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        with pytest.raises(ValueError) as exc_info:
            InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"invalid_key": 100})

        assert "frequency_ratio_percent" in str(exc_info.value) or "raw_value" in str(exc_info.value)

    def test_outdoor_compressor_frc_to_bytes_wrong_type(self):
        """Test that non-dict input raises TypeError."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        with pytest.raises(TypeError):
            InOutdoorCompressorFrequencyRateControlMessage.to_bytes(100)

    def test_outdoor_compressor_frc_roundtrip(self):
        """Test roundtrip: parse -> to_bytes -> parse produces same result."""
        from pysamsungnasa.protocol.factory.messages.indoor import InOutdoorCompressorFrequencyRateControlMessage

        test_values = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]

        for percent in test_values:
            # Convert to bytes
            payload = InOutdoorCompressorFrequencyRateControlMessage.to_bytes({"frequency_ratio_percent": percent})

            # Parse back
            msg = InOutdoorCompressorFrequencyRateControlMessage.parse_payload(payload)

            assert isinstance(msg.VALUE, dict)
            assert msg.VALUE["frequency_ratio_percent"] == percent
            assert msg.VALUE["status"] == "VALID"
            assert msg.VALUE["is_valid_increment"] is True
