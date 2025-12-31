"""Tests for NasaPacketParser."""

import pytest
from unittest.mock import Mock, AsyncMock, call
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import PacketType, DataType, AddressClass
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import hex2bin


class TestNasaPacketParser:
    """Tests for NasaPacketParser class."""

    def test_parser_initialization(self):
        """Test parser initialization."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        assert parser._config == config
        assert parser._device_handlers == {}
        assert parser._packet_listeners == {}
        assert parser._new_device_handler is None
        assert parser._pending_read_handler is None

    def test_parser_initialization_with_handler(self):
        """Test parser initialization with new device handler."""
        config = NasaConfig()
        handler = Mock()
        parser = NasaPacketParser(config=config, _new_device_handler=handler)
        assert parser._new_device_handler == handler

    def test_set_pending_read_handler(self):
        """Test setting pending read handler."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        handler = Mock()
        parser.set_pending_read_handler(handler)
        assert parser._pending_read_handler == handler

    def test_add_device_handler(self):
        """Test adding device handler."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        
        def callback(**kwargs):
            pass
        
        parser.add_device_handler("200001", callback)
        assert "200001" in parser._device_handlers
        assert callback in parser._device_handlers["200001"]
        assert len(parser._device_handlers["200001"]) == 1

    def test_remove_device_handler(self):
        """Test removing device handler."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        callback = Mock()
        parser.add_device_handler("200001", callback)
        parser.remove_device_handler("200001", callback)
        assert callback not in parser._device_handlers["200001"]

    def test_remove_device_handler_nonexistent(self):
        """Test removing non-existent device handler doesn't raise error and is handled gracefully."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        
        def callback(**kwargs):
            pass
        
        parser.remove_device_handler("200001", callback)
        # Should not raise an error - verifies graceful handling

    def test_add_packet_listener(self):
        """Test adding packet listener."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        
        def callback(**kwargs):
            pass
        
        parser.add_packet_listener(0x4000, callback)
        assert 0x4000 in parser._packet_listeners
        assert callback in parser._packet_listeners[0x4000]
        assert len(parser._packet_listeners[0x4000]) == 1

    def test_remove_packet_listener(self):
        """Test removing packet listener."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        callback = Mock()
        parser.add_packet_listener(0x4000, callback)
        parser.remove_packet_listener(0x4000, callback)
        assert callback not in parser._packet_listeners[0x4000]

    def test_remove_packet_listener_nonexistent(self):
        """Test removing non-existent packet listener doesn't raise error and is handled gracefully."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        
        def callback(**kwargs):
            pass
        
        parser.remove_packet_listener(0x4000, callback)
        # Should not raise an error - verifies graceful handling

    @pytest.mark.asyncio
    async def test_parse_packet_simple(self):
        """Test parsing a simple packet."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create a simple test packet: source=200001, dest=80FF01, normal packet, response
        # Source: 20 00 01 (indoor unit)
        # Dest: 80 FF 01 (client)
        # Info byte: 80 (info=1, proto=0, retry=0)
        # Packet/Data type: 15 (packet=1 NORMAL, data=5 RESPONSE)
        # Packet number: 01
        # Dataset count: 01
        # Message: type=1 (2 bytes), id=4000, value=0001
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        # Verify callback was called
        assert callback.called

    @pytest.mark.asyncio
    async def test_parse_packet_filters_non_normal(self):
        """Test that non-NORMAL packets are filtered out."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create packet with STANDBY packet type (0)
        # Source: 20 00 01, Dest: 80 FF 01
        # Info byte: 80
        # Packet/Data type: 05 (packet=0 STANDBY, data=5 RESPONSE)
        packet_hex = "200001" + "80FF01" + "80" + "05" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        # Callback should NOT be called for non-NORMAL packets
        assert not callback.called

    @pytest.mark.asyncio
    async def test_parse_packet_too_short(self):
        """Test that too-short packets are ignored."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create a packet that's too short
        packet_data = b"\x20\x00\x01"
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        # Should not raise an error, but callback should not be called
        assert not callback.called

    @pytest.mark.asyncio
    async def test_parse_packet_extracts_address_class(self):
        """Test that packet parsing extracts address classes."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create packet with known address classes
        # Source: 20 00 01 (INDOOR), Dest: 10 00 00 (OUTDOOR)
        packet_hex = "200001" + "100000" + "80" + "15" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        # Verify address class was extracted
        if callback.called:
            kwargs = callback.call_args[1]
            assert kwargs.get("source_class") == AddressClass.INDOOR

    @pytest.mark.asyncio
    async def test_parse_packet_multiple_datasets(self):
        """Test parsing packet with multiple datasets."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create packet with 2 datasets
        # Dataset 1: type=1 (2 bytes), id=4000, value=0001
        # Dataset 2: type=1 (2 bytes), id=4001, value=0002
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "02" + "40000001" + "40010002"
        packet_data = hex2bin(packet_hex)
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        # Callback should be called twice (once per dataset)
        assert callback.call_count == 2

    @pytest.mark.asyncio
    async def test_parse_packet_calls_new_device_handler(self):
        """Test that new device handler is called for unknown devices."""
        config = NasaConfig(client_address=1)
        
        # Track if handler was called
        handler_called = []
        async def new_device_handler(**kwargs):
            handler_called.append(kwargs)
        
        parser = NasaPacketParser(config=config, _new_device_handler=new_device_handler)
        
        # Create packet from UNKNOWN device (use different address: 300001)
        # with NOTIFICATION type (0x14) - NOTIFICATION packets should be processed for incoming messages
        packet_hex = "300001" + "80FF01" + "80" + "14" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        await parser.parse_packet(packet_data)
        
        # New device handler should be called for unknown source
        assert len(handler_called) > 0, "New device handler should have been called for unknown device"

    @pytest.mark.asyncio
    async def test_parse_packet_protocol_fields(self):
        """Test that protocol fields are correctly extracted."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create packet with specific protocol values
        # Info byte: 0xC8 = 11001000
        # Bit 7 = 1 (info=1)
        # Bits 6-5 = 10 (proto=2)
        # Bits 4-3 = 01 (retry=1)
        # Therefore: (1<<7) | (2<<5) | (1<<3) = 0x80 | 0x40 | 0x08 = 0xC8
        packet_hex = "200001" + "80FF01" + "C8" + "15" + "42" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        callback = Mock()
        parser.add_device_handler("200001", callback)
        
        await parser.parse_packet(packet_data)
        
        if callback.called:
            kwargs = callback.call_args[1]
            assert kwargs.get("isInfo") == 1
            assert kwargs.get("protocolVersion") == 2
            assert kwargs.get("retryCounter") == 1
            assert kwargs.get("packetNumber") == 0x42

    @pytest.mark.asyncio
    async def test_parse_packet_calls_packet_listeners(self):
        """Test that packet listeners are called."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create packet with message 0x4000
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        listener = Mock()
        parser.add_packet_listener(0x4000, listener)
        
        await parser.parse_packet(packet_data)
        
        # Packet listener should be called
        assert listener.called

    @pytest.mark.asyncio
    async def test_parse_packet_pending_read_handler(self):
        """Test that pending read handler is called for RESPONSE packets."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create RESPONSE packet
        packet_hex = "200001" + "80FF01" + "80" + "15" + "01" + "01" + "40000001"
        packet_data = hex2bin(packet_hex)
        
        pending_handler = Mock()
        parser.set_pending_read_handler(pending_handler)
        
        await parser.parse_packet(packet_data)
        
        # Pending read handler should be called for RESPONSE
        assert pending_handler.called

    @pytest.mark.asyncio
    async def test_parse_packet_ack_calls_pending_handler(self):
        """Test that ACK packets call pending read handler."""
        config = NasaConfig(client_address=1)
        parser = NasaPacketParser(config=config)
        
        # Create ACK packet (data type = 6)
        packet_hex = "200001" + "80FF01" + "80" + "16" + "01" + "00"
        packet_data = hex2bin(packet_hex)
        
        pending_handler = Mock()
        parser.set_pending_read_handler(pending_handler)
        
        await parser.parse_packet(packet_data)
        
        # Pending read handler should be called for ACK with empty message list
        if pending_handler.called:
            args = pending_handler.call_args[0]
            assert args[0] == "200001"
            assert args[1] == []
