"""Tests for structure-based message parsing."""

import pytest
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import PacketType, DataType, AddressClass
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import hex2bin, bin2hex
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
        assert expected["formatted"] == parsed_packet.VALUE["formatted"]
        assert expected["type_id"] == parsed_packet.VALUE["type_id"]
        assert expected["model_name"] == parsed_packet.VALUE["model_name"]

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
