"""Outdoor unit messages."""

from ..messaging import EnumMessage, FloatMessage, BasicTemperatureMessage, BasicPowerMessage, RawMessage, StrMessage
from ...enum import OutdoorOperationStatus, OutdoorOperationMode


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


class OutdoorOperationServiceMessage(RawMessage):
    """Parser for message 0x8000 (Outdoor Operation Service)."""

    MESSAGE_ID = 0x8000
    MESSAGE_NAME = "Outdoor Operation Service"
    MESSAGE_ENUM = OutdoorOperationStatus


class OutdoorOperationStatusMessage(EnumMessage):
    """Parser for message 0x8001 (Outdoor Operation Status)."""

    MESSAGE_ID = 0x8001
    MESSAGE_NAME = "Outdoor Operation Status"
    MESSAGE_ENUM = OutdoorOperationStatus


class OutdoorOperationHeatCoolMessage(EnumMessage):
    """Parser for message 0x8003 (Outdoor Operation Heat/Cool)."""

    MESSAGE_ID = 0x8003
    MESSAGE_NAME = "Outdoor Operation Mode"
    MESSAGE_ENUM = OutdoorOperationMode


class OutdoorCompressor1Status(FloatMessage):
    """Parser for message 0x8010 (Outdoor Compressor 1 Status)."""

    MESSAGE_ID = 0x8010
    MESSAGE_NAME = "Outdoor Compressor 1 Status"


class OutdoorLoadHotGas1(RawMessage):
    """Parser for message 0x8011 (Outdoor Load Hot Gas 1)."""

    MESSAGE_ID = 0x8011
    MESSAGE_NAME = "Outdoor Load Hot Gas 1"


class OutdoorLoadHotGas2(RawMessage):
    """Parser for message 0x8012 (Outdoor Load Hot Gas 2)."""

    MESSAGE_ID = 0x8012
    MESSAGE_NAME = "Outdoor Load Hot Gas 2"


class OutdoorLoad4WayValveMessage(RawMessage):
    """Parser for message 0x801A (Outdoor Load 4-Way Valve)."""

    MESSAGE_ID = 0x801A
    MESSAGE_NAME = "Outdoor Load 4-Way Valve"


class OutdoorLoadOutEev(BasicPowerMessage):
    """Parser for message 0x8020 (Outdoor Load Out EEV)."""

    MESSAGE_ID = 0x8020
    MESSAGE_NAME = "Outdoor Load Out EEV"


class OutdoorSuctionSensorTemperature(BasicTemperatureMessage):
    """Parser for message 0x821A (Outdoor Suction Sensor Temperature)."""

    MESSAGE_ID = 0x821A
    MESSAGE_NAME = "Outdoor Suction Sensor Temperature"


class OutdoorTargetDischargeTemperature(BasicTemperatureMessage):
    """Parser for message 0x8223 (Outdoor Target Discharge Temperature)."""

    MESSAGE_ID = 0x8223
    MESSAGE_NAME = "Outdoor Target Discharge Temperature"


class OutdoorUnknownTemperatureSensorA(BasicTemperatureMessage):
    """Parser for message 0x8225 (Unknown Temperature Sensor)."""

    MESSAGE_ID = 0x8225
    MESSAGE_NAME = "Unknown Temperature Sensor"


class OutdoorOperationCapaSum(FloatMessage):
    """Parser for message 0x8233 (Outdoor Operation Capacity Sum)."""

    MESSAGE_ID = 0x8233
    MESSAGE_NAME = "Outdoor Operation Capacity Sum"
    SIGNED = False
    ARITHMETIC = 0.086  # might need to change this to 8.5


class OutdoorErrorCode(RawMessage):
    """Parser for message 0x8235 (Outdoor Error Code)."""

    MESSAGE_ID = 0x8235
    MESSAGE_NAME = "Outdoor Error Code"


