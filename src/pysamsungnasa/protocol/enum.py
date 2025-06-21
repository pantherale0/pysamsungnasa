"""Protocol enums."""

from enum import Enum, IntEnum


class SamsungEnum(Enum):
    """Define the base samsung enum."""

    def __str__(self):
        return self.name


class AddressClass(SamsungEnum, IntEnum):
    """NASA Device Address Class from protocol byte 3 & 6."""

    UNKNOWN = 0x00
    OUTDOOR = 0x10
    HTU = 0x11
    INDOOR = 0x20
    ERV = 0x30
    DIFFUSER = 0x35
    MCU = 0x38
    RMC = 0x40
    WIRED_REMOTE = 0x50
    PIM = 0x58
    SIM = 0x59
    PEAK = 0x5A
    POWER_DIVIDER = 0x5B
    WIFI_KIT = 0x62  # From "Notes" section in NOTES.md
    CENTRAL_CONTROLLER = 0x65
    JIG_TESTER = 0x80  # Tester
    BML = 0xB0  # Broadcast Self Layer
    BCL = 0xB1  # Broadcast Control Layer
    BSL = 0xB2  # Broadcast Set Layer
    BCSL = 0xB3  # Broadcast Control and Set Layer
    BMDL = 0xB4  # Broadcast Module Layer
    BCSM = 0xB7  # Broadcast CSM
    BLL = 0xB8  # Broadcast Local Layer
    BCSML = 0xB9  # Broadcast CSML
    UNDEFINED = 0xFF


class PacketType(SamsungEnum, IntEnum):
    """NASA Packet Types from protocol byte 10."""

    UNKNOWN = -1
    STANDBY = 0
    NORMAL = 1
    GATHERING = 2
    INSTALL = 3
    DOWNLOAD = 4


class DataType(SamsungEnum, IntEnum):
    """NASA Data Types from protocol byte 10.
    (Previously PayloadTypes as StrEnum)
    """

    UNKNOWN = -1
    UNDEFINED = 0
    READ = 1
    WRITE = 2
    REQUEST = 3
    NOTIFICATION = 4
    RESPONSE = 5
    ACK = 6
    NACK = 7


class MessageSetType(SamsungEnum, IntEnum):
    """NASA Message Set Type derived from Message Number (protocol bytes 13-14)."""

    ENUM = 0  # 1 byte payload
    VARIABLE = 1  # 2 bytes payload
    LONG_VARIABLE = 2  # 4 bytes payload
    STRUCTURE = 3  # structure payload


# Specific Message Enums from NOTES.md


class OutOpCheckRefStep(SamsungEnum, IntEnum):
    """
    Refrigerant amount level (Message 0x808E).
    Label (NASA.prc): ENUM*OUT_OP_CHECK_REF_STEP
    As per NOTES.md, Min = 0, Max = 8.
    The specific semantic meaning of each level (0-8) is not detailed in the notes.
    The notes also mention: "This is Enum in definition. But we need operation,
    so just consider this as variable."
    """

    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8


class InOperationPower(SamsungEnum, IntEnum):
    """
    Indoor unit power on/off (Message 0x4000).
    Label (NASA.prc): ENUM*IN_OPERATION_POWER
    Remarks from NOTES.md: "0 Off, 1 On, 2 On".
    The distinction between ON_STATE_1 and ON_STATE_2 (if any) is not specified.
    """

    OFF = 0
    ON_STATE_1 = 1
    ON_STATE_2 = 2


class InOperationMode(SamsungEnum, IntEnum):
    """
    Indoor unit control mode (Message 0x4001).
    Label (NASA.prc): ENUM_IN_OPERATION_MODE
    Remarks from NOTES.md: "0 Auto, 1 Cool, 2 Dry, 3 Fan, 4 Heat, 21 Cool Storage, 24 Hot water".
    """

    AUTO = 0
    COOL = 1
    DRY = 2
    FAN = 3
    HEAT = 4
    COOL_STORAGE = 21
    HOT_WATER = 24


