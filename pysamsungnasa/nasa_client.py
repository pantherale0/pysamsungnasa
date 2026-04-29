"""TCP Modbus client."""

import asyncio
import logging

import serialx

from .client.commands import nasa_read as do_nasa_read
from .client.commands import nasa_write as do_nasa_write
from .client.commands import send_command as do_send_command
from .client.commands import send_message as do_send_message
from .client.connection import connect as do_connect
from .client.connection import disconnect as do_disconnect
from .client.connection import end_read_queue_session
from .client.connection import end_reader_session
from .client.connection import end_retry_manager_session
from .client.connection import end_writer_session
from .client.connection import handle_connection
from .client.connection import handle_disconnection
from .client.connection import start_read_queue_session
from .client.connection import start_reader_session
from .client.connection import start_retry_manager_session
from .client.connection import start_writer_session
from .client.managers import EventDispatcher, RetryManager, TaskManager
from .client.io import read_buffer_handler, read_queue_processor, serial_reader, write_processor
from .client.retry import (
    clear_pending_read,
    clear_pending_write,
    mark_read_received,
    mark_write_received,
    process_queued_reads,
    retry_manager_loop,
)
from .device import NasaDevice
from .protocol.enum import DataType
from .protocol.factory.types import SendMessage

from .config import NasaConfig

_LOGGER = logging.getLogger(__name__)


