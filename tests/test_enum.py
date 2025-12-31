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

    @pytest.mark.parametrize(
        "enum_val,expected_str",
        [
            (AddressClass.INDOOR, "INDOOR"),
            (AddressClass.OUTDOOR, "OUTDOOR"),
        ],
    )
    def test_enum_str(self, enum_val, expected_str):
        """Test enum string representation."""
        assert str(enum_val) == expected_str

    @pytest.mark.parametrize(
        "value,has_value",
        [
            (0x20, True),
            (0x10, True),
            (0x99, False),
        ],
    )
    def test_enum_has_value(self, value, has_value):
        """Test has_value class method."""
        assert AddressClass.has_value(value) == has_value


class TestAddressClass:
    """Tests for AddressClass enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("UNKNOWN", 0x00),
            ("OUTDOOR", 0x10),
            ("HTU", 0x11),
            ("INDOOR", 0x20),
            ("ERV", 0x30),
            ("DIFFUSER", 0x35),
            ("MCU", 0x38),
            ("RMC", 0x40),
            ("WIRED_REMOTE", 0x50),
            ("PIM", 0x58),
            ("SIM", 0x59),
            ("PEAK", 0x5A),
            ("POWER_DIVIDER", 0x5B),
            ("WIFI_KIT", 0x62),
            ("CENTRAL_CONTROLLER", 0x65),
            ("JIG_TESTER", 0x80),
            ("BML", 0xB0),
            ("BCL", 0xB1),
            ("BSL", 0xB2),
            ("BCSL", 0xB3),
            ("BMDL", 0xB4),
            ("BCSM", 0xB7),
            ("BLL", 0xB8),
            ("BCSML", 0xB9),
            ("UNDEFINED", 0xFF),
        ],
    )
    def test_address_class_values(self, attr_name, expected_value):
        """Test AddressClass enum values."""
        assert getattr(AddressClass, attr_name) == expected_value

    @pytest.mark.parametrize(
        "value,expected_class",
        [
            (0x20, AddressClass.INDOOR),
            (0x10, AddressClass.OUTDOOR),
        ],
    )
    def test_address_class_from_value(self, value, expected_class):
        """Test creating AddressClass from value."""
        assert AddressClass(value) == expected_class

    @pytest.mark.parametrize(
        "value,has_value",
        [
            (0x20, True),
            (0x10, True),
            (0x21, False),
        ],
    )
    def test_address_class_has_value(self, value, has_value):
        """Test has_value for AddressClass."""
        assert AddressClass.has_value(value) == has_value


class TestPacketType:
    """Tests for PacketType enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("UNKNOWN", -1),
            ("STANDBY", 0),
            ("NORMAL", 1),
            ("GATHERING", 2),
            ("INSTALL", 3),
            ("DOWNLOAD", 4),
        ],
    )
    def test_packet_type_values(self, attr_name, expected_value):
        """Test PacketType enum values."""
        assert getattr(PacketType, attr_name) == expected_value

    @pytest.mark.parametrize(
        "value,expected_type",
        [
            (1, PacketType.NORMAL),
            (0, PacketType.STANDBY),
        ],
    )
    def test_packet_type_from_value(self, value, expected_type):
        """Test creating PacketType from value."""
        assert PacketType(value) == expected_type

    @pytest.mark.parametrize(
        "packet_type,expected_str",
        [
            (PacketType.NORMAL, "NORMAL"),
            (PacketType.STANDBY, "STANDBY"),
        ],
    )
    def test_packet_type_str(self, packet_type, expected_str):
        """Test PacketType string representation."""
        assert str(packet_type) == expected_str


class TestDataType:
    """Tests for DataType enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("UNKNOWN", -1),
            ("UNDEFINED", 0),
            ("READ", 1),
            ("WRITE", 2),
            ("REQUEST", 3),
            ("NOTIFICATION", 4),
            ("RESPONSE", 5),
            ("ACK", 6),
            ("NACK", 7),
        ],
    )
    def test_data_type_values(self, attr_name, expected_value):
        """Test DataType enum values."""
        assert getattr(DataType, attr_name) == expected_value

    @pytest.mark.parametrize(
        "value,expected_type",
        [
            (3, DataType.REQUEST),
            (5, DataType.RESPONSE),
        ],
    )
    def test_data_type_from_value(self, value, expected_type):
        """Test creating DataType from value."""
        assert DataType(value) == expected_type

    @pytest.mark.parametrize(
        "data_type,expected_str",
        [
            (DataType.REQUEST, "REQUEST"),
            (DataType.RESPONSE, "RESPONSE"),
        ],
    )
    def test_data_type_str(self, data_type, expected_str):
        """Test DataType string representation."""
        assert str(data_type) == expected_str


class TestMessageSetType:
    """Tests for MessageSetType enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("ENUM", 0),
            ("VARIABLE", 1),
            ("LONG_VARIABLE", 2),
            ("STRUCTURE", 3),
        ],
    )
    def test_message_set_type_values(self, attr_name, expected_value):
        """Test MessageSetType enum values."""
        assert getattr(MessageSetType, attr_name) == expected_value

    @pytest.mark.parametrize(
        "value,expected_type",
        [
            (0, MessageSetType.ENUM),
            (3, MessageSetType.STRUCTURE),
        ],
    )
    def test_message_set_type_from_value(self, value, expected_type):
        """Test creating MessageSetType from value."""
        assert MessageSetType(value) == expected_type


