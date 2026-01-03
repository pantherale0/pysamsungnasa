"""Outdoor unit messages."""

from ..messaging import (
    EnumMessage,
    FloatMessage,
    BasicTemperatureMessage,
    BasicCurrentMessage,
    BasicPowerMessage,
    BasicEnergyMessage,
    RawMessage,
    StrMessage,
    IntegerMessage,
)
from ...enum import (
    OutdoorOperationStatus,
    OutdoorIndoorDefrostStep,
    OutOutdoorCoolonlyModel,
    OutdoorEviSolenoid,
    OutdoorOperationServiceOp,
    OutdoorOperationHeatCool,
    OutdoorOutEevLoad,
    OutdoorCompressorLoad,
    OutdoorCchLoad,
    OutdoorHotGasLoad,
    OutdoorLiquidLoad,
    Outdoor4WayLoad,
    OutdoorMainCoolLoad,
    OutdoorEviBypassLoad,
    OutdoorGasChargeLoad,
    OutdoorWaterValveLoad,
    OutdoorPumpOutLoad,
)


class OutdoorErrorCode1(RawMessage):
    """Parser for message 0x0202 (Outdoor Error Code 1)."""

    MESSAGE_ID = 0x0202
    MESSAGE_NAME = "Outdoor Error Code 1"


class OutdoorLinkedIndoorUnits(FloatMessage):
    """Parser for message 0x0207 (Outdoor Linked Indoor Units)."""

    MESSAGE_ID = 0x0207
    MESSAGE_NAME = "Outdoor Linked Indoor Units"


class OutdoorOperationModeLimit(FloatMessage):
    """Parser for message 0x0410 (Outdoor Operation Mode Limit)."""

    MESSAGE_ID = 0x0410
    MESSAGE_NAME = "Outdoor Operation Mode Limit"


class OutdoorSerialNumber(StrMessage):
    """Parser for message 0x0607 (Serial Number).

    This is a string structure message containing the device serial number.
    Type: STR (String structure)

    IMPORTANT: This structure returns INCOMPLETE data via submessages:
    - 0x0730: Manufacturer/model prefix (e.g., "TYXP")
    - 0x4654: Serial number suffix (e.g., "900834F")

    Known device example:
    Physical label: "0TYXPAFT900834F"
    Structure response:
      - 0x0730: "TYXP"
      - 0x4654: "900834F"

    Missing from structure: "0" (prefix), "AFT" (middle section)

    The complete serial number cannot be reconstructed from the structure alone.
    Recommendation: Query other message IDs (0x861A, 0x8608, etc.) for complete model info.
    """

    MESSAGE_ID = 0x0607
    MESSAGE_NAME = "Serial Number"


class OutdoorSerialNumberPrefix(StrMessage):
    """Parser for message 0x0730 (Serial Number Manufacturer/Model Prefix).

    Submessage returned as part of the 0x0607 structure response.
    Contains the manufacturer/model code portion of the serial number.

    Example: "TYXP" (from serial "0TYXPAFT900834F")
    """

    MESSAGE_ID = 0x0730
    MESSAGE_NAME = "Serial Number Prefix"


class HeatPumpVoltage(FloatMessage):
    """Parser for message 0x24FC (Heat Pump Voltage)."""

    MESSAGE_ID = 0x24FC
    MESSAGE_NAME = "Heat Pump Voltage"
    UNIT_OF_MEASUREMENT = "V"
    SIGNED = False
    ARITHMETIC = 1.0


class OutdoorProductModelName(StrMessage):
    """Parser for message 0x4548 (Outdoor Product Model Name - from 0x061A structure)."""

    MESSAGE_ID = 0x4548
    MESSAGE_NAME = "Outdoor Product Model Name"


class OutdoorSerialNumberSuffix(StrMessage):
    """Parser for message 0x4654 (Serial Number Numeric Suffix).

    Submessage returned as part of the 0x0607 structure response.
    Contains the numeric suffix portion of the serial number.

    Example: "900834F" (from serial "0TYXPAFT900834F")
    """

    MESSAGE_ID = 0x4654
    MESSAGE_NAME = "Serial Number Suffix"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "OutdoorSerialNumberSuffix":
        """Parse the payload into a string value, stripping null terminators."""
        decoded = payload.decode("utf-8") if payload else None
        if decoded:
            decoded = decoded.rstrip("\x00")
        return cls(value=decoded)


class OutdoorOperationServiceOpMessage(EnumMessage):
    """Parser for message 0x8000 (Outdoor Operation Service Operation)."""

    MESSAGE_ID = 0x8000
    MESSAGE_NAME = "Outdoor Operation Service Operation"
    MESSAGE_ENUM = OutdoorOperationServiceOp


class OutdoorOperationStatusMessage(EnumMessage):
    """Parser for message 0x8001 (Outdoor Operation Status)."""

    MESSAGE_ID = 0x8001
    MESSAGE_NAME = "Outdoor Operation Status"
    MESSAGE_ENUM = OutdoorOperationStatus


class OutdoorOperationHeatCoolMessage(EnumMessage):
    """Parser for message 0x8003 (Outdoor Operation Heat/Cool)."""

    MESSAGE_ID = 0x8003
    MESSAGE_NAME = "Outdoor Operation Heat/Cool Mode"
    MESSAGE_ENUM = OutdoorOperationHeatCool


class OutdoorMessage8005(RawMessage):
    """Parser for message 0x8005 (Message 8005)."""

    MESSAGE_ID = 0x8005
    MESSAGE_NAME = "Message 8005"


class OutdoorMessage800d(RawMessage):
    """Parser for message 0x800D (Message 800D)."""

    MESSAGE_ID = 0x800D
    MESSAGE_NAME = "Message 800D"


class OutdoorCompressor1LoadMessage(EnumMessage):
    """Parser for message 0x8010 (Outdoor Compressor 1 Load)."""

    MESSAGE_ID = 0x8010
    MESSAGE_NAME = "Outdoor Compressor 1 Load"
    MESSAGE_ENUM = OutdoorCompressorLoad


class OutdoorCompressor2LoadMessage(EnumMessage):
    """Parser for message 0x8011 (Outdoor Compressor 2 Load)."""

    MESSAGE_ID = 0x8011
    MESSAGE_NAME = "Outdoor Compressor 2 Load"
    MESSAGE_ENUM = OutdoorCompressorLoad


class OutdoorCompressor3LoadMessage(EnumMessage):
    """Parser for message 0x8012 (Outdoor Compressor 3 Load)."""

    MESSAGE_ID = 0x8012
    MESSAGE_NAME = "Outdoor Compressor 3 Load"
    MESSAGE_ENUM = OutdoorCompressorLoad


class OutdoorCch1LoadMessage(EnumMessage):
    """Parser for message 0x8013 (Outdoor CCH1 Load)."""

    MESSAGE_ID = 0x8013
    MESSAGE_NAME = "Outdoor CCH1 Load"
    MESSAGE_ENUM = OutdoorCchLoad


class OutdoorCch2LoadMessage(EnumMessage):
    """Parser for message 0x8014 (Outdoor CCH2 Load)."""

    MESSAGE_ID = 0x8014
    MESSAGE_NAME = "Outdoor CCH2 Load"
    MESSAGE_ENUM = OutdoorCchLoad


class OutdoorHotGas1LoadMessage(EnumMessage):
    """Parser for message 0x8017 (Outdoor Hot Gas 1 Load)."""

    MESSAGE_ID = 0x8017
    MESSAGE_NAME = "Outdoor Hot Gas 1 Load"
    MESSAGE_ENUM = OutdoorHotGasLoad


class OutdoorHotGas2LoadMessage(EnumMessage):
    """Parser for message 0x8018 (Outdoor Hot Gas 2 Load)."""

    MESSAGE_ID = 0x8018
    MESSAGE_NAME = "Outdoor Hot Gas 2 Load"
    MESSAGE_ENUM = OutdoorHotGasLoad


class OutdoorLiquidLoadMessage(EnumMessage):
    """Parser for message 0x8019 (Outdoor Liquid Load)."""

    MESSAGE_ID = 0x8019
    MESSAGE_NAME = "Outdoor Liquid Load"
    MESSAGE_ENUM = OutdoorLiquidLoad


