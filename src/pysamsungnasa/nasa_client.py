"""TCP Modbus client."""

import binascii
import logging
import asyncio
import struct

from .config import NasaConfig
from .helpers import bin2hex, hex2bin

_LOGGER = logging.getLogger(__name__)


class NasaClient:
    """Represent a NASA Client."""

    _serial_lock = asyncio.Lock()
    _reader_lock = asyncio.Lock()
    _socket_reader: asyncio.streams.StreamReader | None = None
    _socket_writer: asyncio.streams.StreamWriter | None = None
    _reader_task: asyncio.Task | None = None
    _queue_processor_task: asyncio.Task | None = None
    _writer_task: asyncio.Task | None = None
    _tx_queue: asyncio.Queue[bytes] | None = None
    _rx_queue: asyncio.Queue[bytes] | None = None
    _packet_number_counter: int = 0

    def __init__(
        self,
        host: str,
        port: int,
        config: NasaConfig,
        recv_event_handler=None,
        send_event_handler=None,
        disconnect_event_handler=None,
    ) -> None:
        """Init a NASA Client."""
        self.host = host
        self.port = port
        self._connection_status = False
        self._rx_event_handler = recv_event_handler
        self._tx_event_handler = send_event_handler
        self._disconnect_event_handler = disconnect_event_handler
        self._config = config

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._connection_status

    async def _handle_disconnection(self, ex: Exception | None = None) -> None:
        """Handle disconnection."""
        if not self._connection_status:
            _LOGGER.debug("Already disconnected or not connected.")
            return
        if ex:
            _LOGGER.warning("NasaClient disconnected due to an error: %s", ex)
        else:
            _LOGGER.info("NasaClient disconnecting.")

        self._connection_status = False
        # Stop tasks and clear queues
        # These methods cancel tasks and set them (and their queues) to None
        await self._end_read_session()
        await self._end_writer_session()
        await self._end_read_queue_session()

        # Close writer stream
        if self._socket_writer:
            writer = self._socket_writer
            self._socket_writer = None  # Clear immediately
            try:
                if not writer.is_closing():
                    writer.close()
                await writer.wait_closed()
            except Exception as close_ex:
                _LOGGER.debug("Error closing socket writer: %s", close_ex)

        # Reader stream is likely closed by the error that triggered this,
        # or will be closed when its task is cancelled.
        self._socket_reader = None  # Ensure it's None

        if self._disconnect_event_handler:
            try:
                res = self._disconnect_event_handler()
                if asyncio.iscoroutine(res):
                    await res
            except Exception as handler_ex:
                _LOGGER.error("Error in disconnection_handler: %s", handler_ex)

    async def connect(self) -> bool:
        """Connect to the server and start background tasks."""
        if not (self.host and self.port):
            _LOGGER.error("Host and port must be set before connecting.")
            return False
        if self._connection_status:
            _LOGGER.error("Already connected. To reconnect, disconnect first or use reconnect method.")
            return True

        async with self._serial_lock:
            if self._connection_status:
                _LOGGER.error("Already connected. To reconnect, disconnect first or use reconnect method.")
                return True
            try:
                self._socket_reader, self._socket_writer = await asyncio.open_connection(self.host, self.port)
                _LOGGER.debug("Successfully connected to %s:%s", self.host, self.port)
                self._connection_status = True
                await self._start_read_queue_session()
                await self._start_writer_session()
                await self._start_read_session()
                return True
            except OSError as ex:
                _LOGGER.error("NASA Connection error: %s", ex)
                await self._handle_disconnection(ex)
                return False
            except Exception as ex:
                _LOGGER.error("Unexpected error during connection: %s", ex)
                await self._handle_disconnection(ex)
                return False

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        await self._handle_disconnection()

    async def _partial_packet_handler(self, bin_data: bytes):
        """A partial packet handler for the reader."""
        if bin_data is None or len(bin_data) == 0:
            return
        while True:
            if not self._connection_status or self._rx_queue is None:
                _LOGGER.debug("Disconnected or rx_queue is None, stopping packet processing.")
                break
            if len(bin_data) < 1 + 2:
                # not enough data yet.
                break
            _LOGGER.debug("Buffer length: %s", len(bin_data))
            _LOGGER.debug("Buffer data: %s", bin2hex(bin_data))
            fields = struct.unpack_from(">BH", bin_data)
            expect_packet_len = 1 + fields[1] + 1
            if fields[0] != 0x32:
                _LOGGER.debug("Invalid prefix, consuming.")
                if len(bin_data) > 1:
                    async with self._reader_lock:
                        bin_data = bin_data[1:]
                continue
            if len(bin_data) < expect_packet_len:
                # not enough data yet.
                break

            # extract packet
            packet = bin_data[:expect_packet_len]
            if len(packet) != expect_packet_len:
                _LOGGER.error("Invalid encoded length: %s", bin2hex(packet))
                break
            try:
                packet_end = struct.unpack_from(">H", packet[-3:])
                if packet[-1] != 0x34:
                    _LOGGER.error("Invalid end of packet (expected 0x34): %s", bin2hex(packet))
                    break
                packet_data = packet[3:-3]
                _LOGGER.debug("CRC computed against packet %s", bin2hex(packet_data))
                packet_crc = binascii.crc_hqx(packet_data, 0)
                if packet_crc != packet_end[0]:
                    _LOGGER.error("Invalid CRC expected %s got %s", hex(packet_crc), hex(packet_end[0]))
                    break
                return packet_data
            except struct.error as e:
                _LOGGER.error(
                    "Struct unpack error during packet processing: %s. Packet: %s. Consuming STX.", e, bin2hex(packet)
                )
                continue
            except Exception as ex:  # Catch-all for other processing errors
                _LOGGER.exception(
                    "Exception while processing a packet: %s. Packet: %s. Consuming STX.", ex, bin2hex(packet)
                )
                continue

    async def _reader(self):
        """Async read task. Reads from socket and passes to partial packet handler."""
        if self._socket_reader is None:
            _LOGGER.debug("Reader: Socket reader is None, exiting.")
            return
        _LOGGER.debug("Reader task started.")
        while self._connection_status:
            try:
                if self._socket_reader is None:  # Should be caught by _connection_status but defensive
                    _LOGGER.warning("Reader: socket_reader became None mid-loop.")
                    await self._handle_disconnection(RuntimeError("socket_reader became None"))
                    break
                data = await self._socket_reader.read(1024)
                if not data:  # EOF, connection closed by peer
                    _LOGGER.info("Reader: Connection closed by peer (EOF).")
                    await self._handle_disconnection(EOFError("Connection closed by peer"))
                    break
                await self._rx_queue.put(data)
                _LOGGER.debug(
                    "Received data and queued for packet processing (pending=%s): %s",
                    self._rx_queue.qsize(),
                    bin2hex(data),
                )
            except (asyncio.IncompleteReadError, ConnectionResetError, OSError) as ex:
                _LOGGER.warning("Reader: Read error, assuming disconnection: %s", ex)
                await self._handle_disconnection(ex)
                break
            except asyncio.CancelledError:
                _LOGGER.info("Reader task was cancelled.")
                break
            except Exception as ex:
                _LOGGER.exception("Reader: Unexpected error: %s", ex)
                await self._handle_disconnection(ex)  # Treat as critical failure
                break
        _LOGGER.debug("Reader task finished.")

    async def _start_read_session(self) -> bool:
        """Start reader task."""
        if self._reader_task and not self._reader_task.done():
            _LOGGER.error("Reader task already running.")
            return True
        if not self._connection_status or not self._socket_reader:
            _LOGGER.error("Cannot start reader session: not connected or no socket reader.")
            return False
        self._reader_task = asyncio.create_task(self._reader())
        _LOGGER.debug("Reader session started.")
        return True

    async def _end_read_session(self) -> bool:
        """End a reader session."""
        task_was_present = self._reader_task is not None
        if self._reader_task:
            task = self._reader_task
            self._reader_task = None  # Clear before await
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    _LOGGER.debug("Reader task successfully cancelled.")
                except Exception as e:
                    _LOGGER.exception("Exception during reader task cancellation/cleanup: %s", e)
            _LOGGER.debug("Reader session ended.")
        return task_was_present

    async def _start_writer_session(self) -> bool:
        """Start writer task from queue."""
        if self._writer_task and not self._writer_task.done():
            _LOGGER.error("Writer task already running.")
            return True
        if not self._connection_status or not self._socket_writer:
            _LOGGER.error("Cannot start writer session: not connected or no socket writer.")
            return False
        self._tx_queue = asyncio.Queue()
        self._writer_task = asyncio.create_task(self._writer())
        _LOGGER.debug("Writer session started.")
        return True

    async def _end_writer_session(self) -> bool:
        """End a writer session."""
        task_was_present = self._writer_task is not None
        if self._writer_task:
            task = self._writer_task
            self._writer_task = None
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    _LOGGER.debug("Writer task successfully cancelled.")
                except Exception as e:
                    _LOGGER.exception("Exception during writer task cancellation/cleanup: %s", e)
            _LOGGER.debug("Writer session ended.")

        if self._tx_queue:  # Drain and clear queue
            while not self._tx_queue.empty():
                try:
                    self._tx_queue.get_nowait()
                    self._tx_queue.task_done()  # Call task_done for each item removed
                except asyncio.QueueEmpty:
                    break
            self._tx_queue = None
        return task_was_present

    async def _start_read_queue_session(self) -> bool:
        """Start reader task from queue."""
        if self._queue_processor_task and not self._queue_processor_task.done():
            _LOGGER.error("Queue processor task already running.")
            return True
        # This task doesn't directly depend on socket, but on _rx_queue
        self._rx_queue = asyncio.Queue()
        self._queue_processor_task = asyncio.create_task(self._read_queue_processor())
        _LOGGER.debug("Read queue session started.")
        return True

    async def _end_read_queue_session(self) -> bool:
        """End a reader queue session."""
        task_was_present = self._queue_processor_task is not None
        if self._queue_processor_task:
            task = self._queue_processor_task
            self._queue_processor_task = None
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    _LOGGER.debug("Queue processor task successfully cancelled.")
                except Exception as e:
                    _LOGGER.debug("Exception during queue processor task cancellation/cleanup: %s", e)
            _LOGGER.debug("Read queue session ended.")

        if self._rx_queue:  # Drain and clear queue
            while not self._rx_queue.empty():
                try:
                    self._rx_queue.get_nowait()
                    self._rx_queue.task_done()
                except asyncio.QueueEmpty:
                    break
            self._rx_queue = None
        return task_was_present

    async def _read_queue_processor(self):
        """Async read queue processor task."""
        if self._rx_queue is None:
            _LOGGER.error("QueueProcessor: RX queue is None at start, exiting.")

        _LOGGER.debug("Queue processor task started.")
        while self._connection_status or (self._rx_queue and not self._rx_queue.empty()):
            # Process remaining items if disconnected but queue has items
            try:
                # Use a timeout to allow the loop to check _connection_status
                # and gracefully exit if queue becomes None externally.
                data = await asyncio.wait_for(self._rx_queue.get(), timeout=1.0)
                if data is not None and self._rx_event_handler:
                    _LOGGER.debug("QueueProcessor: Processing data: %s", bin2hex(data))
                    data = await self._partial_packet_handler(data)
                    try:
                        self._rx_event_handler(data)
                    except Exception as eh_ex:
                        _LOGGER.error("Error in rx_event_handler: %s", eh_ex)
                self._rx_queue.task_done()
            except asyncio.TimeoutError:
                if not self._connection_status and self._rx_queue and self._rx_queue.empty():
                    break  # Exit if disconnected and queue is now empty
                continue  # Loop again to check _connection_status or get next item
            except asyncio.CancelledError:
                _LOGGER.info("Queue processor task was cancelled.")
                break
            except Exception as ex:
                _LOGGER.exception("QueueProcessor: Error processing queue item: %s", ex)
            if self._rx_queue is None:  # Check if queue was set to None by disconnect
                _LOGGER.debug("QueueProcessor: RX queue became None, exiting.")
                break
        _LOGGER.debug("Queue processor task finished.")

    async def _writer(self):
        """Async write task."""
        if self._tx_queue is None or self._socket_writer is None:
            _LOGGER.error("Writer: TX queue or socket writer is None at start, exiting.")
            return
        _LOGGER.debug("Writer task started.")
        while self._connection_status:
            try:
                # Use timeout to allow periodic check of _connection_status
                cmd = await asyncio.wait_for(self._tx_queue.get(), timeout=1.0)
                if cmd is not None:
                    if self._socket_writer is None or self._socket_writer.is_closing():
                        _LOGGER.warning("Writer: Socket writer is None or closing, cannot write.")
                        self._tx_queue.task_done()  # Still mark as done
                        # Re-queue or discard? For now, discard and log.
                        break  # Exit writer as connection is likely lost

                    _LOGGER.debug("Writer: Writing data: %s", bin2hex(cmd))
                    self._socket_writer.write(cmd)
                    await self._socket_writer.drain()  # Crucial for flow control

                    if self._tx_event_handler:
                        try:
                            self._tx_event_handler(cmd)
                        except Exception as eh_ex:
                            _LOGGER.error("Error in tx_event_handler: %s", eh_ex)
                self._tx_queue.task_done()
            except asyncio.TimeoutError:
                continue  # Loop again to check _connection_status or get next item
            except (ConnectionResetError, BrokenPipeError, OSError) as ex:
                _LOGGER.warning("Writer: Write error, assuming disconnection: %s", ex)
                await self._handle_disconnection(ex)
                break
            except asyncio.CancelledError:
                _LOGGER.info("Writer task was cancelled.")
                break
            except Exception as ex:
                _LOGGER.exception("Writer: Unexpected error: %s", ex)
                await self._handle_disconnection(ex)  # Treat as critical failure
                break

    async def send_command(self, message: list[str]) -> bool:
        """Send a command to the NASA device."""
        if not self._connection_status or self._tx_queue is None:
            return False
        for msg in message:
            try:
                self._packet_number_counter = (self._packet_number_counter + 1) % 256
                current_packet_num_hex = f"{self._packet_number_counter:02x}"
                data_for_crc = msg.format(CUR_PACK_NUM=current_packet_num_hex)
                data_bytes = hex2bin(data_for_crc)
                packet_size = len(data_bytes) + 4
                packet_size_hex = f"{packet_size:04x}"
                crc_val = binascii.crc_hqx(data_bytes, 0)
                crc_hex = f"{crc_val:04x}"
                full_packet_hex = f"32{packet_size_hex}{data_for_crc}{crc_hex}34"  # STX, Size, Data, CRC, ETX
                data = hex2bin(full_packet_hex)
                await self._tx_queue.put(data)
                _LOGGER.debug("Command enqueued: %s", bin2hex(data))
            except (binascii.Error, ValueError) as e:
                _LOGGER.error("Error encoding command %s: %s", msg, e)
                return False
            except asyncio.QueueFull:
                _LOGGER.error("TX queue is full, cannot send command: %s", msg)
                return False
            except Exception as e:
                _LOGGER.error("Unexpected error sending command %s: %s", msg, e)
                return False
        _LOGGER.debug("All commands sent to TX queue.")
        return True
