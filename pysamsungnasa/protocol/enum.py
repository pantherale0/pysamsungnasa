"""Protocol enums."""

from enum import Enum, IntEnum


class SamsungEnum(Enum):
    """Define the base samsung enum."""

    def __str__(self):
        return self.name

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class AddressClass(SamsungEnum, IntEnum):
    """NASA Device Address Class from protocol byte 3 & 6."""

    UNKNOWN = 0x00
    """Unknown or unspecified device address class"""
    OUTDOOR = 0x10
    """Outdoor unit (condenser)"""
    HTU = 0x11
    """Heat Transfer Unit"""
    INDOOR = 0x20
    """Indoor unit (evaporator)"""
    ERV = 0x30
    """Energy Recovery Ventilation unit"""
    DIFFUSER = 0x35
    """Air diffuser or outlet device"""
    MCU = 0x38
    """Master Control Unit"""
    RMC = 0x40
    """Remote Control Module"""
    WIRED_REMOTE = 0x50
    """Wired remote control"""
    PIM = 0x58
    """PIM module"""
    SIM = 0x59
    """SIM module"""
    PEAK = 0x5A
    """PEAK device"""
    POWER_DIVIDER = 0x5B
    """Power divider device"""
    WIFI_KIT = 0x62
    """WiFi connectivity kit"""
    CENTRAL_CONTROLLER = 0x65
    """Central control system"""
    JIG_TESTER = 0x80
    """JIG tester equipment"""
    BML = 0xB0
    """Broadcast Self Layer"""
    BCL = 0xB1
    """Broadcast Control Layer"""
    BSL = 0xB2
    """Broadcast Set Layer"""
    BCSL = 0xB3
    """Broadcast Control and Set Layer"""
    BMDL = 0xB4
    """Broadcast Module Layer"""
    BCSM = 0xB7
    """Broadcast CSM"""
    BLL = 0xB8
    """Broadcast Local Layer"""
    BCSML = 0xB9
    """Broadcast CSML"""
    UNDEFINED = 0xFF
    """Undefined or invalid address class"""


class PacketType(SamsungEnum, IntEnum):
    """NASA Packet Types from protocol byte 10."""

    UNKNOWN = -1
    """Unknown packet type"""
    STANDBY = 0
    """Standby mode packet"""
    NORMAL = 1
    """Normal operation packet"""
    GATHERING = 2
    """Data gathering packet"""
    INSTALL = 3
    """Installation mode packet"""
    DOWNLOAD = 4
    """Download/firmware packet"""


class DataType(SamsungEnum, IntEnum):
    """NASA Data Types from protocol byte 10.

    (Previously PayloadTypes as StrEnum)
    """

    UNKNOWN = -1
    """Unknown data type"""
    UNDEFINED = 0
    """Undefined payload"""
    READ = 1
    """Read request or data"""
    WRITE = 2
    """Write command"""
    REQUEST = 3
    """Request message"""
    NOTIFICATION = 4
    """Notification or notification data"""
    RESPONSE = 5
    """Response to a request"""
    ACK = 6
    """Acknowledgement"""
    NACK = 7
    """Negative acknowledgement"""


class MessageSetType(SamsungEnum, IntEnum):
    """NASA Message Set Type derived from Message Number (protocol bytes 13-14)."""

    ENUM = 0
    """1 byte payload"""
    VARIABLE = 1
    """2 bytes payload"""
    LONG_VARIABLE = 2
    """4 bytes payload"""
    STRUCTURE = 3
    """Structure payload"""


# Specific Message Enums from NOTES.md


class OutOpCheckRefStep(SamsungEnum, IntEnum):
    """Refrigerant amount level (Message 0x808E).

    Label (NASA.prc): ENUM*OUT_OP_CHECK_REF_STEP

    As per NOTES.md, Min = 0, Max = 8.
    """

    LEVEL_0 = 0
    """Refrigerant level 0"""
    LEVEL_1 = 1
    """Refrigerant level 1"""
    LEVEL_2 = 2
    """Refrigerant level 2"""
    LEVEL_3 = 3
    """Refrigerant level 3"""
    LEVEL_4 = 4
    """Refrigerant level 4"""
    LEVEL_5 = 5
    """Refrigerant level 5"""
    LEVEL_6 = 6
    """Refrigerant level 6"""
    LEVEL_7 = 7
    """Refrigerant level 7"""
    LEVEL_8 = 8
    """Refrigerant level 8"""


class InOperationPower(SamsungEnum, IntEnum):
    """Indoor unit power on/off (Message 0x4000).

    Label (NASA.prc): ENUM*IN_OPERATION_POWER
    """

    OFF = 0
    """Power is off"""
    ON_STATE_1 = 1
    """Power is on (state 1)"""
    ON_STATE_2 = 2
    """Power is on (state 2)"""


class InOperationMode(SamsungEnum, IntEnum):
    """Indoor unit control mode (Message 0x4001).

    Label (NASA.prc): ENUM_IN_OPERATION_MODE
    """

    AUTO = 0
    """Auto mode"""
    COOL = 1
    """Cool mode"""
    DRY = 2
    """Dry mode"""
    FAN = 3
    """Fan only mode"""
    HEAT = 4
    """Heat mode"""
    COOL_STORAGE = 21
    """Cool storage mode"""
    HOT_WATER = 24
    """Hot water mode"""


class InFanMode(SamsungEnum, IntEnum):
    """Indoor unit fan mode (Message 0x4006)."""

    AUTO = 0
    """Auto fan speed"""
    LOW = 1
    """Low fan speed"""
    MID = 2
    """Medium fan speed"""
    HIGH = 3
    """High fan speed"""
    TURBO = 4
    """Turbo/Maximum fan speed"""


class InAltMode(SamsungEnum, IntEnum):
    """Indoor unit alternative mode (Message 0x4060)."""

    OFF = 0
    """Alternative mode is off"""
    ON = 9
    """Alternative mode is on"""


class OutdoorOperationStatus(SamsungEnum, IntEnum):
    """Outdoor Driving Mode / Outdoor Operation Status (Message 0x8001).

    Derived from Label (NasaConst.java): NASA_OUTDOOR_OPERATION_STATUS
    and remarks for ENUM_OUT_OPERATION_ODU_MODE.
    """

    OP_STOP = 0
    """Operation stopped"""
    OP_SAFETY = 1
    """Safety mode operation"""
    OP_NORMAL = 2
    """Normal operation"""
    OP_BALANCE = 3
    """Balance mode operation"""
    OP_RECOVERY = 4
    """Recovery mode operation"""
    OP_DEICE = 5
    """Defrosting operation"""
    OP_COMPDOWN = 6
    """Compressor down mode"""
    OP_PROHIBIT = 7
    """Operation prohibited"""
    OP_LINEJIG = 8
    """Line JIG testing"""
    OP_PCBJIG = 9
    """PCB JIG testing"""
    OP_TEST = 10
    """General test mode"""
    OP_CHARGE = 11
    """Refrigerant charging operation"""
    OP_PUMPDOWN = 12
    """Pump down operation"""
    OP_PUMPOUT = 13
    """Pump out operation"""
    OP_VACCUM = 14
    """Vacuum operation"""
    OP_CALORYJIG = 15
    """Calorimeter JIG testing"""
    OP_PUMPDOWNSTOP = 16
    """Pump down stopped"""
    OP_SUBSTOP = 17
    """Substation stopped"""
    OP_CHECKPIPE = 18
    """Pipe check operation"""
    OP_CHECKREF = 19
    """Refrigerant check operation"""
    OP_FPTJIG = 20
    """FPT JIG testing"""
    OP_NONSTOP_HEAT_COOL_CHANGE = 21
    """Non-stop heat/cool mode change"""
    OP_AUTO_INSPECT = 22
    """Automatic inspection"""
    OP_ELECTRIC_DISCHARGE = 23
    """Electric discharge operation"""
    OP_SPLIT_DEICE = 24
    """Split defrost operation"""
    OP_INVETER_CHECK = 25
    """Inverter check operation"""
    OP_NONSTOP_DEICE = 26
    """Non-stop defrost operation"""
    OP_REM_TEST = 27
    """REM test operation"""
    OP_RATING = 28
    """Rating operation"""
    OP_PC_TEST = 29
    """PC test operation"""
    OP_PUMPDOWN_THERMOOFF = 30
    """Pump down with thermostat off"""
    OP_3PHASE_TEST = 31
    """3-phase test operation"""
    OP_SMARTINSTALL_TEST = 32
    """Smart install test operation"""
    OP_DEICE_PERFORMANCE_TEST = 33
    """Defrost performance test"""
    OP_INVERTER_FAN_PBA_CHECK = 34
    """Inverter fan PBA check"""
    OP_AUTO_PIPE_PAIRING = 35
    """Automatic pipe pairing"""
    OP_AUTO_CHARGE = 36
    """Automatic refrigerant charging"""


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
    """Indoor unit current operation mode (Message 0x4002).

    Label (NASA.prc): ENUM_IN_OPERATION_MODE_REAL

    XML ProtocolID: ENUM_in_operation_mode_real
    """

    AUTO = 0
    """Auto mode"""
    COOL = 1
    """Cool mode"""
    DRY = 2
    """Dry mode"""
    FAN = 3
    """Fan only mode"""
    HEAT = 4
    """Heat mode"""
    AUTO_COOL = 11
    """Auto cool mode"""
    AUTO_DRY = 12
    """Auto dry mode"""
    AUTO_FAN = 13
    """Auto fan mode"""
    AUTO_HEAT = 14
    """Auto heat mode"""
    COOL_STORAGE = 21
    """Cool storage mode"""
    HOT_WATER = 24
    """Hot water mode"""
    NULL_MODE = 255
    """Null/unknown mode"""


