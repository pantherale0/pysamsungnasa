"""Tests for NasaDevice write_attributes and message to_bytes functionality."""

import pytest
from unittest.mock import AsyncMock, Mock
from pysamsungnasa.device import NasaDevice
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.parser import NasaPacketParser
from pysamsungnasa.protocol.enum import AddressClass, DataType, InOperationPower, InOperationMode
from pysamsungnasa.protocol.factory.types import (
    BoolMessage,
    FloatMessage,
    BasicTemperatureMessage,
)
from pysamsungnasa.protocol.factory.messages.indoor import (
    InOperationPowerMessage,
    InOperationModeMessage,
    InTargetTemperature,
)


class TestBoolMessageToBytes:
    """Tests for BoolMessage.to_bytes() method."""

    def test_bool_message_true_to_bytes(self):
        """Test converting True to bytes."""
        payload = BoolMessage.to_bytes(True)
        assert payload == b"\x01"

    def test_bool_message_false_to_bytes(self):
        """Test converting False to bytes."""
        payload = BoolMessage.to_bytes(False)
        assert payload == b"\x00"

    def test_bool_message_round_trip(self):
        """Test parsing and rebuilding bool message gives same bytes."""
        original_payload = b"\x01"
        parsed = BoolMessage.parse_payload(original_payload)
        rebuilt_payload = BoolMessage.to_bytes(parsed.VALUE)
        assert rebuilt_payload == original_payload

    def test_bool_message_false_round_trip(self):
        """Test parsing False and rebuilding gives same bytes."""
        original_payload = b"\x00"
        parsed = BoolMessage.parse_payload(original_payload)
        rebuilt_payload = BoolMessage.to_bytes(parsed.VALUE)
        assert rebuilt_payload == original_payload


class TestEnumMessageToBytes:
    """Tests for EnumMessage.to_bytes() method."""

    def test_enum_message_to_bytes_operation_power(self):
        """Test converting enum value to bytes."""
        payload = InOperationPowerMessage.to_bytes(InOperationPower.ON_STATE_1)
        assert payload == b"\x01"

    def test_enum_message_to_bytes_operation_mode(self):
        """Test converting InOperationMode enum to bytes."""
        payload = InOperationModeMessage.to_bytes(InOperationMode.COOL)
        assert isinstance(payload, bytes)
        assert len(payload) == 1
        assert payload[0] == InOperationMode.COOL.value

    def test_enum_message_round_trip_power(self):
        """Test parsing and rebuilding power enum gives same bytes."""
        original_payload = b"\x01"
        parsed = InOperationPowerMessage.parse_payload(original_payload)
        rebuilt_payload = InOperationPowerMessage.to_bytes(parsed.VALUE)
        assert rebuilt_payload == original_payload
        assert parsed.VALUE == InOperationPower.ON_STATE_1

    def test_enum_message_round_trip_mode(self):
        """Test parsing and rebuilding operation mode gives same bytes."""
        original_payload = bytes([InOperationMode.HEAT.value])
        parsed = InOperationModeMessage.parse_payload(original_payload)
        rebuilt_payload = InOperationModeMessage.to_bytes(parsed.VALUE)
        assert rebuilt_payload == original_payload

    def test_enum_message_type_validation(self):
        """Test that EnumMessage properly encodes enum values."""
        # EnumMessage.to_bytes expects a SamsungEnum, so passing InOperationMode to InOperationPowerMessage
        # should work because both are valid enums - validation happens at the message level, not the base class
        payload = InOperationModeMessage.to_bytes(InOperationMode.HEAT)
        assert isinstance(payload, bytes)
        assert len(payload) == 1


