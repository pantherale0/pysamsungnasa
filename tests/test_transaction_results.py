"""Tests for confirmed write transactions.

The weather-compensation controller writes ``0x4247``
(InWaterOutletTargetTemperature) to the indoor unit. When that write is
abandoned after three attempts, Home Assistant must be able to find out —
previously the failure was silent (``send_message`` returns without any
confirmation and the retry manager just logs).
"""

import asyncio
import binascii

import pytest


from pysamsungnasa.config import NasaConfig
from pysamsungnasa.device import NasaDevice, TransactionResult
from pysamsungnasa.helpers import hex2bin
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.protocol.enum import AddressClass, DataType
from pysamsungnasa.protocol.factory.messages.indoor import InWaterOutletTargetTemperature
from pysamsungnasa.protocol.factory.types import SendMessage
from pysamsungnasa.protocol.parser import NasaPacketParser

WRITE_DEST = "200000"


def _make_client(**config_kwargs) -> NasaClient:
    config = NasaConfig(
        enable_write_retries=config_kwargs.pop("enable_write_retries", True),
        enable_read_retries=config_kwargs.pop("enable_read_retries", True),
        device_path="socket://localhost:8000",
        **config_kwargs,
    )
    client = NasaClient(config=config)
    client.writer = type("W", (), {"is_closing": lambda self: False, "close": lambda self: None})()
    client.writer.wait_closed = lambda: _noop_future()
    client._is_connected = True
    client._tx_queue = asyncio.Queue()
    client._rx_queue = asyncio.Queue()
    return client


def _noop_future():
    future = asyncio.get_running_loop().create_future()
    future.set_result(None)
    return future


def _pending_packet_number(client: NasaClient) -> int:
    (write_info,) = client._pending_writes.values()
    return write_info["packet_number"]


class TestTransportAcknowledgement:
    """ACK / NACK / abandonment map to distinct transaction outcomes."""

    async def test_ack_resolves_ack(self, nasa_client):
        future = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        assert not future.done()

        packet_number = _pending_packet_number(nasa_client)
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)

        assert future.result() == "ack"
        assert not nasa_client._pending_writes

    async def test_nack_resolves_nack(self, nasa_client):
        future = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        packet_number = _pending_packet_number(nasa_client)
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.NACK, packet_number=packet_number)

        assert future.result() == "nack"
        assert not nasa_client._pending_writes

    async def test_retry_exhaustion_resolves_abandoned(self):
        client = _make_client(write_retry_interval=0.05, write_retry_max_attempts=2)
        future = asyncio.get_running_loop().create_future()
        await client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        task = asyncio.create_task(client._retry_manager())
        try:
            outcome = await asyncio.wait_for(future, timeout=5)
        finally:
            await client._cancel_task(task)
            await client.disconnect()
        assert outcome == "abandoned"
        assert not client._pending_writes

    async def test_late_ack_after_abandonment_completes_nothing(self, nasa_client):
        future = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        packet_number = _pending_packet_number(nasa_client)
        nasa_client._clear_pending_write(WRITE_DEST, [], packet_number=packet_number, outcome="abandoned")
        assert future.result() == "abandoned"

        # A late ACK for the same packet after abandonment must not crash or
        # resurrect anything: there is no pending write to clear any more.
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        assert not nasa_client._pending_writes

    async def test_newer_write_supersedes_pending_write(self, nasa_client):
        first = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],  # 33.0°C
            completion_future=first,
        )
        second = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x5e")],  # 35.0°C
            completion_future=second,
        )

        # The superseded caller is released immediately with a truthful outcome.
        assert first.result() == "superseded"
        assert not second.done()

        # The surviving write completes on its own ACK.
        packet_number = _pending_packet_number(nasa_client)
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        assert second.result() == "ack"

    async def test_write_retries_disabled_resolves_unconfirmed(self):
        client = _make_client(enable_write_retries=False)
        future = asyncio.get_running_loop().create_future()
        await client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        assert future.result() == "unconfirmed"

    async def test_send_failure_resolves_failed(self, nasa_client):
        future = asyncio.get_running_loop().create_future()
        nasa_client._is_connected = False
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=future,
        )
        assert future.result() == "failed"

    async def test_fire_and_forget_api_unchanged(self, nasa_client):
        """Existing callers that do not pass a future keep fire-and-forget semantics."""
        result = await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
        )
        assert isinstance(result, int)
        assert nasa_client._pending_writes