class InOperationVentMode(SamsungEnum, IntEnum):
    """Ventilation operation mode (Message 0x4004).

    Label (NASA.prc): ENUM_IN_OPERATION_VENT_MODE

    Label (NasaConst.java): NASA_ERV_OPMODE

    XML ProtocolID: ENUM_IN_OPERATION_VENT_MODE
    """

    NORMAL = 0
    """Normal ventilation mode"""
    HEAT_EXCHANGE = 1
    """Heat exchange mode"""
    BYPASS = 2
    """Bypass mode"""
    NORMAL_PURIFY = 3
    """Normal with purification"""
    HEAT_EXCHANGE_PURIFY = 4
    """Heat exchange with purification"""
    PURIFY = 5
    """Purification mode"""
    SLEEP = 6
    """Sleep mode"""
    BYPASS_PURIFY = 7
    """Bypass with purification"""


class InFanModeReal(SamsungEnum, IntEnum):
    """Indoor unit current air volume (Message 0x4007).

    Label (NASA.prc): ENUM_IN_FAN_MODE_REAL

    XML ProtocolID: ENUM_in_fan_mode_real
    """

    LOW = 1
    """Low fan speed"""
    MID = 2
    """Medium fan speed"""
    HIGH = 3
    """High fan speed"""
    TURBO = 4
    """Turbo fan speed"""
    AUTO_LOW = 10
    """Auto low fan speed"""
    AUTO_MID = 11
    """Auto medium fan speed"""
    AUTO_HIGH = 12
    """Auto high fan speed"""
    UL = 13
    """Ultra low fan speed"""
    LL = 14
    """Very low fan speed"""
    HH = 15
    """Very high fan speed"""
    SPEED = 16
    """Generic speed mode"""
    NATURAL_LOW = 17
    """Natural low wind speed"""
    NATURAL_MID = 18
    """Natural medium wind speed"""
    NATURAL_HIGH = 19
    """Natural high wind speed"""
    OFF = 254
    """Fan is off"""


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


class ErvFanSpeed(SamsungEnum, IntEnum):
    """Indoor unit current air volume for ERV (Message 0x4008).

    Label (NASA.prc): ENUM_IN_FAN_VENT_MODE

    Label (NasaConst.java): NASA_ERV_FANSPEED

    XML ProtocolID: ENUM_IN_FAN_VENT_MODE
    """

    AUTO = 0
    """Auto fan speed"""
    LOW = 1
    """Low fan speed"""
    MID = 2
    """Medium fan speed"""
    HIGH = 3
    """High fan speed"""
    TURBO = 4
    """Turbo fan speed"""


class DhwOpMode(SamsungEnum, IntEnum):
    """Water heater mode (DHW) (Message 0x4066).

    Label (NASA.prc): ENUM_IN_WATER_HEATER_MODE

    Label (NasaConst.java): NASA_DHW_OPMODE
    """

    ECO = 0
    """Eco mode"""
    STANDARD = 1
    """Standard mode"""
    POWER = 2
    """Power mode"""
    FORCE = 3
    """Force mode"""


class InThermostatStatus(SamsungEnum, IntEnum):
    """Hydro External Thermostat status (Message 0x4069).

    Label (NASA.prc): ENUM_IN_THERMOSTAT_STATUS
    """

    OFF = 0
    """Thermostat is off"""
    COOL = 1
    """Thermostat in cool mode"""
    HEAT = 2
    """Thermostat in heat mode"""


class InBackupHeater(SamsungEnum, IntEnum):
    """Backup heater mode (Message 0x406C).

    Label (NASA.prc): ENUM_IN_BACKUP_HEATER
    """

    OFF = 0
    """Backup heater is off"""
    STEP_1 = 1
    """Backup heater step 1"""
    STEP_2 = 2
    """Backup heater step 2"""


class DhwReferenceTemp(SamsungEnum, IntEnum):
    """Hydro Control Choice / DHW Reference Temperature source (Message 0x406F).

    Label (NASA.prc): ENUM_IN_REFERENCE_EHS_TEMP

    Label (NasaConst.java): NASA_DHW_REFERENCE_TEMP
    """

    ROOM = 0
    """Room temperature as reference"""
    WATER_OUT = 1
    """Water outlet temperature as reference"""


class In2WayValve(SamsungEnum, IntEnum):
    """
    2-Way Valve state (Message 0x408A).
    Label (NASA.prc): ENUM_IN_2WAY_VALVE
    Remarks: "0 Off, 2 CV, 3 Boiler"
    """

    OFF = 0
    """2-Way valve is off"""
    VALUE_1 = 1
    """2-Way valve in state 1"""
    CV = 2
    """2-Way valve in CV mode"""
    BOILER = 3
    """2-Way valve in boiler mode"""


class InFsv2041WaterLawTypeHeating(SamsungEnum, IntEnum):
    """
    FSV #2041: Water Law Type for Heating (Message 0x4093).

    Selects water law for floor heating (UFHs) or fan coil unit (FCU) heating systems.
    Default: 1 (Floor). Range: 1-2.

    Label (NASA.prc): ENUM_IN_FSV_2041
    """

    FLOOR = 1
    """Water law for floor heating (UFH)"""
    FCU = 2
    """Water law for fan coil unit (FCU) heating"""


class InFsv2081WaterLawTypeCooling(SamsungEnum, IntEnum):
    """
    FSV #2081: Water Law Type for Cooling (Message 0x4094).

    Selects water law for floor cooling (UFHs) or fan coil unit (FCU) cooling systems.
    Default: 1 (Floor). Range: 1-2.

    Label (NASA.prc): ENUM_IN_FSV_2081
    """

    FLOOR = 1
    """Water law for floor cooling (UFH)"""
    FCU = 2
    """Water law for fan coil unit (FCU) cooling"""


class InUseThermostat(SamsungEnum, IntEnum):
    """FSV Use Thermostat setting (FSV 209*)."""

    NO = 0
    """Thermostat is not used"""
    VALUE_1 = 1
    """Setting option 1"""
    VALUE_2 = 2
    """Setting option 2"""
    VALUE_3 = 3
    """Setting option 3"""
    VALUE_4 = 4
    """Setting option 4"""


class InFsv3011EnableDhw(SamsungEnum, IntEnum):
    """
    FSV #3011: Enable Domestic Hot Water (DHW) (Message 0x4097).

    Controls DHW heating operation mode. Required for DHW operation.
    Default: 0 (No). Range: 0-2.

    Label (NASA.prc): ENUM_IN_FSV_3011
    """

    NO = 0
    """DHW heating disabled"""
    YES_THERMO_ON = 1
    """DHW enabled based on thermostat ON state"""
    YES_THERMO_OFF = 2
    """DHW enabled based on thermostat OFF state"""


class InFsv3042DayOfWeek(SamsungEnum, IntEnum):
    """
    FSV #3042: Day of Week for Schedule (Message 0x409A).

    Selects day(s) for scheduled operation in field setting mode.
    Range: 0-7 (Sunday through Everyday).

    Label (NASA.prc): ENUM_IN_FSV_3042
    """

    SUNDAY = 0
    """Sunday"""
    MONDAY = 1
    """Monday"""
    TUESDAY = 2
    """Tuesday"""
    WEDNESDAY = 3
    """Wednesday"""
    THURSDAY = 4
    """Thursday"""
    FRIDAY = 5
    """Friday"""
    SATURDAY = 6
    """Saturday"""
    EVERYDAY = 7
    """Every day of the week"""


