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

    attributes: dict[int, Any]

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
        self._packet_callbacks = {}
        self._client = client
        packet_parser.add_device_handler(address, self.handle_packet)

    def add_device_callback(self, callback):
        """Add a device callback."""
        if callback not in self._device_callbacks:
            self._device_callbacks.append(callback)

    def add_packet_callback(self, message_number: int, callback):
        """Add a packet callback."""
        if message_number not in self._packet_callbacks:
            self._packet_callbacks[message_number] = []
        if callback not in self._packet_callbacks[message_number]:
            self._packet_callbacks[message_number].append(callback)

    def remove_packet_callback(self, message_number: int, callback):
        """Remove a packet callback."""
        if message_number in self._packet_callbacks:
            if callback in self._packet_callbacks[message_number]:
                self._packet_callbacks[message_number].remove(callback)

    def remove_device_callback(self, callback):
        """Remove a device callback."""
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    def handle_packet(self, *nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now().isoformat()
        if str(self.config.address) == kwargs["dest"] or self.config.log_all_messages:
            _LOGGER.debug("Handing packet for device %s: %s", self.address, kwargs)
        self.attributes[kwargs["messageNumber"]] = {
            **kwargs["packet"],
            "formatted_message": kwargs["formattedMessageNumber"],
        }
        if str(self.config.address) == kwargs["dest"] or self.config.log_all_messages:
            _LOGGER.debug(
                "Device %s: Stored parsed attribute for msg %s (%s): %s",
                self.address,
                kwargs["formattedMessageNumber"],
                kwargs["messageNumber"],
                self.attributes[kwargs["messageNumber"]],
            )
        for callback in self._device_callbacks:
            try:
                callback(self)
            except Exception as e:
                _LOGGER.error("Error in device %s callback: %s", self.address, e)
        if kwargs["messageNumber"] in self._packet_callbacks:
            for callback in self._packet_callbacks[kwargs["messageNumber"]]:
                try:
                    callback(self, **kwargs)
                except Exception as e:
                    _LOGGER.error("Error in device %s packet callback: %s", self.address, e)
