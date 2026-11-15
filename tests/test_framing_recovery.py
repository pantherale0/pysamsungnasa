"""Tests for bounded frame-length rejection and parser resynchronisation.

A corrupted packet-length field previously made the parser wait for the
declared number of bytes before any resync attempt, stalling processing of
subsequent valid frames for seconds at 9600 baud. NASA frames declare their
size in a 16-bit field, so a single flipped bit can claim up to 65535 bytes
(~68 seconds of bus traffic). Peer implementations of this protocol treat a
declared size above ~1500 bytes as misframed and resync byte-by-byte.
"""

import asyncio


from pysamsungnasa.config import NasaConfig
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.helpers import hex2bin

# A real-shaped RESPONSE packet: 100000 -> client, message 0x8204 = -1.0°C.
VALID_PACKET_HEX = "320012100000200000815001028204fff65ddd34"


def _build_client(**config_kwargs) -> NasaClient:
    config = NasaConfig(device_path="x", log_buffer_messages=False, **config_kwargs)
    client = NasaClient(config)
    client._rx_queue = asyncio.Queue()
    return client


async def _drain(client: NasaClient) -> list[bytes]:
    packets = []
    while not client._rx_queue.empty():
        packets.append(client._rx_queue.get_nowait())
    return packets


class TestBoundedLengthRejection:
    async def test_oversized_declared_length_resyncs_immediately(self):
        """A garbage STX declaring 0xFFFF must not stall the valid frame behind it."""
        client = _build_client()
        garbage = hex2bin("32ffff") + b"\x00" * 40  # declares 65535+2 bytes
        await client._read_buffer_handler(garbage + hex2bin(VALID_PACKET_HEX))
        packets = await _drain(client)
        assert packets == [hex2bin(VALID_PACKET_HEX)]
        assert client._rx_buffer == b""

    async def test_oversized_declared_length_resyncs_across_chunks(self):
        """Resync must also work when the garbage and the frame arrive separately."""
        client = _build_client()
        await client._read_buffer_handler(hex2bin("32ffff") + b"\x00" * 10)
        assert await _drain(client) == []
        await client._read_buffer_handler(b"\x00" * 30 + hex2bin(VALID_PACKET_HEX))
        packets = await _drain(client)
        assert packets == [hex2bin(VALID_PACKET_HEX)]

    async def test_below_minimum_declared_length_resyncs_immediately(self):
        """A NASA payload is at least 10 bytes; declared sizes below 14 are garbage."""
        client = _build_client()
        garbage = hex2bin("320005") + b"\x00" * 20
        await client._read_buffer_handler(garbage + hex2bin(VALID_PACKET_HEX))
        packets = await _drain(client)
        assert packets == [hex2bin(VALID_PACKET_HEX)]

    async def test_configurable_bound(self):
        """The bound is configurable; raising it restores wait-for-bytes behaviour."""
        client = _build_client(max_packet_size=30000)
        # Declares 4000 bytes: within the raised bound, so the parser waits for
        # the declared bytes instead of resyncing.
        garbage = hex2bin("320fa0") + b"\x00" * 40
        await client._read_buffer_handler(garbage + hex2bin(VALID_PACKET_HEX))
        packets = await _drain(client)
        assert packets == []

    async def test_legitimate_max_size_packet_still_accepted(self):
        """A packet at the bound (declared 1500) must not be rejected."""
        client = _build_client()
        # Payload: 10 header bytes + filler message data. The framing layer
        # must not police message counts — only the declared length matters.
        import binascii

        payload = "10000080ff0120150132" + "ff" * (1500 - 4 - 10)
        data = hex2bin(payload)
        crc = binascii.crc_hqx(data, 0)
        frame = hex2bin(f"32{1500:04x}{payload}{crc:04x}34")
        assert len(frame) == 1502
        await client._read_buffer_handler(frame)
        packets = await _drain(client)
        assert packets == [frame]


def binascii_crc(data: bytes) -> int:
    import binascii

    return binascii.crc_hqx(data, 0)


class TestFragmentedDelivery:
    async def test_valid_frames_still_fragmented(self):
        """Fragmented reads of a valid frame must still assemble correctly."""
        client = _build_client()
        frame = hex2bin(VALID_PACKET_HEX)
        for chunk in (frame[:2], frame[2:9], frame[9:]):
            await client._read_buffer_handler(chunk)
        packets = await _drain(client)
        assert packets == [frame]

    async def test_frame_with_delimiter_bytes_inside_payload(self):
        """Frames containing 0x32/0x34 inside their payload must not break framing."""
        client = _build_client()
        import binascii

        # CRC bytes chosen to contain 0x32/0x34 patterns: build frame, corrupt nothing.
        payload = "10000080ff012015018217" + "3234"
        data = hex2bin(payload)
        crc = binascii.crc_hqx(data, 0)
        frame = hex2bin(f"32{len(data) + 4:04x}{payload}{crc:04x}34")
        await client._read_buffer_handler(frame)
        packets = await _drain(client)
        assert packets == [frame]

    async def test_bounded_buffer_garbage_does_not_grow_unbounded(self):
        """Garbage without STX is discarded, never accumulating without bound."""
        client = _build_client()
        await client._read_buffer_handler(b"\x00" * 1000)
        assert client._rx_buffer == b""