class TestFloatMessageToBytes:
    """Tests for FloatMessage.to_bytes() method."""

    def test_temperature_message_to_bytes_simple(self):
        """Test converting temperature to bytes."""
        # 22.5°C * 10 = 225 = 0x00E1
        payload = BasicTemperatureMessage.to_bytes(22.5)
        assert isinstance(payload, bytes)
        # 225 as big-endian 2-byte unsigned = b'\x00\xe1'
        assert payload == b"\x00\xe1"

    def test_temperature_message_to_bytes_zero(self):
        """Test converting 0°C to bytes."""
        payload = BasicTemperatureMessage.to_bytes(0.0)
        # 0 * 10 = 0, which encodes to single byte b'\x00'
        assert payload == b"\x00"

    def test_temperature_message_to_bytes_negative(self):
        """Test converting negative temperature to bytes."""
        # -5.0°C * 10 = -50 (as signed 2-byte big-endian)
        payload = BasicTemperatureMessage.to_bytes(-5.0)
        assert isinstance(payload, bytes)
        assert len(payload) in [1, 2]

    def test_temperature_message_round_trip(self):
        """Test parsing and rebuilding temperature gives same value."""
        # 22.5°C encoded as 2 bytes big-endian unsigned
        original_payload = b"\x00\xe1"  # 225 = 22.5 * 10
        parsed = BasicTemperatureMessage.parse_payload(original_payload)
        rebuilt_payload = BasicTemperatureMessage.to_bytes(parsed.VALUE)
        assert rebuilt_payload == original_payload
        assert parsed.VALUE == 22.5

    def test_temperature_message_round_trip_various(self):
        """Test round-trip for various temperature values."""
        test_values = [0.0, 10.0, 22.5, 30.0, 45.0, 50.0]
        for temp in test_values:
            payload = BasicTemperatureMessage.to_bytes(temp)
            parsed = BasicTemperatureMessage.parse_payload(payload)
            rebuilt = BasicTemperatureMessage.to_bytes(parsed.VALUE)
            assert rebuilt == payload, f"Round-trip failed for {temp}°C"

    def test_float_message_arithmetic_validation(self):
        """Test that FloatMessage with ARITHMETIC=0 raises error."""

        class BadFloatMessage(FloatMessage):
            ARITHMETIC = 0

        with pytest.raises(ValueError, match="ARITHMETIC cannot be zero"):
            BadFloatMessage.to_bytes(10.0)


