"""Tests for CRC failure diagnostics.

Sustained bus corruption can produce thousands of CRC failures per day. The
diagnostic design keeps failures visible without flooding the log: packet
detail at DEBUG, a rate-limited WARNING summary, and an optional bounded ring
buffer of recent RX frames for post-hoc inspection.
"""

import asyncio
import binascii
import logging
import time


from pysamsungnasa.config import NasaConfig
from pysamsungnasa.helpers import hex2bin
from pysamsungnasa.nasa_client import NasaClient


def _build_client(**config_kwargs) -> NasaClient:
    config = NasaConfig(device_path="x", **config_kwargs)
    client = NasaClient(config)
    client._rx_queue = asyncio.Queue()
    return client


def _valid_packet() -> bytes:
    data = hex2bin("10000080ff0120150182040000")
    crc = binascii.crc_hqx(data, 0)
    return hex2bin(f"32{len(data) + 4:04x}10000080ff0120150182040000{crc:04x}34")


class TestCrcFailureLogging:
    async def test_crc_failure_recorded_and_debug_contains_packet_hex(self, caplog):
        client = _build_client()
        packet = _valid_packet()
        with caplog.at_level(logging.DEBUG, logger="pysamsungnasa.nasa_client"):
            client._record_crc_failure(packet, 0x1234, 0x5678)
        assert client._crc_failure_count == 1
        debug_messages = [r.message for r in caplog.records if "Invalid CRC" in r.message]
        assert any(binascii.hexlify(packet).decode() in m for m in debug_messages)

    async def test_summary_warning_rate_limited(self, caplog):
        client = _build_client(crc_log_interval=60.0)
        packet = _valid_packet()
        with caplog.at_level(logging.DEBUG, logger="pysamsungnasa.nasa_client"):
            with caplog.at_level(logging.WARNING, logger="pysamsungnasa.nasa_client"):
                # First failure emits the summary; subsequent failures within
                # the interval must not emit more warnings.
                for _ in range(5):
                    client._record_crc_failure(packet, 0x1234, 0x5678)
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING and "CRC validation failure" in r.message]
        assert len(warnings) == 1
        assert client._crc_failure_count == 5

    async def test_summary_repeats_after_interval(self, caplog):
        client = _build_client(crc_log_interval=60.0)
        packet = _valid_packet()
        with caplog.at_level(logging.WARNING, logger="pysamsungnasa.nasa_client"):
            client._record_crc_failure(packet, 0x1234, 0x5678)
            # Simulate the interval elapsing.
            client._last_crc_summary_time = time.monotonic() - client._config.crc_log_interval - 1
            client._record_crc_failure(packet, 0x89AB, 0xCDEF)
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING and "CRC validation failure" in r.message]
        assert len(warnings) == 2
        assert "0x89ab" in warnings[-1].message or "0x89ab" in warnings[-1].getMessage()

    async def test_summary_disabled_by_default(self, caplog):
        """crc_log_interval defaults to 0: no WARNING summaries unless configured."""
        client = _build_client()
        assert client._config.crc_log_interval == 0.0
        packet = _valid_packet()
        with caplog.at_level(logging.WARNING, logger="pysamsungnasa.nasa_client"):
            for _ in range(5):
                client._record_crc_failure(packet, 0x1234, 0x5678)
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING and "CRC validation failure" in r.message]
        assert warnings == []
        assert client._crc_failure_count == 5

    async def test_corrupted_packet_through_queue_processor(self, caplog):
        """An actually corrupted frame is dropped and recorded, not parsed."""
        client = _build_client()
        received = []

        async def rx_handler(data):
            received.append(data)

        client._rx_event_handler = rx_handler
        packet = bytearray(_valid_packet())
        packet[5] ^= 0xFF  # corrupt a payload byte
        await client._rx_queue.put(bytes(packet))

        # Run one iteration of the queue processor by simulating its core work.
        # (Directly invoking the processing logic keeps this test fast.)
        task = asyncio.create_task(client._read_queue_processor())
        await asyncio.sleep(0.05)
        await client._cancel_task(task)

        assert received == []
        assert client._crc_failure_count == 1


class TestPacketCapture:
    async def test_capture_disabled_by_default(self):
        client = _build_client()
        await client._read_buffer_handler(_valid_packet())
        assert client.rx_capture == ()

    async def test_capture_ring_buffer_bounded(self):
        client = _build_client(enable_packet_capture=True, packet_capture_size=3)
        for _ in range(5):
            await client._read_buffer_handler(_valid_packet())
        entries = client.rx_capture
        assert len(entries) == 3
        # Newest entries retained, oldest dropped. Each feed produces a raw
        # chunk entry and a parsed packet entry; the last three are
        # (pkt, raw, pkt).
        assert [entry.split()[1] for entry in entries] == ["pkt", "raw", "pkt"]

    async def test_capture_records_raw_chunks_and_packets(self):
        client = _build_client(enable_packet_capture=True)
        frame = _valid_packet()
        await client._read_buffer_handler(frame[:5])
        await client._read_buffer_handler(frame[5:])
        entries = client.rx_capture
        kinds = [entry.split()[1] for entry in entries]
        assert kinds == ["raw", "raw", "pkt"]

    async def test_capture_records_crc_failures(self):
        client = _build_client(enable_packet_capture=True)
        client._record_crc_failure(_valid_packet(), 0x1234, 0x5678)
        entries = client.rx_capture
        assert len(entries) == 1
        assert " crc_error " in entries[0]
