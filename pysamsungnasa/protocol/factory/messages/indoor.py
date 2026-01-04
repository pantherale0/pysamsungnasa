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
    InFsv4011 as InFsv4011Enum,
    InFsv4021 as InFsv4021Enum,
    InFsv4022 as InFsv4022Enum,
    InFsv4041 as InFsv4041Enum,
    InFsv4051 as InFsv4051Enum,
    InFsv4061 as InFsv4061Enum,
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
    InDischargeTempControl,
    InLouverHlAuto,
    InLouverHlAutoUpDown,
    InWallMountedRemoteControl,
    InFsv302LouverControl,
    InFsv302LouverValue,
    InFsv302TimeSchedule,
    InModelInformation,
    InAutoStaticPressure,
    InChillerWaterlawSensor,
    InChillerWaterlaw,
    InChillerSettingSilentLevel,
    InChillerSettingDemandLevel,
    InTdmIndoorType,
    InWaterValve,
    InEnthalpyControl,
    InFreeCooling,
    InGasLevel,
    InFsv5094,
    In3WayValve,
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


class InOutingModeMessage(BoolMessage):
    """Parser for message 0x406D (Indoor Outing Mode)."""

    MESSAGE_ID = 0x406D
    MESSAGE_NAME = "Indoor Outing Mode"


class InQuietModeMessage(BoolMessage):
    """Parser for message 0x406E (Indoor Quiet Mode)."""

    MESSAGE_ID = 0x406E
    MESSAGE_NAME = "Indoor Quiet Mode"


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
    """Parser for message 0x4093 (FSV 2041 Water Law Type Heating).

    Selects water law control type for heating based on heating device type.
    Default: 1 (Floor/UFH), Range: 1-2

    1 = WL1 for floor heating (UFHs)
    2 = WL2 for fan coil units (FCUs) or radiators
    """

    MESSAGE_ID = 0x4093
    MESSAGE_NAME = "FSV 2041 Water Law Type Heating"
    MESSAGE_ENUM = InFsv2041WaterLawTypeHeatingEnum


class InFsv2081WaterLawTypeCooling(EnumMessage):
    """Parser for message 0x4094 (FSV 2081 Water Law Type Cooling).

    Selects water law control type for cooling based on cooling device type.
    Default: 1 (Floor/UFH), Range: 1-2

    1 = WL1 for floor cooling (UFHs)
    2 = WL2 for fan coil units (FCUs) or radiators
    """

    MESSAGE_ID = 0x4094
    MESSAGE_NAME = "FSV 2081 Water Law Type Cooling"
    MESSAGE_ENUM = InFsv2081WaterLawTypeCoolingEnum


class InFsv2091UseThermostat1(EnumMessage):
    """Parser for message 0x4095 (FSV 2091 Use Thermostat 1).

    External room thermostat control for UFHs (floor heating/cooling).
    Default: 0 (No thermostat), Range: 0-4

    0 = Disable (use wired remote controller)
    1 = Thermostat only controls compressor on/off
    2-4 = Thermostat controls compressor + water pump based on WL mode
    """

    MESSAGE_ID = 0x4095
    MESSAGE_NAME = "FSV 2091 Use Thermostat 1"
    MESSAGE_ENUM = InUseThermostat


class InFsv2092UseThermostat2(EnumMessage):
    """Parser for message 0x4096 (FSV 2092 Use Thermostat 2).

    External room thermostat control for FCUs (fan coil units).
    Default: 0 (No thermostat), Range: 0-4

    0 = Disable (use wired remote controller)
    1 = Thermostat only controls compressor on/off
    2 = Thermostat controls compressor + water pump off when disabled
    3 = Thermostat controls compressor + water pump stays on when disabled
    4 = Thermostat controls compressor + water pump cycles (7min off, 3min on)
    """

    MESSAGE_ID = 0x4096
    MESSAGE_NAME = "FSV 2092 Use Thermostat 2"
    MESSAGE_ENUM = InUseThermostat


class InFsv3011EnableDhw(EnumMessage):
    """Parser for message 0x4097 (FSV 3011 Enable DHW).

    Enables DHW (Domestic Hot Water) operation with different control modes.
    Default: 1 (Yes), Range: 0-2

    0 = Disable DHW
    1 = DHW starts at thermo on temperature, stops at thermo off temperature
    2 = DHW starts immediately, stops based on thermo off temperature

    When set to 1: DHW only operates when tank temperature <= thermo on (THP ON)
    When set to 2: DHW operates on demand regardless of thermo on setting
    """

    MESSAGE_ID = 0x4097
    MESSAGE_NAME = "FSV 3011 Enable DHW"
    MESSAGE_ENUM = InFsv3011EnableDhwEnum


class InFsv3031(BoolMessage):
    """Parser for message 0x4098 (FSV 3031 - Enable Booster Heater).

    Enable booster heater as additional heat source for DHW tank.
    Default: 1 (On), Range: 0-1

    0 = Disable booster heater
    1 = Enable booster heater for DHW tank heating

    Booster heater activates when target temperature exceeds heat pump maximum (THP MAX).
    Operates with configurable delay (FSV #3032) from heat pump startup.
    """

    MESSAGE_ID = 0x4098
    MESSAGE_NAME = "NASA_USE_BOOSTER_HEATER"


class InFsv3041(BoolMessage):
    """Parser for message 0x4099 (FSV 3041 - Enable Disinfection).

    Enable periodic disinfection heating of DHW tank.
    Default: 1 (On), Range: 0-1

    0 = Disable periodic disinfection
    1 = Enable periodic disinfection cycle

    When enabled, tank is automatically heated to target temperature (FSV #3044)
    on specified interval (FSV #3042) at configured time (FSV #3043).
    """

    MESSAGE_ID = 0x4099
    MESSAGE_NAME = "FSV 3041"


class InFsv3042(EnumMessage):
    """Parser for message 0x409A (FSV 3042 - Disinfection Interval Day).

    Day of week for periodic disinfection heating cycle.
    Default: 5 (Friday), Range: 0-7

    0 = Sunday
    1 = Monday
    2 = Tuesday
    3 = Wednesday
    4 = Thursday
    5 = Friday
    6 = Saturday
    7 = All days (daily)

    Disinfection runs on selected day at time specified in FSV #3043.
    """

    MESSAGE_ID = 0x409A
    MESSAGE_NAME = "FSV Day of Week"
    MESSAGE_ENUM = InFsv3042DayOfWeek


class InFsv3051(BoolMessage):
    """Parser for message 0x409B (FSV 3051 - Forced DHW Timer Function).

    Enable/disable timer-based forced DHW operation.
    Default: 0 (No), Range: 0-1

    0 = Disable forced DHW timer
    1 = Enable forced DHW with duration specified in FSV #3052

    When enabled, DHW operates for the set duration independent of tank temperature.
    """

    MESSAGE_ID = 0x409B
    MESSAGE_NAME = "FSV 3051"


class InFsv3061UseDhwThermostat(EnumMessage):
    """Parser for message 0x409C (FSV 3061 - DHW Thermostat Control).

    External room thermostat control for DHW operation.
    Default: 0 (No), Range: 0-2

    0 = Disable thermostat (use wired remote controller)
    1 = Thermostat only (not supported in typical installations)
    2 = Combined thermostat and water law control

    Note: Solar panel application (FSV #3061 = 1) not supported - requires secondary coil.
    """

    MESSAGE_ID = 0x409C
    MESSAGE_NAME = "FSV 3061 Use DHW Thermostat"
    MESSAGE_ENUM = InFsv3061UseDhwThermostatEnum


class InFsv3071(EnumMessage):
    """Parser for message 0x409D (FSV 3071 - 3-Way Valve Direction).

    Default water flow direction for 3-way diverter valve.
    Default: 0 (Room), Range: 0-1

    0 = Room/Space heating (water flows to heating)
    1 = Tank/DHW (water flows to DHW tank)

    Determines which circuit receives water flow when valve is in neutral position.
    """

    MESSAGE_ID = 0x409D
    MESSAGE_NAME = "FSV 3071"
    MESSAGE_ENUM = InFsv3071Enum


class InFsv4011(EnumMessage):
    """Parser for message 0x409E (FSV 4011 - Heat/DHW Priority).

    Priority mode selection for simultaneous heating and DHW demands.
    Default: 0 (DHW), Range: 0-1

    When both space heating and DHW heating are required at the same time:
    - 0 (DHW): DHW takes priority, space heating delayed by mode timer (FSV #3025)
    - 1 (Heating): Space heating takes priority, but only when outdoor temperature
      is lower than the threshold temperature specified by FSV #4012
    """

    MESSAGE_ID = 0x409E
    MESSAGE_NAME = "FSV 4011 Heat/DHW Priority"
    MESSAGE_ENUM = InFsv4011Enum


