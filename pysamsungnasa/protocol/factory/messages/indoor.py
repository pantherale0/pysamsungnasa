"""Messages from the indoor unit."""

from ..messaging import (
    BoolMessage,
    EnumMessage,
    FloatMessage,
    BasicTemperatureMessage,
    BasicPowerMessage,
    RawMessage,
    IntegerMessage,
)

from ...enum import (
    InOperationMode,
    InOperationModeReal,
    InFanMode,
    InAltMode,
    InOperationVentMode,
    InFanModeReal,
    InFsv3042DayOfWeek,
    InOperationPower,
    ErvFanSpeed,
    InLouverHlPartSwing,
    DhwOpMode,
    InThermostatStatus,
    InBackupHeater as InBackupHeaterEnum,
    DhwReferenceTemp,
    In2WayValve,
    InFsv2041WaterLawTypeHeating as InFsv2041WaterLawTypeHeatingEnum,
    InFsv2081WaterLawTypeCooling as InFsv2081WaterLawTypeCoolingEnum,
    InUseThermostat,
    InFsv2093 as InFsv2093Enum,
    InFsv2094,
    InFsv3011EnableDhw as InFsv3011EnableDhwEnum,
    InFsv3061UseDhwThermostat as InFsv3061UseDhwThermostatEnum,
    InFsv3071 as InFsv3071Enum,
    InFsv5022 as InFsv5022Enum,
    InFsv5033,
    InFsv5061,
    InOperationVentPower,
    InOperationVentPowerSetting,
    InOperationRoomFan,
    InOperationRoomFanControl,
    InOperationOutdoorFan,
    InLouverLrFull,
    InLouverLr,
    InLouverVlRightDownSwing,
    InLouverVlLeftDownSwing,
    InDrainPumpPower,
    InBackupHeaterPower,
    InIceCtrlState,
    InCoilFreezingControl,
    InStateDefrostControl,
    InStateDefrostMode,
    InMtfc,
    InLouverVlFull,
    InThermistorOpen,
    InIceCheckPoint,
    InSilence,
    InWifiKitPower,
    InWifiKitControl,
    InLouverVl,
    InLouverHlDownUp,
    InLouverHlNowPos,
    InLouverVlPos,
    InSolarPump,
    InThermostat0,
    InOutingMode,
    InQuietMode,
    InDischargeTempControl,
    InLouverHlAuto,
    InLouverHlAutoUpDown,
    InWallMountedRemoteControl,
    InFsv302LouverControl,
    InFsv302LouverValue,
    InFsv302TimeSchedule,
    InModelInformation,
    InAutoStaticPressure,
    InVacancyControl,
    InEnterRoomControl,
    InChillerWaterlawSensor,
    InChillerWaterlaw,
    InChillerSettingSilentLevel,
    InChillerSettingDemandLevel,
    InTdmIndoorType,
    InWaterValve,
    InEnthalpyControl,
    InFreeCooling,
    InZone1Power,
    InGasLevel,
    InDiffuserOperation,
    InFsv4061,
    InFsv5081,
    InFsv5091,
    InFsv5094,
    InZone2Power,
    In3WayValve,
    InPvContactState,
    InSgReadyModeState,
)


class InModelCode2Message(RawMessage):
    """Parser for message 0x0D00 (Model/Build Identifier 2).

    Submessage returned as part of the indoor unit model information query.
    Contains model-specific or build-specific identifier code.
    Value may change based on device configuration or operation state.

    Example: "08000efe" or "00000efe"
    """

    MESSAGE_ID = 0x0D00
    MESSAGE_NAME = "Model Code 2"


class InOperationPowerMessage(EnumMessage):
    """Parser for message 0x4000 (Indoor Operation Power)."""

    MESSAGE_ID = 0x4000
    MESSAGE_NAME = "Indoor Operation Power"
    MESSAGE_ENUM = InOperationPower


class InOperationModeMessage(EnumMessage):
    """Parser for message 0x4001 (Indoor Operation Mode)."""

    MESSAGE_ID = 0x4001
    MESSAGE_NAME = "Indoor Operation Mode"
    MESSAGE_ENUM = InOperationMode


class InOperationModeRealMessage(EnumMessage):
    """Parser for message 0x4002 (Indoor Operation Mode Real)."""

    MESSAGE_ID = 0x4002
    MESSAGE_NAME = "Indoor Operation Mode Real"
    MESSAGE_ENUM = InOperationModeReal


class InOperationVentPowerMessage(EnumMessage):
    """Parser for message 0x4003 (Indoor Operation Ventilation Power)."""

    MESSAGE_ID = 0x4003
    MESSAGE_NAME = "Indoor Operation Ventilation Power"
    MESSAGE_ENUM = InOperationVentPower


class InOperationVentModeMessage(EnumMessage):
    """Parser for message 0x4004 (Indoor Operation Ventilation Mode Setting)."""

    MESSAGE_ID = 0x4004
    MESSAGE_NAME = "Indoor Operation Ventilation Mode Setting"
    MESSAGE_ENUM = InOperationVentPowerSetting


class InOperationVentModeMessage2(EnumMessage):
    """Parser for message 0x4005 (Indoor Operation Ventilation Mode 2)."""

    MESSAGE_ID = 0x4005
    MESSAGE_NAME = "Indoor Operation Ventilation Mode 2"
    MESSAGE_ENUM = InOperationVentMode


class InFanModeMessage(EnumMessage):
    """Parser for message 0x4006 (Indoor Fan Mode)."""

    MESSAGE_ID = 0x4006
    MESSAGE_NAME = "Indoor Fan Mode"
    MESSAGE_ENUM = InFanMode


class InFanModeRealMessage(EnumMessage):
    """Parser for message 0x4007 (Indoor Fan Mode Real)."""

    MESSAGE_ID = 0x4007
    MESSAGE_NAME = "Indoor Fan Mode Real"
    MESSAGE_ENUM = InFanModeReal


class InErvFanSpeedMessage(EnumMessage):
    """Parser for message 0x4008 (Indoor ERV Fan Speed)."""

    MESSAGE_ID = 0x4008
    MESSAGE_NAME = "Indoor ERV Fan Speed"
    MESSAGE_ENUM = ErvFanSpeed


class InOperationRoomFanMessage(EnumMessage):
    """Parser for message 0x400F (Indoor Operation Room Fan)."""

    MESSAGE_ID = 0x400F
    MESSAGE_NAME = "Indoor Operation Room Fan"
    MESSAGE_ENUM = InOperationRoomFan


class InOperationRoomFanControlMessage(EnumMessage):
    """Parser for message 0x4010 (Indoor Operation Room Fan Control)."""

    MESSAGE_ID = 0x4010
    MESSAGE_NAME = "Indoor Operation Room Fan Control"
    MESSAGE_ENUM = InOperationRoomFanControl


class InLouverHlSwing(BoolMessage):
    """Parser for message 0x4011 (Indoor Louver HL Swing)."""

    MESSAGE_ID = 0x4011
    MESSAGE_NAME = "Indoor Louver HL Swing"


class InLouverHlPartSwingMessage(EnumMessage):
    """Parser for message 0x4012 (Indoor Louver HL Part Swing)."""

    MESSAGE_ID = 0x4012
    MESSAGE_NAME = "Indoor Louver HL Part Swing"
    MESSAGE_ENUM = InLouverHlPartSwing


class InOperationOutdoorFanMessage(EnumMessage):
    """Parser for message 0x4015 (Indoor Operation Outdoor Fan)."""

    MESSAGE_ID = 0x4015
    MESSAGE_NAME = "Indoor Operation Outdoor Fan"
    MESSAGE_ENUM = InOperationOutdoorFan


class InLouverLrFullMessage(EnumMessage):
    """Parser for message 0x4019 (Indoor Louver LR Full)."""

    MESSAGE_ID = 0x4019
    MESSAGE_NAME = "Indoor Louver LR Full"
    MESSAGE_ENUM = InLouverLrFull


class InLouverLrMessage(EnumMessage):
    """Parser for message 0x401B (Indoor Louver LR)."""

    MESSAGE_ID = 0x401B
    MESSAGE_NAME = "Indoor Louver LR"
    MESSAGE_ENUM = InLouverLr


class InLouverVlRightDownSwingMessage(EnumMessage):
    """Parser for message 0x4023 (Indoor Louver VL Right Down Swing)."""

    MESSAGE_ID = 0x4023
    MESSAGE_NAME = "Indoor Louver VL Right Down Swing"
    MESSAGE_ENUM = InLouverVlRightDownSwing


