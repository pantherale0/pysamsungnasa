"""Represent a NASA device and expose attributes."""

from __future__ import annotations

import asyncio
import logging

from typing import TYPE_CHECKING
from datetime import datetime, timezone

from .controllers import DhwController, ClimateController, WaterLawMode
from ..config import NasaConfig
from ..protocol.enum import AddressClass, OutOutdoorCoolonlyModel, InUseThermostat
from ..protocol.parser import NasaPacketParser
from ..protocol.factory.messaging import BaseMessage

if TYPE_CHECKING:
    from ..nasa_client import NasaClient

_LOGGER = logging.getLogger(__name__)


class NasaDevice:
    """NASA Device."""

    _MESSAGES_TO_LISTEN: list[int] = []

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
        self._device_callbacks = []
        self._packet_callbacks = {}
        self._client = client
        self._attribute_events: dict[int, asyncio.Event] = {}
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

    async def get_configuration(self):
        """Get the configuration (FSVs) of the device."""
        if self.device_type != AddressClass.INDOOR:
            return  # Nothing to do
        _LOGGER.debug("Requesting FSV configuration for device %s", self.address)
        # Batch reads in groups of 10
        attributes_set = set(self.attributes)
        for i in range(0, len(self._MESSAGES_TO_LISTEN), 10):
            missing_msgs = [k for k in self._MESSAGES_TO_LISTEN[i : i + 10] if k not in attributes_set]
            if missing_msgs:
                await self._client.nasa_read(
                    msgs=missing_msgs,
                    destination=self.address,
                )

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
            except Exception as e:
                _LOGGER.error("Error in device %s callback: %s", self.address, e)
        if message_number in self._packet_callbacks:
            for callback in self._packet_callbacks[message_number]:
                try:
                    callback(self, **kwargs)
                except Exception as e:
                    _LOGGER.error("Error in device %s packet callback: %s", self.address, e)


class IndoorNasaDevice(NasaDevice):
    """NASA Indoor Device."""

    _MESSAGES_TO_LISTEN = [0x8001, 0x8003, 0x8061, 0x809D]  # Reflect NASA outdoor status.

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
        0x8061: "outdoor_defrost_status",
        # Water law mode configuration messages
        0x4093: "heating_water_law_type",  # FSV 2041 Water Law Type Heating
        0x4094: "cooling_water_law_type",  # FSV 2081 Water Law Type Cooling
        0x4095: "use_external_thermostat_1",  # FSV 2091 Use Thermostat 1
        0x4096: "use_external_thermostat_2",  # FSV 2092 Use Thermostat 2
    }

    def __init__(
        self,
        address: str,
        packet_parser: NasaPacketParser,
        config: NasaConfig,
        client: NasaClient,
    ) -> None:
        self._dhw_controller = DhwController(address=address, message_sender=client.send_message)
        self._climate_controller = ClimateController(address=address, message_sender=client.send_message)
        # Set default water law mode (will be updated when config messages arrive)
        self._climate_controller.water_law_mode = WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT
        super().__init__(address, AddressClass.INDOOR, packet_parser, config, client)

    @property
    def dhw_controller(self) -> DhwController | None:
        """Return the DHW state."""
        if self.device_type != AddressClass.INDOOR:
            return None
        if self._dhw_controller is None:
            return None
        # If we've received the cool-only model indicator and it's a cool-only model
        # with no current temperature, don't expose the DHW controller
        if 0x809D in self.attributes:
            if (
                self.attributes[0x809D].VALUE == OutOutdoorCoolonlyModel.NO_HEAT_PUMP
                and self._dhw_controller.current_temperature is None
            ):
                return None
        # Otherwise, expose the DHW controller
        return self._dhw_controller

    @property
    def climate_controller(self) -> ClimateController | None:
        """Return the climate state."""
        if self.device_type != AddressClass.INDOOR:
            return None
        return self._climate_controller

    async def get_configuration(self):
        """Get the configuration (FSVs) of the device."""
        await super().get_configuration()
        for k in self._CLIMATE_MESSAGE_MAP:
            if k not in self.fsv_config:
                await self._client.nasa_read(
                    msgs=[k],
                    destination=self.address,
                )
        for k in self._DHW_MESSAGE_MAP:
            if k not in self.fsv_config:
                await self._client.nasa_read(
                    msgs=[k],
                    destination=self.address,
                )

    def _infer_water_law_mode(self):
        """
        Infer the water law mode based on device configuration packets.

        This method analyzes the use_external_thermostat_1 and use_external_thermostat_2
        settings received from the device to determine which water law mode is active:

        - If any external thermostat is enabled (VALUE_1, VALUE_2, or VALUE_3):
          → WATER_LAW_EXTERNAL_THERMOSTAT
        - Otherwise:
          → WATER_LAW_INTERNAL_THERMOSTAT (default for most systems)

        Note: We infer INTERNAL_THERMOSTAT as the default because:
        1. Most modern systems use internal room temperature feedback
        2. The device will only send external thermostat configs if using external sensors
        3. If no external thermostat is configured, the system must be using internal feedback
        """
        if not self._climate_controller:
            return

        # Check if any external thermostat is enabled (non-zero and not explicitly "NO")
        thermostat_1_enabled = (
            self._climate_controller.use_external_thermostat_1 is not None
            and self._climate_controller.use_external_thermostat_1 != InUseThermostat.NO
        )
        thermostat_2_enabled = (
            self._climate_controller.use_external_thermostat_2 is not None
            and self._climate_controller.use_external_thermostat_2 != InUseThermostat.NO
        )

        if thermostat_1_enabled or thermostat_2_enabled:
            # External thermostat is enabled
            inferred_mode = WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT
            _LOGGER.debug(
                "Device %s: Inferred water law mode EXTERNAL_THERMOSTAT (thermostat_1=%s, thermostat_2=%s)",
                self.address,
                self._climate_controller.use_external_thermostat_1,
                self._climate_controller.use_external_thermostat_2,
            )
        else:
            # No external thermostat, must be using internal room temperature feedback
            inferred_mode = WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT
            _LOGGER.debug(
                "Device %s: Inferred water law mode INTERNAL_THERMOSTAT (no external thermostat detected)",
                self.address,
            )

        self._climate_controller.water_law_mode = inferred_mode

    def handle_packet(self, *_nargs, **kwargs):
        message_number = kwargs["messageNumber"]
        packet_data: BaseMessage = kwargs["packet"]
        # Update DHW controller if it exists and the message is relevant
        if self._dhw_controller and message_number in self._DHW_MESSAGE_MAP:
            attr_name = self._DHW_MESSAGE_MAP[message_number]
            setattr(self._dhw_controller, attr_name, packet_data.VALUE)
        # Update Climate controller if it exists and the message is relevant
        if self._climate_controller and message_number in self._CLIMATE_MESSAGE_MAP:
            attr_name = self._CLIMATE_MESSAGE_MAP[message_number]
            setattr(self._climate_controller, attr_name, packet_data.VALUE)

        # Infer water law mode if we have updated a relevant configuration message
        if self._climate_controller and message_number in (0x4095, 0x4096):
            self._infer_water_law_mode()
        return super().handle_packet(*_nargs, **kwargs)