class OutdoorLoad4WayValveMessage(EnumMessage):
    """Parser for message 0x801A (Outdoor Load 4-Way Valve)."""

    MESSAGE_ID = 0x801A
    MESSAGE_NAME = "Outdoor Load 4-Way Valve"
    MESSAGE_ENUM = Outdoor4WayLoad


class OutdoorMainCoolLoadMessage(EnumMessage):
    """Parser for message 0x801F (Outdoor Main Cool Load)."""

    MESSAGE_ID = 0x801F
    MESSAGE_NAME = "Outdoor Main Cool Load"
    MESSAGE_ENUM = OutdoorMainCoolLoad


class OutdoorLoadOutEevMessage(EnumMessage):
    """Parser for message 0x8020 (Load EEV status) - Enum value indicating on/off state."""

    MESSAGE_ID = 0x8020
    MESSAGE_NAME = "Load EEV status"
    MESSAGE_ENUM = OutdoorOutEevLoad


class OutdoorEviBypassLoadMessage(EnumMessage):
    """Parser for message 0x8021 (EVI Bypass Load)."""

    MESSAGE_ID = 0x8021
    MESSAGE_NAME = "EVI Bypass Load"
    MESSAGE_ENUM = OutdoorEviBypassLoad


class OutdoorVapourInjectionSolenoid1Status(EnumMessage):
    """Parser for message 0x8022 (Vapour injection solenoid1 status)."""

    MESSAGE_ID = 0x8022
    MESSAGE_NAME = "Vapour injection solenoid1 status"
    MESSAGE_ENUM = OutdoorEviSolenoid


class OutdoorVapourInjectionSolenoid2Status(EnumMessage):
    """Parser for message 0x8023 (Vapour injection solenoid2 status)."""

    MESSAGE_ID = 0x8023
    MESSAGE_NAME = "Vapour injection solenoid2 status"
    MESSAGE_ENUM = OutdoorEviSolenoid


class OutdoorGasChargeValveStatus(EnumMessage):
    """Parser for message 0x8025 (Gas charge valve status)."""

    MESSAGE_ID = 0x8025
    MESSAGE_NAME = "Gas charge valve status"
    MESSAGE_ENUM = OutdoorGasChargeLoad


class OutdoorWaterLoadValveStatus(EnumMessage):
    """Parser for message 0x8026 (Water load valve status)."""

    MESSAGE_ID = 0x8026
    MESSAGE_NAME = "Water load valve status"
    MESSAGE_ENUM = OutdoorWaterValveLoad


class OutdoorPumpOutValveStatus(EnumMessage):
    """Parser for message 0x8027 (Pump out valve status)."""

    MESSAGE_ID = 0x8027
    MESSAGE_NAME = "Pump out valve status"
    MESSAGE_ENUM = OutdoorPumpOutLoad


class Outdoor4wayValve2StatusMessage(EnumMessage):
    """Parser for message 0x802A (4Way valve 2 status)."""

    MESSAGE_ID = 0x802A
    MESSAGE_NAME = "4-Way Valve 2 Load"
    MESSAGE_ENUM = Outdoor4WayLoad


class OutdoorMessage8031(RawMessage):
    """Parser for message 0x8031 (Message 8031)."""

    MESSAGE_ID = 0x8031
    MESSAGE_NAME = "Message 8031"


class OutdoorMessage8032(RawMessage):
    """Parser for message 0x8032 (Message 8032)."""

    MESSAGE_ID = 0x8032
    MESSAGE_NAME = "Message 8032"


class OutdoorMessage8033(RawMessage):
    """Parser for message 0x8033 (Message 8033)."""

    MESSAGE_ID = 0x8033
    MESSAGE_NAME = "Message 8033"


class OutdoorLiquidTubeLoadStatus(RawMessage):
    """Parser for message 0x8034 (Liquid tube load status)."""

    MESSAGE_ID = 0x8034
    MESSAGE_NAME = "Liquid tube load status"


class OutdoorAccumulatorReturnValveStatus(RawMessage):
    """Parser for message 0x8037 (Accumulator return valve status)."""

    MESSAGE_ID = 0x8037
    MESSAGE_NAME = "Accumulator return valve status"


class OutdoorFlowSwitchStatus(RawMessage):
    """Parser for message 0x803B (Flow switch status)."""

    MESSAGE_ID = 0x803B
    MESSAGE_NAME = "Flow switch status"


class OutdoorAutomaticCheckStep(RawMessage):
    """Parser for message 0x803C (Automatic check step)."""

    MESSAGE_ID = 0x803C
    MESSAGE_NAME = "Automatic check step"


class OutdoorMessage803f(RawMessage):
    """Parser for message 0x803F (Message 803F)."""

    MESSAGE_ID = 0x803F
    MESSAGE_NAME = "Message 803F"


class OutdoorMessage8045(RawMessage):
    """Parser for message 0x8045 (Message 8045)."""

    MESSAGE_ID = 0x8045
    MESSAGE_NAME = "Message 8045"


class OutdoorAutomaticCheckStatus(RawMessage):
    """Parser for message 0x8046 (Automatic check status)."""

    MESSAGE_ID = 0x8046
    MESSAGE_NAME = "Automatic check status"


class OutdoorMessage8048(RawMessage):
    """Parser for message 0x8048 (Message 8048)."""

    MESSAGE_ID = 0x8048
    MESSAGE_NAME = "Message 8048"


class OutdoorMcuACoolingLoad(RawMessage):
    """Parser for message 0x8049 (MCU A cooling load)."""

    MESSAGE_ID = 0x8049
    MESSAGE_NAME = "MCU A cooling load"


class OutdoorMcuAHeatingLoad(RawMessage):
    """Parser for message 0x804A (MCU A heating load)."""

    MESSAGE_ID = 0x804A
    MESSAGE_NAME = "MCU A heating load"


class OutdoorMcuBCoolingLoad(RawMessage):
    """Parser for message 0x804B (MCU B cooling load)."""

    MESSAGE_ID = 0x804B
    MESSAGE_NAME = "MCU B cooling load"


class OutdoorMcuBHeatingLoad(RawMessage):
    """Parser for message 0x804C (MCU B heating load)."""

    MESSAGE_ID = 0x804C
    MESSAGE_NAME = "MCU B heating load"


class OutdoorMcuCCoolingLoad(RawMessage):
    """Parser for message 0x804D (MCU C cooling load)."""

    MESSAGE_ID = 0x804D
    MESSAGE_NAME = "MCU C cooling load"


class OutdoorMcuCHeatingLoad(RawMessage):
    """Parser for message 0x804E (MCU C heating load)."""

    MESSAGE_ID = 0x804E
    MESSAGE_NAME = "MCU C heating load"


class OutdoorMcuDCoolingLoad(RawMessage):
    """Parser for message 0x804F (MCU D cooling load)."""

    MESSAGE_ID = 0x804F
    MESSAGE_NAME = "MCU D cooling load"


class OutdoorMcuDHeatingLoad(RawMessage):
    """Parser for message 0x8050 (MCU D heating load)."""

    MESSAGE_ID = 0x8050
    MESSAGE_NAME = "MCU D heating load"


class OutdoorMcuECoolingLoad(RawMessage):
    """Parser for message 0x8051 (MCU E cooling load)."""

    MESSAGE_ID = 0x8051
    MESSAGE_NAME = "MCU E cooling load"


class OutdoorMcuEHeatingLoad(RawMessage):
    """Parser for message 0x8052 (MCU E heating load)."""

    MESSAGE_ID = 0x8052
    MESSAGE_NAME = "MCU E heating load"


class OutdoorMcuFCoolingLoad(RawMessage):
    """Parser for message 0x8053 (MCU F cooling load)."""

    MESSAGE_ID = 0x8053
    MESSAGE_NAME = "MCU F cooling load"


class OutdoorMcuFHeatingLoad(RawMessage):
    """Parser for message 0x8054 (MCU F heating load)."""

    MESSAGE_ID = 0x8054
    MESSAGE_NAME = "MCU F heating load"


class OutdoorMcuLiquidLoad(RawMessage):
    """Parser for message 0x8055 (MCU liquid load)."""

    MESSAGE_ID = 0x8055
    MESSAGE_NAME = "MCU liquid load"


class OutdoorMcuPort0Address(RawMessage):
    """Parser for message 0x8058 (MCU port 0 address)."""

    MESSAGE_ID = 0x8058
    MESSAGE_NAME = "MCU port 0 address"