class OutdoorOperationStatus(SamsungEnum, IntEnum):
    """
    Outdoor Driving Mode / Outdoor Operation Status (Message 0x8001).
    Derived from Label (NasaConst.java): NASA_OUTDOOR_OPERATION_STATUS
    and remarks for ENUM_OUT_OPERATION_ODU_MODE.
    """

    OP_STOP = 0
    OP_SAFETY = 1
    OP_NORMAL = 2
    OP_BALANCE = 3
    OP_RECOVERY = 4
    OP_DEICE = 5
    OP_COMPDOWN = 6
    OP_PROHIBIT = 7
    OP_LINEJIG = 8
    OP_PCBJIG = 9
    OP_TEST = 10
    OP_CHARGE = 11
    OP_PUMPDOWN = 12
    OP_PUMPOUT = 13
    OP_VACCUM = 14  # Note: "VACCUM" as per NOTES.md, likely "VACUUM"
    OP_CALORYJIG = 15
    OP_PUMPDOWNSTOP = 16
    OP_SUBSTOP = 17
    OP_CHECKPIPE = 18
    OP_CHECKREF = 19
    OP_FPTJIG = 20
    OP_NONSTOP_HEAT_COOL_CHANGE = 21
    OP_AUTO_INSPECT = 22
    OP_ELECTRIC_DISCHARGE = 23
    OP_SPLIT_DEICE = 24
    OP_INVETER_CHECK = 25  # Note: "INVETER" as per NOTES.md, likely "INVERTER"
    OP_NONSTOP_DEICE = 26
    OP_REM_TEST = 27
    OP_RATING = 28
    OP_PC_TEST = 29
    OP_PUMPDOWN_THERMOOFF = 30
    OP_3PHASE_TEST = 31
    OP_SMARTINSTALL_TEST = 32
    OP_DEICE_PERFORMANCE_TEST = 33
    OP_INVERTER_FAN_PBA_CHECK = 34
    OP_AUTO_PIPE_PAIRING = 35
    OP_AUTO_CHARGE = 36


class AdMultiTenantNo(SamsungEnum, IntEnum):
    """
    WiFi Kit Multi Tenant No. (Message 0x0025).
    Label (NASA.prc): ENUM_AD_MULTI_TENANT_NO
    Specific members not detailed in NOTES.md.
    """

    # Example: VALUE_0 = 0, VALUE_1 = 1 ... (actual values unknown)
    pass


class PnpPhase(SamsungEnum, IntEnum):
    """
    PNP (Plug and Play) Phase (Message 0x2004).
    Derived from usage in pysamsungnasa.pnp and NASA_PNP label.
    """

    PHASE_0_END = 0  # nasa_is_pnp_end
    PHASE_1_REQUEST = 1
    # PHASE_2 is not explicitly mentioned with 0x2004 in pnp logic
    PHASE_3_ADDRESSING = 3
    PHASE_4_ACK = 4


class PnpStep(SamsungEnum, IntEnum):
    """
    PNP (Plug and Play) Step (Message 0x2012).
    Derived from usage in pysamsungnasa.pnp.
    Label (NASA.prc): ENUM_NM*?
    """

    STEP_1 = 1  # Used in nasa_is_pnp_phase3_addressing
    STEP_4 = 4  # Used in nasa_pnp_phase4_ack


class InOperationModeReal(SamsungEnum, IntEnum):
    """
    Indoor unit current operation mode (Message 0x4002).
    Label (NASA.prc): ENUM_IN_OPERATION_MODE_REAL.
    XML ProtocolID: ENUM_in_operation_mode_real.
    Remarks: "0 Auto, 1 Cool, 2 Dry, 3 Fan, 4 Heat, 11 Auto Cool, 12 Auto Dry, 13 Auto Fan, 14 Auto Heat, 21 Cool Storage, 24 Hot water, 255 NULL mode"
    XML Item Value="0" is "Unknown", NOTES.md is "Auto". Preferring "Auto" from NOTES.md for semantic meaning.
    """

    AUTO = 0
    COOL = 1
    DRY = 2
    FAN = 3
    HEAT = 4
    AUTO_COOL = 11
    AUTO_DRY = 12
    AUTO_FAN = 13
    AUTO_HEAT = 14
    COOL_STORAGE = 21
    HOT_WATER = 24
    NULL_MODE = 255


