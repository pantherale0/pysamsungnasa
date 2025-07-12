"""Messages from the indoor unit."""

from ..messaging import BoolMessage, EnumMessage, FloatMessage, BasicTemperatureMessage, BasicPowerMessage

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
    InFsv2094 as InFsv2094Enum,
    InFsv3011EnableDhw as InFsv3011EnableDhwEnum,
    InFsv3061UseDhwThermostat as InFsv3061UseDhwThermostatEnum,
    InFsv3071 as InFsv3071Enum,
    InFsv4011,
    InFsv4021,
    InFsv4022,
    InFsv4041,
    InFsv5022 as InFsv5022Enum,
)


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


class InOperationVentModeMessage(EnumMessage):
    """Parser for message 0x4005 (Indoor Operation Ventilation Mode)."""

    MESSAGE_ID = 0x4005
    MESSAGE_NAME = "Indoor Operation Ventilation Mode"
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


class InLouverHlSwing(BoolMessage):
    """Parser for message 0x4011 (Indoor Louver HL Swing)."""

    MESSAGE_ID = 0x4011
    MESSAGE_NAME = "Indoor Louver HL Swing"


class InLouverHlPartSwingMessage(EnumMessage):
    """Parser for message 0x4012 (Indoor Louver HL Part Swing)."""

    MESSAGE_ID = 0x4012
    MESSAGE_NAME = "Indoor Louver HL Part Swing"
    MESSAGE_ENUM = InLouverHlPartSwing


class InStateThermo(BoolMessage):
    """Parser for message 0x4028 (Indoor Thermo State)."""

    MESSAGE_ID = 0x4028
    MESSAGE_NAME = "Indoor Thermo State"


class InHumidity(FloatMessage):
    """Parser for message 0x4038 (Indoor Humidity)."""

    MESSAGE_ID = 0x4038
    MESSAGE_NAME = "Indoor Humidity"
    UNIT_OF_MEASUREMENT = "%"
    SIGNED = False
    ARITHMETIC = 1.0


class InAutomaticCleaning(BoolMessage):
    """Parser for message 0x4111 (Indoor Automatic Cleaning)."""

    MESSAGE_ID = 0x4111
    MESSAGE_NAME = "Indoor Automatic Cleaning"


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


class InThermostatZone1Status(EnumMessage):
    """Parser for message 0x4067 (Indoor Thermostat Zone 1 Status)."""

    MESSAGE_ID = 0x4069
    MESSAGE_NAME = "Indoor Thermostat Zone 1 Status"
    MESSAGE_ENUM = InThermostatStatus


class InThermostatZone2Status(EnumMessage):
    """Parser for message 0x4068 (Indoor Thermostat Zone 2 Status)."""

    MESSAGE_ID = 0x406A
    MESSAGE_NAME = "Indoor Thermostat Zone 2 Status"
    MESSAGE_ENUM = InThermostatStatus


class InBackupHeater(EnumMessage):
    """Parser for message 0x406C (Indoor Backup Heater Status)."""

    MESSAGE_ID = 0x406C
    MESSAGE_NAME = "Indoor Backup Heater"
    MESSAGE_ENUM = InBackupHeaterEnum


class DhwReferenceTemperatureMessage(EnumMessage):
    """Parser for message 0x406F (Indoor DHW Reference Temperature)."""

    MESSAGE_ID = 0x406F
    MESSAGE_NAME = "Indoor DHW Reference Temperature"
    MESSAGE_ENUM = DhwReferenceTemp


class InRoomTempSensorMessage(BoolMessage):
    """Parser for message 0x4076 (Indoor Room Temperature Sensor)."""

    MESSAGE_ID = 0x4076
    MESSAGE_NAME = "Indoor Room Temperature Sensor"


class InLouverLrSwing(BoolMessage):
    """Parser for message 0x407E (Indoor Louver LR Swing)."""

    MESSAGE_ID = 0x407E
    MESSAGE_NAME = "Indoor Louver LR Swing"


class In2WayValveMessage(EnumMessage):
    """Parser for message 0x408A (Indoor 2-Way Valve)."""

    MESSAGE_ID = 0x408A
    MESSAGE_NAME = "Indoor 2-Way Valve"
    MESSAGE_ENUM = In2WayValve


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


class VacancyStatus(BoolMessage):
    """Parser for message 0x40BC (Indoor Vacancy Status)."""

    MESSAGE_ID = 0x40BC
    MESSAGE_NAME = "Indoor Vacancy Status"


class InErrorHistoryClearMessage(BoolMessage):
    """Parser for message 0x40D6 (Indoor Error History Clear)."""

    MESSAGE_ID = 0x40D6
    MESSAGE_NAME = "Indoor Error History Clear"


