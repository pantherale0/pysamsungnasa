"""Protocol factory."""

import logging

from .messages import load_message_classes
from .messaging import BaseMessage, RawMessage, SendMessage
from ...helpers import bin2hex
from ..enum import DataType, PacketType


MESSAGE_PARSERS: dict[int, BaseMessage] = load_message_classes()
_LOGGER = logging.getLogger(__name__)


def build_message(source: str, destination: str, data_type: DataType, messages: list[SendMessage]) -> str:
    """Build a message to send to a device."""
    if not messages:
        raise ValueError("At least one message is required to build.")
    msg_parts = []
    msg_parts.append(source)
    msg_parts.append(destination)
    # Per NOTES.md: bit 7=1, proto ver (bits 6,5), retry (bits 4,3)
    command_byte1_val = (
        0x80  # packetInformation (assuming it's true for normal packets)
        | (2 << 5)  # protocolVersion = 2
        | (0 << 3)  # retryCount = 0
    )
    msg_parts.append(f"{command_byte1_val:02x}")  # Packet Info/ProtoVer/Retry (1 byte)

    # Per NOTES.md: byte 10 is a single byte for Packet Type and Data Type
    byte10_val = (PacketType.NORMAL.value << 4) | data_type.value
    msg_parts.append(f"{byte10_val:02x}")

    msg_parts.append("{CUR_PACK_NUM}")  # Packet Number (1 byte, to be filled later)
    msg_parts.append(f"{len(messages):02x}")  # Capacity (Number of Messages)
    for msg in messages:
        msg_parts.append(f"{msg.MESSAGE_ID:04x}")  # Message Number
        payload = msg.PAYLOAD
        if data_type == DataType.READ:
            ## Generate dummy payload
            # The payload size for a READ request is encoded in the message number.
            # Bits 9 and 10 of the message number determine the size.
            kind = ((msg.MESSAGE_ID >> 8) & 0x06) >> 1
            size = 0
            if kind == 0:  # e.g. bool, enum
                size = 1
            elif kind == 1:  # e.g. temperature
                size = 2
            elif kind == 2:  # e.g. long var
                size = 4
            payload = b"\x00" * size
            msg_parts.append(bin2hex(payload))  # Message Payload in hex
        else:
            msg_parts.append(bin2hex(msg.PAYLOAD))  # Message Payload in hex
    return "".join(msg_parts).upper()


def get_nasa_message_name(message_number: int) -> str | None:
    """Get the name of a NASA message by its number."""
    if message_number in MESSAGE_PARSERS:
        if (
            hasattr(MESSAGE_PARSERS[message_number], "MESSAGE_NAME")
            and MESSAGE_PARSERS[message_number].MESSAGE_NAME is not None
        ):
            return MESSAGE_PARSERS[message_number].MESSAGE_NAME
    return f"Message {hex(message_number)}"


def get_nasa_message_id(message_name: str) -> int:
    """Get the message number by its name."""
    for message_id, parser in MESSAGE_PARSERS.items():
        if parser.MESSAGE_NAME == message_name:
            return message_id
    raise ValueError(f"No message ID found for name: {message_name}")


def parse_message(message_number: int, payload: bytes, description: str) -> BaseMessage:
    parser_class = MESSAGE_PARSERS.get(message_number)
    if not parser_class:
        parser_class = RawMessage
    try:
        parser = parser_class.parse_payload(payload)
    except Exception as e:
        _LOGGER.exception("Error parsing packet for %s (%s): %s", message_number, bin2hex(payload), e)
        parser = RawMessage.parse_payload(payload)
    return parser