class InLouverVlLeftDownSwingMessage(EnumMessage):
    """Parser for message 0x4024 (Indoor Louver VL Left Down Swing)."""

    MESSAGE_ID = 0x4024
    MESSAGE_NAME = "Indoor Louver VL Left Down Swing"
    MESSAGE_ENUM = InLouverVlLeftDownSwing


class InDrainPumpPowerMessage(EnumMessage):
    """Parser for message 0x4027 (Indoor Drain Pump Power)."""

    MESSAGE_ID = 0x4027
    MESSAGE_NAME = "Indoor Drain Pump Power"
    MESSAGE_ENUM = InDrainPumpPower


class InStateThermo(BoolMessage):
    """Parser for message 0x4028 (Indoor Thermo State)."""

    MESSAGE_ID = 0x4028
    MESSAGE_NAME = "Indoor Thermo State"


class InBackupHeaterPowerMessage(EnumMessage):
    """Parser for message 0x4029 (Indoor Backup Heater Power)."""

    MESSAGE_ID = 0x4029
    MESSAGE_NAME = "Indoor Backup Heater Power"
    MESSAGE_ENUM = InBackupHeaterPower


class InIceCtrlStateMessage(EnumMessage):
    """Parser for message 0x402A (Indoor Ice Control State)."""

    MESSAGE_ID = 0x402A
    MESSAGE_NAME = "Indoor Ice Control State"
    MESSAGE_ENUM = InIceCtrlState


class InCoilFreezingControlMessage(EnumMessage):
    """Parser for message 0x402B (Indoor Coil Freezing Control)."""

    MESSAGE_ID = 0x402B
    MESSAGE_NAME = "Indoor Coil Freezing Control"
    MESSAGE_ENUM = InCoilFreezingControl


class InStateDefrostControlMessage(EnumMessage):
    """Parser for message 0x402D (Indoor State Defrost Control)."""

    MESSAGE_ID = 0x402D
    MESSAGE_NAME = "Indoor State Defrost Control"
    MESSAGE_ENUM = InStateDefrostControl


class InStateDefrostModeMessage(EnumMessage):
    """Parser for message 0x402E (Indoor State Defrost Mode)."""

    MESSAGE_ID = 0x402E
    MESSAGE_NAME = "Indoor State Defrost Mode"
    MESSAGE_ENUM = InStateDefrostMode


class InMtfcMessage(EnumMessage):
    """Parser for message 0x402F (Indoor MTFC)."""

    MESSAGE_ID = 0x402F
    MESSAGE_NAME = "Indoor MTFC"
    MESSAGE_ENUM = InMtfc


class InLouverVlFullMessage(EnumMessage):
    """Parser for message 0x4031 (Indoor Louver VL Full)."""

    MESSAGE_ID = 0x4031
    MESSAGE_NAME = "Indoor Louver VL Full"
    MESSAGE_ENUM = InLouverVlFull


class InThermistorOpenMessage(EnumMessage):
    """Parser for message 0x4035 (Indoor Thermistor Open)."""

    MESSAGE_ID = 0x4035
    MESSAGE_NAME = "Indoor Thermistor Open"
    MESSAGE_ENUM = InThermistorOpen


class InHumidity(FloatMessage):
    """Parser for message 0x4038 (Indoor Humidity)."""

    MESSAGE_ID = 0x4038
    MESSAGE_NAME = "Indoor Humidity"
    UNIT_OF_MEASUREMENT = "%"
    SIGNED = False
    ARITHMETIC = 1.0


class InIceCheckPointMessage(EnumMessage):
    """Parser for message 0x4043 (Indoor Ice Check Point)."""

    MESSAGE_ID = 0x4043
    MESSAGE_NAME = "Indoor Ice Check Point"
    MESSAGE_ENUM = InIceCheckPoint


class InSilenceMessage(EnumMessage):
    """Parser for message 0x4046 (Indoor Silence Mode)."""

    MESSAGE_ID = 0x4046
    MESSAGE_NAME = "Indoor Silence Mode"
    MESSAGE_ENUM = InSilence


class InWifiKitPowerMessage(EnumMessage):
    """Parser for message 0x4047 (Indoor WiFi Kit Power)."""

    MESSAGE_ID = 0x4047
    MESSAGE_NAME = "Indoor WiFi Kit Power"
    MESSAGE_ENUM = InWifiKitPower


class InWifiKitControlMessage(EnumMessage):
    """Parser for message 0x4048 (Indoor WiFi Kit Control)."""

    MESSAGE_ID = 0x4048
    MESSAGE_NAME = "Indoor WiFi Kit Control"
    MESSAGE_ENUM = InWifiKitControl


class InLouverVlMessage(EnumMessage):
    """Parser for message 0x404F (Indoor Louver VL)."""

    MESSAGE_ID = 0x404F
    MESSAGE_NAME = "Indoor Louver VL"
    MESSAGE_ENUM = InLouverVl


class InLouverHlDownUpMessage(EnumMessage):
    """Parser for message 0x4051 (Indoor Louver HL Down Up)."""

    MESSAGE_ID = 0x4051
    MESSAGE_NAME = "Indoor Louver HL Down Up"
    MESSAGE_ENUM = InLouverHlDownUp


class InLouverHlNowPosMessage(EnumMessage):
    """Parser for message 0x4059 (Indoor Louver HL Now Position)."""

    MESSAGE_ID = 0x4059
    MESSAGE_NAME = "Indoor Louver HL Now Position"
    MESSAGE_ENUM = InLouverHlNowPos


class InLouverVlPosMessage(EnumMessage):
    """Parser for message 0x405F (Indoor Louver VL Position)."""

    MESSAGE_ID = 0x405F
    MESSAGE_NAME = "Indoor Louver VL Position"
    MESSAGE_ENUM = InLouverVlPos


class InAltModeMessage(EnumMessage):
    """Parser for message 0x4060 (Indoor Alternative Mode)."""

    MESSAGE_ID = 0x4060
    MESSAGE_NAME = "Indoor Alternative Mode"
    MESSAGE_ENUM = InAltMode


class InDhwWaterHeaterPower(BoolMessage):
    """Parser for message 0x4065 (Indoor DHW Water Heater Power)."""

    MESSAGE_ID = 0x4065
    MESSAGE_NAME = "Indoor DHW Water Heater Power"


class InDhwOpMode(EnumMessage):
    """Parser for message 0x4066 (Indoor DHW Operation Mode)."""

    MESSAGE_ID = 0x4066
    MESSAGE_NAME = "Indoor DHW Operation Mode"
    MESSAGE_ENUM = DhwOpMode


class In3WayValveMessage(EnumMessage):
    """Parser for message 0x4067 (3-Way Valve control)."""

    MESSAGE_ID = 0x4067
    MESSAGE_NAME = "3-Way Valve control"
    MESSAGE_ENUM = In3WayValve


class InSolarPumpMessage(EnumMessage):
    """Parser for message 0x4068 (Indoor Solar Pump)."""

    MESSAGE_ID = 0x4068
    MESSAGE_NAME = "Indoor Solar Pump"
    MESSAGE_ENUM = InSolarPump


class InThermostatZone1Status(EnumMessage):
    """Parser for message 0x4069 (Indoor Thermostat Zone 1 Status)."""

    MESSAGE_ID = 0x4069
    MESSAGE_NAME = "Indoor Thermostat Zone 1 Status"
    MESSAGE_ENUM = InThermostatStatus


class InThermostatZone2Status(EnumMessage):
    """Parser for message 0x4068 (Indoor Thermostat Zone 2 Status)."""

    MESSAGE_ID = 0x406A
    MESSAGE_NAME = "Indoor Thermostat Zone 2 Status"
    MESSAGE_ENUM = InThermostatStatus


class InThermostat0Message(EnumMessage):
    """Parser for message 0x406B (Indoor Thermostat 0)."""

    MESSAGE_ID = 0x406B
    MESSAGE_NAME = "Indoor Thermostat 0"
    MESSAGE_ENUM = InThermostat0


class InBackupHeater(EnumMessage):
    """Parser for message 0x406C (Indoor Backup Heater Status)."""

    MESSAGE_ID = 0x406C
    MESSAGE_NAME = "Indoor Backup Heater"
    MESSAGE_ENUM = InBackupHeaterEnum