class InFsv3061UseDhwThermostat(SamsungEnum, IntEnum):
    """
    FSV Use DHW Thermostat setting (Message 0x409C).
    Label (NASA.prc): ENUM_IN_FSV_3061
    Label (NasaConst.java): NASA_USE_DHW_THERMOSTAT
    XML ProtocolID: ENUM_IN_FSV_3061
    """

    NO = 0
    """DHW thermostat is not used"""
    VALUE_1 = 1
    """Setting option 1"""
    VALUE_2 = 2
    """Setting option 2"""
    VALUE_3 = 3
    """Setting option 3"""


class InFsv3071(SamsungEnum, IntEnum):
    """
    FSV #3071: Room/Tank Mode Selection (Message 0x409D).

    Selects temperature control reference for heating/cooling.
    Default: Room. Range: 0-1.

    Label (NASA.prc): ENUM_IN_FSV_3071
    """

    ROOM = 0
    """Use room temperature as control reference"""
    TANK = 1
    """Use tank temperature as control reference"""


class InStateAutoStaticPressureRunning(SamsungEnum, IntEnum):
    """
    Auto Static Pressure Running state (Message 0x40BB).
    Label (NASA.prc): ENUM*IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    XML ProtocolID: ENUM_IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    """

    OFF = 0
    """Auto static pressure control is off"""
    COMPLETE = 1
    """Auto static pressure control is complete"""
    RUNNING = 2
    """Auto static pressure control is running"""


class InFsv2093(SamsungEnum, IntEnum):
    """
    FSV #2093: Remote Controller Room Temperature Control (Message 0x4127).

    Sets remote controller room temperature control mode/sensitivity.
    Range: 1-4 (sensitivity levels).

    Label (NASA.prc): ENUM_IN_FSV_2093
    """

    VALUE_1 = 1
    """Sensitivity level 1 (lowest)"""
    VALUE_2 = 2
    """Sensitivity level 2"""
    VALUE_3 = 3
    """Sensitivity level 3"""
    VALUE_4 = 4
    """Sensitivity level 4 (highest)"""


class InFsv5022(SamsungEnum, IntEnum):
    """
    FSV setting (Message 0x4128).
    Label (NASA.prc): ENUM_IN_FSV_5022
    Remarks: "Min = 0 Max = 1"
    """

    VALUE_0 = 0
    """Setting option 0"""
    VALUE_1 = 1
    """Setting option 1"""


class OutOperationServiceOp(SamsungEnum, IntEnum):
    """Outdoor unit service operation steps (Message 0x8000).

    Label (NASA.prc): ENUM_OUT_OPERATION_SERVICE_OP
    """

    HEATING_TEST_RUN = 2
    """Heating test run"""
    PUMP_OUT = 3
    """Pump out operation"""
    COOLING_TEST_RUN = 13
    """Cooling test run"""
    PUMP_DOWN = 14
    """Pump down operation"""


class OutdoorIndoorDefrostStep(SamsungEnum, IntEnum):
    """Indoor unit defrost operation steps (from outdoor unit's perspective) (Message 0x8061).

    Label (NASA.prc): ENUM*OUT_DEICE_STEP_INDOOR

    Label (NasaConst.java): NASA_OUTDOOR_INDOOR_DEFROST_STEP
    """

    DEFROST_STAGE_1 = 1
    """Defrost stage 1"""
    DEFROST_STAGE_2 = 2
    """Defrost stage 2"""
    DEFROST_STAGE_3 = 3
    """Defrost stage 3"""
    DEFROST_END_STAGE = 7
    """Defrost operation end stage"""
    NO_DEFROST_OPERATION = 255
    """No defrost operation"""


class OutOutdoorSystemReset(SamsungEnum, IntEnum):
    """Outdoor unit system reset command/status (Message 0x8065).

    Label (NasaConst.java): NASA_OUTDOOR_SYSTEM_RESET
    """

    NO_ACTION = 0
    """No reset action"""
    RESET = 1
    """System reset"""


class OutCheckRefResult(SamsungEnum, IntEnum):
    """Refrigerant amount determination result (Message 0x809C).

    Label (NASA.prc): ENUM_OUT_CHECK_REF_RESULT
    """

    NOT_INSPECTED = 0
    """Refrigerant not yet inspected"""
    NORMAL_COMPLETION = 1
    """Normal completion of refrigerant check"""
    NOT_JUDGED = 2
    """Refrigerant check not judged"""
    SUBCOOLING_FAIL = 3
    """Subcooling cannot be secured"""
    NORMAL = 4
    """Refrigerant amount is normal"""
    INSUFFICIENT = 5
    """Refrigerant amount is insufficient"""
    CANNOT_JUDGE = 6
    """Cannot judge refrigerant amount"""
    TEMP_RANGE_EXCEEDED = 7
    """Temperature range exceeded"""


class OutOutdoorCoolonlyModel(SamsungEnum, IntEnum):
    """Outdoor unit cool-only model status (Message 0x809D).

    Label (NasaConst.java): NASA_OUTDOOR_COOLONLY_MODEL
    """

    NO_HEAT_PUMP = 0
    """Unit is cool-only (no heat pump)"""
    YES_HEAT_PUMP = 1
    """Unit has heat pump capability"""


class OutEhsWateroutType(SamsungEnum, IntEnum):
    """EHS Water Outlet Type (Message 0x80D8).

    Label (NASA.prc): ENUM_OUT_EHS_WATEROUT_TYPE
    """

    DEFAULT = 0
    """Default water outlet temperature"""
    TEMP_70C = 1
    """70°C water outlet temperature"""


# Generic Enums for unknown ?? messages based on prefix
class InUnknown400F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x400F. Specifics unknown."""


class InUnknown4010(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4010. Specifics unknown."""