class OutdoorMcuPort1Address(RawMessage):
    """Parser for message 0x8059 (MCU port 1 address)."""

    MESSAGE_ID = 0x8059
    MESSAGE_NAME = "MCU port 1 address"


class OutdoorMcuPort2Address(RawMessage):
    """Parser for message 0x805A (MCU port 2 address)."""

    MESSAGE_ID = 0x805A
    MESSAGE_NAME = "MCU port 2 address"


class OutdoorMcuPort3Address(RawMessage):
    """Parser for message 0x805B (MCU port 3 address)."""

    MESSAGE_ID = 0x805B
    MESSAGE_NAME = "MCU port 3 address"


class OutdoorMcuPort4Address(RawMessage):
    """Parser for message 0x805C (MCU port 4 address)."""

    MESSAGE_ID = 0x805C
    MESSAGE_NAME = "MCU port 4 address"


class OutdoorMcuPort5Address(RawMessage):
    """Parser for message 0x805D (MCU port 5 address)."""

    MESSAGE_ID = 0x805D
    MESSAGE_NAME = "MCU port 5 address"


class OutdoorMessage805e(RawMessage):
    """Parser for message 0x805E (Message 805E)."""

    MESSAGE_ID = 0x805E
    MESSAGE_NAME = "Message 805E"


class OutdoorDefrostStatus(EnumMessage):
    """Parser for message 0x8061 (Outdoor Defrost Status)."""

    MESSAGE_ID = 0x8061
    MESSAGE_NAME = "Outdoor Defrost Status"
    MESSAGE_ENUM = OutdoorIndoorDefrostStep
    ENUM_DEFAULT = OutdoorIndoorDefrostStep.NO_DEFROST_OPERATION


class OutdoorMessage8062(RawMessage):
    """Parser for message 0x8062 (Message 8062)."""

    MESSAGE_ID = 0x8062
    MESSAGE_NAME = "Message 8062"


class OutdoorMessage8063(RawMessage):
    """Parser for message 0x8063 (Message 8063)."""

    MESSAGE_ID = 0x8063
    MESSAGE_NAME = "Message 8063"


class OutdoorMessage8066(RawMessage):
    """Parser for message 0x8066 (Message 8066)."""

    MESSAGE_ID = 0x8066
    MESSAGE_NAME = "Message 8066"


class OutdoorMessage8075(RawMessage):
    """Parser for message 0x8075 (Message 8075)."""

    MESSAGE_ID = 0x8075
    MESSAGE_NAME = "Message 8075"


class OutdoorMessage8077(RawMessage):
    """Parser for message 0x8077 (Message 8077)."""

    MESSAGE_ID = 0x8077
    MESSAGE_NAME = "Message 8077"


class OutdoorMessage8078(RawMessage):
    """Parser for message 0x8078 (Message 8078)."""

    MESSAGE_ID = 0x8078
    MESSAGE_NAME = "Message 8078"


class OutdoorMessage8079(RawMessage):
    """Parser for message 0x8079 (Message 8079)."""

    MESSAGE_ID = 0x8079
    MESSAGE_NAME = "Message 8079"


class OutdoorMessage807a(RawMessage):
    """Parser for message 0x807A (Message 807A)."""

    MESSAGE_ID = 0x807A
    MESSAGE_NAME = "Message 807A"


class OutdoorMessage807b(RawMessage):
    """Parser for message 0x807B (Message 807B)."""

    MESSAGE_ID = 0x807B
    MESSAGE_NAME = "Message 807B"


class OutdoorMessage807c(RawMessage):
    """Parser for message 0x807C (Message 807C)."""

    MESSAGE_ID = 0x807C
    MESSAGE_NAME = "Message 807C"


class OutdoorMessage807d(RawMessage):
    """Parser for message 0x807D (Message 807D)."""

    MESSAGE_ID = 0x807D
    MESSAGE_NAME = "Message 807D"


class OutdoorMessage807e(RawMessage):
    """Parser for message 0x807E (Message 807E)."""

    MESSAGE_ID = 0x807E
    MESSAGE_NAME = "Message 807E"


class OutdoorMessage807f(RawMessage):
    """Parser for message 0x807F (Message 807F)."""

    MESSAGE_ID = 0x807F
    MESSAGE_NAME = "Message 807F"


class OutdoorMessage8081(RawMessage):
    """Parser for message 0x8081 (Message 8081)."""

    MESSAGE_ID = 0x8081
    MESSAGE_NAME = "Message 8081"


class OutdoorMessage8083(RawMessage):
    """Parser for message 0x8083 (Message 8083)."""

    MESSAGE_ID = 0x8083
    MESSAGE_NAME = "Message 8083"


class OutdoorMessage808d(RawMessage):
    """Parser for message 0x808D (Message 808D)."""

    MESSAGE_ID = 0x808D
    MESSAGE_NAME = "Message 808D"


class OutdoorOperationReferenceStep(RawMessage):
    """Parser for message 0x808E (Operation reference step)."""

    MESSAGE_ID = 0x808E
    MESSAGE_NAME = "Operation reference step"


class OutdoorNoOfOutdoorUnits(RawMessage):
    """Parser for message 0x8092 (No. of Outdoor Units)."""

    MESSAGE_ID = 0x8092
    MESSAGE_NAME = "No. of Outdoor Units"


class OutdoorNoOfFans(RawMessage):
    """Parser for message 0x8099 (No. of fans)."""

    MESSAGE_ID = 0x8099
    MESSAGE_NAME = "No. of fans"


class OutdoorRefrigerantInventory(RawMessage):
    """Parser for message 0x809C (Refrigerant inventory)."""

    MESSAGE_ID = 0x809C
    MESSAGE_NAME = "Refrigerant inventory"


class OutdoorCoolOnlyModel(EnumMessage):
    """Parser for message 0x809D (Outdoor Cool Only Model)."""

    MESSAGE_ID = 0x809D
    MESSAGE_NAME = "Outdoor Cool Only Model"
    MESSAGE_ENUM = OutOutdoorCoolonlyModel


class OutdoorCboxCoolingFanStatus(RawMessage):
    """Parser for message 0x809E (Cbox cooling fan status)."""

    MESSAGE_ID = 0x809E
    MESSAGE_NAME = "Cbox cooling fan status"


class OutdoorBackupOperationStatus(RawMessage):
    """Parser for message 0x80A5 (Backup operation status)."""

    MESSAGE_ID = 0x80A5
    MESSAGE_NAME = "Backup operation status"


class OutdoorCompressorProtectionControlOperationStatus(RawMessage):
    """Parser for message 0x80A6 (Compressor protection control operation status)."""

    MESSAGE_ID = 0x80A6
    MESSAGE_NAME = "Compressor protection control operation status"


class OutdoorMessage80a7(RawMessage):
    """Parser for message 0x80A7 (Message 80A7)."""

    MESSAGE_ID = 0x80A7
    MESSAGE_NAME = "Message 80A7"


class OutdoorMessage80a9(RawMessage):
    """Parser for message 0x80A9 (Message 80A9)."""

    MESSAGE_ID = 0x80A9
    MESSAGE_NAME = "Message 80A9"


class OutdoorMessage80aa(RawMessage):
    """Parser for message 0x80AA (Message 80AA)."""

    MESSAGE_ID = 0x80AA
    MESSAGE_NAME = "Message 80AA"


class OutdoorBaseHeater(RawMessage):
    """Parser for message 0x80AF (Base Heater)."""

    MESSAGE_ID = 0x80AF
    MESSAGE_NAME = "Base Heater"


class OutdoorMessage80b1(RawMessage):
    """Parser for message 0x80B1 (Message 80B1)."""

    MESSAGE_ID = 0x80B1
    MESSAGE_NAME = "Message 80B1"


class OutdoorMessage80b2(RawMessage):
    """Parser for message 0x80B2 (Message 80B2)."""

    MESSAGE_ID = 0x80B2
    MESSAGE_NAME = "Message 80B2"


class OutdoorAccumulatorValveStatus(RawMessage):
    """Parser for message 0x80B4 (Accumulator valve status)."""

    MESSAGE_ID = 0x80B4
    MESSAGE_NAME = "Accumulator valve status"


class OutdoorMessage80b6(RawMessage):
    """Parser for message 0x80B6 (Message 80B6)."""

    MESSAGE_ID = 0x80B6
    MESSAGE_NAME = "Message 80B6"