class InOutingModeMessage(EnumMessage):
    """Parser for message 0x406D (Indoor Outing Mode)."""

    MESSAGE_ID = 0x406D
    MESSAGE_NAME = "Indoor Outing Mode"
    MESSAGE_ENUM = InOutingMode


class InQuietModeMessage(EnumMessage):
    """Parser for message 0x406E (Indoor Quiet Mode)."""

    MESSAGE_ID = 0x406E
    MESSAGE_NAME = "Indoor Quiet Mode"
    MESSAGE_ENUM = InQuietMode


class DhwReferenceTemperatureMessage(EnumMessage):
    """Parser for message 0x406F (Indoor DHW Reference Temperature)."""

    MESSAGE_ID = 0x406F
    MESSAGE_NAME = "Indoor DHW Reference Temperature"
    MESSAGE_ENUM = DhwReferenceTemp


class InDischargeTempControlMessage(EnumMessage):
    """Parser for message 0x4070 (Indoor Discharge Temperature Control)."""

    MESSAGE_ID = 0x4070
    MESSAGE_NAME = "Indoor Discharge Temperature Control"
    MESSAGE_ENUM = InDischargeTempControl


class InLouverHlAutoMessage(EnumMessage):
    """Parser for message 0x4073 (Indoor Louver HL Auto)."""

    MESSAGE_ID = 0x4073
    MESSAGE_NAME = "Indoor Louver HL Auto"
    MESSAGE_ENUM = InLouverHlAuto


class InLouverHlAutoUpDownMessage(EnumMessage):
    """Parser for message 0x4074 (Indoor Louver HL Auto Up Down)."""

    MESSAGE_ID = 0x4074
    MESSAGE_NAME = "Indoor Louver HL Auto Up Down"
    MESSAGE_ENUM = InLouverHlAutoUpDown


class InRoomTempSensorMessage(BoolMessage):
    """Parser for message 0x4076 (Indoor Room Temperature Sensor)."""

    MESSAGE_ID = 0x4076
    MESSAGE_NAME = "Indoor Room Temperature Sensor"


class InWallMountedRemoteControlMessage(EnumMessage):
    """Parser for message 0x4077 (Indoor Wall Mounted Remote Control)."""

    MESSAGE_ID = 0x4077
    MESSAGE_NAME = "Indoor Wall Mounted Remote Control"
    MESSAGE_ENUM = InWallMountedRemoteControl


class InFsv302LouverControlMessage(EnumMessage):
    """Parser for message 0x407B (Indoor FSV 302 Louver Control)."""

    MESSAGE_ID = 0x407B
    MESSAGE_NAME = "Indoor FSV 302 Louver Control"
    MESSAGE_ENUM = InFsv302LouverControl


class InFsv302LouverValueMessage(EnumMessage):
    """Parser for message 0x407D (Indoor FSV 302 Louver Value)."""

    MESSAGE_ID = 0x407D
    MESSAGE_NAME = "Indoor FSV 302 Louver Value"
    MESSAGE_ENUM = InFsv302LouverValue


class InLouverLrSwing(BoolMessage):
    """Parser for message 0x407E (Indoor Louver LR Swing)."""

    MESSAGE_ID = 0x407E
    MESSAGE_NAME = "Indoor Louver LR Swing"


class InFsv302TimeScheduleMessage(EnumMessage):
    """Parser for message 0x4085 (Indoor FSV 302 Time Schedule)."""

    MESSAGE_ID = 0x4085
    MESSAGE_NAME = "Indoor FSV 302 Time Schedule"
    MESSAGE_ENUM = InFsv302TimeSchedule


class InEnumUnknown6086Message(RawMessage):
    """Parser for message 0x4086 (Unknown enum message)."""

    MESSAGE_ID = 0x4086
    MESSAGE_NAME = "InEnumUnknown6086Message"


class InBoosterHeaterMessage(BoolMessage):
    """Parser for message 0x4087 (Booster Heater)."""

    MESSAGE_ID = 0x4087
    MESSAGE_NAME = "Booster Heater"


class InWaterPumpStateMessage(BoolMessage):
    """Parser for message 0x4089 (Water Pump State)."""

    MESSAGE_ID = 0x4089
    MESSAGE_NAME = "Water Pump State"


class In2WayValveMessage(EnumMessage):
    """Parser for message 0x408A (Indoor 2-Way Valve)."""

    MESSAGE_ID = 0x408A
    MESSAGE_NAME = "Indoor 2-Way Valve"
    MESSAGE_ENUM = In2WayValve


class InDhwOperating(BoolMessage):
    """Parser for message 0x408b (Indoor DHW Operating)."""

    MESSAGE_ID = 0x408B
    MESSAGE_NAME = "Indoor DHW Operating"


class InFsv2041WaterLawTypeHeating(EnumMessage):
    """Parser for message 0x4093 (FSV 2041 Water Law Type Heating)."""

    MESSAGE_ID = 0x4093
    MESSAGE_NAME = "FSV 2041 Water Law Type Heating"
    MESSAGE_ENUM = InFsv2041WaterLawTypeHeatingEnum


class InFsv2081WaterLawTypeCooling(EnumMessage):
    """Parser for message 0x4094 (FSV 2081 Water Law Type Cooling)."""

    MESSAGE_ID = 0x4094
    MESSAGE_NAME = "FSV 2081 Water Law Type Cooling"
    MESSAGE_ENUM = InFsv2081WaterLawTypeCoolingEnum


class InFsv2091UseThermostat1(EnumMessage):
    """Parser for message 0x4095 (FSV 2091 Use Thermostat 1)."""

    MESSAGE_ID = 0x4095
    MESSAGE_NAME = "FSV 2091 Use Thermostat 1"
    MESSAGE_ENUM = InUseThermostat


class InFsv2092UseThermostat2(EnumMessage):
    """Parser for message 0x4096 (FSV 2092 Use Thermostat 2)."""

    MESSAGE_ID = 0x4096
    MESSAGE_NAME = "FSV 2092 Use Thermostat 2"
    MESSAGE_ENUM = InUseThermostat


class InFsv3011EnableDhw(EnumMessage):
    """Parser for message 0x4097 (FSV 3011 Enable DHW)."""

    MESSAGE_ID = 0x4097
    MESSAGE_NAME = "FSV 3011 Enable DHW"
    MESSAGE_ENUM = InFsv3011EnableDhwEnum


class InFsv3031(BoolMessage):
    """Parser for message 0x4098 (NASA_USE_BOOSTER_HEATER 3031)."""

    MESSAGE_ID = 0x4098
    MESSAGE_NAME = "NASA_USE_BOOSTER_HEATER"


class InFsv3041(BoolMessage):
    """Parser for message 0x4099 (FSV 3041)."""

    MESSAGE_ID = 0x4099
    MESSAGE_NAME = "FSV 3041"


class InFsv3042(EnumMessage):
    """Parser for message 0x409A (FSV 3042)."""

    MESSAGE_ID = 0x409A
    MESSAGE_NAME = "FSV Day of Week"
    MESSAGE_ENUM = InFsv3042DayOfWeek


class InFsv3051(BoolMessage):
    """Parser for message 0x409B (FSV 3051)."""

    MESSAGE_ID = 0x409B
    MESSAGE_NAME = "FSV 3051"


class InFsv3061UseDhwThermostat(EnumMessage):
    """Parser for message 0x409C (FSV 3061 Use DHW Thermostat)."""

    MESSAGE_ID = 0x409C
    MESSAGE_NAME = "FSV 3061 Use DHW Thermostat"
    MESSAGE_ENUM = InFsv3061UseDhwThermostatEnum


class InFsv3071(EnumMessage):
    """Parser for message 0x409D (FSV 3071)."""

    MESSAGE_ID = 0x409D
    MESSAGE_NAME = "FSV 3071"
    MESSAGE_ENUM = InFsv3071Enum


class InFsv4023(BoolMessage):
    """Parser for message 0x40A1 (FSV 4023)."""

    MESSAGE_ID = 0x40A1
    MESSAGE_NAME = "FSV 4023"


class InFsv4031(BoolMessage):
    """Parser for message 0x40A0 (FSV 4031)."""

    MESSAGE_ID = 0x40A2
    MESSAGE_NAME = "FSV 4031"


class InFsv4032(BoolMessage):
    """Parser for message 0x40A3 (FSV 4032)."""

    MESSAGE_ID = 0x40A3
    MESSAGE_NAME = "FSV 4032"


class InFsv5041(BoolMessage):
    """Parser for message 0x40A4 (FSV 5041)."""

    MESSAGE_ID = 0x40A4
    MESSAGE_NAME = "FSV 5041"