class NasaClient:
    """Represent a NASA Client."""

    def __init__(
        self,
        url: str | None = None,
        config: NasaConfig | None = None,
        recv_event_handler=None,
        send_event_handler=None,
        disconnect_event_handler=None,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        """Init a NASA Client."""
        if config is None:
            raise ValueError("config is required")

        # Config
        self.host = host
        self.port = port
        self.url = url or (f"{host}:{port}" if host and port else "")
        self.pnp_auto_discovery_packet_handler = None

        # Internal state
        self._task_manager = TaskManager()
        self._retry_state = RetryManager()
        self._logger = _LOGGER
        self._event_dispatcher = EventDispatcher(_LOGGER)
        self._event_dispatcher.set_handler("receive", recv_event_handler)
        self._event_dispatcher.set_handler("send", send_event_handler)
        self._event_dispatcher.set_handler("disconnect", disconnect_event_handler)
        self._tx_queue: asyncio.Queue[bytes] | None = None
        self._rx_queue: asyncio.Queue[bytes] | None = None
        self._queue_processor_task: asyncio.Task | None = None
        self._writer_task: asyncio.Task | None = None
        self._retry_manager_task: asyncio.Task | None = None
        self._rx_buffer = b""
        self._packet_number_counter = 0
        self._reader: asyncio.StreamReader | None = None
        self._read_task: asyncio.Task | None = None
        self._writer: serialx.SerialStreamWriter | None = None
        self._pending_reads = self._retry_state.pending_reads
        self._queued_reads = self._retry_state.queued_reads
        self._pending_writes = self._retry_state.pending_writes
        self._config = config
        self._address = config.address
        self._last_rx_time = asyncio.get_running_loop().time()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._connected

    @property
    def logger(self):
        """Public logger accessor for helper modules."""
        return self._logger

    @property
    def config(self) -> NasaConfig:
        """Public config accessor for helper modules."""
        return self._config

    @property
    def rx_buffer(self) -> bytes:
        """Buffered unread RX bytes."""
        return self._rx_buffer

    @rx_buffer.setter
    def rx_buffer(self, value: bytes) -> None:
        self._rx_buffer = value

    @property
    def rx_queue(self) -> asyncio.Queue[bytes] | None:
        """RX packet queue."""
        return self._rx_queue

    @rx_queue.setter
    def rx_queue(self, value: asyncio.Queue[bytes] | None) -> None:
        self._rx_queue = value

    @property
    def tx_queue(self) -> asyncio.Queue[bytes] | None:
        """TX command queue."""
        return self._tx_queue

    @tx_queue.setter
    def tx_queue(self, value: asyncio.Queue[bytes] | None) -> None:
        self._tx_queue = value

    @property
    def reader(self) -> asyncio.StreamReader | None:
        """Serial reader."""
        return self._reader

    @reader.setter
    def reader(self, value: asyncio.StreamReader | None) -> None:
        self._reader = value

    @property
    def writer(self) -> serialx.SerialStreamWriter | None:
        """Serial writer."""
        return self._writer

    @writer.setter
    def writer(self, value: serialx.SerialStreamWriter | None) -> None:
        self._writer = value

    @property
    def event_dispatcher(self) -> EventDispatcher:
        """Public event dispatcher accessor for helper modules."""
        return self._event_dispatcher

    async def handle_disconnection(self, ex: Exception | None = None) -> None:
        """Public wrapper for disconnection handling used by helper modules."""
        await self._handle_disconnection(ex)

    def set_receive_event_handler(self, handler) -> None:
        """Set the receive event handler."""
        self._event_dispatcher.set_handler("receive", handler)

    def set_send_event_handler(self, handler) -> None:
        """Set the send event handler."""
        self._event_dispatcher.set_handler("send", handler)

    def set_disconnect_event_handler(self, handler) -> None:
        """Set the disconnection event handler."""
        self._event_dispatcher.set_handler("disconnect", handler)

    async def _handle_disconnection(self, ex: Exception | None = None) -> None:
        """Handle disconnection and cleanup."""
        await handle_disconnection(self, ex)

    async def _handle_connection(self) -> None:
        """Handle connection."""
        await handle_connection(self)

    async def connect(self) -> bool:
        """Connect to the server and start background tasks."""
        return await do_connect(self)

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        await do_disconnect(self)

    async def _read_buffer_handler(self, message: bytes):
        """Read buffer handler."""
        await read_buffer_handler(self, message)

    async def _serial_reader(self):
        """Serial reader task."""
        await serial_reader(self)

    async def _start_writer_session(self) -> bool:
        """Start writer task from queue."""
        return await start_writer_session(self)

    async def _start_reader_session(self) -> bool:
        """Start reader task."""
        return await start_reader_session(self)

    async def _end_reader_session(self) -> bool:
        """End reader session."""
        return await end_reader_session(self)

    async def _end_writer_session(self) -> bool:
        """End a writer session."""
        return await end_writer_session(self)

    async def _start_read_queue_session(self) -> bool:
        """Start reader task from queue."""
        return await start_read_queue_session(self)

    async def _end_read_queue_session(self) -> bool:
        """End a reader queue session."""
        return await end_read_queue_session(self)

    async def _start_retry_manager_session(self) -> bool:
        """Start retry manager task."""
        return await start_retry_manager_session(self)

    async def _end_retry_manager_session(self) -> bool:
        """End retry manager session."""
        return await end_retry_manager_session(self)

    async def _read_queue_processor(self):
        """Async read queue processor task. Processes complete packets from the queue."""
        await read_queue_processor(self)

    async def _write_processor(self):
        """Async write processor."""
        await write_processor(self)

    async def send_command(
        self,
        message: list[str],
    ) -> int | bytes | None:
        """Send a command to the NASA device."""
        return await do_send_command(self, message)

    async def send_message(
        self,
        destination: NasaDevice | str,
        request_type: DataType = DataType.REQUEST,
        messages: list[SendMessage] | None = None,
    ) -> int | bytes | None:
        """Send a message to the device using the client."""
        return await do_send_message(self, destination, request_type, messages)

    async def nasa_read(self, msgs: list[int], destination: NasaDevice | str = "B0FF20") -> int | bytes | None:
        """Send read requests to a device to read data."""
        return await do_nasa_read(self, msgs, destination)

    async def nasa_write(
        self, msg: int, value: str, destination: NasaDevice | str, data_type: DataType
    ) -> int | bytes | None:
        """Send write requests to a device to write data."""
        return await do_nasa_write(self, msg, value, destination, data_type)

    def _clear_pending_write(self, destination: str, message_numbers: list[int]) -> list[str]:
        """Clear pending write requests for a destination when an ACK is received."""
        return clear_pending_write(self, destination, message_numbers)

    async def _mark_write_received(self, destination: str, message_numbers: list[int]) -> None:
        """Mark write requests as received when an ACK is received (event callback from parser).

        Args:
            destination: The destination address
            message_numbers: List of message IDs in the ACK packet
        """
        await mark_write_received(self, destination, message_numbers)

    def _clear_pending_read(self, destination: str, message_numbers: list[int]) -> bool:
        """Clear a pending read request when a response is received with matching message numbers."""
        return clear_pending_read(self, destination, message_numbers)

    async def _mark_read_received(self, destination: str, message_numbers: list[int]) -> None:
        """Mark a read/write request as received (event callback from parser).

        Args:
            destination: The destination address
            message_numbers: List of message IDs from the packet (could be from RESPONSE or ACK packets)
        """
        await mark_read_received(self, destination, message_numbers)

    async def _process_queued_reads(self, destination: str) -> None:
        """Process queued reads for a destination after a response is received."""
        await process_queued_reads(self, destination)

    async def _retry_manager(self):
        """Manage retry logic for pending read and write requests."""
        await retry_manager_loop(self)