class InFsv4021(EnumMessage):
    """Parser for message 0x409F (FSV 4021 - Backup Heater Application).

    Enables electric backup heater for space heating support.
    Default: 0 (No), Range: 0-2

    Modes:
    - 0 (No): Backup heater disabled
    - 1 (BUH 1+2): Two-step backup heater (BUH 1 + BUH 2) for total capacity
    - 2 (BUH 1 only): Single-step backup heater (BUH 1) only

    Backup heater provides supplementary heating below threshold temperature
    (FSV #4024) or during defrost mode (FSV #4025).
    """

    MESSAGE_ID = 0x409F
    MESSAGE_NAME = "FSV 4021 Backup Heater Application"
    MESSAGE_ENUM = InFsv4021Enum


class InFsv4022(EnumMessage):
    """Parser for message 0x40A0 (FSV 4022 - BUH/BSH Priority).

    Priority selection between Booster Heater (BSH) and Backup Heater (BUH).
    Default: 2 (BSH), Range: 0-2

    Modes:
    - 0 (Both): Both heaters can operate simultaneously
    - 1 (BUH): Backup heater has priority, booster heater idle until BUH offline
    - 2 (BSH): Booster heater has priority (default), backup heater only when BSH is unavailable

    When BSH has priority: DHW uses booster first, backup heater assists or provides
    alternative when booster demand is low.
    """

    MESSAGE_ID = 0x40A0
    MESSAGE_NAME = "FSV 4022 BUH/BSH Priority"
    MESSAGE_ENUM = InFsv4022Enum


class InFsv4023(BoolMessage):
    """Parser for message 0x40A1 (FSV 4023 - Cold Weather Compensation).

    Enables backup heater operation to compensate for reduced heat pump efficiency.
    Default: 1 (Yes), Range: 0-1

    Modes:
    - 0 (No): Backup heater does not operate for cold weather compensation
    - 1 (Yes): Backup heater activates below threshold (FSV #4024) to maintain
      space heating capacity when outdoor temperature is very cold

    Automatic mode: Backup heater assists heat pump when outdoor temperature
    drops and heat pump capacity becomes insufficient.
    """

    MESSAGE_ID = 0x40A1
    MESSAGE_NAME = "FSV 4023 Cold Weather Compensation"


class InFsv4031(BoolMessage):
    """Parser for message 0x40A2 (FSV 4031 - External Boiler Application).

    Enables external backup boiler for space heating support.
    Default: 0 (No), Range: 0-1

    Modes:
    - 0 (No): External boiler disabled
    - 1 (Yes): External boiler enabled as backup heat source below threshold temperature

    When enabled, boiler operates independently below FSV #4033 threshold, providing
    alternative heating when heat pump is offline. Boiler requires autonomous operation
    of its own zone and pump control systems during backup mode.
    """

    MESSAGE_ID = 0x40A2
    MESSAGE_NAME = "FSV 4031 Backup Boiler Application"


class InFsv4032(BoolMessage):
    """Parser for message 0x40A3 (FSV 4032 - Boiler Priority).

    Prioritizes backup boiler over heat pump for space heating.
    Default: 0 (No), Range: 0-1

    Modes:
    - 0 (No): Heat pump priority (default), boiler is backup only
    - 1 (Yes): Boiler priority, boiler operates first below threshold, heat pump idles

    When boiler has priority: External boiler system controls space heating below
    FSV #4033 threshold temperature. Heat pump becomes backup/supplementary source.
    """

    MESSAGE_ID = 0x40A3
    MESSAGE_NAME = "FSV 4032 Boiler Priority"


class InFsv5041(BoolMessage):
    """Parser for message 0x40A4 (FSV 5041 - Power Peak Control Application).

    Enables Power Peak Control function for demand limiting via external input signal.
    Default: 0 (No), Range: 0-1

    Modes:
    - 0 (No): Power Peak Control disabled
    - 1 (Yes): Power Peak Control enabled

    When enabled, accepts external signal (input contact) from power company to reduce
    system load during power surges. System enters forced off mode (Thermo off) for
    selected components (FSV #5042) when signal is received. Signal type determined
    by FSV #5043 (High/Low). Typical power company demand limit functionality.
    """

    MESSAGE_ID = 0x40A4
    MESSAGE_NAME = "FSV 5041 Power Peak Control Application"


class InFsv5042(IntegerMessage):
    """Parser for message 0x40A5 (FSV 5042 - Select Forced Off Parts).

    Selects which system components are forced off during Power Peak Control.
    Default: 0 (All off), Range: 0-3

    When external power limit signal is received (FSV #5041 = 1):
    - 0 (All): Booster heater OFF, Backup heater OFF, Compressor ON
    - 1 (Booster): Booster heater OFF, Backup heater OFF, Compressor ON
    - 2 (Backup): Backup heater OFF, Booster heater ON, Compressor ON
    - 3 (All): Booster heater OFF, Backup heater OFF, Compressor OFF

    Allows flexible load shedding during power surges from utility grid.
    """

    MESSAGE_ID = 0x40A5
    MESSAGE_NAME = "FSV 5042 Power Peak Control Forced Off Parts"


class InFsv5043(BoolMessage):
    """Parser for message 0x40A6 (FSV 5043 - Using Input Voltage).

    Selects input signal type for Power Peak Control.
    Default: 1 (High), Range: 0-1

    Modes:
    - 0 (Low): Low input signal (voltage not applied triggers forced off)
    - 1 (High): High input signal (voltage applied triggers forced off)

    When signal matches configured level, system enters forced off mode according to FSV #5042.
    Adapts to different power company signaling requirements.
    """

    MESSAGE_ID = 0x40A6
    MESSAGE_NAME = "FSV 5043 Power Peak Control Input Voltage Type"


class InFsv5051(BoolMessage):
    """Parser for message 0x40A7 (FSV 5051 - Frequency Ratio Control).

    Enables external compressor frequency control for demand limiting.
    Default: 0 (Disable), Range: 0-1

    Modes:
    - 0 (Disable): Frequency ratio control disabled
    - 1 (Use): Frequency ratio control enabled

    When enabled, accepts external DC signal (0-10V) or Modbus communication to limit
    compressor frequency between 50-150% of normal operation. Prevents grid overload
    during peak demand periods. Maps DC voltage to frequency ratio:
    0V=50%, 5V=100%, 10V=150% with intermediate 10% steps.
    """

    MESSAGE_ID = 0x40A7
    MESSAGE_NAME = "FSV 5051 Frequency Ratio Control"


class InFsv5061Message(EnumMessage):
    """Parser for message 0x40B4 (FSV 5061 - CH/DHW Supply Ratio).

    Controls the heat supply ratio between space heating (CH) and domestic hot water (DHW).
    Default: 4 (1:1 balanced ratio), Range: 1-7

    Determines energy distribution when both CH (space heating) and DHW demands exist
    simultaneously. The heat pump prioritizes one system over the other based on this ratio.

    Ratio meanings:
    - Value 1: Maximum DHW priority (1 part CH, 7 parts DHW)
    - Value 2: 2/5 CH, 5/7 DHW
    - Value 3: 3/7 CH, 4/7 DHW
    - Value 4: Balanced 4/7 CH, 3/7 DHW (default, slightly CH-favoring)
    - Value 5: 5/7 CH, 2/7 DHW
    - Value 6: 6/7 CH, 1/7 DHW
    - Value 7: Maximum CH priority (7 parts CH, 0 parts DHW)

    Practical usage: For homes with radiant heating, higher ratios (5-7) ensure room
    comfort. For homes relying on DHW for comfort and heating, lower ratios (1-3) ensure
    hot water availability. Balanced ratio (4) suits general applications.

    Note: Different from FSV #5033 (TDM priority), which determines timing in sequential
    operation. FSV #5061 controls energy split when simultaneous operation occurs.

    Related: FSV #5033 (TDM priority for sequential operation).
    """

    MESSAGE_ID = 0x40B4
    MESSAGE_NAME = "CH/DHW Supply Ratio"
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


class InVacancyControlMessage(BoolMessage):
    """Parser for message 0x40BD (Vacancy control).

    Enables/disables vacancy detection and energy-saving operation mode.
    Default: 0 (Disabled), Range: 0-1
    """

    MESSAGE_ID = 0x40BD
    MESSAGE_NAME = "Vacancy control"


class InFsv4041(EnumMessage):
    """Parser for message 0x40C0 (FSV 4041 - Mixing Valve Application).

    Enables and selects control mode for mixing valve installation.
    Default: 0 (No), Range: 0-2

    Modes:
    - 0 (No): Mixing valve disabled/not installed
    - 1 (ΔT control): Valve modulates based on temperature difference target (FSV #4042, #4043)
    - 2 (WL control): Valve modulates based on Water Law (WL) value from control system

    Mixing valve reduces excessive heat pump outlet temperature by blending hot
    water with return circuit water. Improves floor heating comfort and reduces energy.
    """

    MESSAGE_ID = 0x40C0
    MESSAGE_NAME = "FSV 4041 Mixing Valve Application"
    MESSAGE_ENUM = InFsv4041Enum