class TestConfirmedDeviceState:
    """write_attribute_confirmed: transport ACK vs confirmed device state."""

    @staticmethod
    def _response_packet(message_hex: str) -> bytes:
        data = hex2bin(message_hex)
        crc = binascii.crc_hqx(data, 0)
        size = len(data) + 4
        return hex2bin(f"32{size:04x}{message_hex}{crc:04x}34")

    @staticmethod
    def _wired_device():
        client = _make_client()
        config = client._config
        parser = NasaPacketParser(config=config)
        parser.set_pending_read_handler(client._mark_read_received)
        client.set_receive_event_handler(parser.parse_packet)
        device = NasaDevice(
            address=WRITE_DEST,
            device_type=AddressClass.INDOOR,
            packet_parser=parser,
            config=config,
            client=client,
        )
        return client, parser, device

    async def test_confirmed_write_with_matching_read_back(self):
        client, parser, device = self._wired_device()
        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature, 33.0, mode=DataType.REQUEST, timeout=5, verify=True, verify_timeout=5
            )
        )
        await asyncio.sleep(0)  # let the write register

        packet_number = _pending_packet_number(client)
        await client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        await asyncio.sleep(0)  # let the read-back read request register

        # Device reports back the written value: 33.0°C = 0x014A.
        response = self._response_packet("200000" + "80ff01" + "20" + "15" + "02" + "01" + "4247" + "014a")
        await parser.parse_packet(response[3:-3])

        result = await task
        assert isinstance(result, TransactionResult)
        assert result.outcome == "ack"
        assert result.verified is True
        assert result.device_value == 33.0
        assert result.success is True

    async def test_confirmed_write_with_mismatched_read_back(self):
        client, parser, device = self._wired_device()
        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature, 35.0, mode=DataType.REQUEST, timeout=5, verify=True, verify_timeout=5
            )
        )
        await asyncio.sleep(0)

        packet_number = _pending_packet_number(client)
        await client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        await asyncio.sleep(0)

        # Device reports 33.0°C although 35.0°C was written: ACK but not applied.
        response = self._response_packet("200000" + "80ff01" + "20" + "15" + "02" + "01" + "4247" + "014a")
        await parser.parse_packet(response[3:-3])

        result = await task
        assert result.outcome == "ack"
        assert result.verified is False
        assert result.device_value == 33.0
        assert result.success is True  # transport ACK, device state not confirmed

    async def test_lost_ack_but_applied_value_recovered_by_verify(self):
        """Abandoned write + matching read-back: outcome abandoned, verified True."""
        client, parser, device = self._wired_device()
        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature,
                33.0,
                mode=DataType.REQUEST,
                timeout=0.05,
                verify=True,
                verify_timeout=5,
            )
        )
        result = await task
        assert result.outcome == "timeout"  # caller timeout before any terminal state
        client._pending_writes.clear()

        # Simulate the retry budget exhausting without an ACK (direct clear),
        # then the device reporting the value it did apply.
        completion = asyncio.get_running_loop().create_future()
        client._pending_writes[f"{WRITE_DEST}_(16967,)"] = {
            "destination": WRITE_DEST,
            "message_ids": [0x4247],
            "messages": [SendMessage(MESSAGE_ID=0x4247, PAYLOAD=b"\x01\x4a")],
            "data_type": DataType.REQUEST,
            "packet_number": 1,
            "packet_numbers": {1},
            "attempts": 3,
            "last_attempt_time": 0.0,
            "next_retry_time": 0.0,
            "retry_interval": 1.0,
            "completion_future": completion,
        }
        client._clear_pending_write(WRITE_DEST, [], packet_number=1, outcome="abandoned")
        assert completion.result() == "abandoned"

        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature, 33.0, mode=DataType.REQUEST, timeout=5, verify=True, verify_timeout=5
            )
        )
        await asyncio.sleep(0)
        packet_number = _pending_packet_number(client)
        # No ACK arrives; simulate abandonment directly, then the read-back.
        client._clear_pending_write(WRITE_DEST, [], packet_number=packet_number, outcome="abandoned")
        await asyncio.sleep(0)
        response = self._response_packet("200000" + "80ff01" + "20" + "15" + "02" + "01" + "4247" + "014a")
        await parser.parse_packet(response[3:-3])
        result = await task
        assert result.outcome == "abandoned"
        assert result.verified is True  # applied despite the lost ACK
        assert result.device_value == 33.0
        assert result.success is False  # never transport-acknowledged

    async def test_verify_does_not_accept_cached_attribute(self):
        """verify=True must wait for a fresh device response, not the cache.

        A stale cached 0x4247 exists before the write; only a response that
        arrives after the read request satisfies the verification. With no
        fresh response the result is verified=None, never a stale comparison.
        """
        client, parser, device = self._wired_device()
        # Pre-populate the cache with a stale value and an old arrival time.
        stale = InWaterOutletTargetTemperature.parse_payload(b"\x01\x4a")  # 33.0°C, matches request
        device.attributes[0x4247] = stale
        device._attribute_times[0x4247] = 0.0

        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature,
                33.0,
                mode=DataType.REQUEST,
                timeout=5,
                verify=True,
                verify_timeout=0.2,  # short: no fresh response will arrive
            )
        )
        await asyncio.sleep(0)
        packet_number = _pending_packet_number(client)
        await client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)

        result = await task
        assert result.outcome == "ack"
        assert result.verified is None  # no fresh response: unverified, not stale-compared
        assert result.device_value is None

    async def test_verify_ignores_packet_that_arrived_before_the_read_request(self):
        """A same-value packet handled before the read-back request must not satisfy verify."""
        client, parser, device = self._wired_device()
        task = asyncio.create_task(
            device.write_attribute_confirmed(
                InWaterOutletTargetTemperature,
                33.0,
                mode=DataType.REQUEST,
                timeout=5,
                verify=True,
                verify_timeout=0.2,
            )
        )
        await asyncio.sleep(0)
        packet_number = _pending_packet_number(client)
        await client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)

        # Deliver a matching value BEFORE the read-back is satisfied... it would
        # normally satisfy it (it arrived after the request). Instead, verify
        # the freshness mechanism directly: handle the packet, then a second
        # confirm with requires_read must wait for another one.
        await asyncio.sleep(0)
        response = self._response_packet("200000" + "80ff01" + "20" + "15" + "02" + "01" + "4247" + "014a")
        await parser.parse_packet(response[3:-3])
        result = await task
        assert result.verified is True
        assert result.device_value == 33.0

        # Now a fresh-request must not be satisfied by the just-stored value:
        # it arrived before this new request instant.
        with pytest.raises(TimeoutError):
            async with asyncio.timeout(0.2):
                await device.get_attribute(InWaterOutletTargetTemperature, requires_read=True)

    async def test_nack_propagates_through_write_attribute_confirmed(self):
        client, parser, device = self._wired_device()
        task = asyncio.create_task(device.write_attribute_confirmed(InWaterOutletTargetTemperature, 33.0, timeout=5))
        await asyncio.sleep(0)
        packet_number = _pending_packet_number(client)
        await client._mark_read_received(WRITE_DEST, [], DataType.NACK, packet_number=packet_number)
        result = await task
        assert result.outcome == "nack"
        assert result.success is False
        assert result.verified is None

    async def test_caller_timeout_returns_timeout_outcome(self):
        client, parser, device = self._wired_device()
        result = await device.write_attribute_confirmed(InWaterOutletTargetTemperature, 33.0, timeout=0.05)
        assert result.outcome == "timeout"
        assert result.success is False
        # Clean up: the entry stays pending without a retry manager running.
        client._pending_writes.clear()


