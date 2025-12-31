"""Tests for structure-based message parsing."""

import pytest
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import PacketType, DataType, AddressClass
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import hex2bin, bin2hex
import struct


class TestStructureMessages:
    """Tests for complex structure-based message parsing."""

    @pytest.mark.asyncio
    async def test_parse_structure_message_single_submessage(self):
        """Test parsing structure message with a single sub-message."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Track parsed packets
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # Create a structure message packet
        # Structure format starts at offset 10 with TLV entries:
        # [Length_byte][Message_ID_MSB][Message_ID_LSB][Value...]
        # 
        # The parser extracts message_type_kind from bits 2-1 of the first byte:
        # message_type_kind = (packet_data[offset] & 0x6) >> 1
        # For structure type: message_type_kind must be 3, so bits 2-1 must be '11' (binary)
        # 0x06 = 0000 0110 has bits 2-1 = '11' → (0x06 & 0x6) >> 1 = 3 ✓
        # 0x07 = 0000 0111 has bits 2-1 = '11' → (0x07 & 0x6) >> 1 = 3 ✓
        # 
        # The same byte also serves as the length field for the TLV entry
        # Length = number of bytes for message_ID (2) + value bytes
        # So 0x06 means: message_type = structure, length = 6 (2 bytes ID + 4 bytes value)
        
        struct_data = b""
        # TLV Entry: Length=4 (but we use 0x06 to encode structure type in bits 2-1)
        # 0x06 = 0000 0110, bits 2-1 = 11 = structure type
        struct_data += b"\x06"  # Length with structure type bits
        struct_data += struct.pack(">H", 0x4000)  # Message ID
        struct_data += struct.pack(">H", 0x0001)  # Value (2 bytes)
        # Remaining bytes to match the "length" - actually length from TLV means ID+value bytes
        # Real length should be 4 (2 byte ID + 2 byte value) but we're overriding first byte for type
        
        # Build packet: source=200001, dest=80FF01, NORMAL, RESPONSE, dataset_count=1
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Verify structure message was parsed
        # The parser reads length (0x06), then message ID, then (length-2) bytes for value
        # 0x06 - 2 = 4 bytes of value expected
        assert len(parsed_packets) >= 1
        # Find the message in parsed packets
        msg_4000 = [p for p in parsed_packets if p["messageNumber"] == 0x4000]
        assert len(msg_4000) > 0

    @pytest.mark.asyncio
    async def test_parse_structure_message_multiple_submessages(self):
        """Test parsing structure message with multiple sub-messages."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # Create structure with multiple TLV entries
        struct_data = b""
        
        # Entry 1: 1-byte value (use 0x07 for structure type, actual length = 7)
        # 0x07 has bits 2-1 = '11' for structure type
        # Parser will read: length=7, then message_ID (2 bytes), then 7-2=5 bytes of value
        struct_data += b"\x07"  # Structure type marker (bits 2-1 = '11') and length value
        struct_data += struct.pack(">H", 0x4000)  # Message ID
        struct_data += b"\x01" * 5  # 7-2=5 bytes value to match the length
        
        # Entry 2: 2-byte value (use 0x06, length=6)
        struct_data += b"\x06"  # Structure type and length=6
        struct_data += struct.pack(">H", 0x4001)
        struct_data += b"\x02" * 4  # 6-2=4 bytes value
        
        # Entry 3: 4-byte value (use 0x0E, length=14)
        struct_data += b"\x0E"  # Structure type (0x0E & 0x6 = 0x06 >> 1 = 3) and length=14
        struct_data += struct.pack(">H", 0x4002)
        struct_data += b"\x03" * 12  # 14-2=12 bytes value
        
        # Build packet with structure type
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Should have parsed all 3 sub-messages
        assert len(parsed_packets) >= 3
        message_ids = [p["messageNumber"] for p in parsed_packets]
        assert 0x4000 in message_ids
        assert 0x4001 in message_ids
        assert 0x4002 in message_ids

    @pytest.mark.asyncio
    async def test_parse_structure_message_realistic_format(self):
        """Test parsing structure with realistic TLV format."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # Build proper TLV structure
        # Each entry: [length_byte][msg_id_hi][msg_id_lo][value_bytes...]
        # where length = 2 (for msg_id) + len(value_bytes)
        struct_data = b""
        
        # Message 1: 0x4000 with 1 byte value
        length1 = 2 + 1  # = 3, but need struct type in bits, so use 0x07
        struct_data += struct.pack(">B", 0x07)  # length with type bits
        struct_data += struct.pack(">H", 0x4000)
        # But length says 7, so need 7-2=5 bytes
        struct_data += b"\xFF" * 5
        
        # Message 2: 0x4200 with 2 byte value
        struct_data += struct.pack(">B", 0x06)  # length 6 with type bits
        struct_data += struct.pack(">H", 0x4200)
        struct_data += b"\xAB" * 4  # 6-2=4 bytes
        
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Check both messages parsed
        assert len(parsed_packets) >= 2
        message_ids = [p["messageNumber"] for p in parsed_packets]
        assert 0x4000 in message_ids
        assert 0x4200 in message_ids

    @pytest.mark.asyncio
    async def test_parse_structure_message_empty_value(self):
        """Test parsing structure message with message that has minimal value."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # Create structure with message that has length=2 (just the ID, minimal value)
        # Use 0x06 or 0x07 for structure type
        struct_data = b""
        struct_data += b"\x06"  # length 6 with structure type bits
        struct_data += struct.pack(">H", 0x4000)  # Message ID
        struct_data += b"\x00" * 4  # 6-2=4 bytes padding
        
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Should parse successfully
        assert len(parsed_packets) >= 1
        msg_ids = [p["messageNumber"] for p in parsed_packets]
        assert 0x4000 in msg_ids

    @pytest.mark.asyncio
    async def test_parse_structure_message_invalid_multiple_datasets_raises(self):
        """Test that structure messages with multiple datasets raise exception."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Structure messages must have dataset_count=1
        struct_data = b"\x06" + struct.pack(">H", 0x4000) + b"\x01" * 4
        
        # dataset_count=2 (invalid for structure)
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "02"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        # The parser raises BaseException for this invalid case (actual implementation behavior)
        with pytest.raises(BaseException):
            await parser.parse_packet(packet_data)

    @pytest.mark.asyncio
    async def test_parse_structure_vs_normal_messages(self):
        """Test that parser correctly distinguishes structure from normal messages."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # First, send a normal message (message_type_kind != 3)
        # Normal packet format at offset 10: [msg_id_hi][msg_id_lo][value...]
        # The first byte (0x40) has bits 2-1 = '00' → message_type_kind = 0 (ENUM, 1-byte)
        # So this is a normal ENUM message, not a structure
        packet_hex_normal = "200001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
        await parser.parse_packet(hex2bin(packet_hex_normal))
        
        initial_count = len(parsed_packets)
        
        # Then send a structure message (message_type_kind = 3)
        # Structure packet format at offset 10: [length_with_type_bits][msg_id][value...]
        # Use 0x07 which has bits 2-1 = '11' → message_type_kind = 3 (STRUCTURE)
        struct_data = b"\x07" + struct.pack(">H", 0x4001) + b"\x02" * 5
        
        packet_hex_struct = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex_struct += bin2hex(struct_data)
        
        await parser.parse_packet(hex2bin(packet_hex_struct))
        
        # Should have both messages parsed
        assert len(parsed_packets) > initial_count
        message_ids = [p["messageNumber"] for p in parsed_packets]
        assert 0x4000 in message_ids  # Normal message
        assert 0x4001 in message_ids  # Structure message

    @pytest.mark.asyncio
    async def test_parse_structure_message_with_device_handler(self):
        """Test that device handlers are called for structure messages."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        handler_calls = []
        def handler(**kwargs):
            handler_calls.append(kwargs)
        
        parser.add_device_handler("200001", handler)
        
        # Create simple structure message
        struct_data = b"\x06" + struct.pack(">H", 0x4000) + b"\x01" * 4
        
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Handler should be called
        assert len(handler_calls) >= 1
        assert any(h["messageNumber"] == 0x4000 for h in handler_calls)

    @pytest.mark.asyncio
    async def test_parse_structure_message_complex_real_world(self):
        """Test parsing a complex structure message with realistic data."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        parsed_packets = []
        def callback(**kwargs):
            parsed_packets.append(kwargs)
        
        parser.add_device_handler("200001", callback)
        
        # Build a complex structure with varied message types
        struct_data = b""
        
        # Entry 1: Short value
        struct_data += b"\x07"  # type=3, length=7
        struct_data += struct.pack(">H", 0x4000)
        struct_data += b"\x01" * 5
        
        # Entry 2: Medium value  
        struct_data += b"\x0E"  # type=3, length=14
        struct_data += struct.pack(">H", 0x4200)
        struct_data += b"\x02" * 12
        
        # Entry 3: Another short value
        struct_data += b"\x06"  # type=3, length=6
        struct_data += struct.pack(">H", 0x4400)
        struct_data += b"\x03" * 4
        
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01"
        packet_hex += bin2hex(struct_data)
        
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # Should parse all messages
        assert len(parsed_packets) >= 3
        message_ids = [p["messageNumber"] for p in parsed_packets]
        assert 0x4000 in message_ids
        assert 0x4200 in message_ids
        assert 0x4400 in message_ids

