"""Regression tests for temperature decoding around 0°C.

Field evidence (see investigation notes): the Home Assistant entity
``sensor.samsung_heatpump_heat_pump_outdoor_temperature`` repeatedly became
``unknown`` on 13 November 2026 while valid readings of 0.0°C sat immediately
before and after each episode. NASA temperatures are signed int16 values in
tenths of a degree, so a reading of -0.1°C is encoded as 0xFFFF — which the
message parser previously misidentified as the "unavailable" sentinel and
decoded to ``None``. The entity then reported ``unknown`` and the weather
compensation template fell back to -5°C.
"""

import binascii
import struct

import pytest

from pysamsungnasa.helpers import hex2bin
from pysamsungnasa.protocol.factory.messages import indoor, outdoor
from pysamsungnasa.protocol.factory.types import BasicTemperatureMessage


class TestTemperatureAroundFreezing:
    """Temperatures above, at and below 0°C must decode as real values."""

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            (b"\x00\x01", 0.1),
            (b"\x00\x00", 0.0),
            (b"\xff\xff", -0.1),
            (b"\xff\xfe", -0.2),
        ],
    )
    def test_outdoor_air_temperature_decodes_signed(self, payload, expected):
        """Message 0x8204 (VAR_OUT_SENSOR_AIROUT) feeds the HA outdoor sensor."""
        msg = outdoor.OutdoorAirTemperature.parse_payload(payload)
        assert msg.VALUE == expected
        assert msg.RAW_PAYLOAD == payload

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            (b"\x00\x01", 0.1),
            (b"\x00\x00", 0.0),
            (b"\xff\xff", -0.1),
            (b"\xff\xfe", -0.2),
        ],
    )
    def test_other_temperature_messages_decode_signed(self, payload, expected):
        """The fix must apply to every BasicTemperatureMessage subclass."""
        for message_class in (
            indoor.InWaterOutletTargetTemperature,
            indoor.InRoomTemperature,
            indoor.IndoorFlowTemperature,
            indoor.InIndoorOuterTempMessage,
            outdoor.CondenserInTemperature,
        ):
            assert message_class.parse_payload(payload).VALUE == expected

    @pytest.mark.parametrize(
        ("value", "expected_payload"),
        [
            (0.1, b"\x00\x01"),
            (0.0, b"\x00\x00"),
            (-0.1, b"\xff\xff"),
            (-0.2, b"\xff\xfe"),
        ],
    )
    def test_temperature_round_trips(self, value, expected_payload):
        """Writes encode the same two's-complement values that reads decode."""
        assert BasicTemperatureMessage.to_bytes(value) == expected_payload
        assert BasicTemperatureMessage.parse_payload(expected_payload).VALUE == value


class TestOutdoorTemperaturePacketPath:
    """End-to-end check: packet bytes → parser → decoded sensor value."""

    @staticmethod
    def build_read_response(message_hex: str) -> bytes:
        """Assemble a NASA packet the same way NasaClient.send_command does."""
        data = hex2bin(message_hex)
        crc = binascii.crc_hqx(data, 0)
        size = len(data) + 4
        return hex2bin(f"32{size:04x}{message_hex}{crc:04x}34")

    @staticmethod
    def _response_packet(raw_temp_payload: str) -> bytes:
        """Outdoor unit 100000 → client 80FF01: RESPONSE with message 0x8204."""
        message_hex = (
            "100000"  # source: outdoor unit
            "80ff01"  # destination: default client address
            "20"  # protocol version 1
            "15"  # packet type NORMAL (1), data type RESPONSE (5)
            "01"  # packet number
            "01"  # capacity: 1 message
            "8204" + raw_temp_payload  # VAR_OUT_SENSOR_AIROUT
        )
        return TestOutdoorTemperaturePacketPath.build_read_response(message_hex)

    @pytest.mark.parametrize(
        ("raw_temp_payload", "expected"),
        [
            ("0001", 0.1),
            ("0000", 0.0),
            ("ffff", -0.1),
            ("fffe", -0.2),
        ],
    )
    async def test_packet_containing_temperature(self, raw_temp_payload, expected):
        from pysamsungnasa.config import NasaConfig
        from pysamsungnasa.protocol.enum import AddressClass
        from pysamsungnasa.protocol.parser import NasaPacketParser
        from pysamsungnasa.device import NasaDevice

        config = NasaConfig()
        parser = NasaPacketParser(config=config)
        device = NasaDevice(
            address="100000",
            device_type=AddressClass.OUTDOOR,
            packet_parser=parser,
            config=config,
            client=None,
        )
        assert device.address == "100000"
        packet = self._response_packet(raw_temp_payload)
        assert struct.unpack_from(">H", packet, -3)[0] == binascii.crc_hqx(packet[3:-3], 0)
        await parser.parse_packet(packet[3:-3])
        parsed = device.attributes[outdoor.OutdoorAirTemperature.MESSAGE_ID]
        assert parsed.VALUE == expected