class TestWriteAttributes:
    """Tests for NasaDevice.write_attributes() method."""

    @pytest.fixture
    def device(self):
        """Create a test device with mocked client."""
        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        client = AsyncMock()
        device = NasaDevice(
            address="200001",
            device_type=AddressClass.INDOOR,
            packet_parser=parser,
            config=config,
            client=client,
        )
        return device

    @pytest.mark.asyncio
    async def test_write_single_attribute(self, device):
        """Test writing a single attribute."""
        await device.write_attribute(InOperationPowerMessage, InOperationPower.ON_STATE_1)

        device._client.send_message.assert_called_once()
        call_args = device._client.send_message.call_args
        assert call_args.kwargs["destination"] == "200001"
        assert call_args.kwargs["request_type"] == DataType.WRITE
        messages = call_args.kwargs["messages"]
        assert len(messages) == 1
        assert messages[0].MESSAGE_ID == 0x4000
        assert messages[0].PAYLOAD == b"\x01"

    @pytest.mark.asyncio
    async def test_write_multiple_attributes(self, device):
        """Test writing multiple attributes in one call."""
        await device.write_attributes(
            {
                InOperationPowerMessage: InOperationPower.ON_STATE_1,
                InOperationModeMessage: InOperationMode.COOL,
                InTargetTemperature: 22.5,
            }
        )

        device._client.send_message.assert_called_once()
        call_args = device._client.send_message.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) == 3

        # Check message IDs are correct
        message_ids = [msg.MESSAGE_ID for msg in messages]
        assert 0x4000 in message_ids  # Power
        assert 0x4001 in message_ids  # Mode
        assert 0x4201 in message_ids  # Target temp

    @pytest.mark.asyncio
    async def test_write_attributes_too_many(self, device):
        """Test that writing more than 10 attributes raises error."""
        # Create 11 different attributes to write
        attributes = {}
        for i in range(11):
            # Use different message classes (mock them)
            mock_msg_class = Mock()
            mock_msg_class.MESSAGE_ID = 0x4000 + i
            attributes[mock_msg_class] = i

        with pytest.raises(ValueError, match="Cannot write more than 10 messages"):
            await device.write_attributes(attributes)

    @pytest.mark.asyncio
    async def test_write_attribute_max_limit(self, device):
        """Test that exactly 10 attributes is allowed."""
        attributes = {}
        for i in range(10):
            mock_msg_class = Mock()
            mock_msg_class.MESSAGE_ID = 0x4000 + i
            attributes[mock_msg_class] = i

        # Should not raise
        await device.write_attributes(attributes)
        device._client.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_attribute_without_message_id(self, device):
        """Test that message class without MESSAGE_ID raises error."""
        mock_msg_class = Mock()
        mock_msg_class.MESSAGE_ID = None

        with pytest.raises(ValueError, match="does not have a MESSAGE_ID"):
            await device.write_attributes({mock_msg_class: "value"})

    @pytest.mark.asyncio
    async def test_write_attribute_payload_encoding(self, device):
        """Test that payload is properly encoded using to_bytes()."""
        await device.write_attribute(InTargetTemperature, 22.5)

        call_args = device._client.send_message.call_args
        messages = call_args.kwargs["messages"]
        payload = messages[0].PAYLOAD

        # Should be encoded as 225 (22.5 * 10) in big-endian
        assert payload == b"\x00\xe1"

    @pytest.mark.asyncio
    async def test_write_attribute_enum_encoding(self, device):
        """Test that enum values are properly encoded."""
        await device.write_attribute(InOperationModeMessage, InOperationMode.HEAT)

        call_args = device._client.send_message.call_args
        messages = call_args.kwargs["messages"]
        payload = messages[0].PAYLOAD

        # HEAT should encode to its enum value
        assert payload == bytes([InOperationMode.HEAT.value])

    @pytest.mark.asyncio
    async def test_write_attribute_correct_destination(self, device):
        """Test that write goes to correct device address."""
        await device.write_attribute(InOperationPowerMessage, InOperationPower.ON_STATE_1)

        call_args = device._client.send_message.call_args
        assert call_args.kwargs["destination"] == device.address

    @pytest.mark.asyncio
    async def test_write_attribute_correct_request_type(self, device):
        """Test that request type is WRITE."""
        await device.write_attribute(InOperationPowerMessage, InOperationPower.ON_STATE_1)

        call_args = device._client.send_message.call_args
        assert call_args.kwargs["request_type"] == DataType.WRITE


class TestMessageRoundTrip:
    """Integration tests for parse -> to_bytes -> parse round-trips."""

    def test_power_message_round_trip(self):
        """Test parsing power on and rebuilding."""
        # Parse power on
        parsed_on = InOperationPowerMessage.parse_payload(b"\x01")
        assert parsed_on.VALUE == InOperationPower.ON_STATE_1

        # Rebuild to bytes
        rebuilt = InOperationPowerMessage.to_bytes(parsed_on.VALUE)
        assert rebuilt == b"\x01"

        # Parse again
        re_parsed = InOperationPowerMessage.parse_payload(rebuilt)
        assert re_parsed.VALUE == InOperationPower.ON_STATE_1

    def test_temperature_round_trip_precision(self):
        """Test that temperature round-trip maintains precision."""
        original_bytes = b"\x00\xe1"  # 225 = 22.5°C
        parsed = InTargetTemperature.parse_payload(original_bytes)
        rebuilt = InTargetTemperature.to_bytes(parsed.VALUE)

        assert rebuilt == original_bytes
        assert parsed.VALUE == 22.5

    def test_operation_mode_round_trip(self):
        """Test operation mode round-trip for all modes."""
        modes = [
            InOperationMode.COOL,
            InOperationMode.HEAT,
            InOperationMode.DRY,
            InOperationMode.FAN,
        ]

        for mode in modes:
            payload = InOperationModeMessage.to_bytes(mode)
            parsed = InOperationModeMessage.parse_payload(payload)
            rebuilt = InOperationModeMessage.to_bytes(parsed.VALUE)

            assert rebuilt == payload, f"Round-trip failed for {mode}"
            assert parsed.VALUE == mode
