"""Tests for protocol enums."""

import pytest
from pysamsungnasa.protocol.enum import (
    SamsungEnum,
    AddressClass,
    PacketType,
    DataType,
    MessageSetType,
    InOperationPower,
    InOperationMode,
    InFanMode,
    OutdoorOperationStatus,
)


class TestSamsungEnum:
    """Tests for SamsungEnum base class."""

    def test_enum_str(self):
        """Test enum string representation."""
        assert str(AddressClass.INDOOR) == "INDOOR"
        assert str(AddressClass.OUTDOOR) == "OUTDOOR"

    def test_enum_has_value(self):
        """Test has_value class method."""
        assert AddressClass.has_value(0x20)
        assert AddressClass.has_value(0x10)
        assert not AddressClass.has_value(0x99)


class TestAddressClass:
    """Tests for AddressClass enum."""

    def test_address_class_values(self):
        """Test AddressClass enum values."""
        assert AddressClass.UNKNOWN == 0x00
        assert AddressClass.OUTDOOR == 0x10
        assert AddressClass.HTU == 0x11
        assert AddressClass.INDOOR == 0x20
        assert AddressClass.ERV == 0x30
        assert AddressClass.DIFFUSER == 0x35
        assert AddressClass.MCU == 0x38
        assert AddressClass.RMC == 0x40
        assert AddressClass.WIRED_REMOTE == 0x50
        assert AddressClass.PIM == 0x58
        assert AddressClass.SIM == 0x59
        assert AddressClass.PEAK == 0x5A
        assert AddressClass.POWER_DIVIDER == 0x5B
        assert AddressClass.WIFI_KIT == 0x62
        assert AddressClass.CENTRAL_CONTROLLER == 0x65
        assert AddressClass.JIG_TESTER == 0x80
        assert AddressClass.BML == 0xB0
        assert AddressClass.BCL == 0xB1
        assert AddressClass.BSL == 0xB2
        assert AddressClass.BCSL == 0xB3
        assert AddressClass.BMDL == 0xB4
        assert AddressClass.BCSM == 0xB7
        assert AddressClass.BLL == 0xB8
        assert AddressClass.BCSML == 0xB9
        assert AddressClass.UNDEFINED == 0xFF

    def test_address_class_from_value(self):
        """Test creating AddressClass from value."""
        assert AddressClass(0x20) == AddressClass.INDOOR
        assert AddressClass(0x10) == AddressClass.OUTDOOR

    def test_address_class_has_value(self):
        """Test has_value for AddressClass."""
        assert AddressClass.has_value(0x20)
        assert AddressClass.has_value(0x10)
        assert not AddressClass.has_value(0x21)


class TestPacketType:
    """Tests for PacketType enum."""

    def test_packet_type_values(self):
        """Test PacketType enum values."""
        assert PacketType.UNKNOWN == -1
        assert PacketType.STANDBY == 0
        assert PacketType.NORMAL == 1
        assert PacketType.GATHERING == 2
        assert PacketType.INSTALL == 3
        assert PacketType.DOWNLOAD == 4

    def test_packet_type_from_value(self):
        """Test creating PacketType from value."""
        assert PacketType(1) == PacketType.NORMAL
        assert PacketType(0) == PacketType.STANDBY

    def test_packet_type_str(self):
        """Test PacketType string representation."""
        assert str(PacketType.NORMAL) == "NORMAL"
        assert str(PacketType.STANDBY) == "STANDBY"


class TestDataType:
    """Tests for DataType enum."""

    def test_data_type_values(self):
        """Test DataType enum values."""
        assert DataType.UNKNOWN == -1
        assert DataType.UNDEFINED == 0
        assert DataType.READ == 1
        assert DataType.WRITE == 2
        assert DataType.REQUEST == 3
        assert DataType.NOTIFICATION == 4
        assert DataType.RESPONSE == 5
        assert DataType.ACK == 6
        assert DataType.NACK == 7

    def test_data_type_from_value(self):
        """Test creating DataType from value."""
        assert DataType(3) == DataType.REQUEST
        assert DataType(5) == DataType.RESPONSE

    def test_data_type_str(self):
        """Test DataType string representation."""
        assert str(DataType.REQUEST) == "REQUEST"
        assert str(DataType.RESPONSE) == "RESPONSE"


