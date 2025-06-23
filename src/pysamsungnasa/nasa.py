"""Represent the NASA protocol."""

import logging
from typing import Any

from .config import NasaConfig
from .device import NasaDevice
from .protocol.enum import DataType
from .protocol.parser import NasaPacketParser
from .nasa_client import NasaClient
from .protocol.factory import build_message, SendMessage

_LOGGER = logging.getLogger(__name__)


class SamsungNasa:
    """Core Samsung NASA protocol."""

    config: NasaConfig
    devices: dict[str, NasaDevice] = {}

    def __init__(self, host: str, port: int, config: dict[str, Any], new_device_event_handler=None, disconnect_event_handler=None) -> None:
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
            if callable(self.new_device_event_handler):
                try:
                    self.new_device_event_handler(self.devices[kwargs["source"]])
                except Exception as e:
                    _LOGGER.exception("Error in new device event handler: %s", e)

    async def start(self):
        """Start the NASA protocol."""
        await self.client.connect()

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
        if not self.client.is_connected:
            _LOGGER.error("Cannot send message, client is not connected.")
            return
        if isinstance(destination, str):
            destination_address = destination
        elif isinstance(destination, NasaDevice):
            destination_address = destination.address
        else:
            _LOGGER.error("Invalid destination type: %s", type(destination))
            return
        if messages is None:
            raise ValueError("At least one message is required.")
        try:
            await self.client.send_command(
                [
                    build_message(
                        source=str(self.config.address),
                        destination=destination_address,
                        data_type=request_type,
                        messages=messages,
                    )
                ],
                wait_for_reply=request_type==DataType.READ or request_type==DataType.WRITE
            )
        except Exception as e:
            _LOGGER.exception("Error sending message to device %s: %s", destination_address, e)
