"""Represent the NASA protocol."""

import logging
from typing import Any, Callable
from asyncio import iscoroutinefunction

from .config import NasaConfig
from .device import NasaDevice, IndoorNasaDevice, OutdoorNasaDevice
from .helpers import Address
from .protocol.enum import DataType, AddressClass
from .protocol.parser import NasaPacketParser
from .nasa_client import NasaClient
from .protocol.factory import SendMessage

_LOGGER = logging.getLogger(__name__)


class SamsungNasa:
    """Core Samsung NASA protocol."""

    config: NasaConfig
    devices: dict[str, NasaDevice] = {}

    def __init__(
        self,
        host: str,
        port: int,
        config: dict[str, Any],
        new_device_event_handler: Callable | None = None,
        disconnect_event_handler: Callable | None = None,
    ) -> None:
        """Initialize the NASA protocol."""
        self.config = NasaConfig(**config)
        self.client = NasaClient(
            host=host,
            port=port,
            config=self.config,
            recv_event_handler=None,
            disconnect_event_handler=disconnect_event_handler,
        )
        self.parser = NasaPacketParser(_new_device_handler=self._new_device_handler, config=self.config)
        self.parser.set_pending_read_handler(self.client._mark_read_received)
        self.client.set_receive_event_handler(self.parser.parse_packet)
        self.new_device_event_handler = new_device_event_handler
        if self.config.device_addresses is not None:
            for address in self.config.device_addresses:
                self._add_device(address)

    def _add_device(self, address: str) -> NasaDevice:
        """Add a device to the devices list."""
        device_type = (Address.parse(address)).class_id
        if device_type == AddressClass.INDOOR:
            new_device = IndoorNasaDevice(
                address=address,
                packet_parser=self.parser,
                config=self.config,
                client=self.client,
            )
        elif device_type == AddressClass.OUTDOOR:
            new_device = OutdoorNasaDevice(
                address=address,
                packet_parser=self.parser,
                config=self.config,
                client=self.client,
            )
        else:
            new_device = NasaDevice(
                address=address,
                device_type=AddressClass(device_type),
                packet_parser=self.parser,
                config=self.config,
                client=self.client,
            )
        self.devices[address] = new_device
        return new_device

    async def _new_device_handler(self, **kwargs):
        """Handle messages from a new device."""
        if kwargs["source"] not in self.devices:
            self.devices[kwargs["source"]] = self._add_device(kwargs["source"])
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
        # if self.client.is_connected:
        # Perform a "poke"
        # await self.client.send_message(
        #     destination="200000",
        #     request_type=DataType.REQUEST,
        #     messages=[SendMessage(0x4242, bytes.fromhex("FFFF"))],
        # )

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