class InFsv4044(IntegerMessage):
    """Parser for message 0x40C1 (FSV 4044 - Control Factor).

    Mixing valve response speed/aggressiveness to temperature error.
    Default: 2, Range: 1-5

    Control factor determines how quickly valve responds to deviations from
    target temperature difference (FSV #4042, #4043):
    - 1 (Slow): Gentle, gradual response (lowest energy waste)
    - 2-3 (Medium): Balanced response
    - 4-5 (Fast): Quick, aggressive response (may cause temperature fluctuation)

    Increase factor for faster control, but risk overshooting and discomfort.
    """

    MESSAGE_ID = 0x40C1
    MESSAGE_NAME = "FSV 4044 Mixing Valve Control Factor"


class InFsv4051(EnumMessage):
    """Parser for message 0x40C2 (FSV 4051 - Inverter Pump Application).

    Enables variable-speed inverter pump and sets maximum PWM output level.
    Default: 1 (Yes/100%), Range: 0-2

    Modes:
    - 0 (No): Inverter pump disabled, fixed-speed pump operation
    - 1 (Yes/100%): Inverter pump enabled, full PWM output (0-100%)
    - 2 (Yes/70%): Inverter pump enabled, limited PWM output (0-70% max)

    Inverter pump reduces energy consumption by modulating flow based on demand.
    70% mode reduces max pump speed for systems with oversized circulation capacity.
    """

    MESSAGE_ID = 0x40C2
    MESSAGE_NAME = "FSV 4051 Inverter Pump Application"
    MESSAGE_ENUM = InFsv4051Enum


class InFsv4053(IntegerMessage):
    """Parser for message 0x40C3 (FSV 4053 - Control Factor).

    Inverter pump response speed to temperature difference error.
    Default: 2, Range: 1-3

    Control factor determines how quickly pump speed adjusts when actual
    temperature difference deviates from target (FSV #4052):
    - 1 (Slow): Gradual speed adjustment, stable flow
    - 2 (Medium): Balanced response (default)
    - 3 (Fast): Quick speed adjustment, responsive to load changes

    Higher factor = faster response but more pump speed variations/noise.
    """

    MESSAGE_ID = 0x40C3
    MESSAGE_NAME = "FSV 4053 Inverter Pump Control Factor"


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


class InEnterRoomControlMessage(BoolMessage):
    """Parser for message 0x40D5 (Enable room entry control option).

    Enables/disables room entry control functionality.
    Default: 0 (Disabled), Range: 0-1
    """

    MESSAGE_ID = 0x40D5
    MESSAGE_NAME = "Enable room entry control option"


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
    """Parser for message 0x4107 (FSV 5033 - TDM Priority A2A vs DHW).

    Priority control when both air-to-air and DHW heating compete for capacity.
    Default: 0 (A2A priority), Range: 0-1

    TDM (Time Division Mode) switches between different operating modes to serve multiple
    heating zones. When a system has both space heating (CH = Central Heating) and hot water
    demands simultaneously, this FSV determines which system gets priority time.

    - Value 0 (A2A Priority): Space heating via indoor unit heat exchanger prioritized
    - Value 1 (DHW Priority): Domestic hot water tank heating prioritized

    Selection depends on user comfort needs: Active heating zones require more continuous
    operation than DHW, which can tolerate periodic heating. In systems with passive
    radiators, DHW priority works well. In systems with active A2A zones, A2A priority
    is more comfortable for occupants.

    Related: FSV #5061 (CH/DHW supply ratio for systems with simultaneous operation).
    """

    MESSAGE_ID = 0x4107
    MESSAGE_NAME = "TDM Priority (A2A vs DHW)"
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


class InZone1PowerMessage(BoolMessage):
    """Parser for message 0x4119 (Zone 1 operating power)."""

    MESSAGE_ID = 0x4119
    MESSAGE_NAME = "Zone 1 operating power"


class InFsv4061Message(EnumMessage):
    """Parser for message 0x411A (FSV 4061 - Zone Control Application).

    Enables two-zone heating/cooling control via wired remote controller.
    Default: 0 (No), Range: 0-1

    Modes:
    - 0 (No): Single-zone operation (zone control disabled)
    - 1 (Yes): Two-zone control enabled via wired remote controller as room sensor

    When enabled, the MWR-WW10** wired remote controller acts as zone 1 room sensor,
    allowing separate temperature control for Zone 1 and Zone 2. Requires disabling
    external thermostat control (FSV #2091 and #2092 = 0) to avoid conflicts.

    NOTE: Model MIM-E03EN supports this function. MIM-E03CN does not.
    When connecting to upper-level controllers, disable zone control to avoid conflicts.
    """

    MESSAGE_ID = 0x411A
    MESSAGE_NAME = "FSV 4061 Zone Control Application"
    MESSAGE_ENUM = InFsv4061Enum


class InFsv5081Message(BoolMessage):
    """Parser for message 0x411B (FSV 5081 - PV Control Application).

    Enables/disables automatic optimization for photovoltaic (solar) energy usage.
    Default: 0 (Disabled), Range: 0-1

    PV Control automatically adjusts heating and cooling setpoints based on solar
    generation to maximize use of free solar energy and reduce grid consumption.

    - Value 0: PV control disabled; system operates normally
    - Value 1: PV control enabled; system adjusts setpoints based on PV generation signal

    When enabled:
    - During high PV generation (cooling needed): System reduces cooling setpoints
      (increases room/water temps) by FSV #5082, reducing cooling capacity needed

    - During high PV generation (heating needed): System increases heating setpoints
      (increases room/water temps) by FSV #5083, shifting heat pump load to sunny periods

    External signal source: Modbus, M-Bus, or on/off relay from PV inverter/monitoring system.
    Signal indicates available solar surplus that can be utilized immediately.

    Energy-saving benefit: Typically 5-10% additional efficiency by shifting electric
    loads toward high-sun periods. Combines with FSV #5091 (Smart Grid) for comprehensive
    demand-side management and renewable integration.

    Related: FSV #5082 (cooling temp shift), FSV #5083 (heating temp shift),
            FSV #5091 (smart grid control).
    """

    MESSAGE_ID = 0x411B
    MESSAGE_NAME = "PV Control Application"


class InFsv5091Message(BoolMessage):
    """Parser for message 0x411C (FSV 5091 - Smart Grid Control Application).

    Enables/disables Smart Grid coordination functionality.
    Default: 0 (Disabled), Range: 0-1

    Smart Grid Control allows the heat pump system to participate in demand response and
    grid stability programs. External signals from utility grids or aggregators instruct
    the system to adjust heating/cooling operation to balance grid load.

    - Value 0: Smart Grid disabled; system operates independently based on user setpoints
    - Value 1: Smart Grid enabled; system receives external control signals

    When enabled, the system can:
    - Reduce heating/DHW capacity during peak demand (load shedding)
    - Increase heating/DHW during off-peak hours (load shifting)
    - Participate in frequency regulation by adjusting compressor speed
    - Support renewable energy integration by shifting loads to high-wind/solar periods

    Control signal format: Via Modbus, M-Bus, or on/off relay depending on system type.
    Response modes set by FSV #5092 (heat temp adjustment) and FSV #5093 (DHW adjustment).

    Energy-saving potential: Users allowing grid control typically reduce peak-time energy
    costs by automatically consuming more during low-cost off-peak periods. Combines with
    FSV #5082/5083 (PV control) and FSV #5022 (DHW Saving) for maximum flexibility.

    Related: FSV #5092 (smart grid heat response), FSV #5093 (smart grid DHW response),
            FSV #5094 (smart grid DHW mode).
    """

    MESSAGE_ID = 0x411C
    MESSAGE_NAME = "Smart Grid Control Application"


class InFsv5094Message(EnumMessage):
    """Parser for message 0x411D (FSV 5094 - Smart Grid DHW Mode).

    Controls DHW behavior when Smart Grid signals demand reduction.
    Default: 0 (Maintain comfort), Range: 0-1

    When the utility grid requests load shedding via Smart Grid Control (FSV #5091),
    this parameter determines how the system manages domestic hot water during the event.

    - Value 0: Comfort mode; DHW heating continues normally despite grid signal
      System maintains target tank temperature, may defer space heating instead
      Users always have hot water available, maximum comfort

    - Value 1: Demand response mode; DHW heating stops/reduces when grid signal active
      System prioritizes grid participation over DHW comfort
      Reduces peak demand more aggressively for better load management
      Risk: Tank may cool below comfort temperature; users may face cold water

    Typical usage:
    - Comfort-focused homes: Value 0 (DHW continues, CH adjusts)
    - Homes with backup electric heater: Value 1 (grid controls everything, backup available)
    - Grid-sensitive areas: Value 1 (aggressive load shedding for stability)

    This works with FSV #5092 (space heating temp response during grid events).
    Together they allow fine-tuning which loads get priority during demand response.

    Safety note: Even in value 1 (demand response), system maintains minimum tank temp
    to prevent bacterial growth and equipment damage. Does not run indefinitely cold.

    Related: FSV #5091 (enable/disable smart grid), FSV #5092 (heating temp response),
            FSV #5093 (DHW temp shift during response).
    """

    MESSAGE_ID = 0x411D
    MESSAGE_NAME = "Smart Grid DHW Mode"
    MESSAGE_ENUM = InFsv5094


