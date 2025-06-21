"""Protocol factory."""

import logging

from .messages import load_message_classes
from .messaging import BaseMessage, RawMessage
from ...helpers import bin2hex
from ..enum import DataType, PacketType


MESSAGE_PARSERS: dict[int, BaseMessage] = load_message_classes()
_LOGGER = logging.getLogger(__name__)


def build_message(source: str, destination: str, data_type: DataType, message_number: int, payload: bytes) -> str:
    """Build a message to send to a device."""
    msg = []
    msg.append(source)
    msg.append(destination)
    command_byte1_val = (
        0x80  # packetInformation (assuming it's true for normal packets)
        | (1 << 4)  # protocolVersion = 1
        | (0 << 2)  # retryCount = 0
        | PacketType.NORMAL.value
    )  # PacketType (e.g., 0 for Normal)
    msg.append(f"{command_byte1_val:02x}")  # Packet Info/ProtoVer/Retry (1 byte)
    msg.append(f"{PacketType.NORMAL.value:02x}")  # Packet Type (1 byte)
    msg.append(f"{data_type.value:02x}")
    msg.append("{CUR_PACK_NUM}")  # Packet Number (1 byte, to be filled later)
    msg.append(f"{message_number:04x}")  # Message Number (4 bytes)
    msg.append(bin2hex(payload))  # Message Payload in hex
    return "".join(msg).upper()


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


def parse_message(message_number: int, payload: bytes, description: str) -> dict:
    parser_class = MESSAGE_PARSERS.get(message_number)
    if not parser_class:
        parser_class = RawMessage
    try:
        parser = parser_class.parse_payload(payload)
    except Exception as e:
        _LOGGER.exception("Error parsing packet for %s (%s): %s", message_number, bin2hex(payload), e)
        parser = RawMessage.parse_payload(payload)
    return parser