class OutdoorOilBypassValve1Status(RawMessage):
    """Parser for message 0x80B8 (Oil bypass valve 1 status)."""

    MESSAGE_ID = 0x80B8
    MESSAGE_NAME = "Oil bypass valve 1 status"


class OutdoorOilBypassValve2Status(RawMessage):
    """Parser for message 0x80B9 (Oil bypass valve 2 status)."""

    MESSAGE_ID = 0x80B9
    MESSAGE_NAME = "Oil bypass valve 2 status"


class OutdoorMessage80bc(RawMessage):
    """Parser for message 0x80BC (Message 80BC)."""

    MESSAGE_ID = 0x80BC
    MESSAGE_NAME = "Message 80BC"


class OutdoorA2CurrentMode(RawMessage):
    """Parser for message 0x80BE (A2* current mode)."""

    MESSAGE_ID = 0x80BE
    MESSAGE_NAME = "A2* current mode"


class OutdoorMessage80bf(RawMessage):
    """Parser for message 0x80BF (Message 80BF)."""

    MESSAGE_ID = 0x80BF
    MESSAGE_NAME = "Message 80BF"


class OutdoorA2aValveStatus(RawMessage):
    """Parser for message 0x80C1 (A2A valve status)."""

    MESSAGE_ID = 0x80C1
    MESSAGE_NAME = "A2A valve status"


class OutdoorMessage80ce(RawMessage):
    """Parser for message 0x80CE (Message 80CE)."""

    MESSAGE_ID = 0x80CE
    MESSAGE_NAME = "Message 80CE"


class OutdoorMessage80cf(RawMessage):
    """Parser for message 0x80CF (Message 80CF)."""

    MESSAGE_ID = 0x80CF
    MESSAGE_NAME = "Message 80CF"


class OutdoorPheHeater(RawMessage):
    """Parser for message 0x80D7 (PHE Heater)."""

    MESSAGE_ID = 0x80D7
    MESSAGE_NAME = "PHE Heater"


class OutdoorWateroutType(RawMessage):
    """Parser for message 0x80D8 (Waterout Type)."""

    MESSAGE_ID = 0x80D8
    MESSAGE_NAME = "Waterout Type"


class OutdoorMessage8200(FloatMessage):
    """Parser for message 0x8200 (Message 8200)."""

    MESSAGE_ID = 0x8200
    MESSAGE_NAME = "Message 8200"


class OutdoorNoOutdoorCompressors(FloatMessage):
    """Parser for message 0x8202 (No. outdoor compressors)."""

    MESSAGE_ID = 0x8202
    MESSAGE_NAME = "No. outdoor compressors"


class OutdoorAirTemperature(BasicTemperatureMessage):
    """Parser for message 0x8204 (Outdoor Air Temperature)."""

    MESSAGE_ID = 0x8204
    MESSAGE_NAME = "Outdoor Air Temperature"


class OutdoorHighPressure(FloatMessage):
    """Parser for message 0x8206 (High Pressure)."""

    MESSAGE_ID = 0x8206
    MESSAGE_NAME = "High Pressure"


class OutdoorLowPressure(FloatMessage):
    """Parser for message 0x8208 (Low Pressure)."""

    MESSAGE_ID = 0x8208
    MESSAGE_NAME = "Low Pressure"


class CondenserInTemperature(BasicTemperatureMessage):
    """Parser for message 0x820A (Condenser In Temperature)."""

    MESSAGE_ID = 0x820A
    MESSAGE_NAME = "Condenser In Temperature"


class OutdoorCompressorDischarge2(FloatMessage):
    """Parser for message 0x820C (Compressor discharge2)."""

    MESSAGE_ID = 0x820C
    MESSAGE_NAME = "Compressor discharge2"


class OutdoorCompressorDischarge3(FloatMessage):
    """Parser for message 0x820E (Compressor discharge3)."""

    MESSAGE_ID = 0x820E
    MESSAGE_NAME = "Compressor discharge3"


class OutdoorCurrent(BasicCurrentMessage):
    """Parser for message 0x8217 (Outdoor Current)."""

    MESSAGE_ID = 0x8217
    MESSAGE_NAME = "Outdoor Current"
    SIGNED = False
    ARITHMETIC = 0.1


class OutdoorCondoutTemp(BasicTemperatureMessage):
    """Parser for message 0x8218 (Evaporator In Temperature)."""

    MESSAGE_ID = 0x8218
    MESSAGE_NAME = "Evaporator In Temperature"


class OutdoorSuctionSensorTemperature(BasicTemperatureMessage):
    """Parser for message 0x821A (Outdoor Suction Sensor Temperature)."""

    MESSAGE_ID = 0x821A
    MESSAGE_NAME = "Outdoor Suction Sensor Temperature"


class OutdoorDoubleTubeTemp(BasicTemperatureMessage):
    """Parser for message 0x821C (Double tube temp)."""

    MESSAGE_ID = 0x821C
    MESSAGE_NAME = "Double tube temp"


class OutdoorEviIn(BasicTemperatureMessage):
    """Parser for message 0x821E (EVI IN)."""

    MESSAGE_ID = 0x821E
    MESSAGE_NAME = "EVI IN"


class OutdoorEviOut(BasicTemperatureMessage):
    """Parser for message 0x8220 (EVI OUT)."""

    MESSAGE_ID = 0x8220
    MESSAGE_NAME = "EVI OUT"


class OutdoorTargetDischargeTemperature(BasicTemperatureMessage):
    """Parser for message 0x8223 (Outdoor Target Discharge Temperature)."""

    MESSAGE_ID = 0x8223
    MESSAGE_NAME = "Outdoor Target Discharge Temperature"


class OutdoorMessage8224(BasicTemperatureMessage):
    """Parser for message 0x8224 (Message 8224)."""

    MESSAGE_ID = 0x8224
    MESSAGE_NAME = "Message 8224"


class OutdoorUnknownTemperatureSensorA(BasicTemperatureMessage):
    """Parser for message 0x8225 (Unknown Temperature Sensor)."""

    MESSAGE_ID = 0x8225
    MESSAGE_NAME = "Unknown Temperature Sensor"


class OutdoorFanSpeedStepSetting(FloatMessage):
    """Parser for message 0x8226 (Fan speed step setting)."""

    MESSAGE_ID = 0x8226
    MESSAGE_NAME = "Fan speed step setting"
    SIGNED = False


class OutdoorMessage8227(FloatMessage):
    """Parser for message 0x8227 (Message 8227)."""

    MESSAGE_ID = 0x8227
    MESSAGE_NAME = "Message 8227"


class OutdoorEev1Opening(FloatMessage):
    """Parser for message 0x8229 (EEV1 Position)."""

    MESSAGE_ID = 0x8229
    MESSAGE_NAME = "EEV1 Position"


class OutdoorEev2Opening(FloatMessage):
    """Parser for message 0x822A (EEV2 Position)."""

    MESSAGE_ID = 0x822A
    MESSAGE_NAME = "EEV2 Position"


class OutdoorEev3Opening(FloatMessage):
    """Parser for message 0x822B (EEV3 Position)."""

    MESSAGE_ID = 0x822B
    MESSAGE_NAME = "EEV3 Position"


class OutdoorEev4Opening(FloatMessage):
    """Parser for message 0x822C (EEV4 Position)."""

    MESSAGE_ID = 0x822C
    MESSAGE_NAME = "EEV4 Position"


class OutdoorEev5Opening(FloatMessage):
    """Parser for message 0x822D (EEV5 Position)."""

    MESSAGE_ID = 0x822D
    MESSAGE_NAME = "EEV5 Position"


class OutdoorEviEev(FloatMessage):
    """Parser for message 0x822E (EVI EEV)."""

    MESSAGE_ID = 0x822E
    MESSAGE_NAME = "EVI EEV"


class OutdoorCompressorRunning(FloatMessage):
    """Parser for message 0x8231 (Compressor running?)."""

    MESSAGE_ID = 0x8231
    MESSAGE_NAME = "Compressor running?"


class OutdoorOperationCapaSum(FloatMessage):
    """Parser for message 0x8233 (Outdoor Operation Capacity Sum)."""

    MESSAGE_ID = 0x8233
    MESSAGE_NAME = "Outdoor Operation Capacity Sum"
    SIGNED = False
    ARITHMETIC = 0.086  # might need to change this to 8.5