class InZone2PowerMessage(BoolMessage):
    """Parser for message 0x411E (Zone 2 operating power)."""

    MESSAGE_ID = 0x411E
    MESSAGE_NAME = "Zone 2 operating power"


class InPvContactStateMessage(BoolMessage):
    """Parser for message 0x4123 (PV Contact State)."""

    MESSAGE_ID = 0x4123
    MESSAGE_NAME = "PV Contact State"


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
    """Parser for message 0x4127 (FSV 2093 Remote Controller Room Temp Control).

    Room temperature sensor control mode for wired remote controller.
    Default: 4, Range: 1-4

    1 = Compressor controlled only by room temperature sensor
    2 = Compressor controlled by room sensor or WL discharged water temp; pump off when WL disabled
    3 = Compressor controlled by room sensor or WL discharged water temp; pump stays on
    4 = Compressor controlled by room sensor or WL discharged water temp; pump cycles (7min off, 3min on)
    """

    MESSAGE_ID = 0x4127
    MESSAGE_NAME = "FSV 2093"
    MESSAGE_ENUM = InFsv2093Enum


class InFsv5022(EnumMessage):
    """Parser for message 0x4128 (FSV 5022 - DHW Saving Mode).

    Selects DHW energy saving mode operation type.
    Default: 0, Range: 0-1

    Modes:
    - 0 (Standard): DHW Saving Temp offset (FSV #5021) active, thermostat off until offset
    - 1 (Advanced): Custom thermo on temperature (FSV #5023) enables earlier heating restart

    In Eco mode of wired remote controller, system reduces target DHW temperature
    by FSV #5021 offset. Mode 1 allows setting custom thermo activation point (FSV #5023)
    for more precise energy saving control. Mode 0 (default) provides simpler operation.
    """

    MESSAGE_ID = 0x4128
    MESSAGE_NAME = "FSV 5022 DHW Saving Mode"
    MESSAGE_ENUM = InFsv5022Enum


class InFsv2094Message(EnumMessage):
    """Parser for message 0x412A (FSV 2094 Heating Water Law for Auto Mode).

    Enables heating water law (weather-dependent control) in auto mode operation.
    Allows the system to adjust water temperature based on outdoor ambient temperature.
    """

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


class InDiffuserOperationMessage(BoolMessage):
    """Parser for message 0x4149 (Diffuser operation)."""

    MESSAGE_ID = 0x4149
    MESSAGE_NAME = "Diffuser operation"


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
    """Parser for message 0x424A (FSV 1011 - Water Out Temp for Cooling Max).

    Target water outlet temperature upper limit for cooling mode.
    Default: 25°C, Range: 18-25°C

    Combined with FSV 1012, users can set target water outlet temperature between 5-25°C.
    """

    MESSAGE_ID = 0x424A
    MESSAGE_NAME = "Cool Max Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1012Message(FloatMessage):
    """Parser for message 0x424B (FSV 1012 - Water Out Temp for Cooling Min).

    Target water outlet temperature lower limit for cooling mode.
    Default: 16°C, Range: 5-18°C

    Combined with FSV 1011, users can set target water outlet temperature between 5-25°C.
    """

    MESSAGE_ID = 0x424B
    MESSAGE_NAME = "Cool Min Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1021Message(FloatMessage):
    """Parser for message 0x424C (FSV 1021 - Room Temp for Cooling Max).

    Target room temperature upper limit for cooling mode.
    Default: 30°C, Range: 28-30°C

    Combined with FSV 1022, users can set target room temperature between 18-30°C.
    Note: Setting a higher room set point for cooling may result in saving energy and reducing energy costs.
    """

    MESSAGE_ID = 0x424C
    MESSAGE_NAME = "Cool Max Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1022Message(FloatMessage):
    """Parser for message 0x424D (FSV 1022 - Room Temp for Cooling Min).

    Target room temperature lower limit for cooling mode.
    Default: 18°C, Range: 18-28°C

    Combined with FSV 1021, users can set target room temperature between 18-30°C.
    """

    MESSAGE_ID = 0x424D
    MESSAGE_NAME = "Cool Min Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1031Message(FloatMessage):
    """Parser for message 0x424E (FSV 1031 - Water Out Temp for Heating Max).

    Target water outlet temperature upper limit for heating mode.
    Default: 70°C, Range: 37-70°C

    Combined with FSV 1032, users can set target water outlet temperature between 15-70°C.
    """

    MESSAGE_ID = 0x424E
    MESSAGE_NAME = "Heat Max Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1032Message(FloatMessage):
    """Parser for message 0x424F (FSV 1032 - Water Out Temp for Heating Min).

    Target water outlet temperature lower limit for heating mode.
    Default: 25°C, Range: 15-37°C

    Combined with FSV 1031, users can set target water outlet temperature between 15-70°C.
    """

    MESSAGE_ID = 0x424F
    MESSAGE_NAME = "Heat Min Water Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1041Message(FloatMessage):
    """Parser for message 0x4250 (FSV 1041 - Room Temp for Heating Max).

    Target room temperature upper limit for heating mode.
    Default: 30°C, Range: 18-30°C

    Combined with FSV 1042, users can set target room temperature between 16-30°C.
    """

    MESSAGE_ID = 0x4250
    MESSAGE_NAME = "Heat Max Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1042Message(FloatMessage):
    """Parser for message 0x4251 (FSV 1042 - Room Temp for Heating Min).

    Target room temperature lower limit for heating mode.
    Default: 16°C, Range: 16-18°C

    Combined with FSV 1041, users can set target room temperature between 16-30°C.
    Note: Setting a lower room heating set point may result in saving energy and reducing energy costs.
    """

    MESSAGE_ID = 0x4251
    MESSAGE_NAME = "Heat Min Room Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1051Message(FloatMessage):
    """Parser for message 0x4252 (FSV 1051 - DHW tank Temp Max).

    Target domestic hot water tank temperature upper limit.
    Default: 55°C, Range: 50-70°C

    Combined with FSV 1052, users can set target tank temperature between 30-70°C.
    Note: A lower DHW set temperature may result in higher efficiency of the heat pump.
    """

    MESSAGE_ID = 0x4252
    MESSAGE_NAME = "DHW Max Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv1052Message(FloatMessage):
    """Parser for message 0x4253 (FSV 1052 - DHW tank Temp Min).

    Target domestic hot water tank temperature lower limit.
    Default: 40°C, Range: 30-40°C

    Combined with FSV 1051, users can set target tank temperature between 30-70°C.
    Note: A lower DHW set temperature may limit the total number of showers before recharging.
    """

    MESSAGE_ID = 0x4253
    MESSAGE_NAME = "DHW Min Temperature"
    UNIT_OF_MEASUREMENT = "°C"


