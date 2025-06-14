"""Represent a NASA device and expose attributes."""

import logging

from typing import Any

from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.enum import PacketTypes, PayloadTypes
from pysamsungnasa.protocol.parser import NasaPacketParser

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

    address: str
    device_type: str
    attributes: dict[str, Any]

    def __init__(self, address: str, device_type: str, packet_parser: NasaPacketParser, config: NasaConfig) -> None:
        self.address = address
        self.device_type = device_type
        self.attributes = {}
        self.config = config
        packet_parser.add_device_handler(address, self.handle_packet)

    def handle_packet(self, *nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        if kwargs["packetType"] != PacketTypes.NORMAL:
            _LOGGER.debug("Ignoring packet type %s", kwargs["packetType"])
            return
        if kwargs["payloadType"] not in [PayloadTypes.NOTIFICATION, PayloadTypes.WRITE, PayloadTypes.RESPONSE]:
            _LOGGER.debug("Ignoring payload type %s", kwargs["payloadType"])
            return
        if self.config.device_dump_only:
            return