class InOperationVentMode(SamsungEnum, IntEnum):
    """
    Ventilation operation mode (Message 0x4004).
    Label (NASA.prc): ENUM_IN_OPERATION_VENT_MODE
    Label (NasaConst.java): NASA_ERV_OPMODE
    XML ProtocolID: ENUM_IN_OPERATION_VENT_MODE
    """

    NORMAL = 0
    HEAT_EXCHANGE = 1  # XML: HeatEx
    BYPASS = 2
    NORMAL_PURIFY = 3  # XML: Normal+Purify
    HEAT_EXCHANGE_PURIFY = 4  # XML: HeatEx+Purify
    PURIFY = 5
    SLEEP = 6
    BYPASS_PURIFY = 7  # XML: Bypass+Purify
    # XML Default: Unknown


class InFanModeReal(SamsungEnum, IntEnum):
    """
    Indoor unit current air volume (Message 0x4007).
    Label (NASA.prc): ENUM_IN_FAN_MODE_REAL
    XML ProtocolID: ENUM_in_fan_mode_real
    """

    LOW = 1
    MID = 2
    HIGH = 3
    TURBO = 4
    AUTO_LOW = 10
    AUTO_MID = 11
    AUTO_HIGH = 12
    UL = 13  # Ultra Low?
    LL = 14  # Low Low?
    HH = 15  # High High?
    SPEED = 16  # Generic speed?
    NATURAL_LOW = 17
    NATURAL_MID = 18
    NATURAL_HIGH = 19
    OFF = 254
    # XML Default: Unknown


class InLouverHlPartSwing(SamsungEnum, IntEnum):
    """
    Up and down wind direction setting/status (partial swing) (Message 0x4012).
    Label (NASA.prc): ENUM_IN_LOUVER_HL_PART_SWING
    XML ProtocolID: ENUM_in_louver_hl_part_swing
    """

    SWING_OFF = 0  # XML: Sing Off
    LOUVER_1 = 1
    LOUVER_2 = 2
    LOUVER_1_2 = 3
    LOUVER_3 = 4
    LOUVER_1_3 = 5
    LOUVER_2_3 = 6
    LOUVER_1_2_3 = 7
    LOUVER_4 = 8
    LOUVER_1_4 = 9
    LOUVER_2_4 = 10
    LOUVER_1_2_4 = 11
    LOUVER_3_4 = 12
    LOUVER_1_3_4 = 13
    LOUVER_2_3_4 = 14
    SWING_ON = 15
    H_H_H = 64
    M_H_H = 65
    V_H_H = 66
    H_M_H = 68
    M_M_H = 69
    V_M_H = 70
    H_V_H = 72
    M_V_H = 73
    V_V_H = 74
    H_H_M = 80
    M_H_M = 81
    V_H_M = 82
    H_M_M = 84
    M_M_M = 85
    V_M_M = 86
    H_V_M = 88
    M_V_M = 89
    V_V_M = 90
    H_H_V = 96
    M_H_V = 97
    V_H_V = 98
    H_M_V = 100
    M_M_V = 101
    V_M_V = 102
    H_V_V = 104
    M_V_V = 105
    V_V_V = 106
    # XML Default: Unknown


class ErvFanSpeed(SamsungEnum, IntEnum):  # Or InFanVentMode
    """
    Indoor unit current air volume for ERV (Message 0x4008).
    Label (NASA.prc): ENUM_IN_FAN_VENT_MODE
    Label (NasaConst.java): NASA_ERV_FANSPEED
    XML ProtocolID: ENUM_IN_FAN_VENT_MODE
    """

    AUTO = 0
    LOW = 1
    MID = 2
    HIGH = 3
    TURBO = 4
    # XML Default: Unknown


class DhwOpMode(SamsungEnum, IntEnum):  # Or InWaterHeaterMode
    """
    Water heater mode (DHW) (Message 0x4066).
    Label (NASA.prc): ENUM_IN_WATER_HEATER_MODE
    Label (NasaConst.java): NASA_DHW_OPMODE
    Remarks: "0 Eco, 1 Standard, 2 Power, 3 Force"
    """

    ECO = 0
    STANDARD = 1
    POWER = 2
    FORCE = 3