class InFsv5061Message(EnumMessage):
    """Parser for message 0x40B4 (FSV 5061 CH/DHW supply ratio)."""

    MESSAGE_ID = 0x40B4
    MESSAGE_NAME = "FSV 5061 CH/DHW supply ratio"
    MESSAGE_ENUM = InFsv5061


class InEnumUnknown40b5Message(RawMessage):
    """Parser for message 0x40B5 (Unknown enum message)."""

    MESSAGE_ID = 0x40B5
    MESSAGE_NAME = "InEnumUnknown40b5Message"


class InAutoStaticPressureMessage(EnumMessage):
    """Parser for message 0x40BB (Automatic pressure control status)."""

    MESSAGE_ID = 0x40BB
    MESSAGE_NAME = "Automatic pressure control status"
    MESSAGE_ENUM = InAutoStaticPressure


class VacancyStatus(BoolMessage):
    """Parser for message 0x40BC (Indoor Vacancy Status)."""

    MESSAGE_ID = 0x40BC
    MESSAGE_NAME = "Indoor Vacancy Status"


class InVacancyControlMessage(EnumMessage):
    """Parser for message 0x40BD (Vacancy control)."""

    MESSAGE_ID = 0x40BD
    MESSAGE_NAME = "Vacancy control"
    MESSAGE_ENUM = InVacancyControl


class InWaterPumpPwmValueMessage(IntegerMessage):
    """Parser for message 0x40C4 (Water Pump PWM Value)."""

    MESSAGE_ID = 0x40C4
    MESSAGE_NAME = "Water Pump Speed"
    UNIT_OF_MEASUREMENT = "%"


class InThermostatWaterHeaterMessage(RawMessage):
    """Parser for message 0x40C5 (Thermostat Water Heater)."""

    MESSAGE_ID = 0x40C5
    MESSAGE_NAME = "Thermostat Water Heater"


class InEnumUnknown40c6Message(RawMessage):
    """Parser for message 0x40C6 (Unknown enum message)."""

    MESSAGE_ID = 0x40C6
    MESSAGE_NAME = "InEnumUnknown40c6Message"


class InEnterRoomControlMessage(EnumMessage):
    """Parser for message 0x40D5 (Enable room entry control option)."""

    MESSAGE_ID = 0x40D5
    MESSAGE_NAME = "Enable room entry control option"
    MESSAGE_ENUM = InEnterRoomControl


class InErrorHistoryClearMessage(BoolMessage):
    """Parser for message 0x40D6 (Indoor Error History Clear)."""

    MESSAGE_ID = 0x40D6
    MESSAGE_NAME = "Indoor Error History Clear"


class InChillerWaterlawSensorMessage(EnumMessage):
    """Parser for message 0x40E7 (Set chiller WL sensor)."""

    MESSAGE_ID = 0x40E7
    MESSAGE_NAME = "Set chiller WL sensor"
    MESSAGE_ENUM = InChillerWaterlawSensor


class InChillerWaterlawMessage(EnumMessage):
    """Parser for message 0x40F7 (Enable chiller WL)."""

    MESSAGE_ID = 0x40F7
    MESSAGE_NAME = "Enable chiller WL"
    MESSAGE_ENUM = InChillerWaterlaw


class InChillerSettingSilentLevelMessage(EnumMessage):
    """Parser for message 0x40FB (Set chiller silence level)."""

    MESSAGE_ID = 0x40FB
    MESSAGE_NAME = "Set chiller silence level"
    MESSAGE_ENUM = InChillerSettingSilentLevel


class InChillerSettingDemandLevelMessage(EnumMessage):
    """Parser for message 0x40FC (Set chiller demand level)."""

    MESSAGE_ID = 0x40FC
    MESSAGE_NAME = "Set chiller demand level"
    MESSAGE_ENUM = InChillerSettingDemandLevel


class InChillerExtWaterOutInput(BoolMessage):
    """Parser for message 0x4101 (Indoor Chiller External Water Out Input)."""

    MESSAGE_ID = 0x4101
    MESSAGE_NAME = "Indoor Chiller External Water Out Input"


class InStateFlowCheck(BoolMessage):
    """Parser for message 0x4102 (Indoor Flow Check State)."""

    MESSAGE_ID = 0x4102
    MESSAGE_NAME = "Indoor Flow Check State"


class InWaterValve1Message(EnumMessage):
    """Parser for message 0x4103 (Set water valve 1)."""

    MESSAGE_ID = 0x4103
    MESSAGE_NAME = "Set water valve 1"
    MESSAGE_ENUM = InWaterValve


class InWaterValve2Message(EnumMessage):
    """Parser for message 0x4104 (Set water valve 2)."""

    MESSAGE_ID = 0x4104
    MESSAGE_NAME = "Set water valve 2"
    MESSAGE_ENUM = InWaterValve


class InEnthalpyControlMessage(EnumMessage):
    """Parser for message 0x4105 (Set enthalpy control state)."""

    MESSAGE_ID = 0x4105
    MESSAGE_NAME = "Set enthalpy control state"
    MESSAGE_ENUM = InEnthalpyControl


class InFsv5033Message(EnumMessage):
    """Parser for message 0x4107 (FSV 5033 set TDM control)."""

    MESSAGE_ID = 0x4107
    MESSAGE_NAME = "FSV 5033 set TDM control"
    MESSAGE_ENUM = InFsv5033


class InTdmIndoorTypeMessage(EnumMessage):
    """Parser for message 0x4108 (Set TDM equipment type)."""

    MESSAGE_ID = 0x4108
    MESSAGE_NAME = "Set TDM equipment type"
    MESSAGE_ENUM = InTdmIndoorType


class InFreeCoolingMessage(EnumMessage):
    """Parser for message 0x410D (Set free cooling state)."""

    MESSAGE_ID = 0x410D
    MESSAGE_NAME = "Set free cooling state"
    MESSAGE_ENUM = InFreeCooling


class InAutomaticCleaning(BoolMessage):
    """Parser for message 0x4111 (Indoor Automatic Cleaning)."""

    MESSAGE_ID = 0x4111
    MESSAGE_NAME = "Indoor Automatic Cleaning"


class In3WayValve2Message(EnumMessage):
    """Parser for message 0x4113 (3-Way Valve 2 control)."""

    MESSAGE_ID = 0x4113
    MESSAGE_NAME = "3-Way Valve 2 control"
    MESSAGE_ENUM = In3WayValve


class InEnumUnknown4117Message(RawMessage):
    """Parser for message 0x4117 (Unknown enum message)."""

    MESSAGE_ID = 0x4117
    MESSAGE_NAME = "InEnumUnknown4117Message"


class InZone1PowerMessage(EnumMessage):
    """Parser for message 0x4119 (Zone 1 operating power)."""

    MESSAGE_ID = 0x4119
    MESSAGE_NAME = "Zone 1 operating power"
    MESSAGE_ENUM = InZone1Power


class InFsv4061Message(EnumMessage):
    """Parser for message 0x411A (FSV 4061)."""

    MESSAGE_ID = 0x411A
    MESSAGE_NAME = "FSV 4061"
    MESSAGE_ENUM = InFsv4061


class InFsv5081Message(EnumMessage):
    """Parser for message 0x411B (FSV 5081)."""

    MESSAGE_ID = 0x411B
    MESSAGE_NAME = "FSV 5081"
    MESSAGE_ENUM = InFsv5081


class InFsv5091Message(EnumMessage):
    """Parser for message 0x411C (FSV 5091)."""

    MESSAGE_ID = 0x411C
    MESSAGE_NAME = "FSV 5091"
    MESSAGE_ENUM = InFsv5091


class InFsv5094Message(EnumMessage):
    """Parser for message 0x411D (FSV 5094)."""

    MESSAGE_ID = 0x411D
    MESSAGE_NAME = "FSV 5094"
    MESSAGE_ENUM = InFsv5094


class InZone2PowerMessage(EnumMessage):
    """Parser for message 0x411E (Zone 2 operating power)."""

    MESSAGE_ID = 0x411E
    MESSAGE_NAME = "Zone 2 operating power"
    MESSAGE_ENUM = InZone2Power


class InPvContactStateMessage(EnumMessage):
    """Parser for message 0x4123 (PV Contact State)."""

    MESSAGE_ID = 0x4123
    MESSAGE_NAME = "PV Contact State"
    MESSAGE_ENUM = InPvContactState