class TestMessageSetType:
    """Tests for MessageSetType enum."""

    def test_message_set_type_values(self):
        """Test MessageSetType enum values."""
        assert MessageSetType.ENUM == 0
        assert MessageSetType.VARIABLE == 1
        assert MessageSetType.LONG_VARIABLE == 2
        assert MessageSetType.STRUCTURE == 3

    def test_message_set_type_from_value(self):
        """Test creating MessageSetType from value."""
        assert MessageSetType(0) == MessageSetType.ENUM
        assert MessageSetType(3) == MessageSetType.STRUCTURE


class TestInOperationPower:
    """Tests for InOperationPower enum."""

    def test_in_operation_power_values(self):
        """Test InOperationPower enum values."""
        assert InOperationPower.OFF == 0
        assert InOperationPower.ON_STATE_1 == 1
        assert InOperationPower.ON_STATE_2 == 2

    def test_in_operation_power_str(self):
        """Test InOperationPower string representation."""
        assert str(InOperationPower.OFF) == "OFF"
        assert str(InOperationPower.ON_STATE_1) == "ON_STATE_1"


class TestInOperationMode:
    """Tests for InOperationMode enum."""

    def test_in_operation_mode_values(self):
        """Test InOperationMode enum values."""
        assert InOperationMode.AUTO == 0
        assert InOperationMode.COOL == 1
        assert InOperationMode.DRY == 2
        assert InOperationMode.FAN == 3
        assert InOperationMode.HEAT == 4
        assert InOperationMode.COOL_STORAGE == 21
        assert InOperationMode.HOT_WATER == 24

    def test_in_operation_mode_str(self):
        """Test InOperationMode string representation."""
        assert str(InOperationMode.AUTO) == "AUTO"
        assert str(InOperationMode.COOL) == "COOL"
        assert str(InOperationMode.HEAT) == "HEAT"


class TestInFanMode:
    """Tests for InFanMode enum."""

    def test_in_fan_mode_values(self):
        """Test InFanMode enum values."""
        assert InFanMode.AUTO == 0
        assert InFanMode.LOW == 1
        assert InFanMode.MID == 2
        assert InFanMode.HIGH == 3
        assert InFanMode.TURBO == 4

    def test_in_fan_mode_str(self):
        """Test InFanMode string representation."""
        assert str(InFanMode.AUTO) == "AUTO"
        assert str(InFanMode.LOW) == "LOW"
        assert str(InFanMode.TURBO) == "TURBO"


class TestOutdoorOperationStatus:
    """Tests for OutdoorOperationStatus enum."""

    def test_outdoor_operation_status_values(self):
        """Test OutdoorOperationStatus enum values."""
        assert OutdoorOperationStatus.OP_STOP == 0
        assert OutdoorOperationStatus.OP_SAFETY == 1
        assert OutdoorOperationStatus.OP_NORMAL == 2
        assert OutdoorOperationStatus.OP_BALANCE == 3
        assert OutdoorOperationStatus.OP_RECOVERY == 4
        assert OutdoorOperationStatus.OP_DEICE == 5

    def test_outdoor_operation_status_str(self):
        """Test OutdoorOperationStatus string representation."""
        assert str(OutdoorOperationStatus.OP_STOP) == "OP_STOP"
        assert str(OutdoorOperationStatus.OP_NORMAL) == "OP_NORMAL"
        assert str(OutdoorOperationStatus.OP_DEICE) == "OP_DEICE"

    def test_outdoor_operation_status_comprehensive(self):
        """Test comprehensive OutdoorOperationStatus values."""
        expected_values = {
            0: "OP_STOP",
            1: "OP_SAFETY",
            2: "OP_NORMAL",
            5: "OP_DEICE",
            11: "OP_CHARGE",
            19: "OP_CHECKREF",
            36: "OP_AUTO_CHARGE",
        }
        for value, name in expected_values.items():
            assert OutdoorOperationStatus(value).name == name