class InFsv2011OutdoorTempHeatingMax(FloatMessage):
    """Parser for message 0x4254 (FSV 2011 - Outdoor Temp for Water Law Heating Max).

    Outdoor air temperature upper limit (Point ①) for water law heating control.
    This is the outdoor temperature at which water outlet reaches its maximum setpoint.
    Default: -10°C, Range: -20 to 5°C

    Combined with FSV 2012, defines the outdoor temperature range for heating water law.
    With defaults (-10 to 15°C), the system automatically adjusts water temperature based on
    outdoor conditions to optimize heating efficiency.
    """

    MESSAGE_ID = 0x4254
    MESSAGE_NAME = "FSV 2011 Outdoor Temp for Heating Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2012OutdoorTempHeatingMin(FloatMessage):
    """Parser for message 0x4255 (FSV 2012 - Outdoor Temp for Water Law Heating Min).

    Outdoor air temperature lower limit (Point ②) for water law heating control.
    This is the outdoor temperature at which water outlet reaches its minimum setpoint.
    Default: 15°C, Range: 10 to 20°C

    Combined with FSV 2011, defines the outdoor temperature range for heating water law.
    """

    MESSAGE_ID = 0x4255
    MESSAGE_NAME = "FSV 2012 Outdoor Temp for Heating Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2021WaterOutTempWL1HeatingMax(FloatMessage):
    """Parser for message 0x4256 (FSV 2021 - Water Out Temp for WL1 Heat Max).

    Maximum water outlet temperature for WL1 (floor/UFH) heating operation.
    Upper limit (Point ①) of water temperature control curve for floor heating.
    Default: 40°C, Range: 17 to 65°C

    Combined with FSV 2022, defines the water temperature range for floor heating water law.
    With defaults (25-40°C), the system maintains optimal floor heating temperature.
    """

    MESSAGE_ID = 0x4256
    MESSAGE_NAME = "FSV 2021 Water Out Temp WL1 Heating Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2022WaterOutTempWL1HeatingMin(FloatMessage):
    """Parser for message 0x4257 (FSV 2022 - Water Out Temp for WL1 Heat Min).

    Minimum water outlet temperature for WL1 (floor/UFH) heating operation.
    Lower limit (Point ②) of water temperature control curve for floor heating.
    Default: 25°C, Range: 17 to 65°C

    Combined with FSV 2021, defines the water temperature range for floor heating water law.
    """

    MESSAGE_ID = 0x4257
    MESSAGE_NAME = "FSV 2022 Water Out Temp WL1 Heating Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2031WaterOutTempWL2HeatingMax(FloatMessage):
    """Parser for message 0x4258 (FSV 2031 - Water Out Temp for WL2 Heat Max).

    Maximum water outlet temperature for WL2 (FCU/radiator) heating operation.
    Upper limit (Point ①) of water temperature control curve for fan coil unit heating.
    Default: 50°C, Range: 17 to 65°C

    Combined with FSV 2032, defines the water temperature range for FCU heating water law.
    With defaults (35-50°C), the system maintains optimal FCU heating temperature.
    """

    MESSAGE_ID = 0x4258
    MESSAGE_NAME = "FSV 2031 Water Out Temp WL2 Heating Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2032WaterOutTempWL2HeatingMin(FloatMessage):
    """Parser for message 0x4259 (FSV 2032 - Water Out Temp for WL2 Heat Min).

    Minimum water outlet temperature for WL2 (FCU/radiator) heating operation.
    Lower limit (Point ②) of water temperature control curve for fan coil unit heating.
    Default: 35°C, Range: 17 to 65°C

    Combined with FSV 2031, defines the water temperature range for FCU heating water law.
    """

    MESSAGE_ID = 0x4259
    MESSAGE_NAME = "FSV 2032 Water Out Temp WL2 Heating Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2051OutdoorTempCoolingMax(FloatMessage):
    """Parser for message 0x425A (FSV 2051 - Outdoor Temp for Water Law Cooling Max).

    Outdoor air temperature upper limit (Point ①) for water law cooling control.
    This is the outdoor temperature at which water outlet reaches its maximum setpoint.
    Default: 30°C, Range: 25 to 35°C

    Combined with FSV 2052, defines the outdoor temperature range for cooling water law.
    With defaults (30-40°C), the system automatically adjusts water temperature based on
    outdoor conditions to optimize cooling efficiency.
    """

    MESSAGE_ID = 0x425A
    MESSAGE_NAME = "FSV 2051 Outdoor Temp for Cooling Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2052OutdoorTempCoolingMin(FloatMessage):
    """Parser for message 0x425B (FSV 2052 - Outdoor Temp for Water Law Cooling Min).

    Outdoor air temperature lower limit (Point ②) for water law cooling control.
    This is the outdoor temperature at which water outlet reaches its minimum setpoint.
    Default: 40°C, Range: 35 to 45°C

    Combined with FSV 2051, defines the outdoor temperature range for cooling water law.
    """

    MESSAGE_ID = 0x425B
    MESSAGE_NAME = "FSV 2052 Outdoor Temp for Cooling Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2061WaterOutTempWL1CoolingMax(FloatMessage):
    """Parser for message 0x425C (FSV 2061 - Water Out Temp for WL1 Cool Max).

    Maximum water outlet temperature for WL1 (floor/UFH) cooling operation.
    Upper limit (Point ①) of water temperature control curve for floor cooling.
    Default: 25°C, Range: 5 to 25°C

    Combined with FSV 2062, defines the water temperature range for floor cooling water law.
    With defaults (18-25°C), the system maintains optimal floor cooling temperature.
    Note: Water temperature must remain above 16°C during cooling to prevent condensation.
    """

    MESSAGE_ID = 0x425C
    MESSAGE_NAME = "FSV 2061 Water Out Temp WL1 Cooling Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2062WaterOutTempWL1CoolingMin(FloatMessage):
    """Parser for message 0x425D (FSV 2062 - Water Out Temp for WL1 Cool Min).

    Minimum water outlet temperature for WL1 (floor/UFH) cooling operation.
    Lower limit (Point ②) of water temperature control curve for floor cooling.
    Default: 18°C, Range: 5 to 25°C

    Combined with FSV 2061, defines the water temperature range for floor cooling water law.
    """

    MESSAGE_ID = 0x425D
    MESSAGE_NAME = "FSV 2062 Water Out Temp WL1 Cooling Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2071WaterOutTempWL2CoolingMax(FloatMessage):
    """Parser for message 0x425E (FSV 2071 - Water Out Temp for WL2 Cool Max).

    Maximum water outlet temperature for WL2 (FCU/radiator) cooling operation.
    Upper limit (Point ①) of water temperature control curve for fan coil unit cooling.
    Default: 18°C, Range: 5 to 25°C

    Combined with FSV 2072, defines the water temperature range for FCU cooling water law.
    With defaults (5-18°C), the system maintains optimal FCU cooling temperature.
    """

    MESSAGE_ID = 0x425E
    MESSAGE_NAME = "FSV 2071 Water Out Temp WL2 Cooling Max"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv2072WaterOutTempWL2CoolingMin(FloatMessage):
    """Parser for message 0x425F (FSV 2072 - Water Out Temp for WL2 Cool Min).

    Minimum water outlet temperature for WL2 (FCU/radiator) cooling operation.
    Lower limit (Point ②) of water temperature control curve for fan coil unit cooling.
    Default: 5°C, Range: 5 to 25°C

    Combined with FSV 2071, defines the water temperature range for FCU cooling water law.
    """

    MESSAGE_ID = 0x425F
    MESSAGE_NAME = "FSV 2072 Water Out Temp WL2 Cooling Min"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True


class InFsv3021(BasicTemperatureMessage):
    """Parser for message 0x4260 (FSV 3021 - DHW Heat Pump Max Temperature).

    Maximum water temperature available through heat pump operation (THP MAX).
    Default: 55°C, Range: 45-55°C

    This sets the upper limit for heat pump DHW heating. Booster heater activates
    when target temperature exceeds this value. Thermo off/on control is based on
    temperature difference from this maximum.
    """

    MESSAGE_ID = 0x4260
    MESSAGE_NAME = "FSV 3021 DHW Heating Mode Max"
    SIGNED = True


class InFsv3022(BasicTemperatureMessage):
    """Parser for message 0x4261 (FSV 3022 - DHW Heat Pump Stop Temperature Difference).

    Temperature difference determining heat pump OFF temperature.
    Default: 0°C, Range: 0-10°C

    THP OFF = THP MAX + FSV #3022
    When tank temperature reaches this point, heat pump stops DHW operation.
    """

    MESSAGE_ID = 0x4261
    MESSAGE_NAME = "FSV 3022"
    SIGNED = True


class InFsv3023(BasicTemperatureMessage):
    """Parser for message 0x4262 (FSV 3023 - DHW Heat Pump Start Temperature Difference).

    Temperature difference determining heat pump ON temperature.
    Default: 5°C, Range: 5-30°C

    THP ON = THP OFF - FSV #3023
    When tank temperature drops below this point, heat pump restarts DHW operation.
    Represents hysteresis between on/off temperatures for stable control.
    """

    MESSAGE_ID = 0x4262
    MESSAGE_NAME = "FSV 3023 DHW Heat Pump Start"
    SIGNED = True


class InFsv3024(FloatMessage):
    """Parser for message 0x4263 (FSV 3024 - Min Space Heating Operation Time).

    Minimum time space heating must operate when both DHW and heating are requested.
    Default: 5 min, Range: 1-20 min

    Ensures space heating receives minimum operating time during combined DHW/heating
    mode timer operation. Applied only when both DHW and space heating requests exist.
    """

    MESSAGE_ID = 0x4263
    MESSAGE_NAME = "FSV 3024 DHW Min Operating Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3025(FloatMessage):
    """Parser for message 0x4264 (FSV 3025 - Max DHW Operation Time).

    Maximum time DHW operation can run when both DHW and space heating are requested.
    Default: 30 min, Range: 5-95 min

    Limits DHW heating during combined DHW/heating mode timer operation.
    Applied only when both DHW and space heating requests exist.
    In single DHW operation, heating continues until target temperature is reached.
    """

    MESSAGE_ID = 0x4264
    MESSAGE_NAME = "FSV 3025 DHW Max Operating Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3026(FloatMessage):
    """Parser for message 0x4265 (FSV 3026 - Max Space Heating Operation Time).

    Maximum time space heating can operate after DHW during combined mode.
    Default: 3 hours, Range: 0.5-10 hours

    Controls duration of space heating operation following DHW mode in mode timer
    management. Applied only when both DHW and space heating requests exist.
    """

    MESSAGE_ID = 0x4265
    MESSAGE_NAME = "FSV 3026 Max Space Heating Operation Time"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3032(FloatMessage):
    """Parser for message 0x4266 (FSV 3032 - Booster Heater Delay Time).

    Startup delay timer for booster heater DHW operation.
    Default: 20 min, Range: 20-95 min

    Delays booster heater activation compared to heat pump when DHW is requested.
    In Power/Forced DHW mode, delay is bypassed and booster starts immediately.
    In Economic DHW mode, only heat pump operates (no booster).
    Must be smaller than maximum heat pump time (FSV #3025).
    """

    MESSAGE_ID = 0x4266
    MESSAGE_NAME = "FSV 3032 Booster Heater Delay Time"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3033(BasicTemperatureMessage):
    """Parser for message 0x4267 (FSV 3033 - Booster Heater Overshoot Temperature).

    Temperature difference for booster heater OFF control.
    Default: 0°C, Range: 0-4°C

    Tbsh OFF = Target temperature + FSV #3033
    Tbsh ON = Tbsh OFF - 2°C

    Controls when booster heater stops operating. Higher values extend heating duration.
    Used only when target temperature exceeds heat pump maximum (THP MAX).
    """

    MESSAGE_ID = 0x4267
    MESSAGE_NAME = "FSV 3033 Booster Heater Overshoot"
    SIGNED = True