class InThermostatStatus(SamsungEnum, IntEnum):  # 0x4069 and 0x406A
    """
    Hydro External Thermostat status (Message 0x4069).
    Label (NASA.prc): ENUM_IN_THERMOSTAT_STATUS
    Remarks: "0 Off, 1 Cool, 2 Heat"
    """

    OFF = 0
    COOL = 1
    HEAT = 2


class InBackupHeater(SamsungEnum, IntEnum):
    """
    Backup heater mode (Message 0x406C).
    Label (NASA.prc): ENUM_IN_BACKUP_HEATER
    Remarks: "0 Off, 1 Step 1, 2 Step 2"
    """

    OFF = 0
    STEP_1 = 1
    STEP_2 = 2


class DhwReferenceTemp(SamsungEnum, IntEnum):  # Or InReferenceEhsTemp
    """
    Hydro Control Choice / DHW Reference Temperature source (Message 0x406F).
    Label (NASA.prc): ENUM_IN_REFERENCE_EHS_TEMP
    Label (NasaConst.java): NASA_DHW_REFERENCE_TEMP
    Remarks: "0 Room, 1 Water out"
    """

    ROOM = 0
    WATER_OUT = 1


class In2WayValve(SamsungEnum, IntEnum):
    """
    2-Way Valve state (Message 0x408A).
    Label (NASA.prc): ENUM_IN_2WAY_VALVE
    Remarks: "0 Off, 2 CV, 3 Boiler"
    """

    OFF = 0
    VALUE_1 = 1
    CV = 2  # Constant Value?
    BOILER = 3


class InFsv2041WaterLawTypeHeating(SamsungEnum, IntEnum):
    """
    FSV Water Law Type for Heating (Message 0x4093).
    Label (NASA.prc): ENUM_IN_FSV_2041
    Remarks: "1 Floor, 2 FCU"
    """

    FLOOR = 1
    FCU = 2


class InFsv2081WaterLawTypeCooling(SamsungEnum, IntEnum):
    """
    FSV Water Law Type for Cooling (Message 0x4094).
    Label (NASA.prc): ENUM_IN_FSV_2081
    Remarks: "1 Floor, 2 FCU"
    """

    FLOOR = 1
    FCU = 2


class InUseThermostat(SamsungEnum, IntEnum):
    """FSV Use Thermostat setting (FSV 209*)."""

    NO = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4


class InFsv3011EnableDhw(SamsungEnum, IntEnum):
    """
    FSV Enable DHW setting (Message 0x4097).
    Label (NASA.prc): ENUM_IN_FSV_3011
    Label (NasaConst.java): NASA_ENABLE_DHW
    Remarks: "values 0="No" up to 2="2""
    """

    NO = 0
    VALUE_1 = 1  # Possibly YES or some level
    VALUE_2 = 2  # Possibly another level


class InFsv3042DayOfWeek(SamsungEnum, IntEnum):
    """
    FSV Day of Week setting (Message 0x409A).
    Label (NASA.prc): ENUM_IN_FSV_3042
    Remarks: "Sunday=0, Monday=1 .. up to 7=Everyday"
    """

    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    EVERYDAY = 7


class InFsv3061UseDhwThermostat(SamsungEnum, IntEnum):
    """
    FSV Use DHW Thermostat setting (Message 0x409C).
    Label (NASA.prc): ENUM_IN_FSV_3061
    Label (NasaConst.java): NASA_USE_DHW_THERMOSTAT
    XML ProtocolID: ENUM_IN_FSV_3061
    """

    NO = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3


class InFsv3071(SamsungEnum, IntEnum):
    """FSV setting (Message 0x409D). Label (NASA.prc): ENUM_IN_FSV_3071"""

    ROOM = 0
    TANK = 1


class InStateAutoStaticPressureRunning(SamsungEnum, IntEnum):
    """
    Auto Static Pressure Running state (Message 0x40BB).
    Label (NASA.prc): ENUM*IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    XML ProtocolID: ENUM_IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    """

    OFF = 0
    COMPLETE = 1
    RUNNING = 2


