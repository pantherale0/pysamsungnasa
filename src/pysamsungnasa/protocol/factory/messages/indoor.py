"""Messages from the indoor unit."""

from ..messaging import EnumMessage, BoolMessage

from ...enum import (
    InOperationMode,
    InOperationModeReal,
    InOperationVentMode,
    InFanModeReal,
    InFsv3042DayOfWeek,
    InOperationPower,
    ErvFanSpeed,
    InLouverHlPartSwing,
    DhwOpMode,
    InThermostatStatus,
    InBackupHeater,
    DhwReferenceTemp,
    In2WayValve,
    InFsv2041WaterLawTypeHeating,
    InFsv2081WaterLawTypeCooling,
    InUseThermostat,
    InFsv2093,
    InFsv2094,
    InFsv3011EnableDhw,
    InFsv3061UseDhwThermostat,
    InFsv3071,
    InFsv4011,
    InFsv4021,
    InFsv4022,
    InFsv4041,
    InFsv5022,
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


class InLouverHlPartSwingMessage(EnumMessage):
    """Parser for message 0x4012 (Indoor Louver HL Part Swing)."""

    MESSAGE_ID = 0x4012
    MESSAGE_NAME = "Indoor Louver HL Part Swing"
    MESSAGE_ENUM = InLouverHlPartSwing


class InStateThermo(BoolMessage):
    """Parser for message 0x4028 (Indoor Thermo State)."""

    MESSAGE_ID = 0x4028
    MESSAGE_NAME = "Indoor Thermo State"


class InDhwWaterHeaterPower(BoolMessage):
    """Parser for message 0x4029 (Indoor DHW Water Heater Power)."""

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
    MESSAGE_ENUM = InBackupHeater


class DhwReferenceTemperatureMessage(EnumMessage):
    """Parser for message 0x406F (Indoor DHW Reference Temperature)."""

    MESSAGE_ID = 0x406F
    MESSAGE_NAME = "Indoor DHW Reference Temperature"
    MESSAGE_ENUM = DhwReferenceTemp


class InRoomTempSensorMessage(BoolMessage):
    """Parser for message 0x4076 (Indoor Room Temperature Sensor)."""

    MESSAGE_ID = 0x4076
    MESSAGE_NAME = "Indoor Room Temperature Sensor"


class AirflowLeftRightMessage(BoolMessage):
    """Parser for message 0x407E (Indoor Airflow Swing)."""

    MESSAGE_ID = 0x407E
    MESSAGE_NAME = "Indoor Airflow Swing"


class In2WayValveMessage(EnumMessage):
    """Parser for message 0x408A (Indoor 2-Way Valve)."""

    MESSAGE_ID = 0x408A
    MESSAGE_NAME = "Indoor 2-Way Valve"
    MESSAGE_ENUM = In2WayValve


class InFsv2041WaterLawTypeHeating(EnumMessage):
    """Parser for message 0x4093 (FSV 2041 Water Law Type Heating)."""

    MESSAGE_ID = 0x4093
    MESSAGE_NAME = "FSV 2041 Water Law Type Heating"
    MESSAGE_ENUM = InFsv2041WaterLawTypeHeating


class InFsv2081WaterLawTypeCooling(EnumMessage):
    """Parser for message 0x4094 (FSV 2081 Water Law Type Cooling)."""

    MESSAGE_ID = 0x4094
    MESSAGE_NAME = "FSV 2081 Water Law Type Cooling"
    MESSAGE_ENUM = InFsv2081WaterLawTypeCooling


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
    MESSAGE_ENUM = InFsv3011EnableDhw


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
    MESSAGE_ENUM = InFsv3061UseDhwThermostat


class InFsv3071(EnumMessage):
    """Parser for message 0x409D (FSV 3071)."""

    MESSAGE_ID = 0x409D
    MESSAGE_NAME = "FSV 3071"
    MESSAGE_ENUM = InFsv3071


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
    MESSAGE_ENUM = InFsv2093


class InFsv5022(EnumMessage):
    """Parser for message 0x4128 (FSV 5022)."""

    MESSAGE_ID = 0x4128
    MESSAGE_NAME = "FSV 5022"
    MESSAGE_ENUM = InFsv5022


class InFsv2094(EnumMessage):
    """Parser for message 0x4129 (FSV 2094)."""

    MESSAGE_ID = 0x4129
    MESSAGE_NAME = "FSV 2094"
    MESSAGE_ENUM = InFsv2094


class InFsvLoadSaveAlt(BoolMessage):
    """Parser for message 0x412D (Indoor FSV Load Save Alternative)."""

    MESSAGE_ID = 0x412D
    MESSAGE_NAME = "Indoor FSV Load Save Alternative"
