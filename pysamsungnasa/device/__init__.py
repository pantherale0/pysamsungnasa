"""Represent a NASA device and expose attributes."""

from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING
from datetime import datetime

from .controllers import DhwController, ClimateController
from ..config import NasaConfig
from ..protocol.enum import DataType, AddressClass, InFsv3011EnableDhw
from ..protocol.parser import NasaPacketParser
from ..protocol.factory.messaging import SendMessage

if TYPE_CHECKING:
    from ..nasa_client import NasaClient

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

    _MESSAGES_TO_LISTEN = [
        0x8001,
        0x8003,  # Reflect NASA outdoor status.
    ]

    _DHW_MESSAGE_MAP = {
        0x4065: "power",
        0x4066: "operation_mode",
        0x4097: "dhw_enable_status",
        0x406F: "reference_temp_source",
        0x4235: "target_temperature",
        0x4237: "current_temperature",
        0x8001: "outdoor_operation_status",
        0x8003: "outdoor_operation_mode",
    }

    _CLIMATE_MESSAGE_MAP = {
        0x4000: "power",
        0x4001: "current_mode",
        0x4203: "current_temperature",
        0x4201: "target_temperature",
        0x4038: "current_humidity",
        0x4069: "zone_1_status",
        0x406A: "zone_2_status",
        0x4006: "current_fan_mode",
        0x4008: "current_fan_speed",
        0x4238: "water_outlet_current_temperature",
        0x4248: "water_law_target_temperature",
        0x4247: "water_outlet_target_temperature",
        0x8001: "outdoor_operation_status",
        0x8003: "outdoor_operation_mode",
    }

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
        self._dhw_controller = (
            None
            if device_type != AddressClass.INDOOR
            else DhwController(address=address, message_sender=client.send_message)
        )
        self._climate_controller = (
            None
            if device_type != AddressClass.INDOOR
            else ClimateController(address=address, message_sender=client.send_message)
        )
        packet_parser.add_device_handler(address, self.handle_packet)
        for message_number in self._MESSAGES_TO_LISTEN:
            packet_parser.add_packet_listener(message_number, self.handle_packet)

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

    async def read_configuration(self):
        """Read the configuration of the device."""
        if self.device_type != AddressClass.INDOOR:
            return  # Nothing to do
        messages = []
        # Request DHW configuration
        messages.append(SendMessage(MESSAGE_ID=0x4097, PAYLOAD=b""))
        await self._client.send_message(
            destination=self.address,
            request_type=DataType.READ,
            messages=messages,
        )

    @property
    def dhw_controller(self) -> DhwController | None:
        """Return the DHW state."""
        if self.device_type != AddressClass.INDOOR:
            return None
        return self._dhw_controller

    @property
    def climate_controller(self) -> ClimateController | None:
        """Return the climate state."""
        if self.device_type != AddressClass.INDOOR:
            return None
        return self._climate_controller

    def handle_packet(self, *nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now().isoformat()
        message_number = kwargs["messageNumber"]
        packet_data = kwargs["packet"]
        log_message = (
            str(self.config.address) == kwargs["dest"]
            or self.config.log_all_messages
            or kwargs["dest"] in self.config.devices_to_log
        )

        if log_message:
            _LOGGER.debug("Handing packet for device %s: %s", self.address, kwargs)
        self.attributes[message_number] = {
            **packet_data,
            "formatted_message": kwargs["formattedMessageNumber"],
        }
        if log_message:
            _LOGGER.debug(
                "Device %s: Stored parsed attribute for msg %s (%s): %s",
                self.address,
                kwargs["formattedMessageNumber"],
                message_number,
                self.attributes[message_number],
            )

        value = packet_data.get("value")

        if message_number == 0x4097:  # DHW ENABLE
            if value != InFsv3011EnableDhw.NO:
                self._dhw_controller = DhwController(
                    address=self.address,
                    message_sender=self._client.send_message,
                )

        # Update DHW controller if it exists and the message is relevant
        if self._dhw_controller and message_number in self._DHW_MESSAGE_MAP:
            attr_name = self._DHW_MESSAGE_MAP[message_number]
            setattr(self._dhw_controller, attr_name, value)

        # Update Climate controller if it exists and the message is relevant
        if self._climate_controller and message_number in self._CLIMATE_MESSAGE_MAP:
            attr_name = self._CLIMATE_MESSAGE_MAP[message_number]
            setattr(self._climate_controller, attr_name, value)

        for callback in self._device_callbacks:
            try:
                callback(self)
            except Exception as e:
                _LOGGER.error("Error in device %s callback: %s", self.address, e)
        if message_number in self._packet_callbacks:
            for callback in self._packet_callbacks[message_number]:
                try:
                    callback(self, **kwargs)
                except Exception as e:
                    _LOGGER.error("Error in device %s packet callback: %s", self.address, e)