class InFsv3043(FloatMessage):
    """Parser for message 0x4269 (FSV 3043 - Disinfection Start Time).

    Start time for periodic disinfection heating cycle.
    Default: 23 (11 PM), Range: 0-23 (hour of day)

    Disinfection automatically starts at this hour to heat tank to target temperature
    for the specified duration. Operates on schedule defined by FSV #3042 (interval).
    """

    MESSAGE_ID = 0x4269
    MESSAGE_NAME = "FSV 3043 Disinfection Start Time"
    UNIT_OF_MEASUREMENT = "h"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3044(BasicTemperatureMessage):
    """Parser for message 0x426A (FSV 3044 - Disinfection Target Temperature).

    Target water temperature for periodic disinfection heating cycle.
    Default: 70°C, Range: 40-70°C

    Tank is heated to this temperature during disinfection operation.
    Must be maintained for duration specified in FSV #3045.
    """

    MESSAGE_ID = 0x426A
    MESSAGE_NAME = "FSV 3044 Disinfection Target Temp"
    SIGNED = True


class InFsv3045(FloatMessage):
    """Parser for message 0x426B (FSV 3045 - Disinfection Duration).

    Time duration that disinfection heating must maintain target temperature.
    Default: 10 min, Range: 5-60 min

    Tank must remain at target temperature (FSV #3044) for this duration
    to complete disinfection cycle. Runs on schedule (FSV #3042) starting
    at specified time (FSV #3043).
    """

    MESSAGE_ID = 0x426B
    MESSAGE_NAME = "FSV 3045 Disinfection Duration"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv3052(FloatMessage):
    """Parser for message 0x426C (FSV 3052 - Forced DHW Time Duration).

    Duration for forced DHW operation when timer function is enabled.
    Default: 6 (×10 min = 60 min), Range: 3-30 (×10 min = 30-300 min)

    When FSV #3051 is enabled, DHW runs for this duration in forced mode.
    Value is multiplied by 10 minutes (e.g., 6 = 60 minutes).
    """

    MESSAGE_ID = 0x426C
    MESSAGE_NAME = "FSV 3052 Forced DHW Time Duration"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = True
    ARITHMETIC = 10.0


class InFsv4012(BasicTemperatureMessage):
    """Parser for message 0x426D (FSV 4012 - Outdoor Temp. for Priority).

    Outdoor temperature threshold for heating priority changeover.
    Default: 0°C, Range: -15 to 20°C, Step: 1°C

    When FSV #4011 = 1 (Heating priority), space heating only takes priority
    when outdoor temperature falls below this threshold. Above this temperature,
    DHW priority (FSV #4011 = 0) behavior is used instead.
    """

    MESSAGE_ID = 0x426D
    MESSAGE_NAME = "FSV 4012 Outdoor Temp for Priority"
    SIGNED = True


class InFsv4013(BasicTemperatureMessage):
    """Parser for message 0x426E (FSV 4013 - Heat OFF).

    Outdoor temperature at which space heating stops.
    Default: 35°C, Range: 14-35°C, Step: 1°C

    When outdoor temperature exceeds this threshold, the heat pump stops operating
    for space heating. DHW heating can still operate via booster heater (BSH) if needed.
    This prevents unnecessary heating operation during mild/warm weather.
    """

    MESSAGE_ID = 0x426E
    MESSAGE_NAME = "FSV 4013 Heat OFF Outdoor Temp"
    SIGNED = True


class InFsv4024(BasicTemperatureMessage):
    """Parser for message 0x4270 (FSV 4024 - Threshold Temp).

    Threshold outdoor temperature for backup heater cold weather compensation.
    Default: 0°C, Range: -25 to 35°C, Step: 1°C

    When enabled (FSV #4023 = 1), backup heater activates below this temperature
    to maintain space heating capacity when heat pump efficiency drops due to
    extremely cold outdoor conditions. Range allows flexibility for different climates.
    """

    MESSAGE_ID = 0x4270
    MESSAGE_NAME = "FSV 4024 Backup Heater Threshold Temp"
    SIGNED = True


class InFsv4025(BasicTemperatureMessage):
    """Parser for message 0x4271 (FSV 4025 - Defrost Backup Temp).

    Water outlet temperature at which backup heater activates during defrost mode.
    Default: 15°C, Range: 10-55°C, Step: 5°C

    During defrost operation, heat pump reverses to cooling mode (water gets cold).
    When water outlet temperature falls below this threshold, backup heater activates
    to prevent cold draft/discomfort from chilled water circulation in heating circuits.
    Higher values = earlier backup heater activation during defrost.
    """

    MESSAGE_ID = 0x4271
    MESSAGE_NAME = "FSV 4025 Defrost Backup Temp"
    SIGNED = True


class InFsv4033(BasicTemperatureMessage):
    """Parser for message 0x4272 (FSV 4033 - Boiler Threshold Temp).

    Outdoor temperature at which backup boiler activates for space heating.
    Default: -15°C, Range: -20 to 5°C, Step: 1°C

    When outdoor temperature falls below this threshold, backup boiler becomes
    active (if FSV #4031 = 1). Boiler release/deactivation occurs when outdoor
    temperature exceeds FSV #4033 + 3°C (3°C hysteresis prevents chattering).
    """

    MESSAGE_ID = 0x4272
    MESSAGE_NAME = "FSV 4033 Boiler Threshold Temp"
    SIGNED = True