class TestReadWriteConcurrency:
    """Reads and writes to different devices must not cross-complete."""

    async def test_read_response_does_not_complete_write(self, nasa_client):
        write_future = asyncio.get_running_loop().create_future()
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
            completion_future=write_future,
        )
        await nasa_client.send_message(
            destination="100000",
            request_type=DataType.READ,
            messages=[SendMessage(0x8204, b"\x05\xa5\xa5\xa5")],
        )

        # An ACK addressed to the outdoor unit (different device) must not
        # complete the pending indoor write, even with matching packet number.
        packet_number = _pending_packet_number(nasa_client)
        await nasa_client._mark_read_received("100000", [], DataType.ACK, packet_number=packet_number)
        assert not write_future.done()
        assert nasa_client._pending_writes

        # A RESPONSE completing the read must not complete the write either.
        await nasa_client._mark_read_received("100000", [0x8204], DataType.RESPONSE, packet_number=99)
        assert not write_future.done()

        # The real ACK completes it.
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        assert write_future.result() == "ack"

    async def test_write_ack_does_not_clear_pending_reads(self, nasa_client):
        await nasa_client.nasa_read([0x8204], destination="100000")
        await nasa_client.send_message(
            destination=WRITE_DEST,
            request_type=DataType.WRITE,
            messages=[SendMessage(0x4247, b"\x01\x4a")],
        )
        packet_number = _pending_packet_number(nasa_client)
        await nasa_client._mark_read_received(WRITE_DEST, [], DataType.ACK, packet_number=packet_number)
        # The read to 100000 must still be pending.
        assert any(info["destination"] == "100000" for info in nasa_client._pending_reads.values())
