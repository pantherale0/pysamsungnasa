"""NASA Packet Parser."""

from typing import Callable
from asyncio import iscoroutinefunction, Event

import logging
import struct

from ..config import NasaConfig
from ..helpers import bin2hex
from .enum import PacketType, DataType, AddressClass
from .factory import parse_message, get_nasa_message_name

_LOGGER = logging.getLogger(__name__)


class NasaPacketParser:
    """Represents a NASA Packet Parser."""

    def __init__(
        self,
        config: NasaConfig,
        _new_device_handler: Callable | None = None,
    ) -> None:
        """Init a NASA Packet Parser."""
        self._config = config
        self._device_handlers: dict[str, list] = {}
        self._packet_listeners: dict[int, list] = {}
        self._new_device_handler = _new_device_handler
        self._pending_read_handler: Callable | None = None  # Callback for handling received read responses
        self._packet_event = Event()
        self._latest_packet_data: bytes | None = None

    async def get_raw_packet_stream(self):
        """A generator that yields raw packet bytes as they arrive."""
        while True:
            await self._packet_event.wait()
            self._packet_event.clear()
            if self._latest_packet_data is not None:
                yield self._latest_packet_data

    def set_pending_read_handler(self, handler: Callable | None) -> None:
        """Set the pending read handler callback."""
        self._pending_read_handler = handler

    def add_device_handler(self, address: str, callback):
        """Add the device handler."""
        self._device_handlers.setdefault(address, [])
        if callback not in self._device_handlers[address]:
            self._device_handlers[address].append(callback)

    def remove_device_handler(self, address: str, callback):
        """Remove a device handler."""
        self._device_handlers.setdefault(address, [])
        if callback in self._device_handlers[address]:
            self._device_handlers[address].remove(callback)

    def add_packet_listener(self, message_number: int, callback):
        """Add a packet listener."""
        self._packet_listeners.setdefault(message_number, [])
        if callback not in self._packet_listeners[message_number]:
            self._packet_listeners[message_number].append(callback)

    def remove_packet_listener(self, message_number: int, callback):
        """Remove a packet listener."""
        self._packet_listeners.setdefault(message_number, [])
        if callback in self._packet_listeners[message_number]:
            self._packet_listeners[message_number].remove(callback)

    async def _process_packet(self, *nargs, **kwargs: str | bytes | PacketType | DataType | int | list[list]):
        """Process a packet."""
        source_address = str(kwargs["source"]).upper()
        dest_address = str(kwargs["dest"])
        payload_type = kwargs["payloadType"]
        packet_type = kwargs["packetType"]
        client_address = str(self._config.address)

        if kwargs["packetType"] != PacketType.NORMAL:
            _LOGGER.error("Ignoring packet due to non-NORMAL packet type: %s", packet_type)
            return

        # Determine if the packet is an outgoing message from this client
        is_outgoing_from_self = source_address == client_address

        # Filter based on payload type and source/destination
        should_process = False
        if is_outgoing_from_self:
            # For outgoing messages, we process REQUESTs and WRITEs
            if payload_type in [DataType.REQUEST, DataType.WRITE]:
                should_process = True
                _LOGGER.debug(
                    "Processing outgoing packet (type=%s, payload=%s) from self to %s.",
                    packet_type,
                    payload_type,
                    dest_address,
                )
            else:
                _LOGGER.debug("Ignoring outgoing packet with payload type %s from self.", payload_type)
        else:
            # For incoming messages, we process NOTIFICATIONs, WRITEs, and RESPONSEs
            if payload_type in [DataType.NOTIFICATION, DataType.WRITE, DataType.RESPONSE, DataType.ACK]:
                should_process = True
                _LOGGER.debug(
                    "Processing incoming packet (type=%s, payload=%s) from %s.",
                    packet_type,
                    payload_type,
                    source_address,
                )
            elif payload_type == DataType.REQUEST:
                # Incoming REQUESTs are currently ignored as per original logic's implicit filter
                _LOGGER.debug("Ignoring incoming packet with payload type REQUEST from %s.", source_address)
            elif payload_type == DataType.NACK:
                # Incoming NACKs are generally errors from devices about writes
                # They should notify pending_read_handler but not be processed as normal packets
                _LOGGER.warning(
                    "Received NACK from %s for packet number %s.",
                    source_address,
                    kwargs["packetNumber"],
                )
                # Notify pending read handler about the NACK
                if self._pending_read_handler:
                    message_numbers = []
                    for ds in kwargs.get("dataSets", []):  # type: ignore
                        if isinstance(ds, list) and len(ds) > 0:
                            message_numbers.append(ds[0])
                    try:
                        result = self._pending_read_handler(source_address, message_numbers)
                        if iscoroutinefunction(self._pending_read_handler):
                            await result
                    except Exception as e:
                        _LOGGER.error("Error in pending_read_handler: %s", e)
                # Return early - NACKs don't have valid dataSets to process
                return
            else:
                _LOGGER.debug(
                    "Ignoring incoming packet with unknown payload type %s from %s.", payload_type, source_address
                )

        if not should_process:
            return  # Packet was filtered out by the above logic

        # Notify pending read handler when we receive a response or acknowledgment
        # ACK packets can also indicate that a read/write request was processed
        # Note: NACK is handled separately above to avoid processing invalid dataSets
        if (
            not is_outgoing_from_self
            and payload_type in [DataType.RESPONSE, DataType.ACK]
            and self._pending_read_handler
        ):
            # For both RESPONSE and ACK packets, extract message numbers from the datasets
            message_numbers = []
            for ds in kwargs.get("dataSets", []):  # type: ignore
                if isinstance(ds, list) and len(ds) > 0:
                    message_numbers.append(ds[0])

            # Call handler with the extracted message numbers
            # Empty message_numbers is valid for ACK packets that acknowledge without specific message IDs
            try:
                result = self._pending_read_handler(source_address, message_numbers)
                # Handle async callbacks
                if iscoroutinefunction(self._pending_read_handler):
                    await result
            except Exception as e:
                _LOGGER.error("Error in pending_read_handler: %s", e)

        for ds in kwargs["dataSets"]:  # type: ignore
            if not isinstance(ds, list):
                _LOGGER.warning("Invalid data set: %s", ds)
                continue
            msg_number = ds[0]
            formatted_msg_number = f"0x{msg_number:04x}"
            if msg_number == -1 and len(ds) >= 3 and ds[1] == "STRUCTURE":
                # Structure message: index 2 contains the raw bytes of the structure
                payload_bytes = ds[2]
                description = ds[1]
            elif len(ds) >= 4:
                # Normal message: index 3 contains the value_bytes
                payload_bytes = ds[3]
                description = ds[1]
            else:
                _LOGGER.warning("Invalid data set: %s", ds)
                continue

            try:
                parsed_message = parse_message(ds[0], payload_bytes, description)
                if (
                    str(self._config.address) == kwargs["dest"]
                    or self._config.log_all_messages
                    or kwargs["dest"] in self._config.devices_to_log
                    or ds[0] in self._config.messages_to_log
                ):
                    _LOGGER.debug(
                        "Parsed message %s (%s): %s",
                        formatted_msg_number,
                        description,
                        {**parsed_message.as_dict, "raw_payload": payload_bytes.hex()},
                    )
            except Exception as e:
                _LOGGER.error("Failed to parse message %s (%s): %s", formatted_msg_number, description, e)
                continue

            # Prepare arguments for handlers
            handler_kwargs = {
                "source": source_address,
                "source_class": kwargs.get("source_class", AddressClass.UNKNOWN),
                "dest": dest_address,
                "dest_class": kwargs.get("dest_class", AddressClass.UNKNOWN),
                "isInfo": kwargs["isInfo"],
                "protocolVersion": kwargs["protocolVersion"],
                "retryCounter": kwargs["retryCounter"],
                "packetType": packet_type,
                "payloadType": payload_type,
                "packetNumber": kwargs["packetNumber"],
                "formattedMessageNumber": formatted_msg_number,
                "messageNumber": msg_number,
                "packet": parsed_message,
            }

            # Dispatch to the appropriate device handler(s)
            target_handler_address: str = dest_address if is_outgoing_from_self else source_address

            if target_handler_address in self._device_handlers:
                for handler in self._device_handlers[target_handler_address]:
                    try:
                        handler(**handler_kwargs)
                    except Exception as e:
                        _LOGGER.error("Error in device %s handler: %s", target_handler_address, e)
            elif not is_outgoing_from_self and self._new_device_handler is not None:
                # Only call new device handler for incoming packets from unknown sources
                try:
                    if callable(self._new_device_handler) and not iscoroutinefunction(self._new_device_handler):
                        self._new_device_handler(**handler_kwargs)
                    elif callable(self._new_device_handler) and iscoroutinefunction(self._new_device_handler):
                        await self._new_device_handler(**handler_kwargs)
                except Exception as e:
                    _LOGGER.exception("Error in new device event handler: %s", e)

            # some devices can mirror the state of another device (indoor units for current action)
            # broadcast this via the packet handlers
            if msg_number in self._packet_listeners:
                for listener in self._packet_listeners[msg_number]:
                    listener(**handler_kwargs)

    async def parse_packet(self, packet_data: bytes):
        """Parse a NASA packet and process its contents."""
        self._latest_packet_data = packet_data
        self._packet_event.set()

        if len(packet_data) < 3 + 3 + 1 + 1 + 1 + 1:
            return  # too short
        source_address = bin2hex(packet_data[0:3])
        try:
            source_class = AddressClass(packet_data[0])
        except ValueError:
            source_class = AddressClass.UNKNOWN
        destination_address = bin2hex(packet_data[3:6])
        try:
            destination_class = AddressClass(packet_data[3])
        except ValueError:
            destination_class = AddressClass.UNKNOWN
        is_info = (packet_data[6] & 0x80) >> 7
        protocol_version = (packet_data[6] & 0x60) >> 5
        retry_count = (packet_data[6] & 0x18) >> 3
        # rfu = packet_data[6] & 0x7
        try:
            packet_type = PacketType(packet_data[7] >> 4)
        except ValueError:
            packet_type = PacketType.UNKNOWN
        try:
            payload_type = DataType(packet_data[7] & 0xF)
        except ValueError:
            payload_type = DataType.UNKNOWN
        packet_number = packet_data[8]
        dataset_count = packet_data[9]

        datasets = []
        offset = 10
        seen_message_count = 0
        message_number = None
        for i in range(0, dataset_count):
            seen_message_count += 1
            message_type_kind = (packet_data[offset] & 0x6) >> 1
            if message_type_kind == 0:
                payload_size = 1
            elif message_type_kind == 1:
                payload_size = 2
            elif message_type_kind == 2:
                payload_size = 4
            elif message_type_kind == 3:
                if dataset_count != 1:
                    raise BaseException("Invalid encoded packet containing a struct: " + bin2hex(packet_data))
                # Parse structure as TLV-encoded sub-messages
                struct_payload = packet_data[offset:]
                struct_offset = 0
                while struct_offset < len(struct_payload):
                    if struct_offset + 1 >= len(struct_payload):
                        break
                    # First byte is length
                    message_length = struct_payload[struct_offset]
                    struct_offset += 1

                    if struct_offset + 2 > len(struct_payload):
                        break
                    # Next two bytes are message ID
                    try:
                        message_number = struct.unpack(">H", struct_payload[struct_offset : struct_offset + 2])[0]
                    except struct.error:
                        break
                    struct_offset += 2

                    # Remaining bytes are the value
                    if message_length >= 2:
                        value_length = message_length - 2
                        if struct_offset + value_length > len(struct_payload):
                            value = struct_payload[struct_offset:]
                            struct_offset = len(struct_payload)
                        else:
                            value = struct_payload[struct_offset : struct_offset + value_length]
                            struct_offset += value_length
                    else:
                        value = b""

                    value_hex = bin2hex(value)
                    try:
                        message_description = get_nasa_message_name(message_number)
                    except Exception:
                        message_description = "UNSPECIFIED"
                    datasets.append([message_number, message_description, value_hex, value])
                continue
            else:
                raise BaseException("Invalid message type kind value")
            message_number = struct.unpack(">H", packet_data[offset : offset + 2])[0]
            value = packet_data[offset + 2 : offset + 2 + payload_size]
            value_hex = bin2hex(value)
            try:
                message_description = get_nasa_message_name(message_number)
            except Exception:
                message_description = "UNSPECIFIED"
            datasets.append([message_number, message_description, value_hex, value])
            offset += 2 + payload_size

        if seen_message_count != dataset_count:
            raise BaseException("Not every message processed")

        await self._process_packet(
            source=source_address,
            source_class=source_class,
            dest=destination_address,
            dest_class=destination_class,
            isInfo=is_info,
            protocolVersion=protocol_version,
            retryCounter=retry_count,
            packetType=packet_type,
            payloadType=payload_type,
            packetNumber=packet_number,
            dataSets=datasets,
        )