class OutdoorNasaDevice(NasaDevice):
    """NASA Outdoor Device."""

    _MESSAGES_TO_LISTEN = [0x4426, 0x4427]

    def __init__(
        self,
        address: str,
        packet_parser: NasaPacketParser,
        config: NasaConfig,
        client: NasaClient,
    ) -> None:
        super().__init__(address, AddressClass.OUTDOOR, packet_parser, config, client)

    @property
    def outdoor_temperature(self) -> float | None:
        """Return the outdoor air temperature."""
        if 0x8204 in self.attributes:
            try:
                return float(self.attributes[0x8204].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def heatpump_voltage(self) -> float | None:
        """Return the heatpump voltage."""
        if 0x24FC in self.attributes:
            try:
                return float(self.attributes[0x24FC].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def power_consumption(self) -> float | None:
        """Return the current power consumption."""
        if 0x8413 in self.attributes:
            try:
                return float(self.attributes[0x8413].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def power_generated_last_minute(self) -> float | None:
        """Return the power generated in the last minute."""
        if 0x4426 in self.attributes:
            try:
                return float(self.attributes[0x4426].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def power_produced(self) -> float | None:
        """Return the power produced."""
        if 0x4427 in self.attributes:
            try:
                return float(self.attributes[0x4427].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def power_current(self) -> float | None:
        """Return the power current."""
        if 0x82DB in self.attributes:
            try:
                return float(self.attributes[0x82DB].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def cumulative_energy(self) -> float | None:
        """Return the cumulative energy consumption."""
        if 0x8414 in self.attributes:
            try:
                return float(self.attributes[0x8414].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def compressor_frequency(self) -> float | None:
        """Return the compressor frequency."""
        if 0x8238 in self.attributes:
            try:
                return float(self.attributes[0x8238].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def fan_speed(self) -> float | None:
        """Return the fan speed."""
        if 0x823D in self.attributes:
            try:
                return float(self.attributes[0x823D].VALUE)
            except (ValueError, TypeError):
                return None
        return None

    # Virtual properties
    @property
    def cop_rating(self) -> float | None:
        """Return the COP rating (power produced / power consumed)."""
        power_produced = self.power_produced
        cumulative_energy = self.cumulative_energy
        if power_produced is not None and cumulative_energy not in (None, 0):
            try:
                # Ensure both values are numeric
                power_produced = float(power_produced)
                cumulative_energy = float(cumulative_energy)
                return power_produced / cumulative_energy
            except (ValueError, TypeError):
                return None
        return None
