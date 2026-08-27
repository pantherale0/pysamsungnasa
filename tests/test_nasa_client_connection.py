"""Tests for NasaClient connection teardown."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from pysamsungnasa.protocol.factory.types import SendMessage
from pysamsungnasa.protocol.enum import DataType


class TestDisconnectClosesTransport:
    """disconnect() must close the SerialX writer so the port can be reused."""

    @pytest.mark.asyncio
    async def test_disconnect_closes_writer_and_marks_disconnected(self, nasa_client):
        """stop()/disconnect() previously dropped the writer reference without closing it."""
        client = nasa_client
        writer = client.writer

        await client.disconnect()

        writer.close.assert_called_once()
        writer.wait_closed.assert_awaited()
        assert client.writer is None
        assert client.reader is None
        assert client.is_connected is False
        assert client._is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect_is_idempotent(self, nasa_client):
        """A second disconnect after teardown must be a no-op."""
        client = nasa_client
        writer = client.writer

        await client.disconnect()
        await client.disconnect()

        writer.close.assert_called_once()
        assert client.is_connected is False


class TestHandleDisconnection:
    """Write/serial errors must actually drop the connection and await handlers."""

    @pytest.mark.asyncio
    async def test_async_disconnect_handler_is_awaited(self, nasa_client):
        """Regression: is_coroutine_function() was called on the coroutine result.

        That left async reconnect handlers un-awaited after a writer error, so
        Home Assistant-style integrations never recovered.
        """
        client = nasa_client
        resumed = asyncio.Event()

        async def handler():
            await asyncio.sleep(0)
            resumed.set()

        client._disconnect_event_handler = handler
        writer = client.writer
        await client._handle_disconnection(OSError("serial reset"))

        assert resumed.is_set()
        assert client.is_connected is False
        writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_disconnect_handler_is_called(self, nasa_client):
        """Synchronous disconnect handlers must still run."""
        client = nasa_client
        handler = Mock()
        client._disconnect_event_handler = handler

        await client._handle_disconnection(OSError("serial reset"))

        handler.assert_called_once_with()
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_write_error_allows_reconnect(self, nasa_client):
        """After a transport error the client must not report itself as still connected.

        connect() refuses to open a new session while is_connected is True, so a
        leaked 'connected' flag after writer failure permanently wedges the client.
        """
        client = nasa_client
        await client._handle_disconnection(ConnectionResetError("peer closed"))

        assert client.is_connected is False
        assert client.writer is None
        # The early-return 'already connected' path in connect() is skipped.
        assert not (client._is_connected and client.writer is not None)

    @pytest.mark.asyncio
    async def test_write_error_stops_send_command(self, nasa_client):
        """After teardown, queued writes must not look connected-but-unwritable."""
        client = nasa_client
        await client._handle_disconnection(BrokenPipeError())

        result = await client.send_command(["80ff0120000180c1{CUR_PACK_NUM}00"])
        assert result is None

    @pytest.mark.asyncio
    async def test_write_error_tears_down_when_transport_already_closing(self, nasa_client):
        """ConnectionResetError typically leaves writer.is_closing() True.

        is_connected is then False, so gating teardown on that property skipped
        disconnect() and Home Assistant reconnect handlers never ran.
        """
        client = nasa_client
        client.writer.is_closing = Mock(return_value=True)
        writer = client.writer
        handler = Mock()
        client._disconnect_event_handler = handler

        assert client.is_connected is False
        assert client._is_connected is True

        await client._handle_disconnection(ConnectionResetError("peer closed"))

        handler.assert_called_once_with()
        writer.close.assert_called_once()
        writer.wait_closed.assert_awaited()
        assert client.writer is None
        assert client._is_connected is False
        assert client.is_connected is False


class TestDisconnectListenerNoDeadlock:
    """Cancelling the listener must not re-enter disconnect() while the lock is held."""

    @pytest.mark.asyncio
    async def test_disconnect_cancels_listener_without_deadlock(self, nasa_client):
        """Listener CancelledError used to call disconnect() while disconnect held the lock."""
        client = nasa_client
        reading = asyncio.Event()

        async def hanging_readuntil(*_args, **_kwargs):
            reading.set()
            await asyncio.sleep(3600)
            return b""

        client.reader.readuntil = hanging_readuntil
        client.listener_task = asyncio.create_task(client._listener_task())
        await reading.wait()

        handler_ran = asyncio.Event()

        async def handler():
            await asyncio.sleep(0.05)
            handler_ran.set()

        client._disconnect_event_handler = handler

        await asyncio.wait_for(client.disconnect(), timeout=1.0)

        assert handler_ran.is_set()
        assert client.is_connected is False
        assert client.listener_task is None or client.listener_task.done()

    @pytest.mark.asyncio
    async def test_listener_exits_when_transport_closing_still_tears_down(self, nasa_client):
        """If the transport starts closing, is_connected becomes False and the
        listener loop ends without an exception. Teardown and the disconnect
        handler must still run so callers can reconnect.
        """
        client = nasa_client
        client.writer.is_closing = Mock(return_value=True)
        writer = client.writer
        handler = Mock()
        client._disconnect_event_handler = handler

        await asyncio.wait_for(client._listener_task(), timeout=1.0)

        handler.assert_called_once_with()
        writer.close.assert_called_once()
        assert client._is_connected is False
        assert client.writer is None

    @pytest.mark.asyncio
    async def test_disconnect_handler_can_observe_disconnected_state(self, nasa_client):
        """Handler runs after the lock is released, with is_connected already False."""
        client = nasa_client
        seen_connected = []

        async def handler():
            seen_connected.append(client.is_connected)

        client._disconnect_event_handler = handler
        await client.disconnect()

        assert seen_connected == [False]


class TestWriterErrorSelfTeardown:
    """The writer task must be able to disconnect without awaiting itself."""

    @pytest.mark.asyncio
    async def test_writer_oserror_disconnects_without_hanging(self, nasa_client):
        """Writer OSError calls _handle_disconnection, which must not deadlock on the writer task."""
        client = nasa_client
        client._writer_task = asyncio.current_task()
        client.writer.write = Mock(side_effect=ConnectionResetError("reset"))
        client.writer.drain = AsyncMock()

        await asyncio.wait_for(client._handle_disconnection(ConnectionResetError("reset")), timeout=1.0)

        assert client.is_connected is False
        assert client.writer is None
        # Current task was not cancelled by teardown.
        assert not asyncio.current_task().cancelled()

    @pytest.mark.asyncio
    async def test_writer_sees_closing_transport_and_tears_down(self, nasa_client):
        """A write attempted after the peer started closing must still disconnect."""
        client = nasa_client
        writer = client.writer
        handler = Mock()
        client._disconnect_event_handler = handler
        client._last_rx_time = None
        await client._tx_queue.put(b"\x32\x00")

        original_idle = client._wait_for_bus_idle

        async def idle_then_close():
            client.writer.is_closing = Mock(return_value=True)
            await original_idle()

        client._wait_for_bus_idle = idle_then_close

        await asyncio.wait_for(client._writer(), timeout=1.0)

        handler.assert_called_once_with()
        writer.close.assert_called_once()
        assert client._is_connected is False
        assert client.writer is None

    @pytest.mark.asyncio
    async def test_writer_loop_exits_when_transport_closing_still_tears_down(self, nasa_client):
        """Idle writer must still disconnect if is_connected flips False via is_closing()."""
        client = nasa_client
        writer = client.writer
        handler = Mock()
        client._disconnect_event_handler = handler
        client.writer.is_closing = Mock(return_value=True)

        await asyncio.wait_for(client._writer(), timeout=1.0)

        handler.assert_called_once_with()
        writer.close.assert_called_once()
        assert client._is_connected is False
        assert client.writer is None


class TestRxWatchdogIgnoresTransmit:
    """The 120s liveness check must track actual RX, not TX.

    Home Assistant polls continuously. If TX refreshed the same timestamp the
    listener uses for 'no data received', a silent bus (heat pump powered off,
    RS485 unplugged but USB-serial still open) would never trip the watchdog,
    leaving HA with stale climate state indefinitely.
    """

    @pytest.mark.asyncio
    async def test_writer_does_not_refresh_rx_watchdog(self, nasa_client):
        """A successful TX must update bus-idle time only, not last RX time."""
        client = nasa_client
        loop = asyncio.get_running_loop()
        stale_rx = loop.time() - 50.0
        client._last_rx_time = stale_rx
        client._last_bus_time = stale_rx
        client._bus_idle_gap = 0.0
        client.writer.write = Mock()
        client.writer.drain = AsyncMock()

        await client._tx_queue.put(b"\x32\x00\x04test\x00\x00\x34")
        writer_task = asyncio.create_task(client._writer())
        try:
            await asyncio.wait_for(client._tx_queue.join(), timeout=1.0)
        finally:
            writer_task.cancel()
            try:
                await writer_task
            except asyncio.CancelledError:
                pass

        assert client._last_rx_time == stale_rx
        assert client._last_bus_time is not None
        assert client._last_bus_time > stale_rx
        client.writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_silent_bus_disconnects_despite_recent_transmit(self, nasa_client):
        """RX idle >120s must drop the connection even if we transmitted recently."""
        client = nasa_client
        loop = asyncio.get_running_loop()
        client._last_rx_time = loop.time() - 121.0
        client._last_bus_time = loop.time()

        async def hang(*_args, **_kwargs):
            await asyncio.sleep(3600)
            return b""

        client.reader.readuntil = hang
        disconnected = asyncio.Event()

        async def handler():
            disconnected.set()

        client._disconnect_event_handler = handler
        client.listener_task = asyncio.create_task(client._listener_task())

        await asyncio.wait_for(disconnected.wait(), timeout=1.0)
        assert client.is_connected is False
        assert client.writer is None

    @pytest.mark.asyncio
    async def test_recent_rx_does_not_trip_watchdog(self, nasa_client):
        """A client that is still receiving must stay connected."""
        client = nasa_client
        loop = asyncio.get_running_loop()
        client._last_rx_time = loop.time()
        client._last_bus_time = loop.time()

        async def hang(*_args, **_kwargs):
            await asyncio.sleep(3600)
            return b""

        client.reader.readuntil = hang
        handler = Mock()
        client._disconnect_event_handler = handler
        client.listener_task = asyncio.create_task(client._listener_task())
        try:
            await asyncio.sleep(0.15)
            assert client.is_connected is True
            handler.assert_not_called()
        finally:
            await client.disconnect()


class TestSendAfterDisconnect:
    """send_message must fail closed once the transport is gone."""

    @pytest.mark.asyncio
    async def test_send_message_rejected_when_disconnected(self, nasa_client):
        client = nasa_client
        await client.disconnect()
        result = await client.send_message(
            destination="200001",
            request_type=DataType.WRITE,
            messages=[SendMessage(MESSAGE_ID=0x4000, PAYLOAD=b"\x01")],
        )
        assert result is None