class InSgReadyModeStateMessage(EnumMessage):
    """Parser for message 0x4124 (SG Ready Mode State)."""

    MESSAGE_ID = 0x4124
    MESSAGE_NAME = "SG Ready Mode State"
    MESSAGE_ENUM = InSgReadyModeState


class InFsvLoadSave(BoolMessage):
    """Parser for message 0x4125 (Indoor FSV Load Save)."""

    MESSAGE_ID = 0x4125
    MESSAGE_NAME = "Indoor FSV Load Save"


class InFsv2093(EnumMessage):
    """Parser for message 0x4127 (FSV 2093)."""

    MESSAGE_ID = 0x4127
    MESSAGE_NAME = "FSV 2093"
    MESSAGE_ENUM = InFsv2093Enum


class InFsv5022(EnumMessage):
    """Parser for message 0x4128 (FSV 5022)."""

    MESSAGE_ID = 0x4128
    MESSAGE_NAME = "FSV 5022"
    MESSAGE_ENUM = InFsv5022Enum


class InFsv2094Message(EnumMessage):
    """Parser for message 0x412A (FSV 2094)."""

    MESSAGE_ID = 0x412A
    MESSAGE_NAME = "FSV 2094"
    MESSAGE_ENUM = InFsv2094


class InFsvLoadSaveAlt(BoolMessage):
    """Parser for message 0x412D (Indoor FSV Load Save Alternative)."""

    MESSAGE_ID = 0x412D
    MESSAGE_NAME = "Indoor FSV Load Save Alternative"


class InGasLevelMessage(EnumMessage):
    """Parser for message 0x4147 (Gas level / Refrigerant inventory)."""

    MESSAGE_ID = 0x4147
    MESSAGE_NAME = "Gas level"
    MESSAGE_ENUM = InGasLevel


class InDiffuserOperationMessage(EnumMessage):
    """Parser for message 0x4149 (Diffuser operation)."""

    MESSAGE_ID = 0x4149
    MESSAGE_NAME = "Diffuser operation"
    MESSAGE_ENUM = InDiffuserOperation


class InTargetTemperature(BasicTemperatureMessage):
    """Parser for message 0x4201 (Indoor Target Temperature)."""

    MESSAGE_ID = 0x4201
    MESSAGE_NAME = "Indoor Target Temperature"
    SIGNED = True


class InVariableUnknown4202Message(BasicTemperatureMessage):
    """Parser for message 0x4202 (Unknown temperature variable)."""

    MESSAGE_ID = 0x4202
    MESSAGE_NAME = "InVariableUnknown4202Message"


class InRoomTemperature(BasicTemperatureMessage):
    """Parser for message 0x4203 (Indoor Room Temperature)."""

    MESSAGE_ID = 0x4203
    MESSAGE_NAME = "Indoor Room Temperature"
    SIGNED = True


class InModifiedCurrentTempMessage(BasicTemperatureMessage):
    """Parser for message 0x4204 (Modified Current Temperature)."""

    MESSAGE_ID = 0x4204
    MESSAGE_NAME = "Modified Current Temperature"


class InTempEvaIn(BasicTemperatureMessage):
    """Parser for 0x4205 (Indoor Temp Eva In)."""

    MESSAGE_ID = 0x4205
    MESSAGE_NAME = "Indoor Temp Eva In"


class InTempEvaOut(BasicTemperatureMessage):
    """Parser for 0x4206 (Indoor Temp Eva Out)."""

    MESSAGE_ID = 0x4206
    MESSAGE_NAME = "Indoor Temp Eva Out"


class InIndoorOuterTempMessage(BasicTemperatureMessage):
    """Parser for message 0x420C (Indoor Outer Temperature)."""

    MESSAGE_ID = 0x420C
    MESSAGE_NAME = "Indoor Outer Temperature"


class InCapacityRequestMessage(FloatMessage):
    """Parser for message 0x4211 (Capacity Request)."""

    MESSAGE_ID = 0x4211
    MESSAGE_NAME = "Capacity Request"


class InCapacityAbsoluteMessage(FloatMessage):
    """Parser for message 0x4212 (Capacity Absolute)."""

    MESSAGE_ID = 0x4212
    MESSAGE_NAME = "Capacity Absolute"


class InVariableUnknown4213Message(RawMessage):
    """Parser for message 0x4213 (Unknown variable)."""

    MESSAGE_ID = 0x4213
    MESSAGE_NAME = "InVariableUnknown4213Message"


class InEevValue1Message(FloatMessage):
    """Parser for message 0x4217 (Current EEV Development Level 1)."""

    MESSAGE_ID = 0x4217
    MESSAGE_NAME = "EEV Value 1"


class InModelInformationMessage(EnumMessage):
    """Parser for message 0x4229 (Indoor Model Information)."""

    MESSAGE_ID = 0x4229
    MESSAGE_NAME = "Indoor Model Information"
    MESSAGE_ENUM = InModelInformation


class DhwTargetTemperature(BasicTemperatureMessage):
    """Parser for 0x4235 (Indoor DHW Target Temperature)."""

    MESSAGE_ID = 0x4235
    MESSAGE_NAME = "Indoor DHW Target Temperature"
    SIGNED = True


class InTempWaterInMessage(BasicTemperatureMessage):
    """Parser for message 0x4236 (Return Water Temperature)."""

    MESSAGE_ID = 0x4236
    MESSAGE_NAME = "Return Water Temperature"


class DhwCurrentTemperature(BasicTemperatureMessage):
    """Parser for 0x4237 (Indoor DHW Current Temperature)."""

    MESSAGE_ID = 0x4237
    MESSAGE_NAME = "Indoor DHW Current Temperature"


class IndoorFlowTemperature(BasicTemperatureMessage):
    """Parser for 0x4238 (Leaving Water Temperature)."""

    MESSAGE_ID = 0x4238
    MESSAGE_NAME = "Leaving Water Temperature"


class InTempWaterOut2Message(BasicTemperatureMessage):
    """Parser for message 0x4239 (Heater Out Temperature)."""

    MESSAGE_ID = 0x4239
    MESSAGE_NAME = "Heater Out Temperature"


class InUnknown423eMessage(RawMessage):
    """Parser for message 0x423E (Unknown/Undocumented).

    Not found in NASA.ptc documentation. Gap between 0x4239 and 0x4247.
    May be device-specific or reserved for future use.
    """

    MESSAGE_ID = 0x423E
    MESSAGE_NAME = "Unknown 423E"


class InWaterOutletTargetTemperature(BasicTemperatureMessage):
    """Parser for message 0x4247 (Indoor Water Outlet Target Temperature)."""

    MESSAGE_ID = 0x4247
    MESSAGE_NAME = "Indoor Water Outlet Target Temperature"
    SIGNED = True


class InWaterLawTargetTemperature(BasicTemperatureMessage):
    """Parser for message 0x4248 (Indoor Water Law Target Temperature)."""

    MESSAGE_ID = 0x4248
    MESSAGE_NAME = "Indoor Water Law Target Temperature"
    SIGNED = True


class InFsv1011Message(FloatMessage):
    """Parser for message 0x424A (FSV 1011 - Cool Max Water Temp)."""

    MESSAGE_ID = 0x424A
    MESSAGE_NAME = "Cool Max Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1012Message(FloatMessage):
    """Parser for message 0x424B (FSV 1012 - Cool Min Water Temp)."""

    MESSAGE_ID = 0x424B
    MESSAGE_NAME = "Cool Min Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1021Message(FloatMessage):
    """Parser for message 0x424C (FSV 1021 - Cool Max Room Temp)."""

    MESSAGE_ID = 0x424C
    MESSAGE_NAME = "Cool Max Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1022Message(FloatMessage):
    """Parser for message 0x424D (FSV 1022 - Cool Min Room Temp)."""

    MESSAGE_ID = 0x424D
    MESSAGE_NAME = "Cool Min Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1031Message(FloatMessage):
    """Parser for message 0x424E (FSV 1031 - Heat Max Water Temp)."""

    MESSAGE_ID = 0x424E
    MESSAGE_NAME = "Heat Max Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1032Message(FloatMessage):
    """Parser for message 0x424F (FSV 1032 - Heat Min Water Temp)."""

    MESSAGE_ID = 0x424F
    MESSAGE_NAME = "Heat Min Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1041Message(FloatMessage):
    """Parser for message 0x4250 (FSV 1041 - Heat Max Room Temp)."""

    MESSAGE_ID = 0x4250
    MESSAGE_NAME = "Heat Max Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1042Message(FloatMessage):
    """Parser for message 0x4251 (FSV 1042 - Heat Min Room Temp)."""

    MESSAGE_ID = 0x4251
    MESSAGE_NAME = "Heat Min Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1051Message(FloatMessage):
    """Parser for message 0x4252 (FSV 1051 - DHW Max Temp)."""

    MESSAGE_ID = 0x4252
    MESSAGE_NAME = "DHW Max Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1052Message(FloatMessage):
    """Parser for message 0x4253 (FSV 1052 - DHW Min Temp)."""

    MESSAGE_ID = 0x4253
    MESSAGE_NAME = "DHW Min Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv3021(BasicTemperatureMessage):
    """Parser for message 0x4260 (FSV 3021 DHW Heating Mode Max)."""

    MESSAGE_ID = 0x4260
    MESSAGE_NAME = "FSV 3021 DHW Heating Mode Max"
    SIGNED = True