class InFsv5011Message(FloatMessage):
    """Parser for message 0x4273 (FSV 5011 - Water Out Temp for Cooling in Outing Mode).

    Target water outlet temperature during outing mode in cooling operation.
    Default: 25°C, Range: 5-25°C, Step: 1°C

    When outing mode is activated, the system reduces cooling capacity by setting a higher
    target water outlet temperature. This prevents unnecessary system operation during
    extended absence, reducing energy consumption while maintaining equipment protection.

    Related: FSV #5012 (room temp cooling), FSV #5013 (water temp heating),
            FSV #5014 (room temp heating).
    """

    MESSAGE_ID = 0x4273
    MESSAGE_NAME = "Outing Mode Water Out Temp (Cooling)"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5012Message(FloatMessage):
    """Parser for message 0x4274 (FSV 5012 - Room Temperature for Cooling in Outing Mode).

    Target room temperature during outing mode in cooling operation.
    Default: 30°C, Range: 18-30°C, Step: 1°C

    When outing mode is activated, the system reduces cooling by setting a higher target
    room temperature. This relaxed temperature setpoint combined with higher water outlet
    temperature (FSV #5011) minimizes system runtime during extended absence.

    For energy-conscious users, higher values (28-30°C) reduce energy consumption while
    preventing heat accumulation in the home.

    Related: FSV #5011 (water temp cooling), FSV #5013/5014 (heating temps).
    """

    MESSAGE_ID = 0x4274
    MESSAGE_NAME = "Outing Mode Room Temp (Cooling)"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5013Message(FloatMessage):
    """Parser for message 0x4275 (FSV 5013 - Water Out Temp for Heating in Outing Mode).

    Target water outlet temperature during outing mode in heating operation.
    Default: 15°C, Range: 15-55°C, Step: 1°C

    When outing mode is activated during winter/heating season, the system reduces heating
    capacity by setting a lower target water outlet temperature. Prevents overheating during
    extended absence while maintaining frost protection for the system.

    Lower values (15-20°C) provide minimal heating energy while protecting the home and
    equipment. System may circulate water periodically for freeze protection.

    Related: FSV #5014 (room temp heating), FSV #5011/5012 (cooling temps).
    """

    MESSAGE_ID = 0x4275
    MESSAGE_NAME = "Outing Mode Water Out Temp (Heating)"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5014Message(FloatMessage):
    """Parser for message 0x4276 (FSV 5014 - Room Temperature for Heating in Outing Mode).

    Target room temperature during outing mode in heating operation.
    Default: 16°C, Range: 16-30°C, Step: 1°C

    When outing mode is activated during heating season, the system reduces heating by
    setting a lower target room temperature. Combined with lower water outlet temperature
    (FSV #5013), this minimizes heating system runtime during extended absence while
    maintaining frost protection (typically 16°C is above freeze threshold).

    Balances energy savings with protection: 16-18°C provides freeze protection while
    reducing heating costs substantially compared to normal operation.

    Related: FSV #5013 (water temp heating), FSV #5011/5012 (cooling temps).
    """

    MESSAGE_ID = 0x4276
    MESSAGE_NAME = "Outing Mode Room Temp (Heating)"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5015Message(FloatMessage):
    """Parser for message 0x4277 (FSV 5015 - Auto Cooling WL1 Water Temp in Outing Mode).

    Water Law 1 (WL1) target water outlet temperature during auto cooling in outing mode.
    Default: 25°C, Range: 5-25°C, Step: 1°C

    When outing mode and auto cooling are both active, the system uses Water Law curve
    (adjusting water temp based on outdoor temp) but limits it to this maximum value.
    For WL1 (outdoor temp -5°C to 20°C), prevents excessive cooling during absence.

    This parameter constrains the automatic water temperature calculation to prevent
    overshooting during outing periods. Values match FSV #5011 semantics (high water temp
    = reduced cooling). WL1 typically covers mild/moderate outdoor conditions.

    Related: FSV #5016 (WL2 auto cool), FSV #5017/5018 (auto heating WL1/WL2).
    """

    MESSAGE_ID = 0x4277
    MESSAGE_NAME = "Outing Mode Auto Cool WL1 Water Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5016Message(FloatMessage):
    """Parser for message 0x4278 (FSV 5016 - Auto Cooling WL2 Water Temp in Outing Mode).

    Water Law 2 (WL2) target water outlet temperature during auto cooling in outing mode.
    Default: 25°C, Range: 5-25°C, Step: 1°C

    When outing mode and auto cooling are active, system uses Water Law curve limited to
    this maximum value for WL2 (outdoor temp ≥20°C). Prevents excessive cooling during
    extended absence in warmer conditions.

    WL2 typically covers moderate to warm outdoor conditions (≥20°C). This parameter
    maintains consistency with FSV #5015 for different outdoor temp ranges, ensuring
    outing mode energy savings across all seasons.

    For dual-stage cooling systems, both WL1 and WL2 can be active simultaneously
    depending on outdoor temperature region. Outing mode dampens both to save energy.

    Related: FSV #5015 (WL1 auto cool), FSV #5017/5018 (auto heating WL1/WL2).
    """

    MESSAGE_ID = 0x4278
    MESSAGE_NAME = "Outing Mode Auto Cool WL2 Water Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5017Message(FloatMessage):
    """Parser for message 0x4279 (FSV 5017 - Auto Heating WL1 Water Temp in Outing Mode).

    Water Law 1 (WL1) target water outlet temperature during auto heating in outing mode.
    Default: 15°C, Range: 15-55°C, Step: 1°C

    When outing mode and auto heating are active, system uses Water Law curve (adjusting
    water temp based on outdoor temp) limited to this minimum value for WL1 (outdoor temp
    -5°C to 20°C). Reduces heating capacity during extended absence.

    WL1 covers cold to mild outdoor conditions. Lower water temperature reduces heating
    energy while maintaining frost protection. System circulates periodically for equipment
    protection even at reduced temperature setting.

    Auto heating mode dynamically adjusts water temperature based on outdoor conditions,
    but FSV #5017 prevents excessive heating during outing periods. Particularly important
    for preventing unnecessary heating on mild winter days during absence.

    Related: FSV #5018 (WL2 auto heat), FSV #5015/5016 (auto cooling WL1/WL2).
    """

    MESSAGE_ID = 0x4279
    MESSAGE_NAME = "Outing Mode Auto Heat WL1 Water Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5018Message(FloatMessage):
    """Parser for message 0x427A (FSV 5018 - Auto Heating WL2 Water Temp in Outing Mode).

    Water Law 2 (WL2) target water outlet temperature during auto heating in outing mode.
    Default: 15°C, Range: 15-55°C, Step: 1°C

    When outing mode and auto heating are active, system uses Water Law curve limited to
    this minimum value for WL2 (outdoor temp ≥20°C, moderate to warm conditions).
    Reduces heating during extended absence even in warmer winter weather.

    WL2 covers moderate/warm outdoor conditions. Though heating demand is typically lower
    in these conditions, outing mode still constrains the Water Law calculation to prevent
    any unnecessary system operation. Maintains consistent energy-saving behavior across
    all outdoor temperature ranges.

    For systems with dual outdoor temperature zones (WL1/WL2), both regions are covered
    by outing mode restrictions. This ensures predictable energy savings regardless of
    current outdoor temperature. Minimum 15°C protects against freeze conditions.

    Related: FSV #5017 (WL1 auto heat), FSV #5015/5016 (auto cooling WL1/WL2).
    """

    MESSAGE_ID = 0x427A
    MESSAGE_NAME = "Outing Mode Auto Heat WL2 Water Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5019Message(FloatMessage):
    """Parser for message 0x427B (FSV 5019 - Target Tank Temperature in Outing Mode).

    DHW tank temperature setpoint during outing mode.
    Default: 30°C, Range: 30-70°C, Step: 1°C

    When outing mode is active, the system reduces DHW (Domestic Hot Water) heating to
    this lower temperature. Lower tank temperature reduces standby losses and heating time,
    saving energy during extended absence while ensuring some hot water availability if
    occupants return unexpectedly.

    Default 30°C provides minimal heating (tank won't freeze, has some warm water) while
    consuming significantly less energy than normal operation (typically 45-55°C). For
    extended holidays, minimum value (30°C) maximizes savings. For weekend trips, slightly
    higher values (35-40°C) provide more convenient hot water if residents return early.

    Smart scheduling: Can combine outing mode timing with FSV #5022 (DHW Saving mode)
    for layered energy savings. Outing mode reduces tank temp during absence; DHW Saving
    mode reduces it further during off-peak hours when occupied.

    Related: FSV #5022 (DHW Saving mode), FSV #3051 (DHW timer), FSV #3001 (DHW ON/OFF).
    """

    MESSAGE_ID = 0x427B
    MESSAGE_NAME = "Outing Mode Target Tank Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = True
    ARITHMETIC = 1.0


class InFsv5021(FloatMessage):
    """Parser for message 0x427C (FSV 5021 - DHW Saving Temp).

    Temperature reduction offset for DHW energy saving mode.
    Default: 5°C, Range: 0-40°C, Step: 1°C

    In DHW Saving (Eco) mode, the system reduces the target DHW temperature by this offset.
    For example: User sets 45°C, system targets 45°C - 5°C = 40°C for energy saving.
    Reduces energy consumption while still providing sufficient hot water.
    """

    MESSAGE_ID = 0x427C
    MESSAGE_NAME = "FSV 5021 DHW Saving Temp Offset"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 1.0


class InTempWaterLawMessage(BasicTemperatureMessage):
    """Parser for message 0x427F (Water Law Target Temperature)."""

    MESSAGE_ID = 0x427F
    MESSAGE_NAME = "Water Law Target Temperature"


class InFsv4042(BasicTemperatureMessage):
    """Parser for message 0x4286 (FSV 4042 - Target ΔT Heating).

    Target temperature difference between supply and return for heating mode.
    Default: 10°C, Range: 5-15°C, Step: 1°C

    When FSV #4041 = 1 (ΔT control), mixing valve maintains this temperature
    difference. Higher values = greater supply-return difference = less mixing.
    Used for underfloor heating comfort: typical 8-12°C for floor heating systems.
    """

    MESSAGE_ID = 0x4286
    MESSAGE_NAME = "FSV 4042 Target Delta-T Heating"
    SIGNED = True


class InFsv4043(BasicTemperatureMessage):
    """Parser for message 0x4287 (FSV 4043 - Target ΔT Cooling).

    Target temperature difference between supply and return for cooling mode.
    Default: 10°C, Range: 5-15°C, Step: 1°C

    When FSV #4041 = 1 (ΔT control), mixing valve maintains this temperature
    difference during cooling operation. Ensures consistent cooling circuit
    conditions for floor cooling comfort and system stability.
    """

    MESSAGE_ID = 0x4287
    MESSAGE_NAME = "FSV 4043 Target Delta-T Cooling"
    SIGNED = True


