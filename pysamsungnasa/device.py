"""Represent a NASA device and expose attributes."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Any

from .config import NasaConfig
from .protocol.enum import AddressClass, DataType
from .protocol.factory.types import BaseMessage, SendMessage
from .protocol.parser import NasaPacketParser

if TYPE_CHECKING:
    from .nasa_client import NasaClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class TransactionResult:
    """Outcome of a confirmed NASA write transaction.

    ``outcome`` is one of:
      - ``"ack"``: the destination device acknowledged the write (transport ACK).
      - ``"nack"``: the destination device rejected the write (transport NACK).
      - ``"abandoned"``: no acknowledgement arrived within the retry budget.
      - ``"timeout"``: the caller's timeout expired before any terminal state.
      - ``"superseded"``: a newer write to the same message IDs took over.
      - ``"unconfirmed"``: the packet was sent but write-retry tracking is not
        available (e.g. write retries disabled), so no ACK correlation occurs.
      - ``"failed"``: the packet could not be encoded or queued.

    ``verified`` and ``device_value`` are only populated when the write was
    confirmed with ``verify=True``: ``verified`` is True when the device
    subsequently reported the written value back, False when it reported a
    different value, and None when the read-back could not be completed (e.g.
    the device does not support reading the message). A transport ACK is *not*
    proof the device applied the value — ``verified`` provides that stronger
    guarantee when available.
    """

    outcome: str
    verified: bool | None = None
    device_value: Any = None

    @property
    def success(self) -> bool:
        """Return True when the write was transport-acknowledged."""
        return self.outcome == "ack"


class NasaDevice:
    """NASA Device."""

    def __init__(
        self,
        address: str,
        device_type: AddressClass,
        packet_parser: NasaPacketParser,
        config: NasaConfig,
        client: NasaClient,
    ) -> None:
        self.address = address
        self.device_type = device_type
        self.attributes: dict[int, BaseMessage] = {}
        self.config = config
        self.last_packet_time = None
        self.fsv_config = {}
        self._device_callbacks: list[Callable] = []
        self._packet_callbacks: dict[int, list[Callable]] = {}
        self._client = client
        self._attribute_events: dict[int, asyncio.Event] = {}
        # Monotonic arrival time of the latest packet per message ID, used by
        # get_attribute(requires_read=True) to wait for a response that arrived
        # after the read request rather than trusting the cached attribute.
        self._attribute_times: dict[int, float] = {}
        packet_parser.add_device_handler(address, self.handle_packet)

    def add_device_callback(self, callback: Callable):
        """Add a device callback."""
        if callback not in self._device_callbacks:
            self._device_callbacks.append(callback)

    def add_packet_callback(self, message: type[BaseMessage], callback: Callable):
        """Add a packet callback for a specific message type.

        Args:
            message: Message class (subclass of BaseMessage) to listen for.
            callback: Callback function to invoke when the message is received.
        """
        assert issubclass(message, BaseMessage)
        assert message.MESSAGE_ID is not None
        if message.MESSAGE_ID not in self._packet_callbacks:
            self._packet_callbacks[message.MESSAGE_ID] = []
        if callback not in self._packet_callbacks[message.MESSAGE_ID]:
            self._packet_callbacks[message.MESSAGE_ID].append(callback)

    def remove_packet_callback(self, message: type[BaseMessage], callback: Callable):
        """Remove a packet callback for a specific message type.

        Args:
            message: Message class (subclass of BaseMessage) to stop listening for.
            callback: Callback function to remove.
        """
        assert issubclass(message, BaseMessage)
        assert message.MESSAGE_ID is not None
        if message.MESSAGE_ID in self._packet_callbacks and callback in self._packet_callbacks[message.MESSAGE_ID]:
            self._packet_callbacks[message.MESSAGE_ID].remove(callback)

    def remove_device_callback(self, callback: Callable):
        """Remove a device callback."""
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    async def get_attribute(self, attribute: type[BaseMessage], requires_read: bool = False) -> BaseMessage:
        """Get a specific attribute from the device, if it is not already known a request will be sent to the device.

        With ``requires_read=True`` the returned message is guaranteed to have
        arrived from the device *after* the read request was issued: a packet
        received for the same message ID before the request (or the previously
        cached attribute) never satisfies the wait. If the device does not
        respond within the timeout, TimeoutError is raised rather than
        returning a stale cached value.
        """
        assert issubclass(attribute, BaseMessage)
        assert attribute.MESSAGE_ID is not None
        # Capture the freshness baseline before issuing the read request: only
        # packets handled after this instant count as a response to it.
        requested_at = time.monotonic()
        if attribute.MESSAGE_ID not in self.attributes or requires_read:
            await self._client.nasa_read(
                msgs=[attribute.MESSAGE_ID],
                destination=self.address,
            )

        event = self._attribute_events.setdefault(attribute.MESSAGE_ID, asyncio.Event())

        async with asyncio.timeout(10):
            while attribute.MESSAGE_ID not in self.attributes or (
                requires_read and self._attribute_times.get(attribute.MESSAGE_ID, 0.0) <= requested_at
            ):
                event.clear()
                await event.wait()  # Waits until handle_packet sets it

        if attribute.MESSAGE_ID not in self.attributes:
            raise TimeoutError(f"Timeout waiting for attribute {attribute.MESSAGE_ID} from device {self.address}")

        return self.attributes[attribute.MESSAGE_ID]

    async def write_attributes(
        self,
        attributes: dict[type[BaseMessage], Any],
        mode: DataType = DataType.WRITE,
        source: str | None = None,
        destination: str | None = None,
        completion_future: asyncio.Future | None = None,
    ):
        """Write specific attributes to the device.

        NASA protocol can handle up to 10 messages per packet.

        Args:
            attributes: Dictionary mapping message class to value
            mode: DataType to use for writing, default is DataType.WRITE however sometimes DataType.REQUEST
                or DataType.NOTIFICATION may be needed
            source: Optional source address override (defaults to configured client address)
            destination: Optional destination address override (defaults to this device's address)
            completion_future: Optional future resolved when the write reaches a
                terminal state (``"ack"``, ``"nack"``, ``"abandoned"``,
                ``"superseded"``, ``"unconfirmed"`` or ``"failed"``). See
                `write_attribute_confirmed`.

        Raises:
            ValueError: If more than 10 messages or message class lacks MESSAGE_ID
        """
        if len(attributes) > 10:
            raise ValueError(f"Cannot write more than 10 messages in one packet, got {len(attributes)}")

        messages = []
        for message_class, value in attributes.items():
            if message_class.MESSAGE_ID is None:
                raise ValueError(f"Message class {message_class} does not have a MESSAGE_ID.")

            messages.append(SendMessage(MESSAGE_ID=message_class.MESSAGE_ID, PAYLOAD=message_class.to_bytes(value)))
        await self._client.send_message(
            destination=destination if destination is not None else self.address,
            request_type=mode,
            messages=messages,
            source=source,
            completion_future=completion_future,
        )

    async def write_attribute(
        self,
        message_class: type[BaseMessage],
        value: Any,
        mode: DataType = DataType.WRITE,
        source: str | None = None,
        destination: str | None = None,
        completion_future: asyncio.Future | None = None,
    ):
        """Write a single attribute to the device, this is a convenience method of write_attributes."""
        await self.write_attributes(
            {message_class: value},
            mode=mode,
            source=source,
            destination=destination,
            completion_future=completion_future,
        )

    async def write_attribute_confirmed(
        self,
        message_class: type[BaseMessage],
        value: Any,
        mode: DataType = DataType.WRITE,
        timeout: float = 10.0,
        verify: bool = False,
        verify_timeout: float = 10.0,
        verify_tolerance: float = 0.05,
        source: str | None = None,
        destination: str | None = None,
    ) -> TransactionResult:
        """Write an attribute and report the transaction outcome.

        The existing ``write_attribute`` keeps fire-and-forget semantics for
        backward compatibility; this method returns a `TransactionResult`
        describing what happened to the write instead of silently dropping
        failed transactions.

        Note that a transport ACK means the device received and accepted the
        packet — it does not guarantee the value was applied. Pass
        ``verify=True`` to additionally read the message back from the device
        and compare it against the requested value. The read-back also runs
        after an ``"abandoned"`` outcome, recovering the true device state
        when the ACK was lost on the bus but the write was applied.

        Args:
            message_class: Message class to write.
            value: Value to write.
            mode: DataType for the write (default ``DataType.WRITE``; setpoint
                writes commonly use ``DataType.REQUEST``).
            timeout: Seconds to wait for ACK/NACK/abandonment.
            verify: Read the value back from the device after an ACK.
            verify_timeout: Seconds to wait for the read-back.
            verify_tolerance: Absolute tolerance when comparing numeric values.
            source: Optional source address override.
            destination: Optional destination address override.
        """
        loop = asyncio.get_running_loop()
        completion: asyncio.Future = loop.create_future()
        await self.write_attribute(
            message_class,
            value,
            mode=mode,
            source=source,
            destination=destination,
            completion_future=completion,
        )
        try:
            outcome = await asyncio.wait_for(completion, timeout=timeout)
        except TimeoutError:
            return TransactionResult(outcome="timeout")

        result = TransactionResult(outcome=outcome)

        # Verify after an ACK, and also after an abandoned write: a lost ACK
        # does not prove the device failed to apply the value, and a read-back
        # recovers the true state. A NACK means the device rejected the write,
        # so there is nothing to verify.
        if verify and outcome in ("ack", "abandoned"):
            expected_value = message_class.parse_payload(message_class.to_bytes(value)).VALUE
            try:
                read_back = await asyncio.wait_for(
                    self.get_attribute(message_class, requires_read=True),
                    timeout=verify_timeout,
                )
            except TimeoutError, asyncio.TimeoutError:
                result.verified = None
                return result
            result.device_value = read_back.VALUE
            # bool is a subclass of int but compares by equality, not tolerance.
            expected_numeric = isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool)
            read_numeric = isinstance(read_back.VALUE, (int, float)) and not isinstance(read_back.VALUE, bool)
            if expected_numeric and read_numeric:
                result.verified = abs(float(read_back.VALUE) - float(expected_value)) <= verify_tolerance
            else:
                result.verified = read_back.VALUE == expected_value

        return result

    def handle_packet(self, *_nargs, **kwargs):
        """Handle a packet sent to this device from the parser."""
        self.last_packet_time = datetime.now(UTC)
        message_number = kwargs["messageNumber"]
        packet_data: BaseMessage = kwargs["packet"]
        log_message = (
            str(self.config.address) == kwargs["dest"]
            or self.config.log_all_messages
            or kwargs["dest"] in self.config.devices_to_log
            or message_number in self.config.messages_to_log
        )

        if log_message:
            _LOGGER.debug("Handling packet for device %s: %s", self.address, kwargs)
        self.attributes[message_number] = packet_data
        self._attribute_times[message_number] = time.monotonic()
        if message_number in self._attribute_events:
            self._attribute_events[message_number].set()
        if log_message:
            _LOGGER.debug(
                "Device %s: Stored parsed attribute for msg %s (%s): %s",
                self.address,
                kwargs["formattedMessageNumber"],
                message_number,
                self.attributes[message_number],
            )

        # Test if the packet is an FSV configuration packet
        if packet_data.is_fsv_message:
            self.fsv_config[message_number] = packet_data.VALUE

        for callback in self._device_callbacks:
            try:
                callback(self)
            except Exception:
                _LOGGER.exception("Error in device %s callback", self.address)
        if message_number in self._packet_callbacks:
            for callback in self._packet_callbacks[message_number]:
                try:
                    callback(self, **kwargs)
                except Exception:
                    _LOGGER.exception("Error in device %s packet callback", self.address)