class InFsv3022(BasicTemperatureMessage):
    """Parser for message 0x4261 (FSV 3022)."""

    MESSAGE_ID = 0x4261
    MESSAGE_NAME = "FSV 3022"
    SIGNED = True


class InFsv3023(BasicTemperatureMessage):
    """Parser for message 0x4262 (FSV 3023 DHW Heat Pump Start)."""

    MESSAGE_ID = 0x4262
    MESSAGE_NAME = "FSV 3023 DHW Heat Pump Start"
    SIGNED = True


class InFsv3024(FloatMessage):
    """Parser for message 0x4263 (FSV 3024 DHW Min Operating Time)."""

    MESSAGE_ID = 0x4263
    MESSAGE_NAME = "FSV 3024 DHW Min Operating Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3025(FloatMessage):
    """Parser for message 0x4264 (FSV 3025 DHW Max Operating Time)."""

    MESSAGE_ID = 0x4264
    MESSAGE_NAME = "FSV 3025 DHW Max Operating Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3026(FloatMessage):
    """Parser for message 0x4265 (FSV 3026 DHW Operation Interval)."""

    MESSAGE_ID = 0x4265
    MESSAGE_NAME = "FSV 3026 DHW Operation Interval"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3032(FloatMessage):
    """Parser for message 0x4266 (FSV 3032 Booster Heater Delay Time)."""

    MESSAGE_ID = 0x4266
    MESSAGE_NAME = "FSV 3032 Booster Heater Delay Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3033(BasicTemperatureMessage):
    """Parser for message 0x4267 (FSV 3033 Booster Heater Overshoot)."""

    MESSAGE_ID = 0x4267
    MESSAGE_NAME = "FSV 3033 Booster Heater Overshoot"
    SIGNED = True


class InFsv3043(FloatMessage):
    """Parser for message 0x4269 (FSV 3043 Disinfection Start Time)."""

    MESSAGE_ID = 0x4269
    MESSAGE_NAME = "FSV 3043 Disinfection Start Time"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3044(BasicTemperatureMessage):
    """Parser for message 0x426A (FSV 3044 Disinfection Target Temp)."""

    MESSAGE_ID = 0x426A
    MESSAGE_NAME = "FSV 3044 Disinfection Target Temp"
    SIGNED = True


class InFsv3045(FloatMessage):
    """Parser for message 0x426B (FSV 3045 Disinfection Duration)."""

    MESSAGE_ID = 0x426B
    MESSAGE_NAME = "FSV 3045 Disinfection Duration"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv3052(FloatMessage):
    """Parser for message 0x426C (FSV 3052 Forced DHW Time Duration)."""

    MESSAGE_ID = 0x426C
    MESSAGE_NAME = "FSV 3052 Forced DHW Time Duration"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = True
    ARITHMETIC = 10.0


class InFsv5011Message(FloatMessage):
    """Parser for message 0x4273 (FSV 5011 - Outing Mode Cool Temp)."""

    MESSAGE_ID = 0x4273
    MESSAGE_NAME = "Outing Mode Cool Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5012Message(FloatMessage):
    """Parser for message 0x4274 (FSV 5012 - Outing Mode Room Cool Temp)."""

    MESSAGE_ID = 0x4274
    MESSAGE_NAME = "Outing Mode Room Cool Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5013Message(FloatMessage):
    """Parser for message 0x4275 (FSV 5013)."""

    MESSAGE_ID = 0x4275
    MESSAGE_NAME = "FSV 5013"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5014Message(FloatMessage):
    """Parser for message 0x4276 (FSV 5014 - Outing Mode Heat Temp)."""

    MESSAGE_ID = 0x4276
    MESSAGE_NAME = "Outing Mode Heat Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5015Message(FloatMessage):
    """Parser for message 0x4277 (FSV 5015)."""

    MESSAGE_ID = 0x4277
    MESSAGE_NAME = "FSV 5015"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5016Message(FloatMessage):
    """Parser for message 0x4278 (FSV 5016)."""

    MESSAGE_ID = 0x4278
    MESSAGE_NAME = "FSV 5016"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5017Message(FloatMessage):
    """Parser for message 0x4279 (FSV 5017)."""

    MESSAGE_ID = 0x4279
    MESSAGE_NAME = "FSV 5017"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5018Message(FloatMessage):
    """Parser for message 0x427A (FSV 5018 - Outing Mode WL2 Water Temp)."""

    MESSAGE_ID = 0x427A
    MESSAGE_NAME = "Outing Mode WL2 Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv5019Message(FloatMessage):
    """Parser for message 0x427B (FSV 5019)."""

    MESSAGE_ID = 0x427B
    MESSAGE_NAME = "FSV 5019"
    UNIT_OF_MEASUREMENT = "°C"


class InTempWaterLawMessage(BasicTemperatureMessage):
    """Parser for message 0x427F (Water Law Target Temperature)."""

    MESSAGE_ID = 0x427F
    MESSAGE_NAME = "Water Law Target Temperature"


class InTempMixingValveFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x428C (Mixing valve temperature)."""

    MESSAGE_ID = 0x428C
    MESSAGE_NAME = "InTempMixingValveFahrenheitMessage"


class InVariableUnknown428dMessage(RawMessage):
    """Parser for message 0x428D (Unknown variable)."""

    MESSAGE_ID = 0x428D
    MESSAGE_NAME = "InVariableUnknown428dMessage"


class InModulatingValve1Message(FloatMessage):
    """Parser for message 0x42CA (Modulating Valve 1)."""

    MESSAGE_ID = 0x42CA
    MESSAGE_NAME = "Modulating Valve 1"


class InModulatingValve2Message(FloatMessage):
    """Parser for message 0x42CB (Modulating Valve 2)."""

    MESSAGE_ID = 0x42CB
    MESSAGE_NAME = "Modulating Valve 2"


class InModulatingFanMessage(FloatMessage):
    """Parser for message 0x42CC (Modulating Fan)."""

    MESSAGE_ID = 0x42CC
    MESSAGE_NAME = "Modulating Fan"


class InWaterInletTemperature2Message(FloatMessage):
    """Parser for message 0x42CD (Water Inlet Temperature 2)."""

    MESSAGE_ID = 0x42CD
    MESSAGE_NAME = "Water Inlet Temperature 2"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv3046(FloatMessage):
    """Parser for message 0x42CE (FSV 3046 Disinfection Max Time)."""

    MESSAGE_ID = 0x42CE
    MESSAGE_NAME = "FSV 3046 Disinfection Max Time"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InEnthalpySensorOutputMessage(FloatMessage):
    """Parser for message 0x42CF (Enthalpy Sensor Output)."""

    MESSAGE_ID = 0x42CF
    MESSAGE_NAME = "Enthalpy Sensor Output"
    UNIT_OF_MEASUREMENT = "Enthalpy"
    SIGNED = False
    ARITHMETIC = 0.1


class InDustSensorPM10Value(FloatMessage):
    """Parser for message 0x42D1 (Dust Sensor PM10.0 Value).

    Represents the particulate matter (PM10.0) measurement from the dust sensor.
    Type: VAR (2 bytes, unsigned)
    Unit: μg/m³ (micrograms per cubic meter)

    Note: 0xFFFF (65535) typically indicates sensor not available or error.
    """

    MESSAGE_ID = 0x42D1
    MESSAGE_NAME = "Dust Sensor PM10.0 Value"
    UNIT_OF_MEASUREMENT = "μg/m³"
    SIGNED = False


class InDustSensorPM25Value(FloatMessage):
    """Parser for message 0x42D2 (Dust Sensor PM2.5 Value).

    Represents the fine particulate matter (PM2.5) measurement from the dust sensor.
    Type: VAR (2 bytes, unsigned)
    Unit: μg/m³ (micrograms per cubic meter)

    Note: 0xFFFF (65535) typically indicates sensor not available or error.
    """

    MESSAGE_ID = 0x42D2
    MESSAGE_NAME = "Dust Sensor PM2.5 Value"
    UNIT_OF_MEASUREMENT = "μg/m³"
    SIGNED = False


class InDustSensorPM1Value(FloatMessage):
    """Parser for message 0x42D3 (Dust Sensor PM1.0 Value).

    Represents the very fine particulate matter (PM1.0) measurement from the dust sensor.
    Type: VAR (2 bytes, unsigned)
    Unit: μg/m³ (micrograms per cubic meter)

    Note: 0xFFFF (65535) typically indicates sensor not available or error.
    """

    MESSAGE_ID = 0x42D3
    MESSAGE_NAME = "Dust Sensor PM1.0 Value"
    UNIT_OF_MEASUREMENT = "μg/m³"
    SIGNED = False


class InZone2RoomTemperatureFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x42D4 (Zone 2 Room Temperature Fahrenheit)."""

    MESSAGE_ID = 0x42D4
    MESSAGE_NAME = "Zone 2 Room Temperature Fahrenheit"