class InFsv4045(FloatMessage):
    """Parser for message 0x4288 (FSV 4045 - Control Interval).

    Time interval between mixing valve position adjustments.
    Default: 2 minutes, Range: 1-30 minutes, Step: 1 minute

    How often the control system recalculates and adjusts mixing valve position
    based on temperature feedback. Shorter intervals = more responsive but more
    valve movement. Longer intervals = smoother operation but slower response.
    Typical: 1-5 minutes for stable underfloor heating operation.
    """

    MESSAGE_ID = 0x4288
    MESSAGE_NAME = "FSV 4045 Mixing Valve Control Interval"
    UNIT_OF_MEASUREMENT = "min"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv4046(FloatMessage):
    """Parser for message 0x4289 (FSV 4046 - Running Time).

    Total time duration for mixing valve actuator full stroke operation.
    Default: 9 (×10 sec = 90 sec), Range: 6-24 (×10 sec = 60-240 sec)
    Step: 3 (×10 sec = 30 sec increments)

    Specifies how long the valve actuator takes to move from fully open to fully
    closed (or vice versa). Typical: 90-120 seconds for proportional mixing valves.
    Used for calculating valve response speed and movement rate per control interval.
    """

    MESSAGE_ID = 0x4289
    MESSAGE_NAME = "FSV 4046 Mixing Valve Running Time"
    UNIT_OF_MEASUREMENT = "×10 sec"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv4052(BasicTemperatureMessage):
    """Parser for message 0x428A (FSV 4052 - Target ΔT).

    Target temperature difference between supply (Tw2) and return (Tw1) water.
    Default: 5°C, Range: 2-8°C, Step: 1°C

    When inverter pump is enabled (FSV #4051 > 0), pump speed modulates to
    maintain this temperature difference. Inverter pump reduces circulation flow
    during partial loads to minimize energy consumption. Higher target ΔT = lower
    flow rate = less pump energy. Typical: 3-6°C for hydronic heating systems.
    """

    MESSAGE_ID = 0x428A
    MESSAGE_NAME = "FSV 4052 Inverter Pump Target Delta-T"
    SIGNED = True


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
    """Parser for message 0x426E (FSV 3046 - Disinfection Max Time).

    Maximum time allowed for disinfection heating cycle to complete.
    Default: 8 hours, Range: 1-24 hours

    If target temperature is not reached within this time, disinfection cycle
    is terminated. Prevents excessive heating operation during disinfection.
    """

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


class InFsv5082(FloatMessage):
    """Parser for message 0x42DB (FSV 5082 - Setting Temp. Shift Value Cool).

    Temperature reduction offset during PV solar generation mode (cooling).
    Default: 1°C, Range: 0-5°C, Step: 0.5°C

    When PV panels generate surplus solar energy, system reduces cooling setpoints
    by this offset to utilize the free energy:
    - Room sensor: Current value - FSV #5082 (Min = FSV #1022)
    - Water outlet: Current value - FSV #5082 (Min = FSV #1012)
    - Water Law: Current value - FSV #5082 (Min = FSV #2061/2062/2071/2072)

    Except DHW mode, only active during outing mode.
    """

    MESSAGE_ID = 0x42DB
    MESSAGE_NAME = "FSV 5082 PV Control Cool Temp Shift"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 0.5


class InFsv5083(FloatMessage):
    """Parser for message 0x42DC (FSV 5083 - Setting Temp. Shift Value Heat).

    Temperature increase offset during PV solar generation mode (heating).
    Default: 1°C, Range: 0-5°C, Step: 0.5°C

    When PV panels generate surplus solar energy, system raises heating setpoints
    by this offset to utilize the free energy:
    - Room sensor: Current value + FSV #5083 (Max = FSV #1041)
    - Water outlet: Current value + FSV #5083 (Max = FSV #1031)
    - Water Law: Current value + FSV #5083 (Max = FSV #2021/2022/2031/2032)

    DHW mode always operates at maximum (FSV #1051) regardless of outing mode.
    Only active during outing mode for space heating/cooling.
    """

    MESSAGE_ID = 0x42DC
    MESSAGE_NAME = "FSV 5083 PV Control Heat Temp Shift"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 0.5


class InFsv5092(FloatMessage):
    """Parser for message 0x42DD (FSV 5092 - Setting Temp. Shift Value Heat).

    Temperature increase offset for Smart Grid Mode 3 & 4 (heating).
    Default: 2°C, Range: 2-5°C, Step: 0.5°C

    When Smart Grid signals step-up operation (Mode 3 or 4):
    - Mode 3: Heating/Room/WL = Current + FSV #5092 (+3°C additional for WL)
    - Mode 4: Heating/WL = Current + FSV #5092 + 5°C, Room = Current + FSV #5092 + 3°C

    Allows power company to request higher heating setpoints during periods of
    grid abundance to store energy and prevent overload situations.
    """

    MESSAGE_ID = 0x42DD
    MESSAGE_NAME = "FSV 5092 Smart Grid Heat Temp Shift"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 0.5


class InFsv5093(FloatMessage):
    """Parser for message 0x42DE (FSV 5093 - Setting Temp. Shift Value DHW).

    Temperature increase offset for Smart Grid Mode 3 DHW operation.
    Default: 5°C, Range: 2-5°C, Step: 0.5°C

    In Smart Grid Mode 3 (step-up), DHW setpoint = Current + FSV #5093
    Raises target DHW temperature during grid abundance periods to store more
    hot water energy and reduce strain on the electrical grid.

    Note: Mode 4 DHW behavior is controlled by FSV #5094 instead:
    - FSV #5094 = 0: Target 55°C (heat pump only)
    - FSV #5094 = 1: Target 70°C (heat pump + booster heater)
    """

    MESSAGE_ID = 0x42DE
    MESSAGE_NAME = "FSV 5093 Smart Grid DHW Temp Shift"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 0.5


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


class InFsv3081(FloatMessage):
    """Parser for message 0x42ED (FSV 3081 - BUH 1 Step Capacity).

    Backup Unit Heater (BUH) 1 electric heating step capacity in kW.
    Default: 2 kW, Range: 1-6 kW, Step: 1 kW

    Sets the heating capacity of the first auxiliary electric heater step.
    Used in systems without booster heater or with split heating stages.
    Combined with FSV 3082, provides total backup heating capacity.
    """

    MESSAGE_ID = 0x42ED
    MESSAGE_NAME = "FSV 3081 BUH 1 Step Capacity"
    UNIT_OF_MEASUREMENT = "kW"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3082(FloatMessage):
    """Parser for message 0x42EE (FSV 3082 - BUH 2 Step Capacity).

    Backup Unit Heater (BUH) 2 electric heating step capacity in kW.
    Default: 2 kW, Range: 0-6 kW, Step: 1 kW

    Sets the heating capacity of the second auxiliary electric heater step.
    Can be set to 0 if second step is not required. Combined with FSV 3081
    for total backup heating capacity (max 12 kW when both at 6 kW).
    """

    MESSAGE_ID = 0x42EE
    MESSAGE_NAME = "FSV 3082 BUH 2 Step Capacity"
    UNIT_OF_MEASUREMENT = "kW"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv3083(FloatMessage):
    """Parser for message 0x42EF (FSV 3083 - BSH Capacity).

    Booster System Heater (BSH) electric heating capacity in kW.
    Default: 3 kW, Range: 1-6 kW, Step: 1 kW

    Sets the heating capacity of the dedicated booster heater. The BSH activates
    when DHW tank temperature exceeds heat pump maximum (THP MAX, FSV #3021).
    Primary function is to reach higher DHW temperatures in heating mode.
    """

    MESSAGE_ID = 0x42EF
    MESSAGE_NAME = "FSV 3083 BSH Capacity"
    UNIT_OF_MEASUREMENT = "kW"
    SIGNED = False
    ARITHMETIC = 1.0


class InFsv5023(FloatMessage):
    """Parser for message 0x42F0 (FSV 5023 - DHW Saving Thermo on Temp).

    Temperature threshold for heating activation in DHW saving mode.
    Default: 25°C, Range: 0-40°C, Step: 1°C

    Sets the water temperature at which thermostat heating turns on during DHW Saving mode.
    When water cools below this temperature in Eco mode, heat pump activates.
    Lower values = less frequent heating operation = more energy saving.
    """

    MESSAGE_ID = 0x42F0
    MESSAGE_NAME = "FSV 5023 DHW Saving Thermo On Temp"
    UNIT_OF_MEASUREMENT = "°C"
    SIGNED = False
    ARITHMETIC = 1.0


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


class InMinutesSinceInstallationMessage(IntegerMessage):
    """Parser for message 0x4423 (Minutes Since Installation)."""

    MESSAGE_ID = 0x4423
    MESSAGE_NAME = "Minutes Since Installation"
    UNIT_OF_MEASUREMENT = "min"


class InMinutesActiveMessage(IntegerMessage):
    """Parser for message 0x4424 (Minutes Active)."""

    MESSAGE_ID = 0x4424
    MESSAGE_NAME = "Minutes Active"
    UNIT_OF_MEASUREMENT = "min"


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
