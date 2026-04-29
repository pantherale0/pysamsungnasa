"""Command/message helpers for NASA client."""

from __future__ import annotations

import asyncio
import binascii
from typing import TYPE_CHECKING

from ..device import NasaDevice
from ..helpers import bin2hex, hex2bin
from ..protocol.enum import DataType
from ..protocol.factory import build_message
from ..protocol.factory.types import SendMessage

if TYPE_CHECKING:
    from ..nasa_client import NasaClient


async def send_command(client: "NasaClient", message: list[str]) -> int | bytes | None:
    """Send command payloads to TX queue."""
    if not client.is_connected or client._tx_queue is None:
        return None

    last_packet_number = None
    for msg in message:
        client._packet_number_counter = (client._packet_number_counter + 1) % 256
        last_packet_number = client._packet_number_counter
        current_packet_num_hex = f"{client._packet_number_counter:02x}"
        msg = msg.format(CUR_PACK_NUM=current_packet_num_hex)

        try:
            data_bytes = hex2bin(msg)
            crc_val = binascii.crc_hqx(data_bytes, 0)
            crc_hex = f"{crc_val:04x}"
            packet_size_hex = f"{(len(data_bytes) + 4):04x}"
            full_packet_hex = f"32{packet_size_hex}{msg}{crc_hex}34"
            data = hex2bin(full_packet_hex)
            await client._tx_queue.put(data)
            client._logger.debug("Command enqueued (no reply): %s", bin2hex(data))
        except (binascii.Error, ValueError) as ex:
            client._packet_number_counter = (client._packet_number_counter - 1) % 256
            client._logger.error("Error encoding command %s: %s", msg, ex)
            return None
        except asyncio.QueueFull:
            client._packet_number_counter = (client._packet_number_counter - 1) % 256
            client._logger.error("TX queue is full, cannot send command: %s", msg)
            return None
        except Exception as ex:
            client._packet_number_counter = (client._packet_number_counter - 1) % 256
            client._logger.error("Unexpected error sending command %s: %s", msg, ex)
            return None

    return last_packet_number


async def send_message(
    client: "NasaClient",
    destination: NasaDevice | str,
    request_type: DataType = DataType.REQUEST,
    messages: list[SendMessage] | None = None,
) -> int | bytes | None:
    """Send a protocol message to a destination device."""
    if not client.is_connected:
        client._logger.error("Cannot send message, client is not connected.")
        return None

    if isinstance(destination, str):
        destination_address = destination
    elif isinstance(destination, NasaDevice):
        destination_address = destination.address
    else:
        client._logger.error("Invalid destination type: %s", type(destination))
        return None

    if messages is None:
        raise ValueError("At least one message is required.")

    try:
        packet_number = await client.send_command(
            [
                build_message(
                    source=str(client._config.address),
                    destination=destination_address,
                    data_type=request_type,
                    messages=messages,
                )
            ],
        )

        if packet_number is not None:
            current_time = asyncio.get_running_loop().time()
            if request_type in (DataType.WRITE, DataType.REQUEST) and client._config.enable_write_retries:
                message_ids = [msg.MESSAGE_ID for msg in messages]
                write_key = f"{destination_address}_{packet_number}"
                client._pending_writes[write_key] = {
                    "destination": destination_address,
                    "message_ids": message_ids,
                    "messages": messages,
                    "data_type": request_type,
                    "packet_number": packet_number,
                    "attempts": 0,
                    "last_attempt_time": current_time,
                    "next_retry_time": current_time + client._config.write_retry_interval,
                    "retry_interval": client._config.write_retry_interval,
                }
            elif request_type == DataType.READ and client._config.enable_read_retries:
                message_ids = [msg.MESSAGE_ID for msg in messages]
                read_key = f"{destination_address}_{tuple(sorted(message_ids))}"
                client._pending_reads[read_key] = {
                    "destination": destination_address,
                    "messages": message_ids,
                    "packet_number": packet_number,
                    "attempts": 0,
                    "last_attempt_time": current_time,
                    "next_retry_time": current_time + client._config.read_retry_interval,
                    "retry_interval": client._config.read_retry_interval,
                }

        return packet_number
    except Exception as ex:
        client._logger.exception("Error sending message to device %s: %s", destination_address, ex)
        return None


async def nasa_read(
    client: "NasaClient",
    msgs: list[int],
    destination: NasaDevice | str = "B0FF20",
) -> int | bytes | None:
    """Send read requests to a destination device."""
    dest_addr = destination if isinstance(destination, str) else destination.address

    if client._config.enable_read_retries:
        has_pending_read = any(read_info["destination"] == dest_addr for read_info in client._pending_reads.values())
        if has_pending_read:
            if dest_addr not in client._queued_reads:
                client._queued_reads[dest_addr] = []
            client._queued_reads[dest_addr].append(msgs)
            client._logger.debug(
                "Queuing read request for messages %s to %s (queue size: %d)",
                msgs,
                dest_addr,
                len(client._queued_reads[dest_addr]),
            )
            return None

    return await send_message(
        client,
        destination=destination,
        request_type=DataType.READ,
        messages=[SendMessage(MESSAGE_ID=imn, PAYLOAD=b"\x05\xa5\xa5\xa5") for imn in msgs],
    )


async def nasa_write(
    client: "NasaClient",
    msg: int,
    value: str,
    destination: NasaDevice | str,
    data_type: DataType,
) -> int | bytes | None:
    """Send write request to a destination device."""
    message = SendMessage(MESSAGE_ID=msg, PAYLOAD=hex2bin(value))
    return await send_message(
        client,
        destination=destination,
        request_type=data_type,
        messages=[message],
    )
