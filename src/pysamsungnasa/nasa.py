"""Represent the NASA protocol."""

import logging
from typing import Any

from .config import NasaConfig
from .device import NasaDevice
from .protocol.parser import NasaPacketParser
from .nasa_client import NasaClient

_LOGGER = logging.getLogger(__name__)


class SamsungNasa:
    """Core Samsung NASA protocol."""

    config: NasaConfig
    devices: dict[str, NasaDevice] = {}

    def __init__(self, host: str, port: int, config: dict[str, Any], disconnect_event_handler=None) -> None:
        """Initialize the NASA protocol."""
        self.config = NasaConfig(**config)
        self.parser = NasaPacketParser(_new_device_handler=self._new_device_handler)
        self.client = NasaClient(
            host=host,
            port=port,
            config=self.config,
            recv_event_handler=self.parser.parse_packet,
            disconnect_event_handler=disconnect_event_handler,
        )
        if self.config.device_addresses is not None:
            for address, device_type in self.config.device_addresses:
                self.devices[address] = NasaDevice(
                    address=address,
                    device_type=device_type,
                    packet_parser=self.parser,
                    config=self.config,
                    client=self.client,
                )

    def _new_device_handler(self, **kwargs):
        """Handle messages from a new device."""
        if kwargs["source"] not in self.devices:
            self.devices[kwargs["source"]] = NasaDevice(
                address=kwargs["source"],
                device_type=kwargs["source_class"],
                packet_parser=self.parser,
                config=self.config,
                client=self.client,
            )
            _LOGGER.info("New %s device discovered: %s", kwargs["source_class"], kwargs["source"])

    async def start(self):
        """Start the NASA protocol."""
        await self.client.connect()

    async def stop(self):
        """Stop the NASA protocol."""
        await self.client.disconnect()
