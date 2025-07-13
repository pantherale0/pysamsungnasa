"""Different controllers for a device."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable

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
)


@dataclass
class DhwController:
    """Data class to store DHW state information."""

    address: str
    message_sender: Callable
    power: Optional[bool] = None
    operation_mode: Optional[DhwOpMode] = None
    reference_temp_source: Optional[DhwReferenceTemp] = None
    target_temperature: Optional[float] = None
    current_temperature: Optional[float] = None
    outdoor_operation_status: Optional[OutdoorOperationStatus] = None

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
            self.message_sender(
                destination=self.address,
                request_type=DataType.REQUEST,
                messages=[
                    SendMessage(MESSAGE_ID=InDhwOpMode.MESSAGE_ID, PAYLOAD=self.operation_mode.value.to_bytes(1, "little"))  # type: ignore
                ],
            )


@dataclass
class ClimateController:
    """Climate controller."""

    address: str
    message_sender: Callable
    power: Optional[bool] = None
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
    outdoor_operation_status: Optional[OutdoorOperationStatus] = None

    @property
    def f_target_temperature(self):
        """Computed target temperature based on current mode."""
        if self.current_mode == InOperationMode.AUTO:
            return self.water_law_target_temperature
        elif self.current_mode == InOperationMode.COOL:
            return self.water_outlet_target_temperature
        elif self.current_mode == InOperationMode.HEAT:
            return self.target_temperature
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
        """Set the mode."""
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

    async def set_target_temperature(self, temperature: float):
        """Set the target temperature of the climate device."""
        messages = []
        if self.current_mode == InOperationMode.AUTO:
            self.water_law_target_temperature = temperature
            messages.append(
                SendMessage(
                    MESSAGE_ID=InWaterLawTargetTemperature.MESSAGE_ID,  # type: ignore
                    PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                )
            )
        elif self.current_mode == InOperationMode.COOL:
            self.water_outlet_target_temperature = temperature
            messages.append(
                SendMessage(
                    MESSAGE_ID=InWaterOutletTargetTemperature.MESSAGE_ID,  # type: ignore
                    PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                )
            )
        elif self.current_mode == InOperationMode.HEAT:
            self.target_temperature = temperature
            messages.append(
                SendMessage(
                    MESSAGE_ID=InTargetTemperature.MESSAGE_ID,  # type: ignore
                    PAYLOAD=int(temperature * 10).to_bytes(2, "big"),
                )
            )
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
