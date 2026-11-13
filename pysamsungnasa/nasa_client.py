"""TCP Modbus client."""

import asyncio
import binascii
import logging
import struct
import time
from asyncio import iscoroutinefunction
from collections import deque

import serialx

from .config import NasaConfig
from .device import NasaDevice
from .helpers import bin2hex, hex2bin
from .protocol.enum import DataType
from .protocol.factory import build_message
from .protocol.factory.types import SendMessage

_LOGGER = logging.getLogger(__name__)


class NasaClient:
    """Represent a NASA Client."""

    def __init__(
        self,
        config: NasaConfig,
        recv_event_handler=None,
        send_event_handler=None,
        disconnect_event_handler=None,
    ) -> None:
        """Init a NASA Client."""
        if config.device_path is None:
            raise ValueError("Device path must be set")
        self._config = config

        # Connection handling
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.listener_task: asyncio.Task | None = None
        self._is_connected = False
        self.timeout = 10
        self._connection_lock = asyncio.Lock()

        # Packet handling
        self.pnp_auto_discovery_packet_handler = None
        self._queue_processor_task: asyncio.Task | None = None
        self._writer_task: asyncio.Task | None = None
        self._retry_manager_task: asyncio.Task | None = None
        self._tx_queue: asyncio.Queue[bytes] | None = None
        # Half-duplex bus lock: held while RX is being processed or TX is in progress.
        self._receiving: asyncio.Lock = asyncio.Lock()
        self._bus_idle_gap = 0.05  # seconds of silence required before TX
        self._rx_queue: asyncio.Queue[bytes] | None = None
        self._rx_buffer = b""
        # Last actual serial RX. Used by the 120s liveness watchdog — must not be
        # refreshed by TX, or a polling client will never notice a silent bus.
        self._last_rx_time: float | None = None
        # Last RX or TX. Used only for the half-duplex inter-frame idle gap.
        self._last_bus_time: float | None = None
        self._packet_number_counter: int = 0
        self._pending_reads: dict = {}  # Track pending read requests for retry logic
        self._queued_reads: dict = {}  # Queue of read requests per destination waiting to be sent
        self._pending_writes: dict = {}  # Track pending write requests for retry logic

        self._rx_event_handler = recv_event_handler
        self._tx_event_handler = send_event_handler
        self._disconnect_event_handler = disconnect_event_handler
        self._config = config
        self._address = config.address

        # CRC failure diagnostics: packet detail goes to DEBUG; a rate-limited
        # WARNING summary keeps failures visible without flooding the log.
        self._crc_failure_count = 0
        self._crc_failures_since_summary = 0
        self._last_crc_summary_time = 0.0
        self._last_crc_error: tuple[int, int] | None = None
        # Optional bounded ring buffer of recent RX frames for diagnostics.
        self._rx_capture: deque[str] | None = (
            deque(maxlen=config.packet_capture_size) if config.enable_packet_capture else None
        )

        _LOGGER.debug("NasaClient initialized with config: %s", config)

    @property
    def rx_capture(self) -> tuple[str, ...]:
        """Return recent captured RX frames (oldest first) when capture is enabled."""
        if self._rx_capture is None:
            return ()
        return tuple(self._rx_capture)

    def _capture(self, kind: str, data: bytes) -> None:
        """Append a bounded diagnostic entry for an RX frame, if capture is enabled."""
        if self._rx_capture is None:
            return
        self._rx_capture.append(f"{time.time():.3f} {kind} {bin2hex(data)}")

    def _record_crc_failure(self, packet: bytes, expected: int, got: int) -> None:
        """Record and log a CRC validation failure.

        The full packet hex is logged at DEBUG so it can be enabled temporarily
        for diagnosis, while a rate-limited WARNING summary keeps a concise
        failure signal visible during sustained operation.
        """
        self._crc_failure_count += 1
        self._crc_failures_since_summary += 1
        self._last_crc_error = (expected, got)
        self._capture("crc_error", packet)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "QueueProcessor: Invalid CRC expected %s got %s. Packet: %s.",
                hex(expected),
                hex(got),
                bin2hex(packet),
            )
        interval = self._config.crc_log_interval
        now = time.monotonic()
        if interval and (now - self._last_crc_summary_time) >= interval:
            total = self._crc_failure_count
            since = self._crc_failures_since_summary
            detail = ""
            if self._last_crc_error is not None:
                detail = f" (last: expected {hex(self._last_crc_error[0])} got {hex(self._last_crc_error[1])})"
            _LOGGER.warning(
                "QueueProcessor: %d CRC validation failure(s) since start, %d since last summary%s. "
                "Enable DEBUG logging for raw packet hex.",
                total,
                since,
                detail,
            )
            self._crc_failures_since_summary = 0
            self._last_crc_summary_time = now

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._is_connected and self.writer is not None and not self.writer.is_closing()

    @property
    def is_read_locked(self) -> bool:
        """Return read lock status."""
        return self._receiving.locked()

    @property
    def is_connection_locked(self) -> bool:
        """Return connection lock status."""
        return self._connection_lock.locked()

    def set_receive_event_handler(self, handler) -> None:
        """Set the receive event handler."""
        self._rx_event_handler = handler

    async def _cancel_task(self, task: asyncio.Task | None) -> None:
        """Cancel a background task, skipping await when called from that task."""
        if task is None or task.done():
            return
        if task is asyncio.current_task():
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception:
            _LOGGER.debug("Exception during task cancellation/cleanup", exc_info=True)

    async def _close_transport(self) -> None:
        """Close the SerialX writer and drop reader/writer references."""
        writer = self.writer
        self.writer = None
        self.reader = None
        if writer is None:
            return
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            _LOGGER.debug("Error closing SerialX writer for %s", self._config.device_path, exc_info=True)

    async def _invoke_disconnect_handler(self) -> None:
        """Invoke the disconnect callback, awaiting coroutine results."""
        if not self._disconnect_event_handler:
            return
        try:
            result = self._disconnect_event_handler()
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            _LOGGER.exception("Error in disconnection_handler")

    async def _handle_disconnection(self, ex: Exception | None = None) -> None:
        """Handle disconnection.

        Writer/listener errors must actually drop the connection: mark disconnected,
        close the SerialX transport, stop background tasks, and await async
        disconnect handlers so callers can reconnect.

        Do not use ``is_connected`` here: that property is False once the
        transport is already closing (typical after ConnectionResetError),
        which previously skipped teardown and left reconnect handlers uncalled.
        """
        if not self._is_connected and self.writer is None:
            _LOGGER.debug("Already disconnected or not connected.")
            return
        if ex:
            _LOGGER.warning("NasaClient disconnected due to an error: %s", ex)
        else:
            _LOGGER.info("NasaClient disconnecting.")
        await self.disconnect()

    async def _handle_connection(self) -> None:
        """Handle connection."""
        _LOGGER.debug("Successfully connected to %s", self._config.device_path)
        now = asyncio.get_running_loop().time()
        self._last_rx_time = now
        self._last_bus_time = now
        await self._start_read_queue_session()
        await self._start_writer_session()
        await self._start_retry_manager_session()

    async def connect(self) -> bool:
        """Connect to the server and start background tasks."""
        if not self._config.device_path:
            _LOGGER.error("URL must be set before connecting.")
            return False
        if self.is_connected:
            _LOGGER.error("Already connected. To reconnect, disconnect first or use reconnect method.")
            return True

        try:
            async with self._connection_lock:
                self.reader, self.writer = await serialx.open_serial_connection(
                    url=self._config.device_path,
                    key=self._config.device_key,
                    baudrate=self._config.client_baudrate,
                    timeout=self.timeout,
                    byte_size=8,
                    parity=serialx.Parity.EVEN,
                    stopbits=serialx.StopBits.ONE,
                )
                if self.listener_task is None or self.listener_task.done():
                    self.listener_task = asyncio.create_task(self._listener_task())
                self._is_connected = True
                await self._handle_connection()
            return True
        except (OSError, TimeoutError) as ex:
            _LOGGER.error("NASA Connection error: %s", ex)
            await self._handle_disconnection(ex)
            return False
        except Exception as ex:
            _LOGGER.error("Unexpected error during connection: %s", ex)
            await self._handle_disconnection(ex)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the server and release the SerialX transport."""
        invoke_handler = False
        async with self._connection_lock:
            if not self._is_connected and self.writer is None:
                _LOGGER.debug("Already disconnected or not connected.")
                return
            invoke_handler = True
            self._is_connected = False

            listener = self.listener_task
            self.listener_task = None
            # Skip cancelling ourselves when the listener is the caller; it will exit
            # after disconnect() returns. Clearing the attribute lets a reconnect
            # handler start a new listener.
            if listener is not None and listener is not asyncio.current_task():
                await self._cancel_task(listener)

            await self._end_writer_session()
            await self._end_read_queue_session()
            await self._end_retry_manager_session()
            await self._close_transport()

        # Invoke outside the connection lock so a handler can call connect().
        if invoke_handler:
            await self._invoke_disconnect_handler()

    async def _wait_for_bus_idle(self) -> None:
        """Wait until the bus has been quiet for `_bus_idle_gap` seconds."""
        while self.is_connected:
            last = self._last_bus_time
            if last is None:
                return
            remaining = self._bus_idle_gap - (asyncio.get_running_loop().time() - last)
            if remaining <= 0:
                return
            await asyncio.sleep(remaining)

    async def _listener_task(self):
        """Listen for incoming messages from the SerialX device."""
        _LOGGER.debug("Starting listener task for SerialX device at URL: %s", self._config.device_path)
        try:
            while self.is_connected and self.reader:
                # Timeout if no data has been received in the last 120 seconds
                if self._last_rx_time is not None and asyncio.get_running_loop().time() - self._last_rx_time > 120:
                    _LOGGER.warning("No data received in the last 120 seconds, closing connection.")
                    await self.disconnect()
                    break
                try:
                    async with asyncio.timeout(30):
                        # Read until ETX (0x34). Timeout means the bus is idle — allow TX.
                        data = await self.reader.readuntil(0x34.to_bytes())
                except TimeoutError:
                    continue

                # Hold the bus lock while RX is active so the writer cannot collide mid-frame.
                async with self._receiving:
                    now = asyncio.get_running_loop().time()
                    self._last_rx_time = now
                    self._last_bus_time = now
                    if data:
                        _LOGGER.debug("Received message from SerialX device at URL: %s", self._config.device_path)
                        await self._read_buffer_handler(data)
                    else:
                        _LOGGER.warning(
                            "SerialX device at URL: %s has closed the connection.", self._config.device_path
                        )
                        await self.disconnect()
                        break
            # Transport closed underneath us (is_closing) without an exception.
            if self._is_connected:
                _LOGGER.warning(
                    "Listener loop exited while session still marked connected for %s.",
                    self._config.device_path,
                )
                await self.disconnect()
        except asyncio.IncompleteReadError:
            _LOGGER.debug("SerialX device at URL: %s has closed the connection.", self._config.device_path)
            await self.disconnect()
        except asyncio.CancelledError:
            # Cancellation is the disconnect path tearing us down. Do not re-enter
            # disconnect() while it holds the connection lock — that deadlocks.
            _LOGGER.info("Listener task for SerialX device at URL %s has been cancelled.", self._config.device_path)
            raise
        except OSError:
            _LOGGER.info(
                "Listener task for SerialX device at URL %s encountered an OS error.", self._config.device_path
            )
            await self.disconnect()
        except Exception:
            _LOGGER.exception(
                "Listener task for SerialX device at URL %s encountered an error.", self._config.device_path
            )
            await self.disconnect()

    async def _read_buffer_handler(self, message: bytes):
        """Read buffer handler."""
        self._capture("raw", message)
        self._rx_buffer += message
        if len(self._rx_buffer) > self._config.max_buffer_size:
            _LOGGER.error(
                "Max buffer sized reached %s/%s",
                len(self._rx_buffer),
                self._config.max_buffer_size,
            )
            self._rx_buffer = b""
            return
        while True:
            if not self._rx_buffer:
                break

            stx_index = self._rx_buffer.find(b"\x32")

            if stx_index == -1:
                if self._config.log_buffer_messages:
                    _LOGGER.debug("No STX found, clearing buffer")
                self._rx_buffer = b""
                break

            if stx_index > 0:
                if self._config.log_buffer_messages:
                    _LOGGER.debug("Skipping %d bytes of garbage", stx_index)
                self._rx_buffer = self._rx_buffer[stx_index:]

            if len(self._rx_buffer) < 3:
                if self._config.log_buffer_messages:
                    _LOGGER.debug("Not enough data for header, waiting for more.")
                break

            expected_packet_len = 0
            try:
                _, packet_len_val = struct.unpack_from(">BH", self._rx_buffer)

                if packet_len_val < 14:
                    # A NASA payload is at least 10 bytes (source + destination
                    # addresses, info, type, packet number, capacity), so any
                    # declared size below 14 (10 payload + 4 CRC/size) cannot be
                    # a real frame. Treat this STX as garbage and resync.
                    _LOGGER.debug(
                        "Parsed packet length %d is below the NASA minimum. Resyncing.",
                        packet_len_val,
                    )
                    self._rx_buffer = self._rx_buffer[1:]
                    continue

                if packet_len_val + 2 > self._config.max_packet_size:
                    # Declared size exceeds the maximum plausible NASA frame.
                    # Resync immediately instead of waiting for the declared
                    # number of bytes, which would stall parsing of subsequent
                    # valid frames for seconds at 9600 baud.
                    _LOGGER.debug(
                        "Parsed packet length %d exceeds plausible maximum %d. Resyncing.",
                        packet_len_val,
                        self._config.max_packet_size - 2,
                    )
                    self._rx_buffer = self._rx_buffer[1:]
                    continue

                expected_packet_len = packet_len_val + 2  # + STX and ETX

                if len(self._rx_buffer) < expected_packet_len:
                    # If the expected packet is suspiciously large, check if there's
                    # another STX marker nearby (indicating a malformed packet)
                    if expected_packet_len > 2000 and len(self._rx_buffer) > 500:
                        # Look for the next STX within a reasonable distance
                        next_stx = self._rx_buffer.find(b"\x32", 1)  # Start searching after current STX
                        if next_stx > 0 and next_stx < 300:
                            # Found another STX marker nearby - current packet is likely malformed
                            self._rx_buffer = self._rx_buffer[next_stx:]
                            continue

                    if self._config.log_buffer_messages:
                        _LOGGER.debug(
                            "Incomplete packet. Have %d, need %d. Waiting for more data.",
                            len(self._rx_buffer),
                            expected_packet_len,
                        )
                    break

                packet = self._rx_buffer[:expected_packet_len]

                if packet[-1] != 0x34:
                    if self._config.log_buffer_messages:
                        _LOGGER.debug("Invalid ETX. Got 0x%02x, expected 0x34.", packet[-1])
                    self._rx_buffer = self._rx_buffer[1:]
                    continue

                if self._rx_queue:
                    await self._rx_queue.put(packet)
                    self._capture("pkt", packet)
                    if self._config.log_buffer_messages:
                        _LOGGER.debug(
                            "Received complete packet and queued for processing (pending=%s): %s",
                            self._rx_queue.qsize(),
                            bin2hex(packet),
                        )

                self._rx_buffer = self._rx_buffer[expected_packet_len:]

            except struct.error:
                _LOGGER.debug("Struct unpack failed. Likely not a valid packet. Discarding STX and continuing.")
                self._rx_buffer = self._rx_buffer[1:]
                continue
            except asyncio.QueueFull:
                _LOGGER.warning("RX queue is full. Packet dropped.")
                if expected_packet_len > 0:
                    self._rx_buffer = self._rx_buffer[expected_packet_len:]
                continue

    async def _start_writer_session(self) -> bool:
        """Start writer task from queue."""
        if self._writer_task and not self._writer_task.done():
            _LOGGER.error("Writer task already running.")
            return True
        if not self.is_connected:
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
            await self._cancel_task(task)
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
            await self._cancel_task(task)
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

    async def _start_retry_manager_session(self) -> bool:
        """Start retry manager task."""
        if self._retry_manager_task and not self._retry_manager_task.done():
            _LOGGER.error("Retry manager task already running.")
            return True
        if not (self._config.enable_read_retries or self._config.enable_write_retries):
            _LOGGER.debug("Retries are disabled in config.")
            return False
        self._retry_manager_task = asyncio.create_task(self._retry_manager())
        _LOGGER.debug("Retry manager session started.")
        return True

    async def _end_retry_manager_session(self) -> bool:
        """End retry manager session."""
        task_was_present = self._retry_manager_task is not None
        if self._retry_manager_task:
            task = self._retry_manager_task
            self._retry_manager_task = None
            await self._cancel_task(task)
            _LOGGER.debug("Retry manager session ended.")
        return task_was_present

    async def _read_queue_processor(self):
        """Async read queue processor task. Processes complete packets from the queue."""
        if self._rx_queue is None:
            _LOGGER.error("QueueProcessor: RX queue is None at start, exiting.")
            return

        _LOGGER.debug("Queue processor task started.")
        while self.is_connected or (self._rx_queue and not self._rx_queue.empty()):
            try:
                if self._rx_queue:
                    try:
                        # Use a timeout to allow the loop to check _connection_status
                        packet = await asyncio.wait_for(self._rx_queue.get(), timeout=1.0)
                        self._rx_queue.task_done()
                    except asyncio.TimeoutError:
                        if not self.is_connected and self._rx_queue.empty():
                            break  # Exit if disconnected and queue is now empty
                        continue  # Loop again to check _connection_status or get next item

                    # Validate packet structure
                    if len(packet) < 6 or packet[0] != 0x32 or packet[-1] != 0x34:
                        _LOGGER.error(
                            "QueueProcessor: Invalid packet structure: %s",
                            bin2hex(packet),
                        )
                        continue
                    try:
                        packet_crc_from_msg = struct.unpack_from(">H", packet, -3)[0]
                        # Extract message data (from after STX+Size to before CRC+ETX)
                        # Packet: [STX] [Size-H] [Size-L] [Data...] [CRC-H] [CRC-L] [ETX]
                        # Index:  [0]   [1]      [2]      [3...]    [-3]    [-2]    [-1]
                        packet_data = packet[3:-3]
                        packet_crc = binascii.crc_hqx(packet_data, 0)

                        if packet_crc != packet_crc_from_msg:
                            self._record_crc_failure(packet, packet_crc, packet_crc_from_msg)
                            continue

                        if self._rx_event_handler and callable(self._rx_event_handler):
                            if iscoroutinefunction(self._rx_event_handler):
                                await self._rx_event_handler(packet_data)
                            else:
                                self._rx_event_handler(packet_data)

                    except struct.error as e:
                        _LOGGER.error(
                            "QueueProcessor: Struct unpack error during packet processing: %s. Packet: %s.",
                            e,
                            bin2hex(packet),
                        )
                    except Exception as ex:
                        _LOGGER.exception(
                            "QueueProcessor: Exception while processing a packet: %s. Packet: %s.",
                            ex,
                            bin2hex(packet),
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
        if self._tx_queue is None or self._rx_queue is None or self.writer is None:
            _LOGGER.error("Writer: TX queue or socket writer is None at start, exiting.")
            return
        _LOGGER.debug("Writer task started.")
        while self.is_connected:
            try:
                # Use timeout to allow periodic check of _connection_status
                cmd = await asyncio.wait_for(self._tx_queue.get(), timeout=1.0)
                if cmd is not None:
                    # Half-duplex: wait for RX silence, then take the bus exclusively for TX.
                    await self._wait_for_bus_idle()
                    async with self._receiving:
                        # Re-check idle after acquiring — RX may have run while we waited for the lock.
                        await self._wait_for_bus_idle()
                        if self.writer is None or self.writer.is_closing():
                            _LOGGER.warning("Writer: Socket writer is None or closing, cannot write.")
                            self._tx_queue.task_done()
                            await self._handle_disconnection()
                            break

                        _LOGGER.debug("Writer: Writing data: %s", bin2hex(cmd))
                        self.writer.write(cmd)
                        await self.writer.drain()
                        # Treat TX as bus activity so the next send also observes the idle gap.
                        # Do not refresh _last_rx_time: outgoing polls must not hide a dead RX path.
                        self._last_bus_time = asyncio.get_running_loop().time()
                        if self._tx_event_handler:
                            try:
                                self._tx_event_handler(cmd)
                            except Exception:
                                _LOGGER.exception("Error in tx_event_handler")
                    # Turnaround gap outside the lock so RX can process replies.
                    await asyncio.sleep(self._bus_idle_gap)
                self._tx_queue.task_done()
            except TimeoutError:
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

        if self._is_connected:
            _LOGGER.warning("Writer loop exited while session still marked connected.")
            await self._handle_disconnection()

    async def send_command(
        self,
        message: list[str],
    ) -> int | bytes | None:
        """Send a command to the NASA device."""
        if not self.is_connected or self._tx_queue is None:
            return None

        last_packet_number = None
        # Note: This loop will wait for a reply for the *first* message in the list
        # if wait_for_reply is True, and then return, not processing subsequent messages.
        # This matches the original logic.
        for msg in message:
            self._packet_number_counter = (self._packet_number_counter + 1) % 256
            last_packet_number = self._packet_number_counter
            current_packet_num_hex = f"{self._packet_number_counter:02x}"
            msg = msg.format(CUR_PACK_NUM=current_packet_num_hex)

            try:
                data_bytes = hex2bin(msg)
                crc_val = binascii.crc_hqx(data_bytes, 0)
                crc_hex = f"{crc_val:04x}"
                packet_size_hex = f"{(len(data_bytes) + 4):04x}"
                full_packet_hex = f"32{packet_size_hex}{msg}{crc_hex}34"  # STX, Size, Data, CRC, ETX
                data = hex2bin(full_packet_hex)
                await self._tx_queue.put(data)
                _LOGGER.debug("Command enqueued (no reply): %s", bin2hex(data))
            except (binascii.Error, ValueError) as e:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("Error encoding command %s: %s", msg, e)
                return None
            except asyncio.QueueFull:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("TX queue is full, cannot send command: %s", msg)
                return None
            except Exception as e:
                self._packet_number_counter = (self._packet_number_counter - 1) % 256
                _LOGGER.error("Unexpected error sending command %s: %s", msg, e)
                return None

        return last_packet_number

    async def send_message(
        self,
        destination: NasaDevice | str,
        request_type: DataType = DataType.REQUEST,
        messages: list[SendMessage] | None = None,
        source: str | None = None,
        completion_future: asyncio.Future | None = None,
    ) -> int | bytes | None:
        """Send a message to the device using the client.

        When ``completion_future`` is provided and the message is a write
        (``DataType.WRITE`` or ``DataType.REQUEST`` with write retries enabled),
        the future resolves when the transaction reaches a terminal state:
        ``"ack"`` (device acknowledged), ``"nack"`` (device rejected),
        ``"abandoned"`` (retry budget exhausted), ``"superseded"`` (a newer
        write to the same message IDs took over), ``"unconfirmed"`` (sent
        without retry tracking) or ``"failed"`` (send error). It never resolves
        for fire-and-forget sends, keeping the existing API untouched.
        """
        if not self.is_connected:
            _LOGGER.error("Cannot send message, client is not connected.")
            if completion_future is not None and not completion_future.done():
                completion_future.set_result("failed")
            return
        if isinstance(destination, str):
            destination_address = destination
        elif isinstance(destination, NasaDevice):
            destination_address = destination.address
        else:
            _LOGGER.error("Invalid destination type: %s", type(destination))
            if completion_future is not None and not completion_future.done():
                completion_future.set_result("failed")
            return
        if messages is None:
            raise ValueError("At least one message is required.")
        source_address = source if source is not None else str(self._config.address)
        future_tracked = False
        try:
            packet_number = await self.send_command(
                [
                    build_message(
                        source=source_address,
                        destination=destination_address,
                        data_type=request_type,
                        messages=messages,
                    )
                ],
            )

            # Track requests for retry logic if enabled.
            # If an entry already exists for the same payload (retry manager resend),
            # preserve attempt/backoff state instead of resetting to zero.
            if packet_number is not None:
                current_time = asyncio.get_running_loop().time()
                if request_type in (DataType.WRITE, DataType.REQUEST) and self._config.enable_write_retries:
                    # Track all messages in the packet together using a stable
                    # dest+message_ids key so retries (which allocate a new packet
                    # number) update the same entry instead of creating duplicates.
                    message_ids = [msg.MESSAGE_ID for msg in messages]
                    write_key = f"{destination_address}_{tuple(sorted(message_ids))}"
                    existing_write = self._pending_writes.get(write_key)
                    if existing_write is None:
                        future_tracked = True
                        self._pending_writes[write_key] = {
                            "destination": destination_address,
                            "message_ids": message_ids,
                            "messages": messages,  # Store full SendMessage objects for retry
                            "data_type": request_type,
                            "packet_number": packet_number,
                            "packet_numbers": {packet_number},
                            "attempts": 0,
                            "last_attempt_time": current_time,
                            "next_retry_time": current_time + self._config.write_retry_interval,
                            "retry_interval": self._config.write_retry_interval,
                            "completion_future": completion_future,
                        }
                    else:
                        # Same message IDs can be a retry of the same payload, or a new
                        # user write (e.g. 20°C then 22°C before the first ACK). Only
                        # retries should accept an ACK for an earlier packet number;
                        # a different payload must not be completed by the old ACK.
                        same_payload = self._write_payload_fingerprint(
                            existing_write.get("messages")
                        ) == self._write_payload_fingerprint(messages)
                        previous_packet = existing_write.get("packet_number")
                        existing_write["destination"] = destination_address
                        existing_write["message_ids"] = message_ids
                        existing_write["messages"] = messages
                        existing_write["data_type"] = request_type
                        existing_write["packet_number"] = packet_number
                        existing_write["last_attempt_time"] = current_time
                        if same_payload:
                            tracked_packets = existing_write.get("packet_numbers")
                            if not isinstance(tracked_packets, set):
                                tracked_packets = set()
                                if previous_packet is not None:
                                    tracked_packets.add(previous_packet)
                                existing_write["packet_numbers"] = tracked_packets
                            tracked_packets.add(packet_number)
                        else:
                            existing_write["packet_numbers"] = {packet_number}
                            existing_write["attempts"] = 0
                            existing_write["retry_interval"] = self._config.write_retry_interval
                            existing_write["next_retry_time"] = current_time + self._config.write_retry_interval
                        # Attach the caller's completion future, superseding any
                        # future a previous caller attached to this entry.
                        if completion_future is not None and existing_write.get("completion_future") not in (
                            None,
                            completion_future,
                        ):
                            self._complete_transaction_future(existing_write["completion_future"], "superseded")
                        if completion_future is not None:
                            future_tracked = True
                            existing_write["completion_future"] = completion_future
                elif request_type == DataType.READ and self._config.enable_read_retries:
                    message_ids = [msg.MESSAGE_ID for msg in messages]
                    read_key = f"{destination_address}_{tuple(sorted(message_ids))}"
                    existing_read = self._pending_reads.get(read_key)
                    if existing_read is None:
                        self._pending_reads[read_key] = {
                            "destination": destination_address,
                            "messages": message_ids,
                            "packet_number": packet_number,
                            "attempts": 0,
                            "last_attempt_time": current_time,
                            "next_retry_time": current_time + self._config.read_retry_interval,
                            "retry_interval": self._config.read_retry_interval,
                        }
                    else:
                        # Keep retry counters/backoff, only refresh packet number and timing metadata.
                        existing_read["destination"] = destination_address
                        existing_read["messages"] = message_ids
                        existing_read["packet_number"] = packet_number
                        existing_read["last_attempt_time"] = current_time

            if completion_future is not None and not future_tracked and not completion_future.done():
                # The packet was not tracked for retries (send failed, retries
                # disabled, or a non-write type): resolve so awaiting callers
                # do not hang until their own timeout.
                _LOGGER.debug(
                    "Write completion future not tracked for %s (packet %s, type %s); completing as unconfirmed.",
                    destination_address,
                    packet_number,
                    request_type,
                )
                completion_future.set_result("unconfirmed")

            return packet_number
        except Exception as e:
            _LOGGER.exception("Error sending message to device %s: %s", destination_address, e)
            if completion_future is not None and not completion_future.done():
                completion_future.set_result("failed")

    async def nasa_read(self, msgs: list[int], destination: NasaDevice | str = "B0FF20") -> int | bytes | None:
        """Send read requests to a device to read data."""
        dest_addr = destination if isinstance(destination, str) else destination.address

        # Check if there's already a pending read to this destination
        if self._config.enable_read_retries:
            has_pending_read = any(read_info["destination"] == dest_addr for read_info in self._pending_reads.values())
            if has_pending_read:
                # Queue this read to be sent after the current one completes
                if dest_addr not in self._queued_reads:
                    self._queued_reads[dest_addr] = []
                self._queued_reads[dest_addr].append(msgs)
                _LOGGER.debug(
                    "Queuing read request for messages %s to %s (queue size: %d)",
                    msgs,
                    dest_addr,
                    len(self._queued_reads[dest_addr]),
                )
                return None

        return await self.send_message(
            destination=destination,
            request_type=DataType.READ,
            messages=[SendMessage(MESSAGE_ID=imn, PAYLOAD=b"\x05\xa5\xa5\xa5") for imn in msgs],
        )

    async def nasa_write(
        self, msg: int, value: str, destination: NasaDevice | str, data_type: DataType
    ) -> int | bytes | None:
        """Send write requests to a device to write data."""
        message = SendMessage(MESSAGE_ID=msg, PAYLOAD=hex2bin(value))

        return await self.send_message(
            destination=destination,
            request_type=data_type,
            messages=[message],
        )

    @staticmethod
    def _write_payload_fingerprint(messages: list[SendMessage] | None) -> tuple[tuple[int, bytes], ...]:
        """Return a stable fingerprint of message IDs and payloads for a write."""
        if not messages:
            return ()
        return tuple(sorted((msg.MESSAGE_ID, bytes(msg.PAYLOAD)) for msg in messages))

    @staticmethod
    def _tracked_write_packet_numbers(write_info: dict) -> set[int]:
        """Return packet numbers associated with a pending write, including retries."""
        tracked = write_info.get("packet_numbers")
        if isinstance(tracked, set):
            return {num for num in tracked if num is not None}
        packet_number = write_info.get("packet_number")
        return {packet_number} if packet_number is not None else set()

    @staticmethod
    def _complete_transaction_future(future: asyncio.Future | None, outcome: str) -> None:
        """Resolve a transaction completion future with the given outcome."""
        if future is None or future.done():
            return
        try:
            future.set_result(outcome)
        except asyncio.InvalidStateError:
            pass

    def _clear_pending_write(
        self,
        destination: str,
        message_numbers: list[int],
        packet_number: int | None = None,
        outcome: str = "ack",
    ) -> list[str]:
        """Clear pending write requests when an ACK or NACK is received.

        Packet number is the only safe correlation for ACK/NACK: a read ACK, a
        RESPONSE containing the same message IDs, or an empty ACK for another
        packet must not complete unrelated in-flight writes.

        When packet_number is omitted (unit tests of message-ID matching), fall
        back to requiring every tracked message ID to be present. An empty
        message list without a packet number does not clear anything.

        ``outcome`` distinguishes an acknowledged write (``"ack"``) from one the
        device rejected (``"nack"``) so awaiting callers can tell success from
        rejection.

        Returns the list of write keys that were cleared.
        """
        cleared_keys = []
        cleared_entries = []
        keys_to_delete = []

        for write_key, write_info in self._pending_writes.items():
            if write_info["destination"] != destination:
                continue
            if packet_number is not None:
                if packet_number in self._tracked_write_packet_numbers(write_info):
                    keys_to_delete.append(write_key)
                    cleared_keys.append(write_key)
                    cleared_entries.append(write_info)
                continue
            if message_numbers:
                packet_message_ids = write_info.get("message_ids", [])
                if packet_message_ids and all(msg_id in message_numbers for msg_id in packet_message_ids):
                    keys_to_delete.append(write_key)
                    cleared_keys.append(write_key)
                    cleared_entries.append(write_info)

        for key in keys_to_delete:
            del self._pending_writes[key]
            _LOGGER.debug("Cleared pending write request for key %s", key)

        for write_info in cleared_entries:
            self._complete_transaction_future(write_info.get("completion_future"), outcome)

        return cleared_keys

    async def _mark_write_received(
        self,
        destination: str,
        message_numbers: list[int],
        packet_number: int | None = None,
        outcome: str = "ack",
    ) -> None:
        """Mark write requests as received when an ACK or NACK is received."""
        cleared = self._clear_pending_write(destination, message_numbers, packet_number=packet_number, outcome=outcome)
        if cleared:
            _LOGGER.debug(
                "Write %s received from %s (packet %s, messages %s), cleared %d pending write(s)",
                outcome.upper(),
                destination,
                packet_number,
                message_numbers if message_numbers else "unspecified",
                len(cleared),
            )

    def _clear_pending_read(self, destination: str, message_numbers: list[int]) -> bool:
        """Clear pending read requests when a response contains the requested messages.

        A response may include extra message IDs beyond those requested. Clear any
        pending read whose requested IDs are a subset of the response.
        """
        if not message_numbers:
            return False

        keys_to_delete = []
        response_ids = set(message_numbers)
        for read_key, read_info in self._pending_reads.items():
            if read_info["destination"] != destination:
                continue
            requested = set(read_info.get("messages", []))
            if requested and requested.issubset(response_ids):
                keys_to_delete.append(read_key)

        for key in keys_to_delete:
            del self._pending_reads[key]
            _LOGGER.debug("Cleared pending read request for key %s from %s", key, destination)

        return bool(keys_to_delete)

    async def _mark_read_received(
        self,
        destination: str,
        message_numbers: list[int],
        payload_type: DataType | None = None,
        packet_number: int | None = None,
    ) -> None:
        """Mark a read or write request as received (event callback from parser).

        ACK/NACK complete the matching write (by packet number). RESPONSE completes
        matching reads. Mixing those paths previously let a poll RESPONSE or an ACK
        for a different packet drop in-flight writes without an actual write ACK.
        """
        if payload_type in (DataType.ACK, DataType.NACK):
            await self._mark_write_received(
                destination,
                message_numbers,
                packet_number=packet_number,
                outcome="ack" if payload_type == DataType.ACK else "nack",
            )
            return

        if payload_type == DataType.RESPONSE or (payload_type is None and message_numbers):
            if self._clear_pending_read(destination, message_numbers):
                _LOGGER.debug("Read response received for messages %s from %s", message_numbers, destination)
            await self._process_queued_reads(destination)

    async def _process_queued_reads(self, destination: str) -> None:
        """Process queued reads for a destination after a response is received."""
        if destination not in self._queued_reads or not self._queued_reads[destination]:
            return

        # Get the next queued read
        queued_msgs = self._queued_reads[destination].pop(0)
        _LOGGER.debug(
            "Processing queued read for messages %s to %s (remaining in queue: %d)",
            queued_msgs,
            destination,
            len(self._queued_reads[destination]),
        )

        # Send the queued read
        try:
            await self.nasa_read(queued_msgs, destination=destination)
        except Exception as e:
            _LOGGER.error("Error processing queued read: %s", e)

    async def _retry_manager(self):
        """Manage retry logic for pending read and write requests."""
        _LOGGER.debug("Retry manager task started.")
        while self.is_connected:
            try:
                await asyncio.sleep(1.0)  # Check every second

                current_time = asyncio.get_running_loop().time()

                # Handle read retries
                if self._config.enable_read_retries and self._pending_reads:
                    reads_to_retry = []
                    reads_to_remove = []
                    abandoned_destinations = set()

                    # Identify reads that need to be retried
                    for read_key, read_info in list(self._pending_reads.items()):
                        if current_time >= read_info["next_retry_time"]:
                            if read_info["attempts"] < self._config.read_retry_max_attempts:
                                reads_to_retry.append(read_info)
                            else:
                                # Max retries exceeded
                                _LOGGER.warning(
                                    "Abandoning read request %s to %s after %d attempts",
                                    read_info["packet_number"],
                                    read_info["destination"],
                                    read_info["attempts"],
                                )
                                reads_to_remove.append(read_key)
                                abandoned_destinations.add(read_info["destination"])

                    # Remove reads that have exceeded max attempts
                    for read_key in reads_to_remove:
                        del self._pending_reads[read_key]

                    # Process queued reads for abandoned destinations
                    for destination in abandoned_destinations:
                        await self._process_queued_reads(destination)

                    # Retry the reads
                    for read_info in reads_to_retry:
                        read_info["attempts"] += 1
                        read_info["last_attempt_time"] = current_time
                        read_info["retry_interval"] *= self._config.read_retry_backoff_factor
                        read_info["next_retry_time"] = current_time + read_info["retry_interval"]

                        _LOGGER.debug(
                            "Retrying read request to %s (attempt %d/%d, interval=%.1fs)",
                            read_info["destination"],
                            read_info["attempts"],
                            self._config.read_retry_max_attempts,
                            read_info["retry_interval"],
                        )

                        # Resend the read request
                        try:
                            await self.send_message(
                                destination=read_info["destination"],
                                request_type=DataType.READ,
                                messages=[
                                    SendMessage(MESSAGE_ID=msg_id, PAYLOAD=b"\x05\xa5\xa5\xa5")
                                    for msg_id in read_info["messages"]
                                ],
                            )
                        except Exception as e:
                            _LOGGER.error("Error retrying read request: %s", e)

                # Handle write retries
                if self._config.enable_write_retries and self._pending_writes:
                    writes_to_retry = []
                    writes_to_remove = []

                    # Identify writes that need to be retried.
                    # Inspect each entry independently so a single bad record cannot
                    # abort the loop (which previously left abandoned writes in place
                    # and re-raised KeyError every second).
                    for write_key, write_info in list(self._pending_writes.items()):
                        try:
                            if current_time < write_info["next_retry_time"]:
                                continue
                            if write_info["attempts"] < self._config.write_retry_max_attempts:
                                writes_to_retry.append((write_key, write_info))
                            else:
                                # Max retries exceeded
                                _LOGGER.warning(
                                    "Abandoning write request %s (messages %s) to %s after %d attempts",
                                    write_info.get("packet_number"),
                                    write_info.get("message_ids"),
                                    write_info.get("destination"),
                                    write_info.get("attempts"),
                                )
                                writes_to_remove.append(write_key)
                        except Exception:
                            _LOGGER.exception(
                                "Error inspecting pending write %s; dropping it to avoid retry-manager stall",
                                write_key,
                            )
                            writes_to_remove.append(write_key)

                    # Remove writes that have exceeded max attempts
                    for _write_key in writes_to_remove:
                        write_info = self._pending_writes.pop(_write_key, None)
                        if write_info is not None:
                            self._complete_transaction_future(write_info.get("completion_future"), "abandoned")
                            _LOGGER.debug("Completed abandoned write request for key %s", _write_key)

                    # Retry the writes
                    for write_key, write_info in writes_to_retry:
                        write_info["attempts"] += 1
                        write_info["last_attempt_time"] = current_time
                        write_info["retry_interval"] *= self._config.write_retry_backoff_factor
                        write_info["next_retry_time"] = current_time + write_info["retry_interval"]

                        _LOGGER.debug(
                            "Retrying write request (messages %s) to %s (attempt %d/%d, interval=%.1fs)",
                            write_info["message_ids"],
                            write_info["destination"],
                            write_info["attempts"],
                            self._config.write_retry_max_attempts,
                            write_info["retry_interval"],
                        )

                        # Resend all messages in the packet together
                        try:
                            await self.send_message(
                                destination=write_info["destination"],
                                request_type=write_info["data_type"],
                                messages=write_info["messages"],
                            )
                        except Exception as e:
                            _LOGGER.error("Error retrying write request: %s", e)

            except asyncio.CancelledError:
                _LOGGER.info("Retry manager task was cancelled.")
                break
            except Exception as e:
                _LOGGER.exception("Error in retry manager: %s", e)

        _LOGGER.debug("Retry manager task finished.")