class OutdoorMessage8234(FloatMessage):
    """Parser for message 0x8234 (Message 8234)."""

    MESSAGE_ID = 0x8234
    MESSAGE_NAME = "Message 8234"


class OutdoorErrorCode(FloatMessage):
    """Parser for message 0x8235 (Duplicate of 0x0202) - Error code as numeric value."""

    MESSAGE_ID = 0x8235
    MESSAGE_NAME = "Outdoor Error Code"


class OutdoorCompressorOrderFrequency(IntegerMessage):
    """Parser for message 0x8236 (Outdoor Compressor Order Frequency)."""

    MESSAGE_ID = 0x8236
    MESSAGE_NAME = "Outdoor Compressor Order Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorCompressorTargetFrequency(IntegerMessage):
    """Parser for message 0x8237 (Outdoor Compressor Target Frequency)."""

    MESSAGE_ID = 0x8237
    MESSAGE_NAME = "Outdoor Compressor Target Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorCompressorRunFrequency(IntegerMessage):
    """Parser for message 0x8238 (Outdoor Compressor Run Frequency)."""

    MESSAGE_ID = 0x8238
    MESSAGE_NAME = "Outdoor Compressor Run Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorMessage8239(FloatMessage):
    """Parser for message 0x8239 (Message 8239)."""

    MESSAGE_ID = 0x8239
    MESSAGE_NAME = "Message 8239"


class OutdoorDcLinkVoltage(FloatMessage):
    """Parser for 0x823b (Outdoor DC Link Voltage)."""

    MESSAGE_ID = 0x823B
    MESSAGE_NAME = "Outdoor DC Link Voltage"
    UNIT_OF_MEASUREMENT = "V"
    ARITHMETIC = 1.0
    SIGNED = False


class OutdoorMessage823c(FloatMessage):
    """Parser for message 0x823C (Message 823C)."""

    MESSAGE_ID = 0x823C
    MESSAGE_NAME = "Message 823C"


class OutdoorFanRpm1(FloatMessage):
    """Parser for message 0x823D (Outdoor Fan RPM 1)."""

    MESSAGE_ID = 0x823D
    MESSAGE_NAME = "Outdoor Fan RPM 1"
    UNIT_OF_MEASUREMENT = "RPM"
    SIGNED = False


class OutdoorFanRpm2(FloatMessage):
    """Parser for message 0x823E (Outdoor Fan RPM 1)."""

    MESSAGE_ID = 0x823E
    MESSAGE_NAME = "Outdoor Fan RPM 2"
    UNIT_OF_MEASUREMENT = "RPM"
    SIGNED = False


class OutdoorControlPrimeUnit(FloatMessage):
    """Parser for message 0x823F (Outdoor Control Prime Unit)."""

    MESSAGE_ID = 0x823F
    MESSAGE_NAME = "Outdoor Control Prime Unit"


class OutdoorMessage8240(FloatMessage):
    """Parser for message 0x8240 (Message 8240)."""

    MESSAGE_ID = 0x8240
    MESSAGE_NAME = "Message 8240"


class OutdoorMessage8243(FloatMessage):
    """Parser for message 0x8243 (Message 8243)."""

    MESSAGE_ID = 0x8243
    MESSAGE_NAME = "Message 8243"


class OutdoorMessage8244(FloatMessage):
    """Parser for message 0x8244 (Message 8244)."""

    MESSAGE_ID = 0x8244
    MESSAGE_NAME = "Message 8244"


class OutdoorMessage8245(FloatMessage):
    """Parser for message 0x8245 (Message 8245)."""

    MESSAGE_ID = 0x8245
    MESSAGE_NAME = "Message 8245"


class OutdoorDefrostStage(FloatMessage):
    """Parser for message 0x8247 (Outdoor Defrost Stage)."""

    MESSAGE_ID = 0x8247
    MESSAGE_NAME = "Outdoor Defrost Stage"


class OutdoorSafetyStart(FloatMessage):
    """Parser for message 0x8248 (Outdoor Safety Start)."""

    MESSAGE_ID = 0x8248
    MESSAGE_NAME = "Outdoor Safety Start"


class OutdoorMessage8249(FloatMessage):
    """Parser for message 0x8249 (Message 8249)."""

    MESSAGE_ID = 0x8249
    MESSAGE_NAME = "Message 8249"


class OutdoorMessage824b(FloatMessage):
    """Parser for message 0x824B (Message 824B)."""

    MESSAGE_ID = 0x824B
    MESSAGE_NAME = "Message 824B"


class OutdoorMessage824c(FloatMessage):
    """Parser for message 0x824C (Message 824C)."""

    MESSAGE_ID = 0x824C
    MESSAGE_NAME = "Message 824C"


class OutdoorRefrigerantVolume(FloatMessage):
    """Parser for message 0x8249 (Outdoor Refrigerant Volume)."""

    MESSAGE_ID = 0x824F
    MESSAGE_NAME = "Outdoor Refrigerant Volume"
    ARITHMETIC = 0.1


class OutdoorIpmTemp1(BasicTemperatureMessage):
    """Parser for message 0x8254 (Outdoor IPM Temp 1)."""

    MESSAGE_ID = 0x8254
    MESSAGE_NAME = "Outdoor IPM Temp 1"


class OutdoorIpmTemp2(BasicTemperatureMessage):
    """Parser for message 0x8255 (Outdoor IPM Temp 2)."""

    MESSAGE_ID = 0x8255
    MESSAGE_NAME = "Outdoor IPM Temp 2"


class OutdoorMessage825a(FloatMessage):
    """Parser for message 0x825A (Message 825A)."""

    MESSAGE_ID = 0x825A
    MESSAGE_NAME = "Message 825A"


class OutdoorMessage825b(FloatMessage):
    """Parser for message 0x825B (Message 825B)."""

    MESSAGE_ID = 0x825B
    MESSAGE_NAME = "Message 825B"


class OutdoorMessage825c(FloatMessage):
    """Parser for message 0x825C (Message 825C)."""

    MESSAGE_ID = 0x825C
    MESSAGE_NAME = "Message 825C"


class OutdoorMessage825d(FloatMessage):
    """Parser for message 0x825D (Message 825D)."""

    MESSAGE_ID = 0x825D
    MESSAGE_NAME = "Message 825D"


class OutdoorWaterTempSensor(FloatMessage):
    """Parser for message 0x825E (Water temp sensor)."""

    MESSAGE_ID = 0x825E
    MESSAGE_NAME = "Water temp sensor"


class OutdoorPipe1InletTemp(FloatMessage):
    """Parser for message 0x825F (Pipe1 inlet temp)."""

    MESSAGE_ID = 0x825F
    MESSAGE_NAME = "Pipe1 inlet temp"


class OutdoorPipe2InletTemp(FloatMessage):
    """Parser for message 0x8260 (Pipe2 inlet temp)."""

    MESSAGE_ID = 0x8260
    MESSAGE_NAME = "Pipe2 inlet temp"


class OutdoorPipe3InletTemp(FloatMessage):
    """Parser for message 0x8261 (Pipe3 inlet temp)."""

    MESSAGE_ID = 0x8261
    MESSAGE_NAME = "Pipe3 inlet temp"


class OutdoorPipe4InletTemp(FloatMessage):
    """Parser for message 0x8262 (Pipe4 inlet temp)."""

    MESSAGE_ID = 0x8262
    MESSAGE_NAME = "Pipe4 inlet temp"


class OutdoorPipe5InletTemp(FloatMessage):
    """Parser for message 0x8263 (Pipe5 inlet temp)."""

    MESSAGE_ID = 0x8263
    MESSAGE_NAME = "Pipe5 inlet temp"


class OutdoorPipe1OutletTemp(FloatMessage):
    """Parser for message 0x8264 (Pipe1 outlet temp)."""

    MESSAGE_ID = 0x8264
    MESSAGE_NAME = "Pipe1 outlet temp"


class OutdoorPipe2OutletTemp(FloatMessage):
    """Parser for message 0x8265 (Pipe2 outlet temp)."""

    MESSAGE_ID = 0x8265
    MESSAGE_NAME = "Pipe2 outlet temp"


class OutdoorPipe3OutletTemp(FloatMessage):
    """Parser for message 0x8266 (Pipe3 outlet temp)."""

    MESSAGE_ID = 0x8266
    MESSAGE_NAME = "Pipe3 outlet temp"


