"""NASA Packet Parser."""

from typing import Callable

import struct

from ..helpers import bin2hex
from .enum import PacketType, DataType, AddressClass
from .messages import nasa_message_name


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
                desc = nasa_message_name(messageNumber)
            except Exception:
                desc = "UNSPECIFIED"
            ds.append([messageNumber, desc, valuehex, value])
            off += 2 + s

        if seenMsgCnt != dsCnt:
            raise BaseException("Not every message processed")

        if src in self._device_handlers:
            for handler in self._device_handlers[src]:
                handler(
                    source=src,
                    dest=dst,
                    isInfo=isInfo,
                    protocolVersion=protVersion,
                    retryCounter=retryCnt,
                    packetType=packetType,
                    payloadType=payloadType,
                    packetNumber=packetNumber,
                    messageNumber=messageNumber,
                    dataSets=ds,
                )
        elif self._new_device_handler is not None:
            self._new_device_handler(
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
