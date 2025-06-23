"""TCP Modbus client."""

import binascii
import logging
import asyncio
import struct

from .protocol.enum import AddressClass
from .config import NasaConfig
from .helpers import Address, bin2hex, hex2bin

_LOGGER = logging.getLogger(__name__)


class NasaClient:
    """Represent a NASA Client."""

    pnp_auto_discovery_packet_handler = None
    _serial_lock = asyncio.Lock()
    _reader_lock = asyncio.Lock()
    _socket_reader: asyncio.streams.StreamReader | None = None
    _socket_writer: asyncio.streams.StreamWriter | None = None
    _reader_task: asyncio.Task | None = None
    _queue_processor_task: asyncio.Task | None = None
    _writer_task: asyncio.Task | None = None
    _tx_queue: asyncio.Queue[bytes] | None = None
    _rx_queue: asyncio.Queue[bytes] | None = None
    _pending_requests: dict[int, asyncio.Future] = {}
    _rx_buffer = b""
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
        self._address = config.address

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

    async def _read_buffer_handler(self, data: bytes):
        """Read buffer handler."""
        self._rx_buffer += data
        if len(self._rx_buffer) > self._config.max_buffer_size:
            _LOGGER.error("Max buffer sized reached %s/%s", len(self._rx_buffer), self._config.max_buffer_size)
            self._rx_buffer = b""
            return
        while len(self._rx_buffer) >= 3:
            if self._config.log_buffer_messages:
                _LOGGER.debug("Buffer (len=%s): %s", len(self._rx_buffer), bin2hex(self._rx_buffer))
            fields = struct.unpack_from(">BH", self._rx_buffer)
            if fields[0] != 0x32:
                next_prefix = self._rx_buffer.find(b'\x32', 1)
                if next_prefix == -1:
                    if self._config.log_buffer_messages:
                        _LOGGER.debug("No prefix found, discarding buffer.")
                    self._rx_buffer = b""
                    break
                if self._config.log_buffer_messages:
                    _LOGGER.debug("Invalid prefix, skipping %s bytes.", next_prefix)
                if len(self._rx_buffer) > 1:
                    self._rx_buffer = self._rx_buffer[next_prefix:]
                continue
            expected_packet_len = 1 + fields[1] + 1
            if len(self._rx_buffer) < expected_packet_len:
                # Not enough data for a full packet
                break
            packet = self._rx_buffer[:expected_packet_len]
            if len(packet) != expected_packet_len:
                _LOGGER.error("Invalid packet length: %s", bin2hex(packet))
                self._rx_buffer = b""
                break
            if packet[-1] != 0x34:
                _LOGGER.error("Invalid end of packet (expected 0x34): %s", bin2hex(packet))
                # Consume prefix and try again
                self._rx_buffer = self._rx_buffer[1:]
                continue
            await self._rx_queue.put(packet)
            if self._config.log_buffer_messages:
                _LOGGER.debug(
                    "Received complete packet and queued for processing (pending=%s): %s",
                    self._rx_queue.qsize(),
                    bin2hex(packet),
                )
            # Remove the processed packet from the buffer
            self._rx_buffer = self._rx_buffer[expected_packet_len:]
            if self._rx_buffer and self._rx_buffer[0] != 0x32:
                next_prefix = self._rx_buffer.find(b'\x32', 1)
                if next_prefix == -1:
                    if self._config.log_buffer_messages:
                        _LOGGER.debug("No prefix found, discarding buffer.")
                    self._rx_buffer = b""
                else:
                    if self._config.log_buffer_messages:
                        _LOGGER.debug("Invalid prefix, skipping %s bytes.", next_prefix)
                    self._rx_buffer = self._rx_buffer[next_prefix:]

    async def _reader(self):
        """Async read task. Reads from socket and passes to partial packet handler."""
        if self._socket_reader is None:
            _LOGGER.debug("Reader: Socket reader is None, exiting.")
            return
        _LOGGER.debug("Reader task started.")
        self._rx_buffer = b""
        while self._connection_status:
            try:
                if self._socket_reader is None:  # Should be caught by _connection_status but defensive
                    _LOGGER.warning("Reader: socket_reader became None mid-loop.")
                    await self._handle_disconnection(RuntimeError("socket_reader became None"))
                    self._rx_buffer = b""
                    break
                if self._rx_queue is None:
                    _LOGGER.warning("Reader: rx_queue became None mid-loop.")
                    self._rx_buffer = b""
                    continue
                data = await self._socket_reader.read(1024)
                if not data:  # EOF, connection closed by peer
                    _LOGGER.info("Reader: Connection closed by peer (EOF).")
                    await self._handle_disconnection(EOFError("Connection closed by peer"))
                    self._rx_buffer = b""
                    break
                await self._read_buffer_handler(data)
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
        """Async read queue processor task. Processes complete packets from the queue."""
        if self._rx_queue is None:
            _LOGGER.error("QueueProcessor: RX queue is None at start, exiting.")
            return

        _LOGGER.debug("Queue processor task started.")
        while self._connection_status or (self._rx_queue and not self._rx_queue.empty()):
            try:
                if self._rx_queue:
                    try:
                        # Use a timeout to allow the loop to check _connection_status
                        packet = await asyncio.wait_for(self._rx_queue.get(), timeout=1.0)
                        self._rx_queue.task_done()
                    except asyncio.TimeoutError:
                        if not self._connection_status and self._rx_queue.empty():
                            break  # Exit if disconnected and queue is now empty
                        continue  # Loop again to check _connection_status or get next item

                    # Validate packet structure
                    if len(packet) < 6 or packet[0] != 0x32 or packet[-1] != 0x34:
                        _LOGGER.error("QueueProcessor: Invalid packet structure: %s", bin2hex(packet))
                        continue
                    try:
                        packet_crc_from_msg = struct.unpack_from(">H", packet, -3)[0]
                        packet_data = packet[3:-3]
                        packet_crc = binascii.crc_hqx(packet_data, 0)

                        if packet_crc != packet_crc_from_msg:
                            _LOGGER.error("QueueProcessor: Invalid CRC expected %s got %s", hex(packet_crc), hex(packet_crc_from_msg))
                            continue

                        if packet_data and len(packet_data)>8:
                            packet_number = packet_data[8]
                            future = self._pending_requests.pop(packet_number, None)
                            if future:
                                future.set_result(packet_data)

                        if self._rx_event_handler:
                            self._rx_event_handler(packet_data)

                    except struct.error as e:
                        _LOGGER.error(
                            "QueueProcessor: Struct unpack error during packet processing: %s. Packet: %s.", e, bin2hex(packet)
                        )
                    except Exception as ex:
                        _LOGGER.exception(
                            "QueueProcessor: Exception while processing a packet: %s. Packet: %s.", ex, bin2hex(packet)
                        )
            except asyncio.CancelledError:
                _LOGGER.info("Queue processor task was cancelled.")
                break
            except Exception as ex:
                _LOGGER.exception("QueueProcessor: Error processing queue item: %s", ex)
            if self._rx_queue is None:
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

    async def send_command(self, message: list[str], wait_for_reply: bool = False, reply_timeout: float = 5.0) -> int | None:
        """Send a command to the NASA device."""
        if not self._connection_status or self._tx_queue is None:
            return False
        last_packet_number = None
        for msg in message:
            self._packet_number_counter = (self._packet_number_counter + 1) % 256
            last_packet_number = self._packet_number_counter
            current_packet_num_hex = f"{self._packet_number_counter:02x}"
            msg = msg.format(CUR_PACK_NUM=current_packet_num_hex)
            try:
                data_bytes = hex2bin(msg)
                # Packet size is the length of the data section (Source Address Class to CRC, inclusive).
                # data_bytes is the data section *before* CRC. CRC is 2 bytes.
                packet_size_hex = f"{(len(data_bytes) + 2):04x}"
                crc_val = binascii.crc_hqx(data_bytes, 0)
                crc_hex = f"{crc_val:04x}"
                full_packet_hex = f"32{packet_size_hex}{msg}{crc_hex}34"  # STX, Size, Data, CRC, ETX
                data = hex2bin(full_packet_hex)
                if wait_for_reply:
                    self._pending_requests[last_packet_number] = asyncio.Future()
                await self._tx_queue.put(data)
                _LOGGER.debug("Command enqueued: %s", bin2hex(data))
                try:
                    if wait_for_reply:
                        await asyncio.wait_for(self._pending_requests[last_packet_number], timeout=reply_timeout)
                except asyncio.TimeoutError as e:
                    raise TimeoutError(f"No response received within {reply_timeout} seconds.") from e
                finally:
                    self._pending_requests.pop(last_packet_number, None)
            except (binascii.Error, ValueError) as e:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("Error encoding command %s: %s", msg, e)
                return False
            except asyncio.QueueFull:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("TX queue is full, cannot send command: %s", msg)
                return False
            except Exception as e:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("Unexpected error sending command %s: %s", msg, e)
                return False
        _LOGGER.debug("All commands sent to TX queue.")
        return last_packet_number
