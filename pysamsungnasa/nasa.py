"""Represent the NASA protocol."""

import logging
from collections.abc import Callable
from typing import Any

from .config import NasaConfig
from .device import NasaDevice
from .helpers import Address, is_coroutine_function
from .nasa_client import NasaClient
from .protocol.enum import AddressClass, DataType
from .protocol.factory import SendMessage
from .protocol.parser import NasaPacketParser

_LOGGER = logging.getLogger(__name__)


class SamsungNasa:
    """Core Samsung NASA protocol."""

    def __init__(
        self,
        config: dict[str, Any],
        new_device_event_handler: Callable | None = None,
        disconnect_event_handler: Callable | None = None,
    ) -> None:
        """Initialize the NASA protocol."""
        self.config = NasaConfig(**config)
        self.devices: dict[str, NasaDevice] = {}
        self.client = NasaClient(
            config=self.config,
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
            # Call the user-defined new device event handler
            if self.new_device_event_handler is None:
                return
            try:
                if is_coroutine_function(self.new_device_event_handler):
                    await self.new_device_event_handler(self.devices[kwargs["source"]])
                else:
                    self.new_device_event_handler(self.devices[kwargs["source"]])
            except Exception:
                _LOGGER.exception("Error in new device event handler")

    async def start(self):
        """Start the NASA protocol."""
        await self.client.connect()

    async def stop(self):
        """Stop the NASA protocol."""
        await self.client.disconnect()

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
