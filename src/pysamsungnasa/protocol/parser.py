"""NASA Packet Parser."""

from typing import Callable

import struct

from pysamsungnasa.helpers import bin2hex
from .enum import PacketTypes, PayloadTypes
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

    def parse_packet(self, p):
        if len(p) < 3 + 3 + 1 + 1 + 1 + 1:
            return  # too short
        src = p[0:3]
        dst = p[3:6]
        isInfo = (p[6] & 0x80) >> 7
        protVersion = (p[6] & 0x60) >> 5
        retryCnt = (p[6] & 0x18) >> 3
        # rfu = p[6] & 0x7
        packetType = p[7] >> 4
        payloadType = p[7] & 0xF
        packetNumber = p[8]
        dsCnt = p[9]

        packetTypStr = "unknown"
        if packetType < len(PacketTypes):
            packetTypStr = PacketTypes[packetType]

        payloadTypeStr = "unknown"
        if payloadType < len(PayloadTypes):
            payloadTypeStr = PayloadTypes[payloadType]

        ds = []
        off = 10
        seenMsgCnt = 0
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
            valuedec = []
            if s == 1:
                intval = struct.unpack(">b", value)[0]
                valuedec.append(intval)
                if value[0] != 0:
                    valuedec.append("ON")
                else:
                    valuedec.append("OFF")
            elif s == 2:
                intval = struct.unpack(">h", value)[0]
                valuedec.append(intval)
                valuedec.append(intval / 10.0)
            elif s == 4:
                intval = struct.unpack(">i", value)[0]
                valuedec.append(intval)
                valuedec.append(intval / 10.0)
            # log.debug(f"  msgnum: {hex(messageNumber)}")
            # log.debug(f"  content: {value}")
            try:
                desc = nasa_message_name(messageNumber)
            except Exception:
                desc = "UNSPECIFIED"
            ds.append([messageNumber, desc, valuehex, value, valuedec])
            off += 2 + s

        if seenMsgCnt != dsCnt:
            raise BaseException("Not every message processed")

        if dst in self._device_handlers:
            for handler in self._device_handlers[dst]:
                handler(
                    source=src,
                    dest=dst,
                    isInfo=isInfo,
                    protocolVersion=protVersion,
                    retryCounter=retryCnt,
                    packetType=packetTypStr,
                    payloadType=payloadTypeStr,
                    packetNumber=packetNumber,
                    dataSets=ds,
                )
        elif self._new_device_handler is not None:
            self._new_device_handler(
                source=src,
                dest=dst,
                isInfo=isInfo,
                protocolVersion=protVersion,
                retryCounter=retryCnt,
                packetType=packetTypStr,
                payloadType=payloadTypeStr,
                packetNumber=packetNumber,
                dataSets=ds,
            )