class InZone2TargetTempMessage(BasicTemperatureMessage):
    """Parser for message 0x42D6 (Zone 2 Target Temperature)."""

    MESSAGE_ID = 0x42D6
    MESSAGE_NAME = "Zone 2 Target Temperature"


class InZone2WaterOutletTargetTempMessage(BasicTemperatureMessage):
    """Parser for message 0x42D7 (Zone 2 Water Outlet Target Temperature)."""

    MESSAGE_ID = 0x42D7
    MESSAGE_NAME = "Zone 2 Water Outlet Target Temperature"


class InZone1WaterOutletTemperatureFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x42D8 (Zone 1 Water Outlet Temperature Fahrenheit)."""

    MESSAGE_ID = 0x42D8
    MESSAGE_NAME = "Zone 1 Water Outlet Temperature Fahrenheit"


class InZone2WaterOutletTemperatureFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x42D9 (Zone 2 Water Outlet Temperature Fahrenheit)."""

    MESSAGE_ID = 0x42D9
    MESSAGE_NAME = "Zone 2 Water Outlet Temperature Fahrenheit"


class InFlowSensorVoltageMessage(FloatMessage):
    """Parser for message 0x42E8 (Flow Sensor Voltage)."""

    MESSAGE_ID = 0x42E8
    MESSAGE_NAME = "Flow Sensor Voltage"
    UNIT_OF_MEASUREMENT = "V"
    SIGNED = False
    ARITHMETIC = 0.1


class InFlowSensorCalculationMessage(FloatMessage):
    """Parser for message 0x42E9 (Flow Sensor Calculation)."""

    MESSAGE_ID = 0x42E9
    MESSAGE_NAME = "Flow Sensor Calculation"
    SIGNED = False
    UNIT_OF_MEASUREMENT = "L/min"
    ARITHMETIC = 0.1


class InOutdoorCompressorFrequencyRateControlMessage(RawMessage):
    """Parser for message 0x42F1 (Outdoor Compressor Frequency Rate Control)."""

    MESSAGE_ID = 0x42F1
    MESSAGE_NAME = "Outdoor Compressor Frequency Rate Control"


class InVariableIndoorUnknownMessage(RawMessage):
    """Parser for message 0x4301 (Variable Indoor Unknown)."""

    MESSAGE_ID = 0x4301
    MESSAGE_NAME = "Variable Indoor Unknown"


class InCapacityVentilationRequestMessage(FloatMessage):
    """Parser for message 0x4302 (Capacity ventilation request)."""

    MESSAGE_ID = 0x4302
    MESSAGE_NAME = "Capacity Ventilation Request"
    UNIT = "kW"
    ARITHMETIC = 0.116279  # 1 / 8.6


class InVariableUnknown4303Message(RawMessage):
    """Parser for message 0x4303 (Unknown variable)."""

    MESSAGE_ID = 0x4303
    MESSAGE_NAME = "InVariableUnknown4303Message"


class InVariableUnknown4304Message(RawMessage):
    """Parser for message 0x4304 (Unknown variable)."""

    MESSAGE_ID = 0x4304
    MESSAGE_NAME = "InVariableUnknown4304Message"


class InVariableUnknown4305Message(RawMessage):
    """Parser for message 0x4305 (Unknown variable)."""

    MESSAGE_ID = 0x4305
    MESSAGE_NAME = "InVariableUnknown4305Message"


class InThermostatInputStatusMessage(RawMessage):
    """Parser for message 0x4306 (Thermostat input status)."""

    MESSAGE_ID = 0x4306
    MESSAGE_NAME = "Thermostat Input Status"


class InThermostatOutputStatusMessage(RawMessage):
    """Parser for message 0x4307 (Thermostat output status)."""

    MESSAGE_ID = 0x4307
    MESSAGE_NAME = "Thermostat Output Status"


class InTempDefrostTargetFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x4308 (Defrost target temperature)."""

    MESSAGE_ID = 0x4308
    MESSAGE_NAME = "Defrost Target Temperature"


class InTempDefrostFahrenheitMessage(BasicTemperatureMessage):
    """Parser for message 0x4309 (Defrost measured temperature)."""

    MESSAGE_ID = 0x4309
    MESSAGE_NAME = "Defrost Measured Temperature"


class InTempAlarmUpperMessage(BasicTemperatureMessage):
    """Parser for message 0x430A (Upper temperature alarm)."""

    MESSAGE_ID = 0x430A
    MESSAGE_NAME = "Upper Temperature Alarm"


class InTempAlarmLowerMessage(BasicTemperatureMessage):
    """Parser for message 0x430B (Lower temperature alarm)."""

    MESSAGE_ID = 0x430B
    MESSAGE_NAME = "Lower Temperature Alarm"


class InTempRoomAdjustMessage(BasicTemperatureMessage):
    """Parser for message 0x430C (Room temperature adjustment)."""

    MESSAGE_ID = 0x430C
    MESSAGE_NAME = "Room Temperature Adjustment"


class InDefrostSchedule1Message(RawMessage):
    """Parser for message 0x430D (Defrost schedule 1)."""

    MESSAGE_ID = 0x430D
    MESSAGE_NAME = "Defrost Schedule 1"


class InDefrostSchedule2Message(RawMessage):
    """Parser for message 0x430E (Defrost schedule 2)."""

    MESSAGE_ID = 0x430E
    MESSAGE_NAME = "Defrost Schedule 2"


class InDefrostSchedule3Message(RawMessage):
    """Parser for message 0x430F (Defrost schedule 3)."""

    MESSAGE_ID = 0x430F
    MESSAGE_NAME = "Defrost Schedule 3"


class InDefrostSchedule4Message(RawMessage):
    """Parser for message 0x4310 (Defrost schedule 4)."""

    MESSAGE_ID = 0x4310
    MESSAGE_NAME = "Defrost Schedule 4"


class InDefrostSchedule5Message(RawMessage):
    """Parser for message 0x4311 (Defrost schedule 5)."""

    MESSAGE_ID = 0x4311
    MESSAGE_NAME = "Defrost Schedule 5"


class InDefrostSchedule6Message(RawMessage):
    """Parser for message 0x4312 (Defrost schedule 6)."""

    MESSAGE_ID = 0x4312
    MESSAGE_NAME = "Defrost Schedule 6"


class InDefrostSchedule7Message(RawMessage):
    """Parser for message 0x4313 (Defrost schedule 7)."""

    MESSAGE_ID = 0x4313
    MESSAGE_NAME = "Defrost Schedule 7"


class InDefrostSchedule8Message(RawMessage):
    """Parser for message 0x4314 (Defrost schedule 8)."""

    MESSAGE_ID = 0x4314
    MESSAGE_NAME = "Defrost Schedule 8"


class InNightStartScheduleMessage(RawMessage):
    """Parser for message 0x4317 (Night time start schedule)."""

    MESSAGE_ID = 0x4317
    MESSAGE_NAME = "Night Time Start Schedule"


class InNightEndScheduleMessage(RawMessage):
    """Parser for message 0x4318 (Night time end schedule)."""

    MESSAGE_ID = 0x4318
    MESSAGE_NAME = "Night Time End Schedule"


class InCurrentTimeMessage(RawMessage):
    """Parser for message 0x4319 (Current time)."""

    MESSAGE_ID = 0x4319
    MESSAGE_NAME = "Current Time"


class InFsv1061Message(BasicTemperatureMessage):
    """Parser for message 0x431E (FSV 1061 - LWT hysteresis for heating)."""

    MESSAGE_ID = 0x431E
    MESSAGE_NAME = "FSV 1061 LWT Hysteresis Heating"


class InFsv1062Message(BasicTemperatureMessage):
    """Parser for message 0x431F (FSV 1062 - LWT hysteresis for cooling)."""

    MESSAGE_ID = 0x431F
    MESSAGE_NAME = "FSV 1062 LWT Hysteresis Cooling"


class InFsv1063Message(BasicTemperatureMessage):
    """Parser for message 0x4320 (FSV 1063 - Roomstat hysteresis for heating)."""

    MESSAGE_ID = 0x4320
    MESSAGE_NAME = "FSV 1063 Roomstat Hysteresis Heating"


class InFsv1064Message(BasicTemperatureMessage):
    """Parser for message 0x4321 (FSV 1064 - Roomstat hysteresis for cooling)."""

    MESSAGE_ID = 0x4321
    MESSAGE_NAME = "FSV 1064 Roomstat Hysteresis Cooling"


class InVariableUnknown4322Message(RawMessage):
    """Parser for message 0x4322 (Unknown variable)."""

    MESSAGE_ID = 0x4322
    MESSAGE_NAME = "InVariableUnknown4322Message"


class InVariableUnknown4323Message(RawMessage):
    """Parser for message 0x4323 (Unknown variable)."""

    MESSAGE_ID = 0x4323
    MESSAGE_NAME = "InVariableUnknown4323Message"


class InVariableUnknown4324Message(RawMessage):
    """Parser for message 0x4324 (Unknown variable)."""

    MESSAGE_ID = 0x4324
    MESSAGE_NAME = "InVariableUnknown4324Message"


class InVariableUnknown4325Message(RawMessage):
    """Parser for message 0x4325 (Unknown variable)."""

    MESSAGE_ID = 0x4325
    MESSAGE_NAME = "InVariableUnknown4325Message"


class InVariableUnknown4326Message(RawMessage):
    """Parser for message 0x4326 (Unknown variable)."""

    MESSAGE_ID = 0x4326
    MESSAGE_NAME = "InVariableUnknown4326Message"


class InVariableUnknown4327Message(RawMessage):
    """Parser for message 0x4327 (Unknown variable)."""

    MESSAGE_ID = 0x4327
    MESSAGE_NAME = "InVariableUnknown4327Message"


class InVariableUnknown4328Message(RawMessage):
    """Parser for message 0x4328 (Unknown variable)."""

    MESSAGE_ID = 0x4328
    MESSAGE_NAME = "InVariableUnknown4328Message"


class InLayerVariableIndoorUnknownMessage(RawMessage):
    """Parser for message 0x4401 (Layer Variable Indoor Unknown)."""

    MESSAGE_ID = 0x4401
    MESSAGE_NAME = "Layer Variable Indoor Unknown"


class InDeviceStatusMessage(RawMessage):
    """Parser for message 0x440A (Device Status - Heatpump/Boiler)."""

    MESSAGE_ID = 0x440A
    MESSAGE_NAME = "Device Status"


class InLayerVariableUnknown440bMessage(RawMessage):
    """Parser for message 0x440B (Unknown layer variable)."""

    MESSAGE_ID = 0x440B
    MESSAGE_NAME = "InLayerVariableUnknown440bMessage"


class InLayerVariableUnknown440cMessage(RawMessage):
    """Parser for message 0x440C (Unknown layer variable)."""

    MESSAGE_ID = 0x440C
    MESSAGE_NAME = "InLayerVariableUnknown440cMessage"


class InLayerVariableUnknown440dMessage(RawMessage):
    """Parser for message 0x440D (Unknown layer variable)."""

    MESSAGE_ID = 0x440D
    MESSAGE_NAME = "InLayerVariableUnknown440dMessage"


class InLayerVariableIndoorUnknown1Message(RawMessage):
    """Parser for message 0x440E (Layer Variable Indoor Unknown 1)."""

    MESSAGE_ID = 0x440E
    MESSAGE_NAME = "Layer Variable Indoor Unknown 1"


class InErrorInOutMessage(RawMessage):
    """Parser for message 0x440F (Error In Out)."""

    MESSAGE_ID = 0x440F
    MESSAGE_NAME = "Error In Out"


class InLayerVariableUnknown4410Message(RawMessage):
    """Parser for message 0x4410 (Unknown layer variable)."""

    MESSAGE_ID = 0x4410
    MESSAGE_NAME = "InLayerVariableUnknown4410Message"


class InLayerVariableUnknown4411Message(RawMessage):
    """Parser for message 0x4411 (Unknown layer variable)."""

    MESSAGE_ID = 0x4411
    MESSAGE_NAME = "InLayerVariableUnknown4411Message"


class InLayerVariableUnknown4412Message(RawMessage):
    """Parser for message 0x4412 (Unknown layer variable)."""

    MESSAGE_ID = 0x4412
    MESSAGE_NAME = "InLayerVariableUnknown4412Message"


class InLayerVariableUnknown4413Message(RawMessage):
    """Parser for message 0x4413 (Unknown layer variable)."""

    MESSAGE_ID = 0x4413
    MESSAGE_NAME = "InLayerVariableUnknown4413Message"


class InLayerVariableUnknown4414Message(RawMessage):
    """Parser for message 0x4414 (Unknown layer variable)."""

    MESSAGE_ID = 0x4414
    MESSAGE_NAME = "InLayerVariableUnknown4414Message"


class InLayerVariableUnknown4416Message(RawMessage):
    """Parser for message 0x4416 (Unknown layer variable)."""

    MESSAGE_ID = 0x4416
    MESSAGE_NAME = "InLayerVariableUnknown4416Message"


class InLayerVariableUnknown4417Message(RawMessage):
    """Parser for message 0x4417 (Unknown layer variable)."""

    MESSAGE_ID = 0x4417
    MESSAGE_NAME = "InLayerVariableUnknown4417Message"


class InLayerVariableUnknown4419Message(RawMessage):
    """Parser for message 0x4419 (Unknown layer variable)."""

    MESSAGE_ID = 0x4419
    MESSAGE_NAME = "InLayerVariableUnknown4419Message"


class InLayerVariableUnknown441aMessage(RawMessage):
    """Parser for message 0x441A (Unknown layer variable)."""

    MESSAGE_ID = 0x441A
    MESSAGE_NAME = "InLayerVariableUnknown441aMessage"


class InLayerVariableUnknown441cMessage(RawMessage):
    """Parser for message 0x441C (Unknown layer variable)."""

    MESSAGE_ID = 0x441C
    MESSAGE_NAME = "InLayerVariableUnknown441cMessage"


class InLayerVariableUnknown441dMessage(RawMessage):
    """Parser for message 0x441D (Unknown layer variable)."""

    MESSAGE_ID = 0x441D
    MESSAGE_NAME = "InLayerVariableUnknown441dMessage"


class InLayerVariableUnknown441eMessage(RawMessage):
    """Parser for message 0x441E (Unknown layer variable)."""

    MESSAGE_ID = 0x441E
    MESSAGE_NAME = "InLayerVariableUnknown441eMessage"


class InMinutesSinceInstallationMessage(FloatMessage):
    """Parser for message 0x4423 (Minutes Since Installation)."""

    MESSAGE_ID = 0x4423
    MESSAGE_NAME = "Minutes Since Installation"


class InMinutesActiveMessage(FloatMessage):
    """Parser for message 0x4424 (Minutes Active)."""

    MESSAGE_ID = 0x4424
    MESSAGE_NAME = "Minutes Active"


class InGeneratedPowerLastMinute(BasicPowerMessage):
    """Parser for message 0x4426 (Generated power last minute)."""

    MESSAGE_ID = 0x4426
    MESSAGE_NAME = "Generated Power Last Minute"
    SIGNED = False
    ARITHMETIC = 0.001


class TotalEnergyGenerated(BasicPowerMessage):
    """Parser for message 0x4427 (Total energy generated)."""

    MESSAGE_ID = 0x4427
    MESSAGE_NAME = "Total Energy Generated"
    SIGNED = False
    ARITHMETIC = 0.001
