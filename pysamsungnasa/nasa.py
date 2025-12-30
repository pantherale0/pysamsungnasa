"""Represent the NASA protocol."""

import logging
from typing import Any, Callable
from asyncio import iscoroutinefunction

from .config import NasaConfig
from .device import NasaDevice
from .helpers import Address
from .protocol.enum import DataType, AddressClass
from .protocol.parser import NasaPacketParser
from .nasa_client import NasaClient
from .protocol.factory import build_message, SendMessage

_LOGGER = logging.getLogger(__name__)


class SamsungNasa:
    """Core Samsung NASA protocol."""

    config: NasaConfig
    devices: dict[str, NasaDevice] = {}

    def __init__(
        self, host: str, port: int, config: dict[str, Any], new_device_event_handler: Callable | None=None, disconnect_event_handler: Callable | None=None
    ) -> None:
        """Initialize the NASA protocol."""
        self.config = NasaConfig(**config)
        self.parser = NasaPacketParser(_new_device_handler=self._new_device_handler, config=self.config)
        self.client = NasaClient(
            host=host,
            port=port,
            config=self.config,
            recv_event_handler=self.parser.parse_packet,
            disconnect_event_handler=disconnect_event_handler,
        )
        self.new_device_event_handler = new_device_event_handler
        if self.config.device_addresses is not None:
            for address in self.config.device_addresses:
                address = Address.parse(address)
                self.devices[str(address)] = NasaDevice(
                    address=str(address),
                    device_type=AddressClass(address.class_id),
                    packet_parser=self.parser,
                    config=self.config,
                    client=self.client,
                )

    async def _new_device_handler(self, **kwargs):
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
            # Request device configuration
            await self.devices[kwargs["source"]].get_configuration()
            # Call the user-defined new device event handler
            if callable(self.new_device_event_handler):
                try:
                    if iscoroutinefunction(self.new_device_event_handler):
                        await self.new_device_event_handler(self.devices[kwargs["source"]])
                    else:
                        self.new_device_event_handler(self.devices[kwargs["source"]])
                except Exception as e:
                    _LOGGER.exception("Error in new device event handler: %s", e)

    async def start(self):
        """Start the NASA protocol."""
        await self.client.connect()
        if self.client.is_connected:
            # Perform a "poke"
            await self.client.send_message(
                destination="200000",
                request_type=DataType.REQUEST,
                messages=[SendMessage(0x4242, bytes.fromhex("FFFF"))],
            )

    async def stop(self):
        """Stop the NASA protocol."""
        await self.client.disconnect()

    async def start_autodiscovery(self):
        """Start NASA autodiscovery."""

    async def send_message(
        self,
        destination: NasaDevice | str,
        request_type: DataType = DataType.REQUEST,
        messages: list[SendMessage] | None = None,
    ) -> None:
        """Send a message to the device using the client."""
        await self.client.send_message(
            destination=destination,
            request_type=request_type,
            messages=messages,
        )