class OutdoorPipe4OutletTemp(FloatMessage):
    """Parser for message 0x8267 (Pipe4 outlet temp)."""

    MESSAGE_ID = 0x8267
    MESSAGE_NAME = "Pipe4 outlet temp"


class OutdoorPipe5OutletTemp(FloatMessage):
    """Parser for message 0x8268 (Pipe5 outlet temp)."""

    MESSAGE_ID = 0x8268
    MESSAGE_NAME = "Pipe5 outlet temp"


class OutdoorMcuSubcoolerInletTemp(FloatMessage):
    """Parser for message 0x826B (MCU subcooler inlet temp)."""

    MESSAGE_ID = 0x826B
    MESSAGE_NAME = "MCU subcooler inlet temp"


class OutdoorMcuSubcoolerOutletTemp(FloatMessage):
    """Parser for message 0x826C (MCU subcooler outlet temp)."""

    MESSAGE_ID = 0x826C
    MESSAGE_NAME = "MCU subcooler outlet temp"


class OutdoorMcuSubcoolerEev(FloatMessage):
    """Parser for message 0x826D (MCU subcooler EEV)."""

    MESSAGE_ID = 0x826D
    MESSAGE_NAME = "MCU subcooler EEV"


class OutdoorMcuChangeoverEev1(FloatMessage):
    """Parser for message 0x826E (MCU changeover EEV1)."""

    MESSAGE_ID = 0x826E
    MESSAGE_NAME = "MCU changeover EEV1"


class OutdoorMcuChangeoverEev2(FloatMessage):
    """Parser for message 0x826F (MCU changeover EEV2)."""

    MESSAGE_ID = 0x826F
    MESSAGE_NAME = "MCU changeover EEV2"


class OutdoorMcuChangeoverEev3(FloatMessage):
    """Parser for message 0x8270 (MCU changeover EEV3)."""

    MESSAGE_ID = 0x8270
    MESSAGE_NAME = "MCU changeover EEV3"


class OutdoorMcuChangeoverEev4(FloatMessage):
    """Parser for message 0x8271 (MCU changeover EEV4)."""

    MESSAGE_ID = 0x8271
    MESSAGE_NAME = "MCU changeover EEV4"


class OutdoorMcuChangeoverEev5(FloatMessage):
    """Parser for message 0x8272 (MCU changeover EEV5)."""

    MESSAGE_ID = 0x8272
    MESSAGE_NAME = "MCU changeover EEV5"


class OutdoorMcuChangeoverEev6(FloatMessage):
    """Parser for message 0x8273 (MCU changeover EEV6)."""

    MESSAGE_ID = 0x8273
    MESSAGE_NAME = "MCU changeover EEV6"


class OutdoorCompressor2OrderFrequency(IntegerMessage):
    """Parser for message 0x8274 (Compressor 2 order frequency)."""

    MESSAGE_ID = 0x8274
    MESSAGE_NAME = "Compressor 2 order frequency"


class OutdoorCompressor2TargetFrequency(IntegerMessage):
    """Parser for message 0x8275 (Compressor 2 target frequency)."""

    MESSAGE_ID = 0x8275
    MESSAGE_NAME = "Compressor 2 target frequency"


class OutdoorCompressor2CurrentFrequency(IntegerMessage):
    """Parser for message 0x8276 (Compressor 2 current frequency)."""

    MESSAGE_ID = 0x8276
    MESSAGE_NAME = "Compressor 2 current frequency"


class OutdoorCompressor2Current(FloatMessage):
    """Parser for message 0x8277 (Compressor 2 current)."""

    MESSAGE_ID = 0x8277
    MESSAGE_NAME = "Compressor 2 current"


class OutdoorOct1(FloatMessage):
    """Parser for message 0x8278 (OCT1)."""

    MESSAGE_ID = 0x8278
    MESSAGE_NAME = "OCT1"


class OutdoorDesuperheaterTemp(FloatMessage):
    """Parser for message 0x827A (Desuperheater temp)."""

    MESSAGE_ID = 0x827A
    MESSAGE_NAME = "Desuperheater temp"


class OutdoorTopSensorTemp1(BasicTemperatureMessage):
    """Parser for message 0x8280 (Outdoor Top Sensor Temp 1)."""

    MESSAGE_ID = 0x8280
    MESSAGE_NAME = "Outdoor Top Sensor Temp 1"


class OutdoorTopSensorTemp2(BasicTemperatureMessage):
    """Parser for message 0x8281 (Outdoor Top Sensor Temp 2)."""

    MESSAGE_ID = 0x8281
    MESSAGE_NAME = "Outdoor Top Sensor Temp 2"


class OutdoorCondenserMidpointTemp(FloatMessage):
    """Parser for message 0x8285 (Condenser mid-point temp)."""

    MESSAGE_ID = 0x8285
    MESSAGE_NAME = "Condenser mid-point temp"


class OutdoorInstalledCapacity(FloatMessage):
    """Parser for message 0x8287 (Installed capacity)."""

    MESSAGE_ID = 0x8287
    MESSAGE_NAME = "Installed capacity"


class OutdoorMessage8298(FloatMessage):
    """Parser for message 0x8298 (Message 8298)."""

    MESSAGE_ID = 0x8298
    MESSAGE_NAME = "Message 8298"


class OutdoorCompressor2SuctionTemp(FloatMessage):
    """Parser for message 0x829A (Compressor 2 suction temp)."""

    MESSAGE_ID = 0x829A
    MESSAGE_NAME = "Compressor 2 suction temp"


class OutdoorMessage829b(FloatMessage):
    """Parser for message 0x829B (Message 829B)."""

    MESSAGE_ID = 0x829B
    MESSAGE_NAME = "Message 829B"


class OutdoorSaturatedTpd(FloatMessage):
    """Parser for message 0x829F (Saturated T_Pd)."""

    MESSAGE_ID = 0x829F
    MESSAGE_NAME = "Saturated T_Pd"


class OutdoorSensorLowPressTemp(BasicTemperatureMessage):
    """Parser for message 0x82A0 (Outdoor Sensor Low Press Temp)."""

    MESSAGE_ID = 0x82A0
    MESSAGE_NAME = "Outdoor Sensor Low Press Temp"


class OutdoorMessage82a2(FloatMessage):
    """Parser for message 0x82A2 (Message 82A2)."""

    MESSAGE_ID = 0x82A2
    MESSAGE_NAME = "Message 82A2"


class OutdoorIduAbsoluteCapacity(FloatMessage):
    """Parser for message 0x82A8 (IDU absolute capacity)."""

    MESSAGE_ID = 0x82A8
    MESSAGE_NAME = "IDU absolute capacity"


class OutdoorMessage82a9(FloatMessage):
    """Parser for message 0x82A9 (Message 82A9)."""

    MESSAGE_ID = 0x82A9
    MESSAGE_NAME = "Message 82A9"


class OutdoorMessage82aa(FloatMessage):
    """Parser for message 0x82AA (Message 82AA)."""

    MESSAGE_ID = 0x82AA
    MESSAGE_NAME = "Message 82AA"


class OutdoorCondenserInstalledSize(FloatMessage):
    """Parser for message 0x82AF (Condenser installed size)."""

    MESSAGE_ID = 0x82AF
    MESSAGE_NAME = "Condenser installed size"


class OutdoorMessage82b2(FloatMessage):
    """Parser for message 0x82B2 (Message 82B2)."""

    MESSAGE_ID = 0x82B2
    MESSAGE_NAME = "Message 82B2"


class OutdoorMessage82b5(FloatMessage):
    """Parser for message 0x82B5 (Message 82B5)."""

    MESSAGE_ID = 0x82B5
    MESSAGE_NAME = "Message 82B5"


class OutdoorCompressorInterstagePressure(FloatMessage):
    """Parser for message 0x82B8 (Compressor interstage pressure)."""

    MESSAGE_ID = 0x82B8
    MESSAGE_NAME = "Compressor interstage pressure"


class OutdoorProjectCode(StrMessage):
    """Parser for message 0x82BC (Outdoor Project Code)."""

    MESSAGE_ID = 0x82BC
    MESSAGE_NAME = "Outdoor Project Code"


class OutdoorFluxValveLoad(FloatMessage):
    """Parser for message 0x82BD (Flux valve load)."""

    MESSAGE_ID = 0x82BD
    MESSAGE_NAME = "Flux valve load"


