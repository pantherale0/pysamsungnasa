"""Connection/session lifecycle helpers for NASA client."""

from __future__ import annotations

import asyncio

import serialx

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..nasa_client import NasaClient


async def handle_disconnection(client: "NasaClient", ex: Exception | None = None) -> None:
    """Handle disconnection and cleanup."""
    if ex:
        client._logger.warning("NasaClient disconnected due to an error: %s", ex)
    else:
        client._logger.info("NasaClient disconnecting.")

    client._connected = False
    client._connection_status = False
    await end_writer_session(client)
    await end_read_queue_session(client)
    await end_retry_manager_session(client)
    await end_reader_session(client)

    if client._writer and not client._writer.is_closing():
        client._writer.close()
        await client._writer.wait_closed()
    client._writer = None
    client._reader = None

    await client._event_dispatcher.dispatch("disconnect", ex)


async def handle_connection(client: "NasaClient") -> None:
    """Handle post-connect startup."""
    client._logger.debug("Successfully connected to %s", client.url)
    client._last_rx_time = asyncio.get_running_loop().time()
    await start_read_queue_session(client)
    await start_writer_session(client)
    await start_retry_manager_session(client)
    await start_reader_session(client)


async def connect(client: "NasaClient") -> bool:
    """Connect to serial endpoint and start background tasks."""
    if not client.url:
        client._logger.error("SerialX formatted URL must be set before connecting.")
        return False
    if client.is_connected:
        client._logger.error("Already connected. To reconnect, disconnect first or use reconnect method.")
        return True

    try:
        client._reader, client._writer = await serialx.open_serial_connection(client.url, baudrate=9600)
        client._connected = True
        client._connection_status = True
        await handle_connection(client)
        return True
    except ConnectionError as ex:
        client._logger.error("NASA Connection error: %s", ex)
        await handle_disconnection(client, ex)
        return False
    except Exception as ex:
        client._logger.error("Unexpected error during connection: %s", ex)
        await handle_disconnection(client, ex)
        return False


async def disconnect(client: "NasaClient") -> None:
    """Disconnect from serial endpoint."""
    if not client._connected:
        client._logger.debug("Already disconnected.")
        return
    await handle_disconnection(client)


async def start_writer_session(client: "NasaClient") -> bool:
    """Start writer task from queue."""
    current_task = client._task_manager.get("writer")
    if current_task and not current_task.done():
        client._logger.error("Writer task already running.")
        return True
    if not client.is_connected:
        client._logger.error("Cannot start writer session: not connected or no socket writer.")
        return False

    client._tx_queue = asyncio.Queue()
    client._writer_task = asyncio.create_task(client._write_processor())
    client._task_manager.set("writer", client._writer_task)
    client._logger.debug("Writer session started.")
    return True


async def start_reader_session(client: "NasaClient") -> bool:
    """Start reader task."""
    current_task = client._task_manager.get("reader")
    if current_task and not current_task.done():
        client._logger.error("Reader task already running.")
        return True
    if not client.is_connected or client._reader is None:
        client._logger.error("Cannot start reader session: not connected or no socket reader.")
        return False

    client._read_task = asyncio.create_task(client._serial_reader())
    client._task_manager.set("reader", client._read_task)
    client._logger.debug("Reader session started.")
    return True


async def end_reader_session(client: "NasaClient") -> bool:
    """End reader session."""
    task_was_present = client._read_task is not None
    await client._task_manager.cancel("reader")
    client._read_task = None
    if task_was_present:
        client._logger.debug("Reader session ended.")
    return task_was_present


async def end_writer_session(client: "NasaClient") -> bool:
    """End writer session."""
    task_was_present = client._writer_task is not None
    await client._task_manager.cancel("writer")
    client._writer_task = None
    if task_was_present:
        client._logger.debug("Writer session ended.")

    if client._tx_queue:
        while not client._tx_queue.empty():
            try:
                client._tx_queue.get_nowait()
                client._tx_queue.task_done()
            except asyncio.QueueEmpty:
                break
        client._tx_queue = None
    return task_was_present


async def start_read_queue_session(client: "NasaClient") -> bool:
    """Start read queue processor task."""
    current_task = client._task_manager.get("queue_processor")
    if current_task and not current_task.done():
        client._logger.error("Queue processor task already running.")
        return True

    client._rx_queue = asyncio.Queue()
    client._queue_processor_task = asyncio.create_task(client._read_queue_processor())
    client._task_manager.set("queue_processor", client._queue_processor_task)
    client._logger.debug("Read queue session started.")
    return True


async def end_read_queue_session(client: "NasaClient") -> bool:
    """End read queue processor session."""
    task_was_present = client._queue_processor_task is not None
    await client._task_manager.cancel("queue_processor")
    client._queue_processor_task = None
    if task_was_present:
        client._logger.debug("Read queue session ended.")

    if client._rx_queue:
        while not client._rx_queue.empty():
            try:
                client._rx_queue.get_nowait()
                client._rx_queue.task_done()
            except asyncio.QueueEmpty:
                break
        client._rx_queue = None
    return task_was_present


async def start_retry_manager_session(client: "NasaClient") -> bool:
    """Start retry manager task."""
    current_task = client._task_manager.get("retry_manager")
    if current_task and not current_task.done():
        client._logger.error("Retry manager task already running.")
        return True
    if not client._config.enable_read_retries:
        client._logger.debug("Read retries are disabled in config.")
        return False

    client._retry_manager_task = asyncio.create_task(client._retry_manager())
    client._task_manager.set("retry_manager", client._retry_manager_task)
    client._logger.debug("Retry manager session started.")
    return True


async def end_retry_manager_session(client: "NasaClient") -> bool:
    """End retry manager session."""
    task_was_present = client._retry_manager_task is not None
    await client._task_manager.cancel("retry_manager")
    client._retry_manager_task = None
    if task_was_present:
        client._logger.debug("Retry manager session ended.")
    return task_was_present