class OutdoorCompressorOrderFrequency(FloatMessage):
    """Parser for message 0x8236 (Outdoor Compressor Order Frequency)."""

    MESSAGE_ID = 0x8236
    MESSAGE_NAME = "Outdoor Compressor Order Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorCompressorTargetFrequency(FloatMessage):
    """Parser for message 0x8237 (Outdoor Compressor Target Frequency)."""

    MESSAGE_ID = 0x8237
    MESSAGE_NAME = "Outdoor Compressor Target Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorCompressorRunFrequency(FloatMessage):
    """Parser for message 0x8238 (Outdoor Compressor Run Frequency)."""

    MESSAGE_ID = 0x8238
    MESSAGE_NAME = "Outdoor Compressor Run Frequency"
    UNIT_OF_MEASUREMENT = "Hz"


class OutdoorDcLinkVoltage(FloatMessage):
    """Parser for 0x823b (Outdoor DC Link Voltage)."""

    MESSAGE_ID = 0x823B
    MESSAGE_NAME = "Outdoor DC Link Voltage"
    UNIT_OF_MEASUREMENT = "V"


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


class OutdoorDefrostStage(FloatMessage):
    """Parser for message 0x8247 (Outdoor Defrost Stage)."""

    MESSAGE_ID = 0x8247
    MESSAGE_NAME = "Outdoor Defrost Stage"


class OutdoorSafetyStart(FloatMessage):
    """Parser for message 0x8248 (Outdoor Safety Start)."""

    MESSAGE_ID = 0x8248
    MESSAGE_NAME = "Outdoor Safety Start"


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


class OutdoorTopSensorTemp1(BasicTemperatureMessage):
    """Parser for message 0x8280 (Outdoor Top Sensor Temp 1)."""

    MESSAGE_ID = 0x8280
    MESSAGE_NAME = "Outdoor Top Sensor Temp 1"


class OutdoorTopSensorTemp2(BasicTemperatureMessage):
    """Parser for message 0x8281 (Outdoor Top Sensor Temp 2)."""

    MESSAGE_ID = 0x8281
    MESSAGE_NAME = "Outdoor Top Sensor Temp 2"


class OutdoorSensorLowPressTemp(BasicTemperatureMessage):
    """Parser for message 0x82A0 (Outdoor Sensor Low Press Temp)."""

    MESSAGE_ID = 0x82A0
    MESSAGE_NAME = "Outdoor Sensor Low Press Temp"


class OutdoorProjectCode(StrMessage):
    """Parser for message 0x82BC (Outdoor Project Code)."""

    MESSAGE_ID = 0x82BC
    MESSAGE_NAME = "Outdoor Project Code"


class OutdoorPhaseCurrent(FloatMessage):
    """Parser for message 0x82DB (Outdoor Phase Current)."""

    MESSAGE_ID = 0x82DB
    MESSAGE_NAME = "Outdoor Phase Current"
    UNIT_OF_MEASUREMENT = "A"
    SIGNED = False


class OutdoorEvaInTemperature(BasicTemperatureMessage):
    """Parser for message 0x82DE (Outdoor Eva In Temperature)."""

    MESSAGE_ID = 0x82DE
    MESSAGE_NAME = "Outdoor Eva In Temperature"


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


class OutdoorTempSet(BasicTemperatureMessage):
    """Parser for message 0x4201 (Outdoor Temp Set)."""

    MESSAGE_ID = 0x4201
    MESSAGE_NAME = "Outdoor Temp Set"


class OutdoorTempEvaIn(BasicTemperatureMessage):
    """Parser for message 0x4204 (Outdoor Temp Eva In)."""

    MESSAGE_ID = 0x4204
    MESSAGE_NAME = "Outdoor Temp Eva In"


class OutdoorTempEvaOut(BasicTemperatureMessage):
    """Parser for message 0x4205 (Outdoor Temp Eva Out)."""

    MESSAGE_ID = 0x4205
    MESSAGE_NAME = "Outdoor Temp Eva Out"