class OutdoorControlBoxTemp(FloatMessage):
    """Parser for message 0x82BE (Control box temp)."""

    MESSAGE_ID = 0x82BE
    MESSAGE_NAME = "Control box temp"


class OutdoorCondenser2OutletTemp(FloatMessage):
    """Parser for message 0x82BF (Condenser2 outlet temp)."""

    MESSAGE_ID = 0x82BF
    MESSAGE_NAME = "Condenser2 outlet temp"


class OutdoorAccumulatorTemp(FloatMessage):
    """Parser for message 0x82C8 (Accumulator temp)."""

    MESSAGE_ID = 0x82C8
    MESSAGE_NAME = "Accumulator temp"


class OutdoorEngineWaterTemp(FloatMessage):
    """Parser for message 0x82C9 (Engine water temp)."""

    MESSAGE_ID = 0x82C9
    MESSAGE_NAME = "Engine water temp"


class OutdoorOilBypassValvePosition(FloatMessage):
    """Parser for message 0x82CA (Oil bypass valve position)."""

    MESSAGE_ID = 0x82CA
    MESSAGE_NAME = "Oil bypass valve position"


class OutdoorCompressorSuctionSuperheat(FloatMessage):
    """Parser for message 0x82CB (Compressor suction superheat)."""

    MESSAGE_ID = 0x82CB
    MESSAGE_NAME = "Compressor suction superheat"


class OutdoorCondenserOutletSuperheat(FloatMessage):
    """Parser for message 0x82CC (Condenser outlet superheat)."""

    MESSAGE_ID = 0x82CC
    MESSAGE_NAME = "Condenser outlet superheat"


class OutdoorOutdoorUnitOutletSubcool(FloatMessage):
    """Parser for message 0x82CD (Outdoor Unit outlet subcool?)."""

    MESSAGE_ID = 0x82CD
    MESSAGE_NAME = "Outdoor Unit outlet subcool?"


class OutdoorCondenserOutletSubcool(FloatMessage):
    """Parser for message 0x82CE (Condenser outlet subcool)."""

    MESSAGE_ID = 0x82CE
    MESSAGE_NAME = "Condenser outlet subcool"


class OutdoorEngineRpm(FloatMessage):
    """Parser for message 0x82CF (Engine rpm)."""

    MESSAGE_ID = 0x82CF
    MESSAGE_NAME = "Engine rpm"


class OutdoorAppearanceRpm(FloatMessage):
    """Parser for message 0x82D0 (Appearance rpm?)."""

    MESSAGE_ID = 0x82D0
    MESSAGE_NAME = "Appearance rpm?"


class OutdoorMessage82d1(FloatMessage):
    """Parser for message 0x82D1 (Message 82D1)."""

    MESSAGE_ID = 0x82D1
    MESSAGE_NAME = "Message 82D1"


class OutdoorSubcoolerEevStep(FloatMessage):
    """Parser for message 0x82D2 (Subcooler EEV step)."""

    MESSAGE_ID = 0x82D2
    MESSAGE_NAME = "Subcooler EEV step"


class OutdoorMessage82d5(FloatMessage):
    """Parser for message 0x82D5 (Message 82D5)."""

    MESSAGE_ID = 0x82D5
    MESSAGE_NAME = "Message 82D5"


class OutdoorMessage82d6(FloatMessage):
    """Parser for message 0x82D6 (Message 82D6)."""

    MESSAGE_ID = 0x82D6
    MESSAGE_NAME = "Message 82D6"


class OutdoorMessage82d7(FloatMessage):
    """Parser for message 0x82D7 (Message 82D7)."""

    MESSAGE_ID = 0x82D7
    MESSAGE_NAME = "Message 82D7"


class OutdoorMessage82d8(FloatMessage):
    """Parser for message 0x82D8 (Message 82D8)."""

    MESSAGE_ID = 0x82D8
    MESSAGE_NAME = "Message 82D8"


class OutdoorPhaseCurrent(FloatMessage):
    """Parser for message 0x82DB (Outdoor Phase Current)."""

    MESSAGE_ID = 0x82DB
    MESSAGE_NAME = "Outdoor Phase Current"
    UNIT_OF_MEASUREMENT = "A"
    SIGNED = False


class CondenserOutTemperature(BasicTemperatureMessage):
    """Parser for message 0x82DE (Condenser Out Temperature)."""

    MESSAGE_ID = 0x82DE
    MESSAGE_NAME = "Condenser Out Temperature"


class OutdoorTw1Temperature(BasicTemperatureMessage):
    """Parser for message 0x82df (Outdoor TW1 Temperature)."""

    MESSAGE_ID = 0x82DF
    MESSAGE_NAME = "Outdoor TW1 Temperature"


class OutdoorTw2Temperature(BasicTemperatureMessage):
    """Parser for message 0x82E0 (Outdoor TW2 Temperature)."""

    MESSAGE_ID = 0x82E0
    MESSAGE_NAME = "Outdoor TW2 Temperature"


class OutdoorProductCapa(BasicPowerMessage):
    """Parser for message 0x82e3 (Outdoor Product Capacity)."""

    MESSAGE_ID = 0x82E3
    MESSAGE_NAME = "Outdoor Product Capacity"


class OutdoorCombinedSuctionTemp(FloatMessage):
    """Parser for message 0x82E7 (Evaporator Out Temperature)."""

    MESSAGE_ID = 0x82E7
    MESSAGE_NAME = "Evaporator Out Temperature"


class OutdoorMotorControlUnitBypassEevPosition(FloatMessage):
    """Parser for message 0x82E8 (Motor Control Unit bypass EEV position)."""

    MESSAGE_ID = 0x82E8
    MESSAGE_NAME = "Motor Control Unit bypass EEV position"


class OutdoorPowerFactorCorrectionElementTemp(FloatMessage):
    """Parser for message 0x82E9 (Power factor correction element temp)."""

    MESSAGE_ID = 0x82E9
    MESSAGE_NAME = "Power factor correction element temp"


class OutdoorMessage82ed(FloatMessage):
    """Parser for message 0x82ED (Message 82ED)."""

    MESSAGE_ID = 0x82ED
    MESSAGE_NAME = "Message 82ED"


class OutdoorPowerFactorCorrectionOverloadDetection(FloatMessage):
    """Parser for message 0x82F5 (Power factor correction overload detection)."""

    MESSAGE_ID = 0x82F5
    MESSAGE_NAME = "Power factor correction overload detection"


class OutdoorMessage82f6(FloatMessage):
    """Parser for message 0x82F6 (Message 82F6)."""

    MESSAGE_ID = 0x82F6
    MESSAGE_NAME = "Message 82F6"


class OutdoorCompressorSuction3Temp(BasicTemperatureMessage):
    """Parser for message 0x82F9 (Compressor suction3 temp)."""

    MESSAGE_ID = 0x82F9
    MESSAGE_NAME = "Compressor suction3 temp"


class OutdoorEviSolEev(FloatMessage):
    """Parser for message 0x82FC (EVI SOL EEV)."""

    MESSAGE_ID = 0x82FC
    MESSAGE_NAME = "EVI SOL EEV"


class OutdoorMessage8401(RawMessage):
    """Parser for message 0x8401 (Message 8401)."""

    MESSAGE_ID = 0x8401
    MESSAGE_NAME = "Message 8401"


class OutdoorMessage8404(RawMessage):
    """Parser for message 0x8404 (Message 8404)."""

    MESSAGE_ID = 0x8404
    MESSAGE_NAME = "Message 8404"


class OutdoorCompressorRunningTime(FloatMessage):
    """Parser for message 0x8405 (Compressor running time 1).

    Represents the total cumulative running time of compressor 1 in hours.
    Type: LVAR (Long Variable - 4 bytes, unsigned)
    Unit: hours
    """

    MESSAGE_ID = 0x8405
    MESSAGE_NAME = "Compressor running time 1"
    ARITHMETIC = 1  # Direct value, no scaling
    SIGNED = False  # Unsigned integer


class OutdoorCompressor2RunningTime(FloatMessage):
    """Parser for message 0x8406 (Compressor running time 2).

    Represents the total cumulative running time of compressor 2 in hours.
    Type: LVAR (Long Variable - 4 bytes, unsigned)
    Unit: hours
    """

    MESSAGE_ID = 0x8406
    MESSAGE_NAME = "Compressor running time 2"
    ARITHMETIC = 1  # Direct value, no scaling
    SIGNED = False  # Unsigned integer


