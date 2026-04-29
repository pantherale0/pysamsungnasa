"""Retry helpers for NASA client runtime."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ..protocol.enum import DataType
from ..protocol.factory.types import SendMessage

if TYPE_CHECKING:
    from ..nasa_client import NasaClient


def clear_pending_write(client: "NasaClient", destination: str, message_numbers: list[int]) -> list[str]:
    """Clear pending write requests for a destination when an ACK is received."""
    return client._retry_state.clear_pending_write(destination, message_numbers, logger=client._logger)


def clear_pending_read(client: "NasaClient", destination: str, message_numbers: list[int]) -> bool:
    """Clear a pending read request when a response is received with matching message numbers."""
    return client._retry_state.clear_pending_read(destination, message_numbers, logger=client._logger)


async def mark_write_received(client: "NasaClient", destination: str, message_numbers: list[int]) -> None:
    """Mark write requests as received when an ACK is received."""
    cleared = clear_pending_write(client, destination, message_numbers)
    if cleared:
        client._logger.debug(
            "Write ACK received from %s for messages %s, cleared %d pending write(s)",
            destination,
            message_numbers if message_numbers else "all",
            len(cleared),
        )


async def process_queued_reads(client: "NasaClient", destination: str) -> None:
    """Process queued reads for a destination after a response is received."""
    if destination not in client._queued_reads or not client._queued_reads[destination]:
        return

    queued_msgs = client._queued_reads[destination].pop(0)
    client._logger.debug(
        "Processing queued read for messages %s to %s (remaining in queue: %d)",
        queued_msgs,
        destination,
        len(client._queued_reads[destination]),
    )

    try:
        await client.nasa_read(queued_msgs, destination=destination)
    except Exception as ex:
        client._logger.error("Error processing queued read: %s", ex)


async def mark_read_received(client: "NasaClient", destination: str, message_numbers: list[int]) -> None:
    """Mark read/write request as received."""
    await mark_write_received(client, destination, message_numbers)

    if message_numbers and clear_pending_read(client, destination, message_numbers):
        client._logger.debug("Read response received for messages %s from %s", message_numbers, destination)

    await process_queued_reads(client, destination)


async def retry_manager_loop(client: "NasaClient") -> None:
    """Manage retry logic for pending read and write requests."""
    client._logger.debug("Retry manager task started.")
    while client.is_connected:
        try:
            await asyncio.sleep(1.0)
            current_time = asyncio.get_running_loop().time()

            if client._config.enable_read_retries and client._pending_reads:
                reads_to_retry = []
                reads_to_remove = []
                abandoned_destinations = set()

                for read_key, read_info in list(client._pending_reads.items()):
                    if current_time >= read_info["next_retry_time"]:
                        if read_info["attempts"] < client._config.read_retry_max_attempts:
                            reads_to_retry.append(read_info)
                        else:
                            client._logger.warning(
                                "Abandoning read request %s to %s after %d attempts",
                                read_info["packet_number"],
                                read_info["destination"],
                                read_info["attempts"],
                            )
                            reads_to_remove.append(read_key)
                            abandoned_destinations.add(read_info["destination"])

                for read_key in reads_to_remove:
                    del client._pending_reads[read_key]

                for destination in abandoned_destinations:
                    await process_queued_reads(client, destination)

                for read_info in reads_to_retry:
                    read_info["attempts"] += 1
                    read_info["last_attempt_time"] = current_time
                    read_info["retry_interval"] *= client._config.read_retry_backoff_factor
                    read_info["next_retry_time"] = current_time + read_info["retry_interval"]

                    client._logger.debug(
                        "Retrying read request to %s (attempt %d/%d, interval=%.1fs)",
                        read_info["destination"],
                        read_info["attempts"],
                        client._config.read_retry_max_attempts,
                        read_info["retry_interval"],
                    )

                    try:
                        await client.send_message(
                            destination=read_info["destination"],
                            request_type=DataType.READ,
                            messages=[
                                SendMessage(MESSAGE_ID=msg_id, PAYLOAD=b"\x05\xa5\xa5\xa5")
                                for msg_id in read_info["messages"]
                            ],
                        )
                    except Exception as ex:
                        client._logger.error("Error retrying read request: %s", ex)

            if client._config.enable_write_retries and client._pending_writes:
                writes_to_retry = []
                writes_to_remove = []

                for write_key, write_info in list(client._pending_writes.items()):
                    if current_time >= write_info["next_retry_time"]:
                        if write_info["attempts"] < client._config.write_retry_max_attempts:
                            writes_to_retry.append((write_key, write_info))
                        else:
                            client._logger.warning(
                                "Abandoning write request %s (messages %s) to %s after %d attempts",
                                write_info["packet_number"],
                                write_info["message_ids"],
                                write_info["destination"],
                                write_info["attempts"],
                            )
                            writes_to_remove.append(write_key)

                for write_key in writes_to_remove:
                    del client._pending_writes[write_key]

                for write_key, write_info in writes_to_retry:
                    write_info["attempts"] += 1
                    write_info["last_attempt_time"] = current_time
                    write_info["retry_interval"] *= client._config.write_retry_backoff_factor
                    write_info["next_retry_time"] = current_time + write_info["retry_interval"]

                    client._logger.debug(
                        "Retrying write request (messages %s) to %s (attempt %d/%d, interval=%.1fs)",
                        write_info["message_ids"],
                        write_info["destination"],
                        write_info["attempts"],
                        client._config.write_retry_max_attempts,
                        write_info["retry_interval"],
                    )

                    try:
                        await client.send_message(
                            destination=write_info["destination"],
                            request_type=write_info["data_type"],
                            messages=write_info["messages"],
                        )
                    except Exception as ex:
                        client._logger.error("Error retrying write request: %s", ex)

        except asyncio.CancelledError:
            client._logger.info("Retry manager task was cancelled.")
            break
        except Exception as ex:
            client._logger.exception("Error in retry manager: %s", ex)

    client._logger.debug("Retry manager task finished.")
