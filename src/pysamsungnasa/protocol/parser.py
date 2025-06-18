"""NASA Packet Parser."""

from typing import Callable

import logging
import struct

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
        _new_device_handler: Callable | None = None,
    ) -> None:
        """Init a NASA Packet Parser."""
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
        if kwargs["packetType"] != PacketType.NORMAL:
            _LOGGER.error("Ignoring packet type %s", kwargs["packetType"])
            return
        if kwargs["payloadType"] not in [DataType.NOTIFICATION, DataType.WRITE, DataType.RESPONSE]:
            _LOGGER.error("Ignoring payload type %s", kwargs["payloadType"])
            return
        for ds in kwargs["dataSets"]:
            if not isinstance(ds, list):
                _LOGGER.warning("Invalid data set: %s", ds)
                continue
            msg_number = ds[0]
            formatted_msg_number = f"0x{msg_number:04x}"
            payload_bytes = None
            description = "UNKNOWN"
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
                _LOGGER.debug(
                    "Parsed message %s (%s): %s",
                    formatted_msg_number,
                    description,
                    parsed_message,
                )
            except Exception as e:
                _LOGGER.error("Failed to parse message %s (%s): %s", formatted_msg_number, description, e)
                continue
            if kwargs["source"] in self._device_handlers:
                for handler in self._device_handlers[kwargs["source"]]:
                    handler(
                        source=kwargs["source"],
                        source_class=kwargs.get("source_class", AddressClass.UNKNOWN),
                        dest=kwargs["dest"],
                        dest_class=kwargs.get("dest_class", AddressClass.UNKNOWN),
                        isInfo=kwargs["isInfo"],
                        protocolVersion=kwargs["protocolVersion"],
                        retryCounter=kwargs["retryCounter"],
                        packetType=kwargs["packetType"],
                        payloadType=kwargs["payloadType"],
                        packetNumber=kwargs["packetNumber"],
                        formattedMessageNumber=f"0x{msg_number:04x}",
                        messageNumber=msg_number,
                        packet=parsed_message,
                    )
            elif self._new_device_handler is not None:
                self._new_device_handler(
                    source=kwargs["source"],
                    source_class=kwargs.get("source_class", AddressClass.UNKNOWN),
                    dest=kwargs["dest"],
                    dest_class=kwargs.get("dest_class", AddressClass.UNKNOWN),
                    isInfo=kwargs["isInfo"],
                    protocolVersion=kwargs["protocolVersion"],
                    retryCounter=kwargs["retryCounter"],
                    packetType=kwargs["packetType"],
                    payloadType=kwargs["payloadType"],
                    packetNumber=kwargs["packetNumber"],
                    formattedMessageNumber=f"0x{msg_number:04x}",
                    messageNumber=msg_number,
                    packet=parsed_message,
                )

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
