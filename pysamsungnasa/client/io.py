"""I/O loop helpers for NASA client runtime."""

from __future__ import annotations

import asyncio
import binascii
import struct
from typing import TYPE_CHECKING

from ..helpers import bin2hex
from ..protocol.factory.parser import extract_packets_from_buffer

if TYPE_CHECKING:
    from ..nasa_client import NasaClient


async def read_buffer_handler(client: "NasaClient", message: bytes) -> None:
    """Process incoming bytes and enqueue complete framed packets."""
    client.rx_buffer += message
    packets, client.rx_buffer = extract_packets_from_buffer(
        client.rx_buffer,
        max_buffer_size=client.config.max_buffer_size,
        log_buffer_messages=client.config.log_buffer_messages,
        logger=client.logger,
    )

    if not client.rx_queue:
        return

    for packet in packets:
        try:
            await client.rx_queue.put(packet)
            if client.config.log_buffer_messages:
                client.logger.debug(
                    "Received complete packet and queued for processing (pending=%s): %s",
                    client.rx_queue.qsize(),
                    bin2hex(packet),
                )
        except asyncio.QueueFull:
            client.logger.warning("RX queue is full. Packet dropped.")


async def serial_reader(client: "NasaClient") -> None:
    """Read bytes from serial stream and pass to frame parser."""
    if client.reader is None:
        client.logger.error("Serial reader is None at start, exiting.")
        return

    client.logger.debug("Serial reader task started.")
    try:
        while client.is_connected:
            data = await client.reader.readuntil(0x34.to_bytes())
            if data:
                await read_buffer_handler(client, data)
            else:
                client.logger.warning("Serial reader received EOF, assuming disconnection.")
                await client.handle_disconnection()
                break
    except asyncio.CancelledError:
        client.logger.info("Serial reader task was cancelled.")
    except Exception as ex:
        client.logger.exception("Serial reader error: %s", ex)
        await client.handle_disconnection(ex)


async def read_queue_processor(client: "NasaClient") -> None:
    """Validate and dispatch complete packets from RX queue."""
    if client.rx_queue is None:
        client.logger.error("QueueProcessor: RX queue is None at start, exiting.")
        return

    client.logger.debug("Queue processor task started.")
    while client.is_connected or (client.rx_queue and not client.rx_queue.empty()):
        try:
            if client.rx_queue:
                try:
                    packet = await asyncio.wait_for(client.rx_queue.get(), timeout=1.0)
                    client.rx_queue.task_done()
                except asyncio.TimeoutError:
                    if not client.is_connected and client.rx_queue.empty():
                        break
                    continue

                if len(packet) < 6 or packet[0] != 0x32 or packet[-1] != 0x34:
                    client.logger.error("QueueProcessor: Invalid packet structure: %s", bin2hex(packet))
                    continue

                try:
                    packet_crc_from_msg = struct.unpack_from(">H", packet, -3)[0]
                    packet_data = packet[3:-3]
                    packet_crc = binascii.crc_hqx(packet_data, 0)

                    if packet_crc != packet_crc_from_msg:
                        client.logger.error(
                            "QueueProcessor: Invalid CRC expected %s got %s",
                            hex(packet_crc),
                            hex(packet_crc_from_msg),
                        )
                        continue

                    await client.event_dispatcher.dispatch("receive", packet_data)
                except struct.error as ex:
                    client.logger.error(
                        "QueueProcessor: Struct unpack error during packet processing: %s. Packet: %s.",
                        ex,
                        bin2hex(packet),
                    )
                except Exception as ex:
                    client.logger.exception(
                        "QueueProcessor: Exception while processing a packet: %s. Packet: %s.",
                        ex,
                        bin2hex(packet),
                    )
        except asyncio.CancelledError:
            client.logger.info("Queue processor task was cancelled.")
            break
        except Exception as ex:
            client.logger.exception("QueueProcessor: Error processing queue item: %s", ex)

        if client.rx_queue is None:
            client.logger.debug("QueueProcessor: RX queue became None, exiting.")
            break

    client.logger.debug("Queue processor task finished.")


async def write_processor(client: "NasaClient") -> None:
    """Write queued commands to serial stream."""
    if client.tx_queue is None or client.rx_queue is None or client.writer is None:
        client.logger.error("Writer: TX queue or socket writer is None at start, exiting.")
        return

    client.logger.debug("Writer task started.")
    while client.is_connected:
        try:
            cmd = await asyncio.wait_for(client.tx_queue.get(), timeout=1.0)
            if cmd is not None:
                if client.writer is None or client.writer.is_closing():
                    client.logger.warning("Writer: Socket writer is None or closing, cannot write.")
                    client.tx_queue.task_done()
                    break

                client.logger.debug("Writer: Writing data: %s", bin2hex(cmd))
                client.writer.write(cmd)
                await client.writer.drain()
                await asyncio.sleep(0.05)
                await client.event_dispatcher.dispatch("send", cmd)

            client.tx_queue.task_done()
        except asyncio.TimeoutError:
            continue
        except (ConnectionResetError, BrokenPipeError, OSError) as ex:
            client.logger.warning("Writer: Write error, assuming disconnection: %s", ex)
            await client.handle_disconnection(ex)
            break
        except asyncio.CancelledError:
            client.logger.info("Writer task was cancelled.")
            break
        except Exception as ex:
            client.logger.exception("Writer: Unexpected error: %s", ex)
            await client.handle_disconnection(ex)
            break
