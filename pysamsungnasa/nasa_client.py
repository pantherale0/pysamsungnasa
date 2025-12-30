"""TCP Modbus client."""

import binascii
import logging
import asyncio
import struct

from aiotelnet import TelnetClient

from .device import NasaDevice
from .protocol.enum import DataType
from .protocol.factory import build_message
from .protocol.factory.messaging import SendMessage

from .config import NasaConfig
from .helpers import bin2hex, hex2bin

_LOGGER = logging.getLogger(__name__)


class NasaClient:
    """Represent a NASA Client."""

    pnp_auto_discovery_packet_handler = None
    _queue_processor_task: asyncio.Task | None = None
    _writer_task: asyncio.Task | None = None
    _tx_queue: asyncio.Queue[bytes] | None = None
    _rx_queue: asyncio.Queue[bytes] | None = None
    _pending_requests: dict[int, asyncio.Future] = {}
    _rx_buffer = b""
    _last_rx_time: float = 0.0
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
        self._client = TelnetClient(
            host=host,
            port=port,
            message_handler=self._read_buffer_handler,
            break_line=0x34.to_bytes(),
            disconnect_callback=self._handle_disconnection,
            connect_callback=self._handle_connection,
        )
        self._rx_event_handler = recv_event_handler
        self._tx_event_handler = send_event_handler
        self._disconnect_event_handler = disconnect_event_handler
        self._config = config
        self._address = config.address
        self._last_rx_time = asyncio.get_event_loop().time()

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._client.is_connected()

    async def _handle_disconnection(self, ex: Exception | None = None) -> None:
        """Handle disconnection."""
        if not self.is_connected:
            _LOGGER.debug("Already disconnected or not connected.")
            return
        if ex:
            _LOGGER.warning("NasaClient disconnected due to an error: %s", ex)
        else:
            _LOGGER.info("NasaClient disconnecting.")

        # Stop tasks and clear queues
        # These methods cancel tasks and set them (and their queues) to None
        await self._end_writer_session()
        await self._end_read_queue_session()

        if self._disconnect_event_handler:
            try:
                res = self._disconnect_event_handler()
                if asyncio.iscoroutine(res):
                    await res
            except Exception as handler_ex:
                _LOGGER.error("Error in disconnection_handler: %s", handler_ex)

    async def _handle_connection(self) -> None:
        """Handle connection."""
        _LOGGER.debug("Successfully connected to %s:%s", self.host, self.port)
        self._last_rx_time = asyncio.get_event_loop().time()
        await self._start_read_queue_session()
        await self._start_writer_session()

    async def connect(self) -> bool:
        """Connect to the server and start background tasks."""
        if not (self.host and self.port):
            _LOGGER.error("Host and port must be set before connecting.")
            return False
        if self.is_connected:
            _LOGGER.error("Already connected. To reconnect, disconnect first or use reconnect method.")
            return True

        try:
            await self._client.connect()
            return True
        except ConnectionError as ex:
            _LOGGER.error("NASA Connection error: %s", ex)
            await self._handle_disconnection(ex)
            return False
        except Exception as ex:
            _LOGGER.error("Unexpected error during connection: %s", ex)
            await self._handle_disconnection(ex)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        await self._client.close()

    async def _read_buffer_handler(self, message: bytes):
        """Read buffer handler."""
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

                if packet_len_val > 4096:
                    _LOGGER.debug(
                        "Parsed packet length %d exceeds max size. Assuming parse error.",
                        packet_len_val,
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
                    _LOGGER.debug(
                        "Exception during queue processor task cancellation/cleanup: %s",
                        e,
                    )
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
                        packet_data = packet[3:-3]
                        packet_crc = binascii.crc_hqx(packet_data, 0)

                        if packet_crc != packet_crc_from_msg:
                            _LOGGER.error(
                                "QueueProcessor: Invalid CRC expected %s got %s",
                                hex(packet_crc),
                                hex(packet_crc_from_msg),
                            )
                            continue

                        if packet_data and len(packet_data) > 8:
                            packet_number = packet_data[8]
                            future = self._pending_requests.pop(packet_number, None)
                            if future:
                                future.set_result(packet_data)

                        if self._rx_event_handler:
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
        if self._tx_queue is None or self._rx_queue is None or self._client.writer is None:
            _LOGGER.error("Writer: TX queue or socket writer is None at start, exiting.")
            return
        _LOGGER.debug("Writer task started.")
        while self.is_connected:
            try:
                # Use timeout to allow periodic check of _connection_status
                cmd = await asyncio.wait_for(self._tx_queue.get(), timeout=1.0)
                if cmd is not None:
                    if self._client.writer is None or self._client.writer.is_closing():
                        _LOGGER.warning("Writer: Socket writer is None or closing, cannot write.")
                        self._tx_queue.task_done()  # Still mark as done
                        # Re-queue or discard? For now, discard and log.
                        break  # Exit writer as connection is likely lost

                    _LOGGER.debug("Writer: Writing data: %s", bin2hex(cmd))
                    self._client.writer.write(cmd)
                    await self._client.writer.drain()  # Crucial for flow control
                    await asyncio.sleep(0.05)  # delay 50ms to prevent overloading the protocol.
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

    async def send_command(
        self,
        message: list[str],
        wait_for_reply: bool = False,
        reply_timeout: float = 5.0,
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

                if not wait_for_reply:
                    await self._tx_queue.put(data)
                    _LOGGER.debug("Command enqueued (no reply): %s", bin2hex(data))
                    continue  # Process next message

                # Logic for sending a command and waiting for a specific reply
                future = asyncio.Future()
                self._pending_requests[last_packet_number] = future
                await self._tx_queue.put(data)
                _LOGGER.debug("Command enqueued (waiting for reply for packet %d)", last_packet_number)

                try:
                    return await asyncio.wait_for(future, timeout=reply_timeout)
                except asyncio.TimeoutError as e:
                    # The future timed out, so we need to clean it up from the pending requests.
                    # The reader task will not have popped it.
                    self._pending_requests.pop(last_packet_number, None)
                    raise TimeoutError(
                        f"No response received for packet {last_packet_number} within {reply_timeout} seconds."
                    ) from e

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
    ) -> int | bytes | None:
        """Send a message to the device using the client."""
        if not self.is_connected:
            _LOGGER.error("Cannot send message, client is not connected.")
            return
        if isinstance(destination, str):
            destination_address = destination
        elif isinstance(destination, NasaDevice):
            destination_address = destination.address
        else:
            _LOGGER.error("Invalid destination type: %s", type(destination))
            return
        if messages is None:
            raise ValueError("At least one message is required.")
        try:
            return await self.send_command(
                [
                    build_message(
                        source=str(self._config.address),
                        destination=destination_address,
                        data_type=request_type,
                        messages=messages,
                    )
                ],
                wait_for_reply=request_type == DataType.READ or request_type == DataType.WRITE,
            )
        except Exception as e:
            _LOGGER.exception("Error sending message to device %s: %s", destination_address, e)

    async def nasa_read(self, msgs: list[int], destination: NasaDevice | str = "B20020") -> int | bytes | None:
        """Send read requests to a device to read data."""
        messages = [SendMessage(MESSAGE_ID=imn, PAYLOAD=b"") for imn in msgs]
        return await self.send_message(
            destination=destination,
            request_type=DataType.READ,
            messages=messages,
        )

    async def nasa_write(
        self, msg: int, value: str, destination: NasaDevice | str, data_type: DataType
    ) -> int | bytes | None:
        """Send write requests to a device to write data."""
        from .helpers import hex2bin

        message = SendMessage(MESSAGE_ID=msg, PAYLOAD=hex2bin(value))
        return await self.send_message(
            destination=destination,
            request_type=data_type,
            messages=[message],
        )
