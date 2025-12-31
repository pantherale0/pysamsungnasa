"""Different controllers for a device."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum

from ..protocol.factory.messaging import SendMessage
from ..protocol.factory.messages.indoor import (
    InDhwWaterHeaterPower,
    InDhwOpMode,
    DhwTargetTemperature,
    InOperationPowerMessage,
    InOperationModeMessage,
    InTargetTemperature,
    InWaterLawTargetTemperature,
    InWaterOutletTargetTemperature,
)
from ..protocol.enum import (
    DataType,
    DhwOpMode,
    DhwReferenceTemp,
    InOperationMode,
    InThermostatStatus,
    InFanMode,
    ErvFanSpeed,
    OutdoorOperationStatus,
    OutdoorOperationHeatCool,
    OutdoorIndoorDefrostStep,
    InFsv3011EnableDhw,
    InFsv2041WaterLawTypeHeating,
    InFsv2081WaterLawTypeCooling,
    InUseThermostat,
)


class WaterLawMode(Enum):
    """Water law operational modes."""

    WATER_TARGET = "water_target"  # Direct water outlet temperature control
    WATER_LAW_EXTERNAL_THERMOSTAT = "water_law_ext_thermo"  # Water law with external thermostat
    WATER_LAW_INTERNAL_THERMOSTAT = "water_law_int_thermo"  # Water law with internal/room thermostat


@dataclass
class ControllerBase:
    """Base class for controllers."""

    address: str
    message_sender: Callable
    power: Optional[bool] = None


@dataclass
class DhwController(ControllerBase):
    """Data class to store DHW state information."""

    operation_mode: Optional[DhwOpMode] = None
    reference_temp_source: Optional[DhwReferenceTemp] = None
    target_temperature: Optional[float] = None
    current_temperature: Optional[float] = None
    outdoor_operation_status: Optional[OutdoorOperationStatus] = None
    outdoor_operation_mode: Optional[OutdoorOperationHeatCool] = None
    dhw_enable_status: Optional[InFsv3011EnableDhw] = None

    async def turn_on(self):
        """Turn on the DHW."""
        messages = []
        if self.operation_mode is not None:
            messages.append(
                SendMessage(MESSAGE_ID=InDhwOpMode.MESSAGE_ID, PAYLOAD=self.operation_mode.value.to_bytes(1, "little"))  # type: ignore
            )
        messages.append(
            SendMessage(
                MESSAGE_ID=InDhwWaterHeaterPower.MESSAGE_ID,  # type: ignore
                PAYLOAD=b"\x01",
            )
        )
        await self.message_sender(destination=self.address, request_type=DataType.REQUEST, messages=messages)
        self.power = True

    async def turn_off(self):
        """Turn off the DHW."""
        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[SendMessage(MESSAGE_ID=InDhwWaterHeaterPower.MESSAGE_ID, PAYLOAD=b"\x00")],  # type: ignore
        )
        self.power = False

    async def set_target_temperature(self, temperature: float):
        """Set the target temperature."""
        self.target_temperature = temperature
        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[
                SendMessage(
                    MESSAGE_ID=DhwTargetTemperature.MESSAGE_ID,  # type: ignore
                    PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                )
            ],
        )

    async def set_operation_mode(self, mode: DhwOpMode):
        """Set the operation mode."""
        self.operation_mode = mode
        if self.operation_mode is not None:
            await self.message_sender(
                destination=self.address,
                request_type=DataType.REQUEST,
                messages=[
                    SendMessage(MESSAGE_ID=InDhwOpMode.MESSAGE_ID, PAYLOAD=self.operation_mode.value.to_bytes(1, "little"))  # type: ignore
                ],
            )


@dataclass
class ClimateController(ControllerBase):
    """Climate controller with multi-mode water law support."""

    supports_h_swing: Optional[bool] = False
    supports_v_swing: Optional[bool] = False
    supports_fan: Optional[bool] = False
    current_mode: Optional[InOperationMode] = None
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    current_humidity: Optional[float] = None
    zone_1_status: Optional[InThermostatStatus] = None
    zone_2_status: Optional[InThermostatStatus] = None
    current_fan_mode: Optional[InFanMode] = None
    current_fan_speed: Optional[ErvFanSpeed] = None
    water_law_target_temperature: Optional[float] = None
    water_outlet_target_temperature: Optional[float] = None
    water_outlet_current_temperature: Optional[float] = None
    outdoor_operation_status: Optional[OutdoorOperationStatus] = None
    outdoor_operation_mode: Optional[OutdoorOperationHeatCool] = None
    outdoor_defrost_status: Optional[OutdoorIndoorDefrostStep] = None

    # Water law mode configuration
    water_law_mode: Optional[WaterLawMode] = None
    heating_water_law_type: Optional[InFsv2041WaterLawTypeHeating] = None  # Floor (1) or FCU (2)
    cooling_water_law_type: Optional[InFsv2081WaterLawTypeCooling] = None  # Floor (1) or FCU (2)
    use_external_thermostat_1: Optional[InUseThermostat] = None  # External thermostat 1
    use_external_thermostat_2: Optional[InUseThermostat] = None  # External thermostat 2

    # Per-mode temperature setpoints (for flexible temperature management)
    room_temperature_setpoint: Optional[float] = None  # For water law with internal thermostat
    external_thermostat_setpoint: Optional[float] = None  # For water law with external thermostat
    water_target_temperature_setpoint: Optional[float] = None  # For direct water outlet temperature

    @property
    def f_target_temperature(self):
        """Computed target temperature based on current mode and water law mode."""
        if self.current_mode == InOperationMode.COOL or self.current_mode == InOperationMode.HEAT:
            return self.water_outlet_target_temperature
        elif self.current_mode == InOperationMode.AUTO:
            # For water law modes, use mode-specific setpoint
            if self.water_law_mode == WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT:
                return self.target_temperature
            elif self.water_law_mode == WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT:
                return self.water_law_target_temperature
            else:
                return self.target_temperature
        return None

    @property
    def f_current_temperature(self):
        """Computed current temperature based on current mode and water law mode."""
        if self.current_mode == InOperationMode.AUTO:
            return self.current_temperature
        elif self.current_mode == InOperationMode.COOL or self.current_mode == InOperationMode.HEAT:
            return self.water_outlet_current_temperature
        return None

    async def turn_on(self):
        """Turn on the climate."""
        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[SendMessage(MESSAGE_ID=InOperationPowerMessage.MESSAGE_ID, PAYLOAD=b"\x01")],  # type: ignore
        )
        self.power = True

    async def turn_off(self):
        """Turn off the climate."""
        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[SendMessage(MESSAGE_ID=InOperationPowerMessage.MESSAGE_ID, PAYLOAD=b"\x00")],  # type: ignore
        )
        self.power = False

    async def set_mode(self, mode: InOperationMode):
        """Set the operation mode."""
        self.current_mode = mode
        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[
                SendMessage(
                    MESSAGE_ID=InOperationModeMessage.MESSAGE_ID,  # type: ignore
                    PAYLOAD=mode.value.to_bytes(1, "little"),
                )
            ],
        )

    async def set_water_law_mode(self, water_law_mode: WaterLawMode):
        """
        Set the water law operational mode.

        This determines how the controller manages temperature setpoints:
        - WATER_TARGET: Direct water outlet temperature control (0x4247)
        - WATER_LAW_EXTERNAL_THERMOSTAT: External device controls room temp via water law curve
        - WATER_LAW_INTERNAL_THERMOSTAT: Uses room temperature feedback for water law curve
        """
        self.water_law_mode = water_law_mode
        # Implementation note: Actual mode activation depends on device capabilities
        # and may require additional configuration messages based on device state

    async def set_water_law_type(
        self,
        heating_type: Optional[InFsv2041WaterLawTypeHeating] = None,
        cooling_type: Optional[InFsv2081WaterLawTypeCooling] = None,
    ):
        """
        Set water law types for heating and cooling.

        Args:
            heating_type: InFsv2041WaterLawTypeHeating.FLOOR or .FCU
            cooling_type: InFsv2081WaterLawTypeCooling.FLOOR or .FCU
        """
        messages = []
        if heating_type is not None:
            self.heating_water_law_type = heating_type
            messages.append(
                SendMessage(
                    MESSAGE_ID=0x4093,  # FSV 2041 Water Law Type Heating
                    PAYLOAD=heating_type.value.to_bytes(1, "little"),
                )
            )
        if cooling_type is not None:
            self.cooling_water_law_type = cooling_type
            messages.append(
                SendMessage(
                    MESSAGE_ID=0x4094,  # FSV 2081 Water Law Type Cooling
                    PAYLOAD=cooling_type.value.to_bytes(1, "little"),
                )
            )
        if messages:
            await self.message_sender(
                destination=self.address,
                request_type=DataType.REQUEST,
                messages=messages,
            )

    async def set_external_thermostat(self, thermostat_index: int, enabled: InUseThermostat):
        """
        Configure external thermostat usage.

        Args:
            thermostat_index: 1 or 2 (for thermostats 1 and 2)
            enabled: InUseThermostat enum value (NO=0, VALUE_1=1, VALUE_2=2, VALUE_3=3)
        """
        if thermostat_index == 1:
            self.use_external_thermostat_1 = enabled
            message_id = 0x4095  # FSV 2091 Use Thermostat 1
        elif thermostat_index == 2:
            self.use_external_thermostat_2 = enabled
            message_id = 0x4096  # FSV 2092 Use Thermostat 2
        else:
            raise ValueError("Thermostat index must be 1 or 2")

        await self.message_sender(
            destination=self.address,
            request_type=DataType.REQUEST,
            messages=[SendMessage(MESSAGE_ID=message_id, PAYLOAD=enabled.value.to_bytes(1, "little"))],
        )

    async def set_target_temperature(self, temperature: float):
        """
        Set the target temperature of the climate device.

        The actual message sent depends on the current operation mode and water law mode:
        - In COOL mode: Sets water outlet target temp (0x4247)
        - In AUTO/HEAT with WATER_LAW_EXTERNAL_THERMOSTAT: Sets water law target temp (0x4248)
        - In AUTO/HEAT with WATER_LAW_INTERNAL_THERMOSTAT: Sets room target via water law (0x4248)
        - In AUTO/HEAT with WATER_TARGET: Sets water outlet target temp (0x4247)
        - In AUTO/HEAT without water law: Sets room target temp (0x4201)
        """
        messages = []

        if self.current_mode == InOperationMode.COOL or self.current_mode == InOperationMode.HEAT:
            # Cooling always uses water outlet target temperature
            self.water_outlet_target_temperature = temperature
            messages.append(
                SendMessage(
                    MESSAGE_ID=InWaterOutletTargetTemperature.MESSAGE_ID,  # type: ignore  # 0x4247
                    PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                )
            )
        elif self.current_mode == InOperationMode.AUTO:
            if self.water_law_mode == WaterLawMode.WATER_TARGET:
                # Direct water outlet temperature control
                self.water_target_temperature_setpoint = temperature
                messages.append(
                    SendMessage(
                        MESSAGE_ID=InWaterOutletTargetTemperature.MESSAGE_ID,  # type: ignore  # 0x4247
                        PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                    )
                )
            elif self.water_law_mode == WaterLawMode.WATER_LAW_EXTERNAL_THERMOSTAT:
                # External thermostat provides room temperature feedback
                # Set water law curve target (ambient-based curve)
                self.external_thermostat_setpoint = temperature
                messages.append(
                    SendMessage(
                        MESSAGE_ID=InWaterLawTargetTemperature.MESSAGE_ID,  # type: ignore  # 0x4248
                        PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                    )
                )
            elif self.water_law_mode == WaterLawMode.WATER_LAW_INTERNAL_THERMOSTAT:
                # Use room temperature feedback via water law curve
                self.room_temperature_setpoint = temperature
                messages.append(
                    SendMessage(
                        MESSAGE_ID=InWaterLawTargetTemperature.MESSAGE_ID,  # type: ignore  # 0x4248
                        PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                    )
                )
            else:
                # No water law mode specified, use standard room temperature setpoint
                self.target_temperature = temperature
                messages.append(
                    SendMessage(
                        MESSAGE_ID=InTargetTemperature.MESSAGE_ID,  # type: ignore  # 0x4201
                        PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                    )
                )

        if messages:
            await self.message_sender(
                destination=self.address,
                request_type=DataType.REQUEST,
                messages=messages,
            )

    async def send_zone_1_temperature(self, temperature: float):
        """Send a zone 1 temperature."""
        # Setting the same value is not the way to inform EHS of the zone temperature
        # For zone 1:
        #   Instead of setting 0x4203
        #   Set 0x4076 <tempsensorenable=01> 0x423A <temp=00fa>
        messages = [SendMessage(MESSAGE_ID=0x4076, PAYLOAD=b"\x01")]
        messages.append(
            SendMessage(
                MESSAGE_ID=0x423A,
                PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
            )
        )
        await self.message_sender(
            destination="B0FF00",
            request_type=DataType.NOTIFICATION,
            messages=messages,
        )

    async def send_zone_2_temperature(self, temperature: float):
        """Send a zone 2 temperature."""
        # Setting the same value is not the way to inform EHS of the zone temperature
        # For zone 2:
        #   Instead of setting 0x42D4
        #   Set 0x4118 <tempsensorenable=01> 0x42DA <temp=00fa>
        messages = [SendMessage(MESSAGE_ID=0x4118, PAYLOAD=b"\x01")]
        messages.append(
            SendMessage(
                MESSAGE_ID=0x42DA,
                PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
            )
        )
        await self.message_sender(
            destination="B0FF00",
            request_type=DataType.NOTIFICATION,
            messages=messages,
        )
