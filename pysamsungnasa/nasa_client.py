"""TCP Modbus client."""

import binascii
import logging
import asyncio
import struct

from asyncio import iscoroutinefunction

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
    _retry_manager_task: asyncio.Task | None = None
    _tx_queue: asyncio.Queue[bytes] | None = None
    _rx_queue: asyncio.Queue[bytes] | None = None
    _rx_buffer = b""
    _last_rx_time: float = 0.0
    _packet_number_counter: int = 0
    _pending_reads: dict = {}  # Track pending read requests for retry logic
    _queued_reads: dict = {}  # Queue of read requests per destination waiting to be sent
    _pending_writes: dict = {}  # Track pending write requests for retry logic

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

    def set_receive_event_handler(self, handler) -> None:
        """Set the receive event handler."""
        self._rx_event_handler = handler

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
        await self._end_retry_manager_session()

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
        await self._start_retry_manager_session()

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

                if packet_len_val > self._config.max_buffer_size:
                    _LOGGER.debug(
                        "Parsed packet length %d exceeds max size %d. Assuming parse error.",
                        packet_len_val,
                        self._config.max_buffer_size,
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

    async def _start_retry_manager_session(self) -> bool:
        """Start retry manager task."""
        if self._retry_manager_task and not self._retry_manager_task.done():
            _LOGGER.error("Retry manager task already running.")
            return True
        if not self._config.enable_read_retries:
            _LOGGER.debug("Read retries are disabled in config.")
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
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    _LOGGER.debug("Retry manager task successfully cancelled.")
                except Exception as e:
                    _LOGGER.debug(
                        "Exception during retry manager task cancellation/cleanup: %s",
                        e,
                    )
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
                        packet_data = packet[3:-3]
                        packet_crc = binascii.crc_hqx(packet_data, 0)

                        if packet_crc != packet_crc_from_msg:
                            _LOGGER.error(
                                "QueueProcessor: Invalid CRC expected %s got %s",
                                hex(packet_crc),
                                hex(packet_crc_from_msg),
                            )
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
            )
        except Exception as e:
            _LOGGER.exception("Error sending message to device %s: %s", destination_address, e)

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

        packet_number = await self.send_message(
            destination=destination,
            request_type=DataType.READ,
            messages=[SendMessage(MESSAGE_ID=imn, PAYLOAD=b"\x05\xa5\xa5\xa5") for imn in msgs],
        )

        # Track this read request for retry logic if enabled
        if self._config.enable_read_retries and packet_number is not None:
            # Use message IDs as the key for matching responses
            read_key = f"{dest_addr}_{tuple(sorted(msgs))}"
            current_time = asyncio.get_event_loop().time()
            self._pending_reads[read_key] = {
                "destination": dest_addr,
                "messages": msgs,
                "packet_number": packet_number,
                "attempts": 0,
                "last_attempt_time": current_time,
                "next_retry_time": current_time + self._config.read_retry_interval,
                "retry_interval": self._config.read_retry_interval,
            }
            _LOGGER.debug(
                "Tracking read request for messages %s to %s for retry (max %d attempts)",
                msgs,
                dest_addr,
                self._config.read_retry_max_attempts,
            )

        return packet_number

    async def nasa_write(
        self, msg: int, value: str, destination: NasaDevice | str, data_type: DataType
    ) -> int | bytes | None:
        """Send write requests to a device to write data."""
        dest_addr = destination if isinstance(destination, str) else destination.address
        message = SendMessage(MESSAGE_ID=msg, PAYLOAD=hex2bin(value))
        
        packet_number = await self.send_message(
            destination=destination,
            request_type=data_type,
            messages=[message],
        )
        
        # Track this write request for retry logic if enabled
        if self._config.enable_write_retries and packet_number is not None:
            # Use message ID and destination as the key for matching ACKs
            write_key = f"{dest_addr}_{msg}"
            current_time = asyncio.get_event_loop().time()
            self._pending_writes[write_key] = {
                "destination": dest_addr,
                "message_id": msg,
                "value": value,
                "data_type": data_type,
                "packet_number": packet_number,
                "attempts": 0,
                "last_attempt_time": current_time,
                "next_retry_time": current_time + self._config.write_retry_interval,
                "retry_interval": self._config.write_retry_interval,
            }
            _LOGGER.debug(
                "Tracking write request for message %s to %s for retry (max %d attempts)",
                msg,
                dest_addr,
                self._config.write_retry_max_attempts,
            )
        
        return packet_number

    def _clear_pending_write(self, destination: str, message_numbers: list[int]) -> list[str]:
        """Clear pending write requests for a destination when an ACK is received.
        
        Args:
            destination: The destination address
            message_numbers: List of message IDs in the ACK packet. If empty, clears all pending writes for the destination.
        
        Returns the list of write keys that were cleared.
        """
        cleared_keys = []
        keys_to_delete = []
        
        for write_key, write_info in self._pending_writes.items():
            if write_info["destination"] == destination:
                # If message_numbers is provided and not empty, only clear writes for those specific messages
                # If message_numbers is empty, clear all pending writes for this destination (ACK without specific message IDs)
                if message_numbers and write_info["message_id"] not in message_numbers:
                    continue
                keys_to_delete.append(write_key)
                cleared_keys.append(write_key)
        
        for key in keys_to_delete:
            del self._pending_writes[key]
            _LOGGER.debug("Cleared pending write request for key %s", key)
        
        return cleared_keys

    async def _mark_write_received(self, destination: str, message_numbers: list[int]) -> None:
        """Mark write requests as received when an ACK is received (event callback from parser).
        
        Args:
            destination: The destination address
            message_numbers: List of message IDs in the ACK packet
        """
        cleared = self._clear_pending_write(destination, message_numbers)
        if cleared:
            _LOGGER.debug(
                "Write ACK received from %s for messages %s, cleared %d pending write(s)",
                destination,
                message_numbers if message_numbers else "all",
                len(cleared)
            )

    def _clear_pending_read(self, destination: str, message_numbers: list[int]) -> bool:
        """Clear a pending read request when a response is received with matching message numbers."""
        # Create a key from the sorted message numbers, same as when we track the request
        read_key = f"{destination}_{tuple(sorted(message_numbers))}"
        if read_key in self._pending_reads:
            del self._pending_reads[read_key]
            _LOGGER.debug("Cleared pending read request for messages %s from %s", message_numbers, destination)
            return True
        return False

    async def _mark_read_received(self, destination: str, message_numbers: list[int]) -> None:
        """Mark a read/write request as received (event callback from parser).
        
        Args:
            destination: The destination address
            message_numbers: List of message IDs from the packet (could be from RESPONSE or ACK packets)
        """
        # Handle pending writes - ACK packets may contain specific message IDs or be empty
        # If empty, it clears all pending writes for the destination
        await self._mark_write_received(destination, message_numbers)
        
        # Handle pending reads - only for RESPONSE packets with specific message numbers
        if message_numbers:
            if self._clear_pending_read(destination, message_numbers):
                _LOGGER.debug("Read response received for messages %s from %s", message_numbers, destination)
        
        # Process any queued reads for this destination
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

                current_time = asyncio.get_event_loop().time()
                
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

                    # Identify writes that need to be retried
                    for write_key, write_info in list(self._pending_writes.items()):
                        if current_time >= write_info["next_retry_time"]:
                            if write_info["attempts"] < self._config.write_retry_max_attempts:
                                writes_to_retry.append((write_key, write_info))
                            else:
                                # Max retries exceeded
                                _LOGGER.warning(
                                    "Abandoning write request %s (message %s) to %s after %d attempts",
                                    write_info["packet_number"],
                                    write_info["message_id"],
                                    write_info["destination"],
                                    write_info["attempts"],
                                )
                                writes_to_remove.append(write_key)

                    # Remove writes that have exceeded max attempts
                    for write_key in writes_to_remove:
                        del self._pending_writes[write_key]

                    # Retry the writes
                    for write_key, write_info in writes_to_retry:
                        write_info["attempts"] += 1
                        write_info["last_attempt_time"] = current_time
                        write_info["retry_interval"] *= self._config.write_retry_backoff_factor
                        write_info["next_retry_time"] = current_time + write_info["retry_interval"]

                        _LOGGER.debug(
                            "Retrying write request (message %s) to %s (attempt %d/%d, interval=%.1fs)",
                            write_info["message_id"],
                            write_info["destination"],
                            write_info["attempts"],
                            self._config.write_retry_max_attempts,
                            write_info["retry_interval"],
                        )

                        # Resend the write request
                        try:
                            message = SendMessage(
                                MESSAGE_ID=write_info["message_id"],
                                PAYLOAD=hex2bin(write_info["value"])
                            )
                            await self.send_message(
                                destination=write_info["destination"],
                                request_type=write_info["data_type"],
                                messages=[message],
                            )
                        except Exception as e:
                            _LOGGER.error("Error retrying write request: %s", e)

            except asyncio.CancelledError:
                _LOGGER.info("Retry manager task was cancelled.")
                break
            except Exception as e:
                _LOGGER.exception("Error in retry manager: %s", e)

        _LOGGER.debug("Retry manager task finished.")
