"""Represent a NASA device and expose attributes."""

from __future__ import annotations

import logging

from typing import Any
from datetime import datetime

from ..nasa_client import NasaClient
from ..config import NasaConfig
from ..protocol.factory import build_message, bin2hex
from ..protocol.enum import AddressClass
from ..protocol.parser import NasaPacketParser

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

    attributes: dict[str, Any]

    def __init__(
        self,
        address: str,
        device_type: AddressClass,
        packet_parser: NasaPacketParser,
        config: NasaConfig,
        client: NasaClient,
    ) -> None:
        self.address = address
        self.device_type = device_type
        self.attributes = {}
        self.config = config
        self.last_packet_time = None
        self._device_callbacks = []
        self._client = client
        packet_parser.add_device_handler(address, self.handle_packet)

    def add_device_callback(self, callback):
        """Add a device callback."""
        if callback not in self._device_callbacks:
            self._device_callbacks.append(callback)

    def remove_device_callback(self, callback):
        """Remove a device callback."""
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    def handle_packet(self, *nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now().isoformat()
        _LOGGER.debug("Handing packet for device %s: %s", self.address, kwargs)
        self.attributes[kwargs["formattedMessageNumber"]] = kwargs["packet"]
        _LOGGER.debug(
            "Device %s: Stored parsed attribute for msg %s: %s",
            self.address,
            kwargs["formattedMessageNumber"],
            self.attributes[kwargs["formattedMessageNumber"]],
        )
        for callback in self._device_callbacks:
            try:
                callback(self)
            except Exception as e:
                _LOGGER.error("Error in device %s callback: %s", self.address, e)

    async def send_message(self, message_id: int, payload: bytes, destination: "NasaDevice | str | None" = None):
        """Send a message to the device using the client."""
        if not self._client.is_connected:
            _LOGGER.error("Cannot send message, client is not connected.")
            return
        try:
            if destination is None:
                destination = self.address
            elif isinstance(destination, NasaDevice):
                destination = destination.address
            elif isinstance(destination, str):
                destination = destination
            else:
                _LOGGER.error("Invalid destination type: %s", type(destination))
                return
            await self._client.send_command(
                [
                    build_message(
                        source=self.address,
                        destination=destination,
                        message_number=message_id,
                        payload=payload,
                    )
                ]
            )
            _LOGGER.info("Sent message %s to device %s", bin2hex(payload), self.address)
        except Exception as e:
            _LOGGER.exception("Error sending message to device %s: %s", self.address, e)
