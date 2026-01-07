"""Represent a NASA device and expose attributes."""

from __future__ import annotations

import asyncio
import logging

from typing import TYPE_CHECKING, Any, Callable
from datetime import datetime, timezone

from .config import NasaConfig
from .protocol.enum import AddressClass, DataType
from .protocol.parser import NasaPacketParser
from .protocol.factory.types import BaseMessage, SendMessage

if TYPE_CHECKING:
    from .nasa_client import NasaClient

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

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
        self.attributes: dict[int, BaseMessage] = {}
        self.config = config
        self.last_packet_time = None
        self.fsv_config = {}
        self._device_callbacks: list[Callable] = []
        self._packet_callbacks: dict[int, list[Callable]] = {}
        self._client = client
        self._attribute_events: dict[int, asyncio.Event] = {}
        packet_parser.add_device_handler(address, self.handle_packet)

    def add_device_callback(self, callback: Callable):
        """Add a device callback."""
        if callback not in self._device_callbacks:
            self._device_callbacks.append(callback)

    def add_packet_callback(self, message_number: int, callback: Callable):
        """Add a packet callback."""
        if message_number not in self._packet_callbacks:
            self._packet_callbacks[message_number] = []
        if callback not in self._packet_callbacks[message_number]:
            self._packet_callbacks[message_number].append(callback)

    def remove_packet_callback(self, message_number: int, callback: Callable):
        """Remove a packet callback."""
        if message_number in self._packet_callbacks:
            if callback in self._packet_callbacks[message_number]:
                self._packet_callbacks[message_number].remove(callback)

    def remove_device_callback(self, callback: Callable):
        """Remove a device callback."""
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    async def get_attribute(self, attribute: int, requires_read: bool = False) -> BaseMessage:
        """Get a specific attribute from the device, if it is not already known a request will be sent to the device."""
        if attribute not in self.attributes or requires_read:
            await self._client.nasa_read(
                msgs=[attribute],
                destination=self.address,
            )

        event = self._attribute_events.setdefault(attribute, asyncio.Event())

        async with asyncio.timeout(10):
            while attribute not in self.attributes or requires_read:
                event.clear()
                await event.wait()  # Waits until handle_packet sets it
                requires_read = False  # Only require read once

        if attribute not in self.attributes:
            raise TimeoutError(f"Timeout waiting for attribute {attribute} from device {self.address}")

        return self.attributes[attribute]

    async def write_attributes(self, attributes: dict[type[BaseMessage], Any]):
        """Write specific attributes to the device.

        NASA protocol can handle up to 10 messages per packet.

        Args:
            attributes: Dictionary mapping message class to value

        Raises:
            ValueError: If more than 10 messages or message class lacks MESSAGE_ID
        """
        if len(attributes) > 10:
            raise ValueError(f"Cannot write more than 10 messages in one packet, got {len(attributes)}")

        messages = []
        for message_class, value in attributes.items():
            if message_class.MESSAGE_ID is None:
                raise ValueError(f"Message class {message_class} does not have a MESSAGE_ID.")

            messages.append(SendMessage(MESSAGE_ID=message_class.MESSAGE_ID, PAYLOAD=message_class.to_bytes(value)))
        await self._client.send_message(
            destination=self.address,
            request_type=DataType.WRITE,
            messages=messages,
        )

    async def write_attribute(self, message_class: type[BaseMessage], value: Any):
        """Write a single attribute to the device, this is a convenience method of write_attributes."""
        await self.write_attributes({message_class: value})

    def handle_packet(self, *_nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now(timezone.utc)
        message_number = kwargs["messageNumber"]
        packet_data: BaseMessage = kwargs["packet"]
        log_message = (
            str(self.config.address) == kwargs["dest"]
            or self.config.log_all_messages
            or kwargs["dest"] in self.config.devices_to_log
            or message_number in self.config.messages_to_log
        )

        if log_message:
            _LOGGER.debug("Handling packet for device %s: %s", self.address, kwargs)
        self.attributes[message_number] = packet_data
        if message_number in self._attribute_events:
            self._attribute_events[message_number].set()
        if log_message:
            _LOGGER.debug(
                "Device %s: Stored parsed attribute for msg %s (%s): %s",
                self.address,
                kwargs["formattedMessageNumber"],
                message_number,
                self.attributes[message_number],
            )

        # Test if the packet is an FSV configuration packet
        if packet_data.is_fsv_message:
            self.fsv_config[message_number] = packet_data.VALUE

        for callback in self._device_callbacks:
            try:
                callback(self)
            except Exception:
                _LOGGER.exception("Error in device %s callback", self.address)
        if message_number in self._packet_callbacks:
            for callback in self._packet_callbacks[message_number]:
                try:
                    callback(self, **kwargs)
                except Exception:
                    _LOGGER.exception("Error in device %s packet callback", self.address)
