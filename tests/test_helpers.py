"""Tests for helper functions."""

import pytest
from pysamsungnasa.helpers import bin2hex, hex2bin, getnonce, resetnonce, Address


class TestBin2Hex:
    """Tests for bin2hex function."""

    @pytest.mark.parametrize(
        "input_bytes,expected",
        [
            (b"\x00\x01\x02", "000102"),
            (b"", ""),
            (b"\xab\xcd\xef", "abcdef"),
        ],
    )
    def test_bin2hex_conversion(self, input_bytes, expected):
        """Test converting bytes to hex."""
        assert bin2hex(input_bytes) == expected

    def test_bin2hex_all_bytes(self):
        """Test converting all possible byte values."""
        test_bytes = bytes(range(256))
        result = bin2hex(test_bytes)
        assert len(result) == 512  # 256 bytes * 2 hex chars


class TestHex2Bin:
    """Tests for hex2bin function."""

    @pytest.mark.parametrize(
        "input_hex,expected",
        [
            ("000102", b"\x00\x01\x02"),
            ("", b""),
            ("ABCDEF", b"\xab\xcd\xef"),
            ("abcdef", b"\xab\xcd\xef"),
            ("AbCdEf", b"\xab\xcd\xef"),
            ("00 01 02", b"\x00\x01\x02"),
            ("00  01  02", b"\x00\x01\x02"),
        ],
    )
    def test_hex2bin_conversion(self, input_hex, expected):
        """Test converting hex to bytes."""
        assert hex2bin(input_hex) == expected


class TestRoundTrip:
    """Test round-trip conversion between bin and hex."""

    def test_roundtrip_bin_to_hex_to_bin(self):
        """Test bin -> hex -> bin conversion."""
        original = b"\x00\x01\x02\xab\xcd\xef"
        hex_value = bin2hex(original)
        result = hex2bin(hex_value)
        assert result == original

    def test_roundtrip_hex_to_bin_to_hex(self):
        """Test hex -> bin -> hex conversion."""
        original = "000102abcdef"
        bin_value = hex2bin(original)
        result = bin2hex(bin_value)
        assert result == original


class TestNonce:
    """Tests for nonce functions."""

    def test_getnonce_increments(self):
        """Test getnonce increments the nonce value."""
        resetnonce()
        first = getnonce()
        second = getnonce()
        assert second == first + 1

    def test_getnonce_wraps_at_256(self):
        """Test getnonce wraps around at 256."""
        resetnonce()
        # After reset, _NONCE is 0
        # Get 256 nonces: 1, 2, 3, ..., 255, 0, 1, 2, ...
        nonce = None
        for i in range(256):
            nonce = getnonce()
        # After 256 calls from 0, we should be at 0 again (wraps at 256)
        assert nonce == 0

    def test_resetnonce_resets_to_initial(self):
        """Test resetnonce resets to initial value."""
        resetnonce()
        getnonce()
        getnonce()
        resetnonce()
        nonce = getnonce()
        # After reset, _NONCE is 0, first call to getnonce returns 1
        assert nonce == 1


class TestAddress:
    """Tests for Address class."""

    def test_address_init(self):
        """Test Address initialization."""
        addr = Address(class_id=0x20, channel=0x00, address=0x01)
        assert addr.class_id == 0x20
        assert addr.channel == 0x00
        assert addr.address == 0x01

    @pytest.mark.parametrize(
        "class_id,channel,addr,expected_str",
        [
            (0x20, 0x00, 0x01, "200001"),
            (0x01, 0x02, 0x03, "010203"),
        ],
    )
    def test_address_str(self, class_id, channel, addr, expected_str):
        """Test Address string representation."""
        address = Address(class_id=class_id, channel=channel, address=addr)
        assert str(address) == expected_str

    def test_address_repr(self):
        """Test Address repr."""
        addr = Address(class_id=0x20, channel=0x00, address=0x01)
        assert repr(addr) == "Address(class_id=32, channel=0, address=1)"

    @pytest.mark.parametrize(
        "input_str,expected_class,expected_channel,expected_addr",
        [
            ("200001", 0x20, 0x00, 0x01),
            ("010203", 0x01, 0x02, 0x03),
        ],
    )
    def test_address_parse(self, input_str, expected_class, expected_channel, expected_addr):
        """Test parsing address string."""
        addr = Address.parse(input_str)
        assert addr.class_id == expected_class
        assert addr.channel == expected_channel
        assert addr.address == expected_addr

    def test_address_parse_roundtrip(self):
        """Test parsing and converting back to string."""
        original = "200001"
        addr = Address.parse(original)
        assert str(addr).upper() == original.upper()

    def test_address_parse_various_values(self):
        """Test parsing various address values."""
        test_cases = [
            ("200001", 0x20, 0x00, 0x01),
            ("100000", 0x10, 0x00, 0x00),
            ("FFFFFF", 0xFF, 0xFF, 0xFF),
            ("000000", 0x00, 0x00, 0x00),
            ("123456", 0x12, 0x34, 0x56),
        ]
        for addr_str, expected_class, expected_channel, expected_addr in test_cases:
            addr = Address.parse(addr_str)
            assert addr.class_id == expected_class
            assert addr.channel == expected_channel
            assert addr.address == expected_addr