class OutdoorMessage8408(RawMessage):
    """Parser for message 0x8408 (Message 8408)."""

    MESSAGE_ID = 0x8408
    MESSAGE_NAME = "Message 8408"


class OutdoorMessage8409(RawMessage):
    """Parser for message 0x8409 (Message 8409)."""

    MESSAGE_ID = 0x8409
    MESSAGE_NAME = "Message 8409"


class OutdoorInspectionResult0(RawMessage):
    """Parser for message 0x840B (Inspection result 0)."""

    MESSAGE_ID = 0x840B
    MESSAGE_NAME = "Inspection result 0"


class OutdoorInspectionResult1(RawMessage):
    """Parser for message 0x840C (Inspection result 1)."""

    MESSAGE_ID = 0x840C
    MESSAGE_NAME = "Inspection result 1"


class OutLayerVariableOut1Message(FloatMessage):
    """Parser for message 0x840F (Layer Variable OUT 1).

    Undocumented outdoor unit layer variable.
    Appears to be a numeric value (4 bytes, 0x00001280 = 4736 decimal).
    Possibly related to system configuration or status.
    """

    MESSAGE_ID = 0x840F
    MESSAGE_NAME = "Layer Variable OUT 1"


class OutdoorMessage8411(RawMessage):
    """Parser for message 0x8411 (Message 8411)."""

    MESSAGE_ID = 0x8411
    MESSAGE_NAME = "Message 8411"


class OutdoorInstantaneousPower(BasicPowerMessage):
    """Parser for message 0x8413 (Outdoor Instantaneous Power)."""

    MESSAGE_ID = 0x8413
    MESSAGE_NAME = "Outdoor Instantaneous Power"
    SIGNED = False
    ARITHMETIC = 0.001


class OutdoorCumulativeEnergy(BasicEnergyMessage):
    """Parser for message 0x8414 (Outdoor Cumulative Energy)."""

    MESSAGE_ID = 0x8414
    MESSAGE_NAME = "Outdoor Cumulative Energy"
    SIGNED = False
    ARITHMETIC = 0.001


class OutdoorMessage8417(RawMessage):
    """Parser for message 0x8417 (Message 8417)."""

    MESSAGE_ID = 0x8417
    MESSAGE_NAME = "Message 8417"


class OutdoorMessage841a(RawMessage):
    """Parser for message 0x841A (Message 841A)."""

    MESSAGE_ID = 0x841A
    MESSAGE_NAME = "Message 841A"


class OutdoorMessage841f(RawMessage):
    """Parser for message 0x841F (Message 841F)."""

    MESSAGE_ID = 0x841F
    MESSAGE_NAME = "Message 841F"


class OutdoorInverter1Micom(StrMessage):
    """Parser for message 0x8601 (Inverter1 Micom)."""

    MESSAGE_ID = 0x8601
    MESSAGE_NAME = "Inverter1 Micom"


class OutdoorMessage8608(StrMessage):
    """Parser for message 0x8608 (Message 8608)."""

    MESSAGE_ID = 0x8608
    MESSAGE_NAME = "Message 8608"


class OutdoorBaseOptionInfo(RawMessage):
    """Parser for message 0x860A (Base option info).

    This is a binary structure message containing base/default option settings
    for the outdoor unit. The structure format is:
    - Bytes 0-3: Header (reserved/metadata)
    - Bytes 4+: Variable-length configuration fields

    Example payload breakdown:
    Header: 00000000 (metadata)
    Data: Configuration option bytes
    """

    MESSAGE_ID = 0x860A
    MESSAGE_NAME = "Base option info"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "OutdoorBaseOptionInfo":
        """Parse the payload into a structured representation."""
        if not payload or len(payload) < 4:
            return cls(value=payload.hex() if payload else None)

        # Extract header (4 bytes) - contains metadata about the structure
        header_bytes = payload[0:4]
        header_int = int.from_bytes(header_bytes, byteorder="big")

        # Extract data portion (remaining bytes)
        data_portion = payload[4:]

        # Return decoded structure with hex representation and interpretations
        result = {
            "header_hex": header_bytes.hex(),
            "header_value": header_int,
            "data_hex": data_portion.hex() if data_portion else "",
            "data_length": len(data_portion),
            "total_length": len(payload),
            "raw_hex": payload.hex(),
            "note": "Structure definition not yet available in NASA.ptc - fields represent outdoor unit base option configuration",
        }
        return cls(value=result)


class OutdoorMessage860c(RawMessage):
    """Parser for message 0x860C (Message 860C).

    This is a binary structure message. The exact purpose is not yet documented.
    The structure format is:
    - Bytes 0-3: Header (reserved/metadata)
    - Bytes 4+: Variable-length configuration fields
    """

    MESSAGE_ID = 0x860C
    MESSAGE_NAME = "Message 860C"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "OutdoorMessage860c":
        """Parse the payload into a structured representation."""
        if not payload or len(payload) < 4:
            return cls(value=payload.hex() if payload else None)

        header_bytes = payload[0:4]
        header_int = int.from_bytes(header_bytes, byteorder="big")
        data_portion = payload[4:]

        result = {
            "header_hex": header_bytes.hex(),
            "header_value": header_int,
            "data_hex": data_portion.hex() if data_portion else "",
            "data_length": len(data_portion),
            "total_length": len(payload),
            "raw_hex": payload.hex(),
        }
        return cls(value=result)


class OutdoorInstalledOutdoorUnitModelInfo(RawMessage):
    """Parser for message 0x860D (Installed Outdoor Unit model info).

    This is a binary structure message containing model information for the
    outdoor unit. The structure format is:
    - Bytes 0-3: Header (reserved/metadata)
    - Bytes 4+: Variable-length configuration fields
    """

    MESSAGE_ID = 0x860D
    MESSAGE_NAME = "Installed Outdoor Unit model info"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "OutdoorInstalledOutdoorUnitModelInfo":
        """Parse the payload into a structured representation."""
        if not payload or len(payload) < 4:
            return cls(value=payload.hex() if payload else None)

        header_bytes = payload[0:4]
        header_int = int.from_bytes(header_bytes, byteorder="big")
        data_portion = payload[4:]

        result = {
            "header_hex": header_bytes.hex(),
            "header_value": header_int,
            "data_hex": data_portion.hex() if data_portion else "",
            "data_length": len(data_portion),
            "total_length": len(payload),
            "raw_hex": payload.hex(),
            "note": "Structure definition not yet available in NASA.ptc - fields represent outdoor unit model information",
        }
        return cls(value=result)


class OutdoorInstalledOutdoorUnitSetupInfo(RawMessage):
    """Parser for message 0x860F (Installed Outdoor Unit setup info).

    This is a binary structure message with the format:
    - Bytes 0-3: Header (reserved, appears to contain a count or version)
    - Bytes 4+: Variable-length configuration fields

    The payload structure contains installation setup information for the outdoor unit,
    including various configuration parameters. The exact field definitions are not yet
    documented in NASA.ptc, but the data is preserved for analysis.

    Example payload breakdown:
    Header: 00000009 (9 configuration items)
    Data: 7 variable-length fields following
    """

    MESSAGE_ID = 0x860F
    MESSAGE_NAME = "Installed Outdoor Unit setup info"

    @classmethod
    def parse_payload(cls, payload: bytes) -> "OutdoorInstalledOutdoorUnitSetupInfo":
        """Parse the payload into a structured representation."""
        if not payload or len(payload) < 4:
            return cls(value=payload.hex() if payload else None)

        # Extract header (4 bytes) - contains metadata about the structure
        header_bytes = payload[0:4]
        header_int = int.from_bytes(header_bytes, byteorder="big")

        # Extract data portion (remaining bytes)
        data_portion = payload[4:]

        # Return decoded structure with hex representation and interpretations
        result = {
            "header_hex": header_bytes.hex(),
            "header_value": header_int,
            "data_hex": data_portion.hex() if data_portion else "",
            "data_length": len(data_portion),
            "total_length": len(payload),
            "raw_hex": payload.hex(),
            "note": "Structure definition not yet available in NASA.ptc - fields represent outdoor unit setup configuration",
        }
        return cls(value=result)


class OutdoorOutdoorUnitCheckInfo(StrMessage):
    """Parser for message 0x8613 (Outdoor Unit check info)."""

    MESSAGE_ID = 0x8613
    MESSAGE_NAME = "Outdoor Unit check info"
