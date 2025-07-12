"""NASA Packet Parser."""

from typing import Callable

import logging
import struct

from ..config import NasaConfig
from ..helpers import bin2hex
from .enum import PacketType, DataType, AddressClass
from .factory import parse_message, get_nasa_message_name

_LOGGER = logging.getLogger(__name__)


class NasaPacketParser:
    """Represents a NASA Packet Parser."""

    _device_handlers: dict[str, list] = {}
    _new_device_handler: Callable | None = None

    def __init__(
        self,
        config: NasaConfig,
        _new_device_handler: Callable | None = None,
    ) -> None:
        """Init a NASA Packet Parser."""
        self._config = config
        self._new_device_handler = _new_device_handler

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

    def _process_packet(self, *nargs, **kwargs: str | bytes | PacketType | DataType | int | list[list]):
        """Process a packet."""
        source_address = str(kwargs["source"]).upper()
        dest_address = kwargs["dest"]
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
            if payload_type in [DataType.NOTIFICATION, DataType.WRITE, DataType.RESPONSE]:
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
            else:
                _LOGGER.debug(
                    "Ignoring incoming packet with unknown payload type %s from %s.", payload_type, source_address
                )

        if not should_process:
            return  # Packet was filtered out by the above logic

        for ds in kwargs["dataSets"]:
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
                ):
                    _LOGGER.debug(
                        "Parsed message %s (%s): %s",
                        formatted_msg_number,
                        description,
                        parsed_message,
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
            target_handler_address = dest_address if is_outgoing_from_self else source_address

            if target_handler_address in self._device_handlers:
                for handler in self._device_handlers[target_handler_address]:
                    try:
                        handler(**handler_kwargs)
                    except Exception as e:
                        _LOGGER.error("Error in device %s handler: %s", target_handler_address, e)
            elif not is_outgoing_from_self and self._new_device_handler is not None:
                # Only call new device handler for incoming packets from unknown sources
                try:
                    self._new_device_handler(**handler_kwargs)
                except Exception as e:
                    _LOGGER.exception("Error in new device event handler: %s", e)

    def parse_packet(self, p: bytes):
        if len(p) < 3 + 3 + 1 + 1 + 1 + 1:
            return  # too short
        src = bin2hex(p[0:3])
        try:
            src_class = AddressClass(p[0])
        except ValueError:
            src_class = AddressClass.UNKNOWN
        dst = bin2hex(p[3:6])
        try:
            dst_class = AddressClass(p[3])
        except ValueError:
            dst_class = AddressClass.UNKNOWN
        isInfo = (p[6] & 0x80) >> 7
        protVersion = (p[6] & 0x60) >> 5
        retryCnt = (p[6] & 0x18) >> 3
        # rfu = p[6] & 0x7
        try:
            packetType = PacketType(p[7] >> 4)
        except ValueError:
            packetType = PacketType.UNKNOWN
        try:
            payloadType = DataType(p[7] & 0xF)
        except ValueError:
            payloadType = DataType.UNKNOWN
        packetNumber = p[8]
        dsCnt = p[9]

        ds = []
        off = 10
        seenMsgCnt = 0
        messageNumber = None
        for i in range(0, dsCnt):
            seenMsgCnt += 1
            kind = (p[off] & 0x6) >> 1
            if kind == 0:
                s = 1
            elif kind == 1:
                s = 2
            elif kind == 2:
                s = 4
            elif kind == 3:
                if dsCnt != 1:
                    raise BaseException("Invalid encoded packet containing a struct: " + bin2hex(p))
                ds.append([-1, "STRUCTURE", p[off:], bin2hex(p[off:]), p[off:], [p[off:]]])
                break
            messageNumber = struct.unpack(">H", p[off : off + 2])[0]
            value = p[off + 2 : off + 2 + s]
            valuehex = bin2hex(value)
            try:
                desc = get_nasa_message_name(messageNumber)
            except Exception:
                desc = "UNSPECIFIED"
            ds.append([messageNumber, desc, valuehex, value])
            off += 2 + s

        if seenMsgCnt != dsCnt:
            raise BaseException("Not every message processed")

        self._process_packet(
            source=src,
            source_class=src_class,
            dest=dst,
            dest_class=dst_class,
            isInfo=isInfo,
            protocolVersion=protVersion,
            retryCounter=retryCnt,
            packetType=packetType,
            payloadType=payloadType,
            packetNumber=packetNumber,
            dataSets=ds,
        )
