"""Represent a NASA device and expose attributes."""

import logging

from typing import Any
from datetime import datetime

from ..config import NasaConfig
from ..helpers import bin2hex
from ..protocol.enum import PacketType, DataType, AddressClass
from ..protocol.parser import NasaPacketParser
from ..protocol.factory import parse_message

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

    attributes: dict[str, Any]

    def __init__(
        self, address: str, device_type: AddressClass, packet_parser: NasaPacketParser, config: NasaConfig
    ) -> None:
        self.address = address
        self.device_type = device_type
        self.attributes = {}
        self.config = config
        self.last_packet_time = None
        packet_parser.add_device_handler(address, self.handle_packet)

    def handle_packet(self, *nargs, **kwargs: dict[str, bytes | PacketType | DataType | int]):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now().isoformat()
        _LOGGER.debug("Handing packet for device %s: %s", self.address, kwargs)
        if kwargs["packetType"] != PacketType.NORMAL:
            _LOGGER.error("Ignoring packet type %s", kwargs["packetType"])
            return
        if kwargs["payloadType"] not in [DataType.NOTIFICATION, DataType.WRITE, DataType.RESPONSE]:
            _LOGGER.error("Ignoring payload type %s", kwargs["payloadType"])
            return
        if self.config.device_dump_only:
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
                _LOGGER.warning("Device %s: Skipping malformed data_item (msg: %s): %s", self.address, msg_number, ds)
                continue
            try:
                self.attributes[formatted_msg_number] = parse_message(msg_number, payload_bytes, description).to_dict()
                _LOGGER.debug(
                    "Device %s: Stored parsed attribute for msg %s (%s): %s",
                    self.address,
                    formatted_msg_number,
                    description,
                    self.attributes[formatted_msg_number],
                )
            except ValueError as e:
                # Typically "No parser defined for message number"
                _LOGGER.debug(
                    "Device %s: No specific parser for msg 0x%04x (%s). Error: %s",
                    self.address,
                    msg_number,
                    description,
                    e,
                )
                self.attributes[formatted_msg_number] = bin2hex(payload_bytes)
            except Exception as e:
                _LOGGER.error("Error parsing message %s: %s", msg_number, e)
                _LOGGER.error(
                    "Device %s: Error processing message 0x%04x (%s) with payload %s: %s",
                    self.address,
                    msg_number,
                    description,
                    payload_bytes,
                    e,
                    exc_info=True,
                )