class TestInOperationPower:
    """Tests for InOperationPower enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("OFF", 0),
            ("ON_STATE_1", 1),
            ("ON_STATE_2", 2),
        ],
    )
    def test_in_operation_power_values(self, attr_name, expected_value):
        """Test InOperationPower enum values."""
        assert getattr(InOperationPower, attr_name) == expected_value

    @pytest.mark.parametrize(
        "power_state,expected_str",
        [
            (InOperationPower.OFF, "OFF"),
            (InOperationPower.ON_STATE_1, "ON_STATE_1"),
        ],
    )
    def test_in_operation_power_str(self, power_state, expected_str):
        """Test InOperationPower string representation."""
        assert str(power_state) == expected_str


class TestInOperationMode:
    """Tests for InOperationMode enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("AUTO", 0),
            ("COOL", 1),
            ("DRY", 2),
            ("FAN", 3),
            ("HEAT", 4),
            ("COOL_STORAGE", 21),
            ("HOT_WATER", 24),
        ],
    )
    def test_in_operation_mode_values(self, attr_name, expected_value):
        """Test InOperationMode enum values."""
        assert getattr(InOperationMode, attr_name) == expected_value

    @pytest.mark.parametrize(
        "mode,expected_str",
        [
            (InOperationMode.AUTO, "AUTO"),
            (InOperationMode.COOL, "COOL"),
            (InOperationMode.HEAT, "HEAT"),
        ],
    )
    def test_in_operation_mode_str(self, mode, expected_str):
        """Test InOperationMode string representation."""
        assert str(mode) == expected_str


class TestInFanMode:
    """Tests for InFanMode enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("AUTO", 0),
            ("LOW", 1),
            ("MID", 2),
            ("HIGH", 3),
            ("TURBO", 4),
        ],
    )
    def test_in_fan_mode_values(self, attr_name, expected_value):
        """Test InFanMode enum values."""
        assert getattr(InFanMode, attr_name) == expected_value

    @pytest.mark.parametrize(
        "mode,expected_str",
        [
            (InFanMode.AUTO, "AUTO"),
            (InFanMode.LOW, "LOW"),
            (InFanMode.TURBO, "TURBO"),
        ],
    )
    def test_in_fan_mode_str(self, mode, expected_str):
        """Test InFanMode string representation."""
        assert str(mode) == expected_str


class TestOutdoorOperationStatus:
    """Tests for OutdoorOperationStatus enum."""

    @pytest.mark.parametrize(
        "attr_name,expected_value",
        [
            ("OP_STOP", 0),
            ("OP_SAFETY", 1),
            ("OP_NORMAL", 2),
            ("OP_BALANCE", 3),
            ("OP_RECOVERY", 4),
            ("OP_DEICE", 5),
        ],
    )
    def test_outdoor_operation_status_values(self, attr_name, expected_value):
        """Test OutdoorOperationStatus enum values."""
        assert getattr(OutdoorOperationStatus, attr_name) == expected_value

    @pytest.mark.parametrize(
        "status,expected_str",
        [
            (OutdoorOperationStatus.OP_STOP, "OP_STOP"),
            (OutdoorOperationStatus.OP_NORMAL, "OP_NORMAL"),
            (OutdoorOperationStatus.OP_DEICE, "OP_DEICE"),
        ],
    )
    def test_outdoor_operation_status_str(self, status, expected_str):
        """Test OutdoorOperationStatus string representation."""
        assert str(status) == expected_str

    @pytest.mark.parametrize(
        "value,expected_name",
        [
            (0, "OP_STOP"),
            (1, "OP_SAFETY"),
            (2, "OP_NORMAL"),
            (5, "OP_DEICE"),
            (11, "OP_CHARGE"),
            (19, "OP_CHECKREF"),
            (36, "OP_AUTO_CHARGE"),
        ],
    )
    def test_outdoor_operation_status_comprehensive(self, value, expected_name):
        """Test comprehensive OutdoorOperationStatus values."""
        assert OutdoorOperationStatus(value).name == expected_name