class InFsv2093(SamsungEnum, IntEnum):
    """
    FSV setting (Message 0x4127).
    Label (NASA.prc): ENUM_IN_FSV_2093
    Remarks: "Min = 1 Max = 4"
    """

    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4


class InFsv5022(SamsungEnum, IntEnum):
    """
    FSV setting (Message 0x4128).
    Label (NASA.prc): ENUM_IN_FSV_5022
    Remarks: "Min = 0 Max = 1"
    """

    VALUE_0 = 0
    VALUE_1 = 1


class InFsv2094(SamsungEnum, IntEnum):
    """
    FSV setting (Message 0x412A).
    Label (NASA.prc): ENUM_IN_FSV_2094
    Remarks: "values 0="No" up to 4="4""
    """

    NO = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4


class OutOperationServiceOp(SamsungEnum, IntEnum):
    """
    Outdoor unit service operation steps (Message 0x8000).
    Label (NASA.prc): ENUM_OUT_OPERATION_SERVICE_OP
    Remarks: "2 Heating test run, 3 Pump out, 13 Cooling test run, 14 Pump down"
    """

    HEATING_TEST_RUN = 2
    PUMP_OUT = 3
    COOLING_TEST_RUN = 13
    PUMP_DOWN = 14


class OutdoorOperationMode(SamsungEnum, IntEnum):  # Or OutOperationHeatCool
    """
    Outdoor unit cooling/heating mode (Message 0x8003).
    Label (NASA.prc): ENUM*OUT_OPERATION_HEATCOOL
    Label (NasaConst.java): NASA_OUTDOOR_OPERATION_MODE
    Remarks: "1 Cool, 2 Heat, 3 CoolMain, 4 HeatMain"
    """

    UNDEFINED = 0
    COOL = 1
    HEAT = 2
    COOL_MAIN = 3
    HEAT_MAIN = 4


class OutOpTestOpComplete(SamsungEnum, IntEnum):
    """
    Outdoor unit test operation complete status (Message 0x8046).
    Label (NASA.prc): ENUM*OUT_OP_TEST_OP_COMPLETE
    Label (NasaConst.java): NASA_OUTDOOR_TEST_OP_COMPLETE
    """

    NOT_COMPLETE = 0  # Assumed
    COMPLETE = 1  # Assumed


class OutdoorIndoorDefrostStep(SamsungEnum, IntEnum):  # Or OutDeiceStepIndoor
    """
    Indoor unit defrost operation steps (from outdoor unit's perspective) (Message 0x8061).
    Label (NASA.prc): ENUM*OUT_DEICE_STEP_INDOOR
    Label (NasaConst.java): NASA_OUTDOOR_INDOOR_DEFROST_STEP
    Remarks: "1 Defrost stage 1, 2 Defrost stage 2, 3 Defrost stage 3, 7 Defrost operation end stage, 255 No defrost operation"
    """

    DEFROST_STAGE_1 = 1
    DEFROST_STAGE_2 = 2
    DEFROST_STAGE_3 = 3
    DEFROST_END_STAGE = 7
    NO_DEFROST_OPERATION = 255


class OutOutdoorSystemReset(SamsungEnum, IntEnum):
    """
    Outdoor unit system reset command/status (Message 0x8065).
    Label (NasaConst.java): NASA_OUTDOOR_SYSTEM_RESET
    """

    NO_ACTION = 0  # Assumed
    RESET = 1  # Assumed


class OutCheckRefResult(SamsungEnum, IntEnum):
    """
    Refrigerant amount determination result (Message 0x809C).
    Label (NASA.prc): ENUM_OUT_CHECK_REF_RESULT
    """

    NOT_INSPECTED = 0  # XML: RefResult_NotInspect
    NORMAL_COMPLETION = 1  # XML: 정상완료 (Normal completion)
    NOT_JUDGED = 2  # XML: RefResult_NotJudgment
    SUBCOOLING_FAIL = 3  # XML: 과냉도 확보불가 (Subcooling cannot be secured)
    NORMAL = 4  # XML: RefResult_Normal
    INSUFFICIENT = 5  # XML: RefResult_Insufficient
    CANNOT_JUDGE = 6  # XML: 판단불가 (Cannot judge)
    TEMP_RANGE_EXCEEDED = 7  # XML: 온도범위 초과 (Temperature range exceeded)


