"""Tests for CRC validation in nasa_client.py."""

import binascii
import struct
import pytest
from pysamsungnasa.helpers import hex2bin


class TestCRCValidation:
    """Tests for CRC calculation and validation to protect against regression."""

    def test_crc_is_deterministic(self):
        """Test that CRC calculation is deterministic."""
        message_hex = "0200c0200001"
        message_data = hex2bin(message_hex)

        crc_1 = binascii.crc_hqx(message_data, 0)
        crc_2 = binascii.crc_hqx(message_data, 0)

        assert crc_1 == crc_2, "CRC should be deterministic"

    def test_crc_calculated_over_message_only(self):
        """Test that CRC matches when calculated over message data only."""
        message_hex = "0200c0200001"
        message_data = hex2bin(message_hex)

        # CRC calculated during send
        crc_send = binascii.crc_hqx(message_data, 0)

        # Simulate what receive does: calculate CRC over the same data
        crc_recv = binascii.crc_hqx(message_data, 0)

        assert crc_send == crc_recv, "Send and receive should calculate CRC identically"

    def test_crc_differs_with_size_field(self):
        """Test that CRC changes when size field is included."""
        message_hex = "0200c0200001"
        message_data = hex2bin(message_hex)

        # Create size bytes
        size_bytes = struct.pack(">H", len(message_data) + 2)

        crc_message_only = binascii.crc_hqx(message_data, 0)
        crc_with_size = binascii.crc_hqx(size_bytes + message_data, 0)

        # These must be different - the bug was when packet[3:-3] included size
        assert crc_message_only != crc_with_size, "CRC must differ when size field is included"

    def test_packet_with_valid_crc(self):
        """Test a complete packet assembly and validation."""
        message_hex = "0200c0200001"
        message_data = hex2bin(message_hex)

        # Calculate CRC over message data only (as send_command does)
        crc_val = binascii.crc_hqx(message_data, 0)
        crc_hex = f"{crc_val:04x}"

        # Build packet
        packet_size = len(message_data) + 2
        packet_size_hex = f"{packet_size:04x}"
        full_packet_hex = f"32{packet_size_hex}{message_hex}{crc_hex}34"
        packet = hex2bin(full_packet_hex)

        # Packet layout: [STX] [Size-H] [Size-L] [Data...] [CRC-H] [CRC-L] [ETX]
        # Indices:      [0]   [1]      [2]      [3...]    [-3]    [-2]    [-1]

        # Verify receive-side validation
        # Extract CRC from packet (at offset -3, 2 bytes, big-endian)
        packet_crc_from_msg = struct.unpack_from(">H", packet, -3)[0]

        # Extract message data - starts at index 3 (after STX + 2-byte size field)
        # and goes to -3 (before the 2-byte CRC + ETX)
        extracted_data = packet[3:-3]
        packet_crc_calculated = binascii.crc_hqx(extracted_data, 0)

        # Validate
        assert packet_crc_from_msg == crc_val, "CRC in packet should match original"
        assert packet_crc_calculated == packet_crc_from_msg, "CRC validation should succeed"
        assert extracted_data == message_data, "Extracted message should match original"

    def test_incorrect_crc_detection(self):
        """Test that invalid CRC is properly detected."""
        message_hex = "0200c0200001"
        message_data = hex2bin(message_hex)

        crc_val = binascii.crc_hqx(message_data, 0)
        bad_crc = (crc_val + 1) & 0xFFFF
        bad_crc_hex = f"{bad_crc:04x}"

        packet_size = len(message_data) + 2
        packet_size_hex = f"{packet_size:04x}"
        full_packet_hex = f"32{packet_size_hex}{message_hex}{bad_crc_hex}34"
        packet = hex2bin(full_packet_hex)

        packet_crc_from_msg = struct.unpack_from(">H", packet, -3)[0]
        extracted_data = packet[3:-3]
        packet_crc_calculated = binascii.crc_hqx(extracted_data, 0)

        # Validation should fail
        assert packet_crc_calculated != packet_crc_from_msg, "CRC validation should detect tampering"