class InChillerExtWaterOutInput(BoolMessage):
    """Parser for message 0x4101 (Indoor Chiller External Water Out Input)."""

    MESSAGE_ID = 0x4101
    MESSAGE_NAME = "Indoor Chiller External Water Out Input"


class InStateFlowCheck(BoolMessage):
    """Parser for message 0x4102 (Indoor Flow Check State)."""

    MESSAGE_ID = 0x4102
    MESSAGE_NAME = "Indoor Flow Check State"


class InPvContactState(BoolMessage):
    """Parser for message 0x4123 (Indoor PV Contact State)."""

    # 0x4102 NASA_IN_STATE_FLOW_CHECK or ENUM_IN_STATE_FLOW_CHECK. OFF/OK=0, ON/FAIL=1
    MESSAGE_ID = 0x4123
    MESSAGE_NAME = "Indoor PV Contact State"


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


class InFsv2094(EnumMessage):
    """Parser for message 0x4129 (FSV 2094)."""

    MESSAGE_ID = 0x4129
    MESSAGE_NAME = "FSV 2094"
    MESSAGE_ENUM = InFsv2094Enum


class InFsvLoadSaveAlt(BoolMessage):
    """Parser for message 0x412D (Indoor FSV Load Save Alternative)."""

    MESSAGE_ID = 0x412D
    MESSAGE_NAME = "Indoor FSV Load Save Alternative"


class InGeneratedPowerLastMinute(BasicPowerMessage):
    """Parser for message 0x4426 (Generated power last minute)."""

    MESSAGE_ID = 0x4426
    MESSAGE_NAME = "Generated Power Last Minute"
    SIGNED = False
    ARITHMETIC = 0.001


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


class InFsv3025(FloatMessage):
    """Parser for message 0x4264 (FSV 3025 DHW Max Operating Time)."""

    MESSAGE_ID = 0x4264
    MESSAGE_NAME = "FSV 3025 DHW Max Operating Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3024(FloatMessage):
    """Parser for message 0x4263 (FSV 3024 DHW Min Operating Time)."""

    MESSAGE_ID = 0x4263
    MESSAGE_NAME = "FSV 3024 DHW Min Operating Time"
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


class InFsv3046(FloatMessage):
    """Parser for message 0x42CE (FSV 3046 Disinfection Max Time)."""

    MESSAGE_ID = 0x42CE
    MESSAGE_NAME = "FSV 3046 Disinfection Max Time"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3052(FloatMessage):
    """Parser for message 0x426C (FSV 3052 Forced DHW Time Duration)."""

    MESSAGE_ID = 0x426C
    MESSAGE_NAME = "FSV 3052 Forced DHW Time Duration"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = True
    ARITHMETIC = 10.0


class InTargetTemperature(BasicTemperatureMessage):
    """Parser for message 0x4201 (Indoor Target Temperature)."""

    MESSAGE_ID = 0x4201
    MESSAGE_NAME = "Indoor Target Temperature"
    SIGNED = True


class InRoomTemperature(BasicTemperatureMessage):
    """Parser for message 0x4203 (Indoor Room Temperature)."""

    MESSAGE_ID = 0x4203
    MESSAGE_NAME = "Indoor Room Temperature"
    SIGNED = True


class InTempEvaIn(BasicTemperatureMessage):
    """Parser for 0x4205 (Indoor Temp Eva In)."""

    MESSAGE_ID = 0x4205
    MESSAGE_NAME = "Indoor Temp Eva In"


class InTempEvaOut(BasicTemperatureMessage):
    """Parser for 0x4206 (Indoor Temp Eva Out)."""

    MESSAGE_ID = 0x4206
    MESSAGE_NAME = "Indoor Temp Eva Out"


class DhwTargetTemperature(BasicTemperatureMessage):
    """Parser for 0x4235 (Indoor DHW Target Temperature)."""

    MESSAGE_ID = 0x4235
    MESSAGE_NAME = "Indoor DHW Target Temperature"
    SIGNED = True


class DhwCurrentTemperature(BasicTemperatureMessage):
    """Parser for 0x4237 (Indoor DHW Current Temperature)."""

    MESSAGE_ID = 0x4237
    MESSAGE_NAME = "Indoor DHW Current Temperature"


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


class IndoorFlowTemperature(BasicTemperatureMessage):
    """Parser for 0x4238 (Indoor Flow Temperature)."""

    MESSAGE_ID = 0x4238
    MESSAGE_NAME = "Indoor Flow Temperature"