class OutOutdoorCoolonlyModel(SamsungEnum, IntEnum):
    """
    Outdoor unit cool-only model status (Message 0x809D).
    Label (NasaConst.java): NASA_OUTDOOR_COOLONLY_MODEL
    """

    NO_HEAT_PUMP = 0  # Assumed (i.e., is cool only)
    YES_HEAT_PUMP = 1  # Assumed (i.e., not cool only)


class OutEhsWateroutType(SamsungEnum, IntEnum):
    """
    EHS Water Outlet Type (Message 0x80D8).
    Label (NASA.prc): ENUM_OUT_EHS_WATEROUT_TYPE
    Remarks: "0 Default, 1 70°C"
    """

    DEFAULT = 0
    TEMP_70C = 1


# Generic Enums for unknown ?? messages based on prefix
class InUnknown400F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x400F. Specifics unknown."""

    pass


class InUnknown4010(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4010. Specifics unknown."""

    pass


class InUnknown4015(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4015. Specifics unknown."""

    pass


class InUnknown4029(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4029. Specifics unknown."""

    pass


class InUnknown402A(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402A. Specifics unknown."""

    pass


class InUnknown402B(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402B. Specifics unknown."""

    pass


class InUnknown402D(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402D. Specifics unknown."""

    pass


class InUnknown4031(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4031. Specifics unknown."""

    pass


class InUnknown4035(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4035. Specifics unknown."""

    pass


class InUnknown4047(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4047. Specifics unknown."""

    pass


class InUnknown4048(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4048. Specifics unknown."""

    pass


class InUnknown404F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x404F. Specifics unknown."""

    pass


class InUnknown4051(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4051. Specifics unknown."""

    pass


class InUnknown4059(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4059. Specifics unknown."""

    pass


class InUnknown405F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x405F. Specifics unknown."""

    pass


class InUnknown4073(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4073. Specifics unknown."""

    pass


class InUnknown4074(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4074. Specifics unknown."""

    pass


class InUnknown4077(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4077. Specifics unknown."""

    pass


class InUnknown407B(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x407B. Specifics unknown."""

    pass


class InUnknown407D(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x407D. Specifics unknown."""

    pass


class InUnknown4085(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4085. Specifics unknown."""

    pass


class InFsv4011(SamsungEnum, IntEnum):
    """FSV setting (Message 0x409E). Label (NASA.prc): ENUM_IN_FSV_4011"""

    DHW = 0
    HEATING = 1


class InFsv4021(SamsungEnum, IntEnum):
    """FSV setting (Message 0x409F). Label (NASA.prc): ENUM_IN_FSV_4021"""

    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2


class InFsv4022(SamsungEnum, IntEnum):
    """FSV setting (Message 0x40A0). Label (NASA.prc): ENUM_IN_FSV_4022"""

    BUH_BSH_BOTH = 0  # XML: BUH/BSH Both
    BUH = 1
    BSH = 2


class InFsv4041(SamsungEnum, IntEnum):
    """FSV setting (Message 0x40C0). Label (NASA.prc): ENUM_IN_FSV_4041"""

    NO = 0
    VALUE_1 = 1
    VALUE_2 = 2


class InFsv4061(SamsungEnum, IntEnum):
    """FSV setting (Message 0x411A). Label (NASA.prc): ENUM_IN_FSV_4061"""

    VALUE_0 = 0
    VALUE_1 = 1


class InFsv5033(SamsungEnum, IntEnum):
    """FSV setting (Message 0x4107). Label (NASA.prc): ENUM_IN_FSV_5033"""

    A2A = 0
    DHW = 1


class InFsv5042(SamsungEnum, IntEnum):
    """FSV setting (Message 0x40A5). Label (NASA.prc): ENUM_IN_FSV_5042"""

    ALL = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3


class InFsv5043(SamsungEnum, IntEnum):
    """FSV setting (Message 0x40A6). Label (NASA.prc): ENUM_IN_FSV_5043"""

    LOW = 0
    HIGH = 1


class InFsv5051(SamsungEnum, IntEnum):
    """FSV setting (Message 0x40A7). Label (NASA.prc): ENUM_IN_FSV_5051"""

    NO = 0
    YES = 1


class InFsv5061(SamsungEnum, IntEnum):  # 0x40B4
    """Indoor unit enum for FSV message 0x40B4. Specifics unknown."""

    pass


class InUnknown40B5(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40B5. Specifics unknown."""

    pass


class InFsv4044(SamsungEnum, IntEnum):  # 0x40C1
    """Indoor unit enum for FSV message 0x40C1. Specifics unknown."""

    pass


class InFsv4051(SamsungEnum, IntEnum):  # 0x40C2
    """Indoor unit enum for FSV message 0x40C2. Specifics unknown."""

    pass


class InFsv4053(SamsungEnum, IntEnum):  # 0x40C3
    """Indoor unit enum for FSV message 0x40C3. Specifics unknown."""

    pass


class InUnknown40C6(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40C6. Specifics unknown."""

    pass


class InUnknown40E3(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40E3. Specifics unknown."""

    pass


class InChillerWaterlawSensor(SamsungEnum, IntEnum):
    """
    DMV Chiller Option / Chiller Water Law Sensor (Message 0x40E7).
    Label (NASA.prc): ENUM*IN_CHILLER_WATERLAW_SENSOR
    XML ProtocolID: ENUM_IN_CHILLER_WATERLAW_SENSOR
    """

    OUTDOOR = 0
    ROOM = 1


class InChillerSettingSilentLevel(SamsungEnum, IntEnum):
    """
    Chiller Setting Silent Level (Message 0x40FB).
    Label (NASA.prc): ENUM_IN_CHILLLER_SETTING_SILENT_LEVEL (Typo in source)
    XML ProtocolID: ENUM_IN_CHILLLER_SETTING_SILENT_LEVEL
    """

    NONE = 0
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3


class InChillerSettingDemandLevel(SamsungEnum, IntEnum):
    """
    Chiller Setting Demand Level (Message 0x40FC).
    Label (NASA.prc): ENUM_IN_CHILLER_SETTING_DEMAND_LEVEL
    XML ProtocolID: ENUM_IN_CHILLER_SETTING_DEMAND_LEVEL
    """

    PERCENT_100 = 0
    PERCENT_95 = 1
    PERCENT_90 = 2
    PERCENT_85 = 3
    PERCENT_80 = 4
    PERCENT_75 = 5
    PERCENT_70 = 6
    PERCENT_65 = 7
    PERCENT_60 = 8
    PERCENT_55 = 9
    PERCENT_50 = 10
    NOT_APPLY = 11
    # XML Default: Unknown


class InTdmIndoorType(SamsungEnum, IntEnum):
    """
    TDM Indoor Type (Message 0x4108).
    Label (NASA.prc): ENUM_IN_TDM_INDOOR_TYPE
    XML ProtocolID: ENUM_IN_TDM_INDOOR_TYPE
    """

    A2A = 0
    A2W = 1


class In3WayValve2(SamsungEnum, IntEnum):
    """
    3-Way Valve 2 state (Message 0x4113).
    Label (NASA.prc): ENUM_IN_3WAY_VALVE_2
    XML ProtocolID: ENUM_IN_3WAY_VALVE_2
    """

    ROOM = 0
    TANK = 1


class InUnknown4117(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4117. Specifics unknown."""

    pass


class InRoomTempSensorZone2(SamsungEnum, IntEnum):  # 0x4118
    """Indoor unit enum for message 0x4118 (Room Temp Sensor Zone 2). Specifics unknown."""

    pass


class InFsv5081(SamsungEnum, IntEnum):  # 0x411B
    """Indoor unit enum for FSV message 0x411B. Specifics unknown."""

    pass


class InFsv5091(SamsungEnum, IntEnum):  # 0x411C
    """Indoor unit enum for FSV message 0x411C. Specifics unknown."""

    pass


class InFsv5094(SamsungEnum, IntEnum):  # 0x411D
    """Indoor unit enum for FSV message 0x411D. Specifics unknown."""

    pass


class InSilenceLevel(SamsungEnum, IntEnum):  # 0x4129
    """Indoor unit enum for message 0x4129 (Silence Level). Specifics unknown."""

    pass


class IndoorModelInformation(SamsungEnum, IntEnum):  # Derived from VAR_in_model_information (0x4229) Enum block in XML
    """Indoor Unit Model Information (derived from Message 0x4229 in XML)."""

    MASTER_N = 12
    SLIM_1WAY = 31
    BIG_SLIM_1WAY = 32
    GLOBAL_4WAY = 51
    GLOBAL_MINI_4WAY = 52
    MINI_4WAY = 53
    BIG_DUCT = 62
    GLOBAL_BIG_DUCT = 63
    FRESH_DUCT = 68
    BIG_CEILING = 71
    MINI_AHU = 98
    ERV_PLUS = 108
    EHS_SPLIT = 115
    EHS_MONO = 116
    EHS_TDM = 117
    EHS_HT = 125  # Also covers 125-129 range
    DIFFUSER = 170
    # Ranges like FSC_PAC (1-9), RAC (10-19) etc. are harder to represent directly in IntEnum members.
    # Only discrete values are added.
    # XML Default: Unknown


class OutUnknown8002(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8002. Specifics unknown."""

    pass


class OutUnknown8005(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8005. Specifics unknown."""

    pass


class OutUnknown800D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x800D. Specifics unknown."""

    pass


class OutUnknown8031(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8031. Specifics unknown."""

    pass


class OutUnknown8032(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8032. Specifics unknown."""

    pass


class OutUnknown8033(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8033. Specifics unknown."""

    pass


class OutUnknown803F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x803F. Specifics unknown."""

    pass


class OutUnknown8043(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8043. Specifics unknown."""

    pass


class OutUnknown8045(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8045. Specifics unknown."""

    pass


class OutUnknown8048(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8048. Specifics unknown."""

    pass


class OutUnknown805E(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x805E. Specifics unknown."""

    pass


class OutUnknown8063(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8063. Specifics unknown."""

    pass


class OutUnknown8077(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8077. Specifics unknown."""

    pass


class OutUnknown8078(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8078. Specifics unknown."""

    pass


class OutUnknown8079(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8079. Specifics unknown."""

    pass


class OutUnknown807A(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807A. Specifics unknown."""

    pass


class OutUnknown807B(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807B. Specifics unknown."""

    pass


class OutUnknown807C(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807C. Specifics unknown."""

    pass


class OutUnknown807D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807D. Specifics unknown."""

    pass


class OutUnknown807E(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807E. Specifics unknown."""

    pass


class OutUnknown807F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807F. Specifics unknown."""

    pass


class OutdoorExtCmdOperation(SamsungEnum, IntEnum):  # 0x8081
    """Outdoor unit enum for message 0x8081 (NASA_OUTDOOR_EXT_CMD_OPERATION). Specifics unknown."""

    pass


class OutUnknown8083(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8083. Specifics unknown."""

    pass


class OutUnknown808C(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808C. Specifics unknown."""

    pass


class OutUnknown808D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808D. Specifics unknown."""

    pass


class OutUnknown808F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808F. Specifics unknown."""

    pass


class OutdoorDredLevel(SamsungEnum, IntEnum):  # 0x80A7
    """Outdoor unit enum for message 0x80A7 (NASA_OUTDOOR_DRED_LEVEL). Specifics unknown."""

    pass


class OutUnknown80A8(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80A8. Specifics unknown."""

    pass


class OutUnknown80A9(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80A9. Specifics unknown."""

    pass


class OutUnknown80AA(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AA. Specifics unknown."""

    pass


class OutUnknown80AB(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AB. Specifics unknown."""

    pass


class OutUnknown80AE(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AE. Specifics unknown."""

    pass


class OutUnknown80B1(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80B1. Specifics unknown."""

    pass


class OutdoorChSwitchValue(SamsungEnum, IntEnum):  # 0x80B2
    """Outdoor unit enum for message 0x80B2 (NASA_OUTDOOR_CH_SWITCH_VALUE). Specifics unknown."""

    pass


class OutUnknown80B6(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80B6. Specifics unknown."""

    pass


class OutUnknown80BC(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80BC. Specifics unknown."""

    pass


class OutUnknown80CE(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80CE. Specifics unknown."""

    pass