class InUnknown4015(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4015. Specifics unknown."""


class InUnknown4029(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4029. Specifics unknown."""


class InUnknown402A(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402A. Specifics unknown."""


class InUnknown402B(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402B. Specifics unknown."""


class InUnknown402D(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x402D. Specifics unknown."""


class InUnknown4031(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4031. Specifics unknown."""


class InUnknown4035(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4035. Specifics unknown."""


class InUnknown4047(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4047. Specifics unknown."""


class InUnknown4048(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4048. Specifics unknown."""


class InUnknown404F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x404F. Specifics unknown."""


class InUnknown4051(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4051. Specifics unknown."""


class InUnknown4059(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4059. Specifics unknown."""


class InUnknown405F(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x405F. Specifics unknown."""


class InUnknown4073(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4073. Specifics unknown."""


class InUnknown4074(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4074. Specifics unknown."""


class InUnknown4077(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4077. Specifics unknown."""


class InUnknown407B(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x407B. Specifics unknown."""


class InUnknown407D(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x407D. Specifics unknown."""


class InUnknown4085(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4085. Specifics unknown."""


class InFsv4011(SamsungEnum, IntEnum):
    """
    FSV #4011: Priority Mode Selection (Message 0x409E).

    Selects priority between DHW and space heating operation.
    Default: DHW. Range: 0-1.

    Label (NASA.prc): ENUM_IN_FSV_4011
    """

    DHW = 0
    """Domestic hot water has priority"""
    HEATING = 1
    """Space heating has priority"""


class InFsv4021(SamsungEnum, IntEnum):
    """
    FSV #4021: Operation Mode Configuration (Message 0x409F).

    Sets operational mode configuration option.
    Range: 0-2.

    Label (NASA.prc): ENUM_IN_FSV_4021
    """

    VALUE_0 = 0
    """Operation mode 0"""
    VALUE_1 = 1
    """Operation mode 1"""
    VALUE_2 = 2
    """Operation mode 2"""


class InFsv4022(SamsungEnum, IntEnum):
    """
    FSV #4022: Backup Heater Type Selection (Message 0x40A0).

    Selects backup heater configuration (BUH=Booster, BSH=Backup).
    Default: Both. Range: 0-2.

    Label (NASA.prc): ENUM_IN_FSV_4022
    """

    BUH_BSH_BOTH = 0
    """Both BUH and BSH backup heaters available"""
    BUH = 1
    """Booster Unit Heater (BUH) only"""
    BSH = 2
    """Backup Supply Heater (BSH) only"""


class InFsv4041(SamsungEnum, IntEnum):
    """
    FSV #4041: Feature Configuration (Message 0x40C0).

    Enables/disables optional feature configuration.
    Default: No. Range: 0-2.

    Label (NASA.prc): ENUM_IN_FSV_4041
    """

    NO = 0
    """Feature disabled"""
    VALUE_1 = 1
    """Feature mode 1"""
    VALUE_2 = 2
    """Feature mode 2"""


class InFsv5033(SamsungEnum, IntEnum):
    """
    FSV #5033: Priority Mode A2A vs DHW (Message 0x4107).

    Sets priority between air-to-air (A2A) and domestic hot water (DHW) operation.
    Controls time-division switching when both systems operate.
    Default: 0 (Priority A2A). Range: 0-1.

    Label (NASA.prc): ENUM_IN_FSV_5033
    """

    A2A = 0
    """Air-to-air operation has priority"""
    DHW = 1
    """Domestic hot water operation has priority"""


class InFsv5042(SamsungEnum, IntEnum):
    """
    FSV #5042: Zone/Area Control Configuration (Message 0x40A5).

    Controls zone or area selection for multi-zone systems.
    Default: All. Range: 0-3.

    Label (NASA.prc): ENUM_IN_FSV_5042
    """

    ALL = 0
    """All zones"""
    VALUE_1 = 1
    """Zone 1"""
    VALUE_2 = 2
    """Zone 2"""
    VALUE_3 = 3
    """Zone 3"""


class InFsv5043(SamsungEnum, IntEnum):
    """
    FSV #5043: System Capacity Configuration (Message 0x40A6).

    Sets system capacity or performance mode.
    Default: Low. Range: 0-1.

    Label (NASA.prc): ENUM_IN_FSV_5043
    """

    LOW = 0
    """Low capacity/performance mode"""
    HIGH = 1
    """High capacity/performance mode"""


class InFsv5051(SamsungEnum, IntEnum):
    """
    FSV #5051: Optional Feature Enable (Message 0x40A7).

    Enables or disables an optional system feature.
    Default: No. Range: 0-1.

    Label (NASA.prc): ENUM_IN_FSV_5051
    """

    NO = 0
    """Feature disabled"""
    YES = 1
    """Feature enabled"""


class InFsv5061(SamsungEnum, IntEnum):
    """
    FSV #5061: CH/DHW Supply Ratio (Message 0x40B4).

    Sets the energy distribution ratio between space heating (CH) and domestic hot water (DHW).
    Controls priority when both systems compete for heat pump capacity.
    Range: 1-7 (1=maximum DHW priority, 7=maximum CH priority).

    Label (NASA.prc): ENUM_IN_FSV_5061
    """

    VALUE_1 = 1
    """DHW priority (ratio 1/7)"""
    VALUE_2 = 2
    """Supply ratio 2/7"""
    VALUE_3 = 3
    """Supply ratio 3/7"""
    VALUE_4 = 4
    """Balanced supply ratio (4/7)"""
    VALUE_5 = 5
    """Supply ratio 5/7"""
    VALUE_6 = 6
    """Supply ratio 6/7"""
    VALUE_7 = 7
    """CH priority (ratio 7/7)"""


class InUnknown40B5(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40B5. Specifics unknown."""


class InFsv4044(SamsungEnum, IntEnum):  # 0x40C1
    """Indoor unit enum for FSV message 0x40C1. Specifics unknown."""


class InFsv4051(SamsungEnum, IntEnum):  # 0x40C2
    """Indoor unit enum for FSV message 0x40C2. Specifics unknown."""


class InFsv4053(SamsungEnum, IntEnum):  # 0x40C3
    """Indoor unit enum for FSV message 0x40C3. Specifics unknown."""


class InUnknown40C6(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40C6. Specifics unknown."""


class InUnknown40E3(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x40E3. Specifics unknown."""


class InAutoStaticPressure(SamsungEnum, IntEnum):
    """
    Automatic pressure control status (Message 0x40BB).
    Label (NASA.prc): ENUM_IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    XML ProtocolID: ENUM_IN_STATE_AUTO_STATIC_PRESSURE_RUNNING
    """

    OFF = 0
    """Automatic pressure control is off"""
    COMPLETE = 1
    """Automatic pressure control is complete"""
    RUNNING = 2
    """Automatic pressure control is running"""


class InVacancyControl(SamsungEnum, IntEnum):
    """
    Vacancy control (Message 0x40BD).
    Label (NASA.prc): ENUM_IN_EMPTY_ROOM_CONTROL_USED
    XML ProtocolID: ENUM_IN_EMPTY_ROOM_CONTROL_USED
    """

    DISABLE = 0
    """Vacancy control is disabled"""
    ENABLE = 1
    """Vacancy control is enabled"""


class InEnterRoomControl(SamsungEnum, IntEnum):
    """
    Enable room entry control option (Message 0x40D5).
    Label (NASA.prc): ENUM_IN_ENTER_ROOM_CONTROL_USED
    XML ProtocolID: ENUM_IN_ENTER_ROOM_CONTROL_USED
    """

    DISABLE = 0
    """Room entry control is disabled"""
    ENABLE = 1
    """Room entry control is enabled"""


class InChillerWaterlawSensor(SamsungEnum, IntEnum):
    """
    DMV Chiller Option / Chiller Water Law Sensor (Message 0x40E7).
    Label (NASA.prc): ENUM*IN_CHILLER_WATERLAW_SENSOR
    XML ProtocolID: ENUM_IN_CHILLER_WATERLAW_SENSOR
    """

    OUTDOOR = 0
    """Outdoor sensor"""
    ROOM = 1
    """Room sensor"""


class InChillerWaterlaw(SamsungEnum, IntEnum):
    """
    Enable chiller WL (Message 0x40F7).
    Label (NASA.prc): ENUM_IN_CHILLER_WATERLAW_ON_OFF
    XML ProtocolID: ENUM_IN_CHILLER_WATERLAW_ON_OFF
    """

    OFF = 0
    """Chiller water law is off"""
    ON = 1
    """Chiller water law is on"""


class InChillerSettingSilentLevel(SamsungEnum, IntEnum):
    """
    Chiller Setting Silent Level (Message 0x40FB).
    Label (NASA.prc): ENUM_IN_CHILLLER_SETTING_SILENT_LEVEL (Typo in source)
    XML ProtocolID: ENUM_IN_CHILLLER_SETTING_SILENT_LEVEL
    """

    NONE = 0
    """No silent level set"""
    LEVEL1 = 1
    """Silent level 1"""
    LEVEL2 = 2
    """Silent level 2"""
    LEVEL3 = 3
    """Silent level 3"""


class InChillerSettingDemandLevel(SamsungEnum, IntEnum):
    """
    Chiller Setting Demand Level (Message 0x40FC).
    Label (NASA.prc): ENUM_IN_CHILLER_SETTING_DEMAND_LEVEL
    XML ProtocolID: ENUM_IN_CHILLER_SETTING_DEMAND_LEVEL
    """

    PERCENT_100 = 0
    """100% demand level"""
    PERCENT_95 = 1
    """95% demand level"""
    PERCENT_90 = 2
    """90% demand level"""
    PERCENT_85 = 3
    """85% demand level"""
    PERCENT_80 = 4
    """80% demand level"""
    PERCENT_75 = 5
    """75% demand level"""
    PERCENT_70 = 6
    """70% demand level"""
    PERCENT_65 = 7
    """65% demand level"""
    PERCENT_60 = 8
    """60% demand level"""
    PERCENT_55 = 9
    """55% demand level"""
    PERCENT_50 = 10
    """50% demand level"""
    NOT_APPLY = 11
    """Demand level not applicable"""


class InWaterValve(SamsungEnum, IntEnum):
    """Water valve state (Messages 0x4103, 0x4104).

    Label (NASA.prc): ENUM_IN_WATER_VALVE_*_ON_OFF

    XML ProtocolID: ENUM_IN_WATER_VALVE_*_ON_OFF
    """

    OFF = 0
    """Water valve is off"""
    ON = 1
    """Water valve is on"""
    """Water valve is on"""


class InEnthalpyControl(SamsungEnum, IntEnum):
    """
    Set enthalpy control state (Message 0x4105).
    Label (NASA.prc): ENUM_IN_ENTHALPY_CONTROL_STATE
    XML ProtocolID: ENUM_IN_ENTHALPY_CONTROL_STATE
    """


class InFreeCooling(SamsungEnum, IntEnum):
    """
    Set free cooling state (Message 0x410D).
    Label (NASA.prc): ENUM_IN_FREE_COOLING_STATE
    XML ProtocolID: ENUM_IN_FREE_COOLING_STATE
    """

    pass


class InZone1Power(SamsungEnum, IntEnum):
    """
    Zone 1 operating power (Message 0x4119).
    Label (NASA.prc): ENUM_IN_OPERATION_POWER_ZONE1
    XML ProtocolID: ENUM_IN_OPERATION_POWER_ZONE1
    Range: 0-1
    """

    OFF = 0
    """Zone 1 is off"""
    ON = 1
    """Zone 1 is on"""


class InGasLevel(SamsungEnum, IntEnum):
    """
    Gas level / Refrigerant inventory (Message 0x4147).
    Label (NASA.prc): ENUM_IN_GAS_LEVEL
    XML ProtocolID: ENUM_IN_GAS_LEVEL
    Range: 0-7
    """

    VALUE_0 = 0
    """Gas level 0"""
    VALUE_1 = 1
    """Gas level 1"""
    VALUE_2 = 2
    """Gas level 2"""
    VALUE_3 = 3
    """Gas level 3"""
    VALUE_4 = 4
    """Gas level 4"""
    VALUE_5 = 5
    """Gas level 5"""
    VALUE_6 = 6
    """Gas level 6"""
    VALUE_7 = 7
    """Gas level 7"""


class InDiffuserOperation(SamsungEnum, IntEnum):
    """
    Diffuser operation (Message 0x4149).
    Label (NASA.prc): ENUM_IN_DIFFUSER_OPERATION_POWER
    XML ProtocolID: ENUM_IN_DIFFUSER_OPERATION_POWER
    """

    OFF = 0
    """Diffuser is off"""
    ON = 1
    """Diffuser is on"""


class InFsv2094(SamsungEnum, IntEnum):
    """
    FSV 2094 setting (Message 0x412A).
    Label (NASA.prc): ENUM_IN_FSV_2094
    XML ProtocolID: ENUM_IN_FSV_2094
    Values 0-4 per user manual
    """

    VALUE_0 = 0
    """Setting option 0"""
    VALUE_1 = 1
    """Setting option 1"""
    VALUE_2 = 2
    """Setting option 2"""
    VALUE_3 = 3
    """Setting option 3"""
    VALUE_4 = 4
    """Setting option 4"""


class InTdmIndoorType(SamsungEnum, IntEnum):
    """
    TDM Indoor Type (Message 0x4108).
    Label (NASA.prc): ENUM_IN_TDM_INDOOR_TYPE
    XML ProtocolID: ENUM_IN_TDM_INDOOR_TYPE
    """

    A2A = 0
    """Air-to-air TDM type"""
    A2W = 1
    """Air-to-water TDM type"""


class In3WayValve(SamsungEnum, IntEnum):
    """
    3-Way Valve state (Message 0x4067/0x4113).
    Label (NASA.prc): ENUM_IN_3WAY_VALVE
    XML ProtocolID: ENUM_IN_3WAY_VALVE
    """

    ROOM = 0
    """Valve is set to room mode"""
    TANK = 1
    """Valve is set to tank mode"""


class InFsv4061(SamsungEnum, IntEnum):
    """
    FSV 4061 (Message 0x411A).
    Label (NASA.prc): ENUM_IN_FSV_4061
    XML ProtocolID: ENUM_IN_FSV_4061
    """

    VALUE_0 = 0
    """Setting value 0"""
    VALUE_1 = 1
    """Setting value 1"""


class InFsv5081(SamsungEnum, IntEnum):
    """
    FSV 5081 (Message 0x411B).
    Label (NASA.prc): ENUM_IN_FSV_5081
    XML ProtocolID: ENUM_IN_FSV_5081
    """

    VALUE_0 = 0
    """Setting value 0"""
    VALUE_1 = 1
    """Setting value 1"""


class InFsv5091(SamsungEnum, IntEnum):
    """
    FSV 5091 (Message 0x411C).
    Label (NASA.prc): ENUM_IN_FSV_5091
    XML ProtocolID: ENUM_IN_FSV_5091
    """

    VALUE_0 = 0
    """Setting value 0"""
    VALUE_1 = 1
    """Setting value 1"""


class InFsv5094(SamsungEnum, IntEnum):
    """
    FSV 5094 (Message 0x411D).
    Label (NASA.prc): ENUM_IN_FSV_5094
    XML ProtocolID: ENUM_IN_FSV_5094
    """

    VALUE_0 = 0
    """Setting value 0"""
    VALUE_1 = 1
    """Setting value 1"""


class InZone2Power(SamsungEnum, IntEnum):
    """
    Zone 2 operating power (Message 0x411E).
    Label (NASA.prc): ENUM_IN_OPERATION_POWER_ZONE2
    XML ProtocolID: ENUM_IN_OPERATION_POWER_ZONE2
    """

    OFF = 0
    """Zone 2 is off"""
    ON = 1
    """Zone 2 is on"""


class InPvContactState(SamsungEnum, IntEnum):
    """
    PV Contact State (Message 0x4123).
    Label (NASA.prc): ENUM_IN_PV_CONTACT_STATE
    XML ProtocolID: ENUM_IN_PV_CONTACT_STATE
    """

    DISABLE = 0
    """PV contact is disabled"""
    ENABLE = 1
    """PV contact is enabled"""


class InSgReadyModeState(SamsungEnum, IntEnum):
    """
    SG Ready Mode State (Message 0x4124).
    Label (NASA.prc): ENUM_IN_SG_READY_MODE_STATE
    XML ProtocolID: ENUM_IN_SG_READY_MODE_STATE
    Values not defined in NASA.ptc
    """

    pass


class NmNetworkPositionLayer(SamsungEnum, IntEnum):
    """
    Network Position Layer (Message 0x200F).
    Label (NASA.prc): ENUM_NM_network_positinon_layer
    XML ProtocolID: ENUM_NM_network_positinon_layer
    """

    CONTROL_LAYER = 0
    SET_LAYER = 1


class NmNetworkTrackingState(SamsungEnum, IntEnum):
    """
    Network Tracking State (Message 0x2010).
    Label (NASA.prc): ENUM_NM_network_tracking_state
    XML ProtocolID: ENUM_NM_network_tracking_state
    Values not defined in NASA.ptc
    """

    pass


class InUnknown4117(SamsungEnum, IntEnum):
    """Indoor unit enum for message 0x4117. Specifics unknown."""


class InRoomTempSensorZone2(SamsungEnum, IntEnum):  # 0x4118
    """Indoor unit enum for message 0x4118 (Room Temp Sensor Zone 2). Specifics unknown."""


class InSilenceLevel(SamsungEnum, IntEnum):  # 0x4129
    """Indoor unit enum for message 0x4129 (Silence Level). Specifics unknown."""


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


class OutUnknown8005(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8005. Specifics unknown."""


class OutUnknown800D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x800D. Specifics unknown."""


class OutUnknown8031(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8031. Specifics unknown."""


class OutUnknown8032(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8032. Specifics unknown."""


class OutUnknown8033(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8033. Specifics unknown."""


class OutUnknown803F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x803F. Specifics unknown."""


class OutUnknown8043(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8043. Specifics unknown."""


class OutUnknown8045(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8045. Specifics unknown."""


class OutUnknown8048(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8048. Specifics unknown."""


class OutUnknown805E(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x805E. Specifics unknown."""


class OutUnknown8063(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8063. Specifics unknown."""


class OutUnknown8077(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8077. Specifics unknown."""


class OutUnknown8078(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8078. Specifics unknown."""


class OutUnknown8079(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8079. Specifics unknown."""


class OutUnknown807A(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807A. Specifics unknown."""


class OutUnknown807B(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807B. Specifics unknown."""


class OutUnknown807C(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807C. Specifics unknown."""


class OutUnknown807D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807D. Specifics unknown."""


class OutUnknown807E(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807E. Specifics unknown."""


class OutUnknown807F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x807F. Specifics unknown."""


class OutdoorExtCmdOperation(SamsungEnum, IntEnum):  # 0x8081
    """Outdoor unit enum for message 0x8081 (NASA_OUTDOOR_EXT_CMD_OPERATION). Specifics unknown."""


class OutUnknown8083(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x8083. Specifics unknown."""


class OutUnknown808C(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808C. Specifics unknown."""


class OutUnknown808D(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808D. Specifics unknown."""


class OutUnknown808F(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x808F. Specifics unknown."""


class OutdoorDredLevel(SamsungEnum, IntEnum):  # 0x80A7
    """Outdoor unit enum for message 0x80A7 (NASA_OUTDOOR_DRED_LEVEL). Specifics unknown."""


class OutUnknown80A8(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80A8. Specifics unknown."""


class OutUnknown80A9(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80A9. Specifics unknown."""


class OutUnknown80AA(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AA. Specifics unknown."""


class OutUnknown80AB(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AB. Specifics unknown."""


class OutUnknown80AE(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80AE. Specifics unknown."""


class OutUnknown80B1(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80B1. Specifics unknown."""


class OutdoorChSwitchValue(SamsungEnum, IntEnum):  # 0x80B2
    """Outdoor unit enum for message 0x80B2 (NASA_OUTDOOR_CH_SWITCH_VALUE). Specifics unknown."""


class OutdoorEviSolenoid(SamsungEnum, IntEnum):
    """
    Outdoor unit EVI solenoid valve state (Messages 0x8022, 0x8023).
    Label (NASA.ptc): ENUM_out_load_evi_sol1, ENUM_out_load_evi_sol2
    """

    OFF = 0
    """EVI solenoid is off"""
    ON = 1
    """EVI solenoid is on"""


class OutdoorOperationServiceOp(SamsungEnum, IntEnum):
    """
    Outdoor operation service operation (Message 0x8000).
    Label (NASA.ptc): ENUM_OUT_OPERATION_SERVICE_OP
    XML ProtocolID: ENUM_OUT_OPERATION_SERVICE_OP
    """

    HEATING_COMMISSIONING = 2
    """Heating commissioning mode"""
    PUMP_OUT = 3
    """Pump out operation"""
    COOLING_COMMISSIONING = 13
    """Cooling commissioning mode"""
    PUMP_DOWN = 14
    """Pump down operation"""


class OutdoorOperationHeatCool(SamsungEnum, IntEnum):
    """
    Outdoor heat/cool mode (Message 0x8003).
    Label (NASA.ptc): ENUM_out_operation_heatcool
    XML ProtocolID: ENUM_out_operation_heatcool
    """

    UNDEFINED = 0
    """Undefined heat/cool mode"""
    COOL = 1
    """Cooling mode"""
    HEAT = 2
    """Heating mode"""
    COOL_MAIN = 3
    """Main cooling mode"""
    HEAT_MAIN = 4
    """Main heating mode"""


class OutdoorCompressorLoad(SamsungEnum, IntEnum):
    """
    Outdoor compressor on/off state (Messages 0x8010, 0x8011, 0x8012).
    Label (NASA.ptc): ENUM_out_load_comp1, ENUM_out_load_comp2, ENUM_out_load_comp3
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Compressor is off"""
    ON = 1
    """Compressor is on"""


class OutdoorCchLoad(SamsungEnum, IntEnum):
    """
    Outdoor CCH (Crankcase Heater) on/off state (Messages 0x8013, 0x8014).
    Label (NASA.ptc): ENUM_out_load_cch1, ENUM_out_load_cch2
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """CCH is off"""
    ON = 1
    """CCH is on"""


class OutdoorHotGasLoad(SamsungEnum, IntEnum):
    """
    Outdoor hot gas on/off state (Messages 0x8017, 0x8018).
    Label (NASA.ptc): ENUM_out_load_hotgas, ENUM_out_load_hotgas2
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Hot gas is off"""
    ON = 1
    """Hot gas is on"""


class OutdoorLiquidLoad(SamsungEnum, IntEnum):
    """
    Outdoor liquid on/off state (Message 0x8019).
    Label (NASA.ptc): ENUM_OUT_LOAD_LIQUID
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Liquid is off"""
    ON = 1
    """Liquid is on"""


class Outdoor4WayLoad(SamsungEnum, IntEnum):
    """
    Outdoor 4-way valve on/off state (Messages 0x801A, 0x802A).
    Label (NASA.ptc): ENUM_out_load_4way, ENUM_OUT_LOAD_4WAY2
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """4-way valve is off"""
    ON = 1
    """4-way valve is on"""


class OutdoorMainCoolLoad(SamsungEnum, IntEnum):
    """
    Outdoor main cool on/off state (Message 0x801F).
    Label (NASA.ptc): ENUM_out_load_maincool
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Main cooling is off"""
    ON = 1
    """Main cooling is on"""


class OutdoorOutEevLoad(SamsungEnum, IntEnum):
    """
    Outdoor expansion valve on/off state (Message 0x8020).
    Label (NASA.ptc): ENUM_out_load_outeev
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Expansion valve is off"""
    ON = 1
    """Expansion valve is on"""


class OutdoorEviBypassLoad(SamsungEnum, IntEnum):
    """
    Outdoor EVI bypass on/off state (Message 0x8021).
    Label (NASA.ptc): ENUM_out_load_evi_bypass
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """EVI bypass is off"""
    ON = 1
    """EVI bypass is on"""


class OutdoorGasChargeLoad(SamsungEnum, IntEnum):
    """
    Outdoor hot gas charging on/off state (Message 0x8025).
    Label (NASA.ptc): ENUM_out_load_gascharge
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Gas charging is off"""
    ON = 1
    """Gas charging is on"""


class OutdoorWaterValveLoad(SamsungEnum, IntEnum):
    """
    Outdoor water valve on/off state (Message 0x8026).
    Label (NASA.ptc): ENUM_out_load_water
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Water valve is off"""
    ON = 1
    """Water valve is on"""


class OutdoorPumpOutLoad(SamsungEnum, IntEnum):
    """
    Outdoor pump out on/off state (Message 0x8027).
    Label (NASA.ptc): ENUM_out_load_pumpout
    Values not defined in NASA.ptc - using OFF/ON pattern
    """

    OFF = 0
    """Pump out is off"""
    ON = 1
    """Pump out is on"""


class OutUnknown80B6(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80B6. Specifics unknown."""


class OutUnknown80BC(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80BC. Specifics unknown."""


class OutUnknown80CE(SamsungEnum, IntEnum):
    """Outdoor unit enum for message 0x80CE. Specifics unknown."""


class InOperationVentPower(SamsungEnum, IntEnum):
    """Indoor unit ventilation power (Message 0x4003).

    Label (NASA.prc): ENUM_IN_OPERATION_VENT_POWER
    """

    OFF = 0
    """Ventilation is off"""
    ON = 1
    """Ventilation is on"""


class InOperationVentPowerSetting(SamsungEnum, IntEnum):
    """
    Indoor unit ventilation mode (Message 0x4004).
    Label (NASA.prc): ENUM_IN_OPERATION_VENT_MODE
    """

    OFF = 0
    """Ventilation is off"""
    ON = 1
    """Ventilation is on"""


class InOperationRoomFan(SamsungEnum, IntEnum):
    """
    Indoor unit room fan operation (Message 0x400F).
    Label (NASA.prc): ENUM_IN_OPERATION_ROOM_FAN
    """

    OFF = 0
    """Room fan is off"""
    ON = 1
    """Room fan is on"""


class InOperationRoomFanControl(SamsungEnum, IntEnum):
    """
    Indoor unit room fan control (Message 0x4010).
    Label (NASA.prc): ENUM_IN_OPERATION_ROOM_FAN_CONTROL
    """

    OFF = 0
    """Room fan control is off"""
    ON = 1
    """Room fan control is on"""


class InOperationOutdoorFan(SamsungEnum, IntEnum):
    """
    Indoor unit outdoor fan operation (Message 0x4015).
    Label (NASA.prc): ENUM_IN_OPERATION_OUTDOOR_FAN
    """

    OFF = 0
    """Outdoor fan is off"""
    ON = 1
    """Outdoor fan is on"""


class InLouverLrFull(SamsungEnum, IntEnum):
    """
    Indoor unit louver LR full control (Message 0x4019).
    Label (NASA.prc): ENUM_IN_LOUVER_LR_FULL
    """

    OFF = 0
    """Louver LR full is off"""
    ON = 1
    """Louver LR full is on"""


class InLouverLr(SamsungEnum, IntEnum):
    """
    Indoor unit louver LR control (Message 0x401B).
    Label (NASA.prc): ENUM_IN_LOUVER_LR
    """

    OFF = 0
    """Louver LR is off"""
    ON = 1
    """Louver LR is on"""


class InLouverVlRightDownSwing(SamsungEnum, IntEnum):
    """
    Indoor unit louver VL right down swing (Message 0x4023).
    Label (NASA.prc): ENUM_IN_LOUVER_VL_RIGHT_DOWN_SWING
    """

    OFF = 0
    """Right down swing is off"""
    ON = 1
    """Right down swing is on"""


class InLouverVlLeftDownSwing(SamsungEnum, IntEnum):
    """
    Indoor unit louver VL left down swing (Message 0x4024).
    Label (NASA.prc): ENUM_IN_LOUVER_VL_LEFT_DOWN_SWING
    """

    OFF = 0
    """Left down swing is off"""
    ON = 1
    """Left down swing is on"""


class InDrainPumpPower(SamsungEnum, IntEnum):
    """
    Indoor unit drain pump power (Message 0x4027).
    Label (NASA.prc): ENUM_IN_DRAIN_PUMP_POWER
    """

    OFF = 0
    """Drain pump is off"""
    ON = 1
    """Drain pump is on"""


class InBackupHeaterPower(SamsungEnum, IntEnum):
    """
    Indoor unit backup heater power (Message 0x4029).
    Label (NASA.prc): ENUM_IN_BACKUP_HEATER_POWER
    """

    OFF = 0
    """Backup heater is off"""
    ON = 1
    """Backup heater is on"""


class InIceCtrlState(SamsungEnum, IntEnum):
    """
    Indoor unit ice control state (Message 0x402A).
    Label (NASA.prc): ENUM_IN_ICE_CTRL_STATE
    """

    STOP = 0
    """Ice control is stopped"""
    RUNNING = 1
    """Ice control is running"""


class InCoilFreezingControl(SamsungEnum, IntEnum):
    """
    Indoor unit coil freezing control (Message 0x402B).
    Label (NASA.prc): ENUM_IN_COIL_FREEZING_CONTROL
    """

    OFF = 0
    """Coil freezing control is off"""
    ON = 1
    """Coil freezing control is on"""


class InStateDefrostControl(SamsungEnum, IntEnum):
    """
    Indoor unit defrost control state (Message 0x402D).
    Label (NASA.prc): ENUM_IN_STATE_DEFROST_CONTROL
    """

    OFF = 0
    """Defrost control is off"""
    ON = 1
    """Defrost control is on"""


class InStateDefrostMode(SamsungEnum, IntEnum):
    """
    Indoor unit defrost mode state (Message 0x402E).
    Label (NASA.prc): ENUM_IN_STATE_DEFROST_MODE
    """

    NORMAL = 0
    """Normal mode"""
    DEFROST = 1
    """Defrost mode"""


class InMtfc(SamsungEnum, IntEnum):
    """
    Indoor unit MTFC control (Message 0x402F).
    Label (NASA.prc): ENUM_IN_MTFC
    """

    OFF = 0
    """MTFC is off"""
    ON = 1
    """MTFC is on"""


class InLouverVlFull(SamsungEnum, IntEnum):
    """
    Indoor unit louver VL full control (Message 0x4031).
    Label (NASA.prc): ENUM_IN_LOUVER_VL_FULL
    """

    OFF = 0
    """Louver VL full is off"""
    ON = 1
    """Louver VL full is on"""


class InThermistorOpen(SamsungEnum, IntEnum):
    """
    Indoor unit thermistor open status (Message 0x4035).
    Label (NASA.prc): ENUM_IN_THERMISTOR_OPEN
    """

    NORMAL = 0
    OPEN = 1


class InIceCheckPoint(SamsungEnum, IntEnum):
    """
    Indoor unit ice check point (Message 0x4043).
    Label (NASA.prc): ENUM_IN_ICE_CHECK_POINT
    """

    NORMAL = 0
    CHECK = 1


class InSilence(SamsungEnum, IntEnum):
    """
    Indoor unit silence mode (Message 0x4046).
    Label (NASA.prc): ENUM_IN_SILENCE
    """

    OFF = 0
    """Silence mode is off"""
    ON = 1
    """Silence mode is on"""


class InWifiKitPower(SamsungEnum, IntEnum):
    """
    Indoor unit WiFi kit power (Message 0x4047).
    Label (NASA.prc): ENUM_IN_WIFI_KIT_POWER
    """

    OFF = 0
    """WiFi kit is off"""
    ON = 1
    """WiFi kit is on"""


class InWifiKitControl(SamsungEnum, IntEnum):
    """
    Indoor unit WiFi kit control (Message 0x4048).
    Label (NASA.prc): ENUM_IN_WIFI_KIT_CONTROL
    """

    DISABLED = 0
    """WiFi kit control is disabled"""
    ENABLED = 1
    """WiFi kit control is enabled"""


class InLouverVl(SamsungEnum, IntEnum):
    """
    Indoor unit louver VL control (Message 0x404F).
    Label (NASA.prc): ENUM_IN_LOUVER_VL
    """

    OFF = 0
    """Louver VL is off"""
    ON = 1
    """Louver VL is on"""


class InLouverHlDownUp(SamsungEnum, IntEnum):
    """
    Indoor unit louver HL down up control (Message 0x4051).
    Label (NASA.prc): ENUM_IN_LOUVER_HL_DOWN_UP
    """

    DOWN = 0
    UP = 1


class InLouverHlNowPos(SamsungEnum, IntEnum):
    """
    Indoor unit louver HL current position (Message 0x4059).
    Label (NASA.prc): ENUM_IN_LOUVER_HL_NOW_POS
    """

    DOWN = 0
    UP = 1


class InLouverVlPos(SamsungEnum, IntEnum):
    """
    Indoor unit louver VL position (Message 0x405F).
    Label (NASA.prc): ENUM_IN_LOUVER_VL_POS
    """

    FULL_CLOSE = 0
    PARTIAL_OPEN = 1
    FULL_OPEN = 2


class InSolarPump(SamsungEnum, IntEnum):
    """
    Indoor unit solar pump control (Message 0x4068).
    Label (NASA.prc): ENUM_IN_SOLAR_PUMP
    """

    OFF = 0
    """Solar pump is off"""
    ON = 1
    """Solar pump is on"""


class InThermostat0(SamsungEnum, IntEnum):
    """
    Indoor unit thermostat 0 mode (Message 0x406B).
    Label (NASA.prc): ENUM_IN_THERMOSTAT0
    """

    DISABLED = 0
    """Thermostat 0 is disabled"""
    ENABLED = 1
    """Thermostat 0 is enabled"""


class InOutingMode(SamsungEnum, IntEnum):
    """
    Indoor unit outing mode (Message 0x406D).
    Label (NASA.prc): ENUM_IN_OUTING_MODE
    """

    OFF = 0
    """Outing mode is off"""
    ON = 1
    """Outing mode is on"""


class InQuietMode(SamsungEnum, IntEnum):
    """
    Indoor unit quiet mode (Message 0x406E).
    Label (NASA.prc): ENUM_IN_QUIET_MODE
    """

    OFF = 0
    """Quiet mode is off"""
    ON = 1
    """Quiet mode is on"""


class InDischargeTempControl(SamsungEnum, IntEnum):
    """
    Indoor unit discharge temperature control (Message 0x4070).
    Label (NASA.prc): ENUM_IN_DISCHARGE_TEMP_CONTROL
    """

    DISABLED = 0
    """Discharge temperature control is disabled"""
    ENABLED = 1
    """Discharge temperature control is enabled"""


class InLouverHlAuto(SamsungEnum, IntEnum):
    """
    Indoor unit louver HL auto control (Message 0x4073).
    Label (NASA.prc): ENUM_IN_LOUVER_HL_AUTO
    """

    MANUAL = 0
    """Louver HL is in manual mode"""
    AUTO = 1
    """Louver HL is in auto mode"""


class InLouverHlAutoUpDown(SamsungEnum, IntEnum):
    """
    Indoor unit louver HL auto up/down control (Message 0x4074).
    Label (NASA.prc): ENUM_IN_LOUVER_HL_AUTO_UP_DOWN
    """

    DOWN = 0
    """Louver HL auto moves down"""
    UP = 1
    """Louver HL auto moves up"""


class InWallMountedRemoteControl(SamsungEnum, IntEnum):
    """
    Indoor unit wall mounted remote control (Message 0x4077).
    Label (NASA.prc): ENUM_IN_WALL_MOUNTED_REMOTE_CONTROL
    """

    DISABLED = 0
    """Wall mounted remote control is disabled"""
    ENABLED = 1
    """Wall mounted remote control is enabled"""


class InFsv302LouverControl(SamsungEnum, IntEnum):
    """
    Indoor unit FSV 302 louver control (Message 0x407B).
    Label (NASA.prc): ENUM_IN_FSV302_LOUVER_CONTROL
    """

    OFF = 0
    """FSV 302 louver control is off"""
    ON = 1
    """FSV 302 louver control is on"""


class InFsv302LouverValue(SamsungEnum, IntEnum):
    """
    Indoor unit FSV 302 louver value (Message 0x407D).
    Label (NASA.prc): ENUM_IN_FSV302_LOUVER_VALUE
    """

    CLOSE = 0
    """Louver is closed"""
    OPEN = 1
    """Louver is open"""


class InFsv302TimeSchedule(SamsungEnum, IntEnum):
    """
    Indoor unit FSV 302 time schedule (Message 0x4085).
    Label (NASA.prc): ENUM_IN_FSV302_TIME_SCHEDULE
    """

    DISABLED = 0
    """Time schedule is disabled"""
    ENABLED = 1
    """Time schedule is enabled"""


class InModelInformation(SamsungEnum, IntEnum):
    """
    Indoor unit model information (Message 0x4229).
    Label (NASA.ptc): VAR_in_model_information
    """

    # Specific model types
    MASTER_N = 0x12
    SLIM_1WAY = 0x1F
    BIG_SLIM_1WAY = 0x20
    GLOBAL_4WAY = 0x33
    GLOBAL_MINI_4WAY = 0x34
    MINI_4WAY = 0x35
    BIG_DUCT = 0x3E
    GLOBAL_BIG_DUCT = 0x3F
    FRESH_DUCT = 0x44
    BIG_CEILING = 0x47
    MINI_AHU = 0x62
    ERV_PLUS = 0x6C
    EHS_SPLIT = 0x73
    EHS_MONO = 0x74
    EHS_TDM = 0x75
    EHS_HT = 0x7D
    DIFFUSER = 0xAA

    # Range-based categories (using representative values)
    # FSC/PAC (1-9)
    FSC_PAC_1 = 0x01
    FSC_PAC_2 = 0x02
    FSC_PAC_3 = 0x03
    FSC_PAC_4 = 0x04
    FSC_PAC_5 = 0x05
    FSC_PAC_6 = 0x06
    FSC_PAC_7 = 0x07
    FSC_PAC_8 = 0x08
    FSC_PAC_9 = 0x09
    # RAC (10-19)
    RAC_10 = 0x0A
    RAC_11 = 0x0B
    RAC_12 = 0x0C
    RAC_13 = 0x0D
    RAC_14 = 0x0E
    RAC_15 = 0x0F
    RAC_16 = 0x10
    RAC_17 = 0x11
    RAC_18 = 0x12
    RAC_19 = 0x13
    # 1Way (30-39)
    ONE_WAY_30 = 0x1E
    ONE_WAY_31 = 0x1F
    ONE_WAY_32 = 0x20
    ONE_WAY_33 = 0x21
    ONE_WAY_34 = 0x22
    ONE_WAY_35 = 0x23
    ONE_WAY_36 = 0x24
    ONE_WAY_37 = 0x25
    ONE_WAY_38 = 0x26
    ONE_WAY_39 = 0x27
    # 2Way (40-49)
    TWO_WAY_40 = 0x28
    TWO_WAY_41 = 0x29
    TWO_WAY_42 = 0x2A
    TWO_WAY_43 = 0x2B
    TWO_WAY_44 = 0x2C
    TWO_WAY_45 = 0x2D
    TWO_WAY_46 = 0x2E
    TWO_WAY_47 = 0x2F
    TWO_WAY_48 = 0x30
    TWO_WAY_49 = 0x31
    # 4Way (50-59)
    FOUR_WAY_50 = 0x32
    FOUR_WAY_51 = 0x33
    FOUR_WAY_52 = 0x34
    FOUR_WAY_53 = 0x35
    FOUR_WAY_54 = 0x36
    FOUR_WAY_55 = 0x37
    FOUR_WAY_56 = 0x38
    FOUR_WAY_57 = 0x39
    FOUR_WAY_58 = 0x3A
    FOUR_WAY_59 = 0x3B
    # Duct (60-69)
    DUCT_60 = 0x3C
    DUCT_61 = 0x3D
    DUCT_62 = 0x3E
    DUCT_63 = 0x3F
    DUCT_64 = 0x40
    DUCT_65 = 0x41
    DUCT_66 = 0x42
    DUCT_67 = 0x43
    DUCT_68 = 0x44
    DUCT_69 = 0x45
    # Ceiling (70-79)
    CEILING_70 = 0x46
    CEILING_71 = 0x47
    CEILING_72 = 0x48
    CEILING_73 = 0x49
    CEILING_74 = 0x4A
    CEILING_75 = 0x4B
    CEILING_76 = 0x4C
    CEILING_77 = 0x4D
    CEILING_78 = 0x4E
    CEILING_79 = 0x4F
    # Console (80-89)
    CONSOLE_80 = 0x50
    CONSOLE_81 = 0x51
    CONSOLE_82 = 0x52
    CONSOLE_83 = 0x53
    CONSOLE_84 = 0x54
    CONSOLE_85 = 0x55
    CONSOLE_86 = 0x56
    CONSOLE_87 = 0x57
    CONSOLE_88 = 0x58
    CONSOLE_89 = 0x59
    # AHU (90-99)
    AHU_90 = 0x5A
    AHU_91 = 0x5B
    AHU_92 = 0x5C
    AHU_93 = 0x5D
    AHU_94 = 0x5E
    AHU_95 = 0x5F
    AHU_96 = 0x60
    AHU_97 = 0x61
    AHU_98 = 0x62
    AHU_99 = 0x63
    # ERV (100-109)
    ERV_100 = 0x64
    ERV_101 = 0x65
    ERV_102 = 0x66
    ERV_103 = 0x67
    ERV_104 = 0x68
    ERV_105 = 0x69
    ERV_106 = 0x6A
    ERV_107 = 0x6B
    ERV_108 = 0x6C
    ERV_109 = 0x6D
    # DVM HE (110-114)
    DVM_HE_110 = 0x6E
    DVM_HE_111 = 0x6F
    DVM_HE_112 = 0x70
    DVM_HE_113 = 0x71
    DVM_HE_114 = 0x72
    # EHS (115-119)
    EHS_115 = 0x73
    EHS_116 = 0x74
    EHS_117 = 0x75
    EHS_118 = 0x76
    EHS_119 = 0x77
    # DVM HT (120-124)
    DVM_HT_120 = 0x78
    DVM_HT_121 = 0x79
    DVM_HT_122 = 0x7A
    DVM_HT_123 = 0x7B
    DVM_HT_124 = 0x7C
    # EHS HT (125-129)
    EHS_HT_125 = 0x7D
    EHS_HT_126 = 0x7E
    EHS_HT_127 = 0x7F
    EHS_HT_128 = 0x80
    EHS_HT_129 = 0x81
    # DVM Chiller (140-149)
    DVM_CHILLER_140 = 0x8C
    DVM_CHILLER_141 = 0x8D
    DVM_CHILLER_142 = 0x8E
    DVM_CHILLER_143 = 0x8F
    DVM_CHILLER_144 = 0x90
    DVM_CHILLER_145 = 0x91
    DVM_CHILLER_146 = 0x92
    DVM_CHILLER_147 = 0x93
    DVM_CHILLER_148 = 0x94
    DVM_CHILLER_149 = 0x95
    # 360CST (150-159)
    CST_360_150 = 0x96
    CST_360_151 = 0x97
    CST_360_152 = 0x98
    CST_360_153 = 0x99
    CST_360_154 = 0x9A
    CST_360_155 = 0x9B
    CST_360_156 = 0x9C
    CST_360_157 = 0x9D
    CST_360_158 = 0x9E
    CST_360_159 = 0x9F
    # FCU Kit (160-169)
    FCU_KIT_160 = 0xA0
    FCU_KIT_161 = 0xA1
    FCU_KIT_162 = 0xA2
    FCU_KIT_163 = 0xA3
    FCU_KIT_164 = 0xA4
    FCU_KIT_165 = 0xA5
    FCU_KIT_166 = 0xA6
    FCU_KIT_167 = 0xA7
    FCU_KIT_168 = 0xA8
    FCU_KIT_169 = 0xA9
    # CAC (256-511)
    CAC_256 = 0x100
    CAC_511 = 0x1FF
    # CAC Inverter (512-767)
    CAC_INVERTER_512 = 0x200
    CAC_INVERTER_767 = 0x2FF
