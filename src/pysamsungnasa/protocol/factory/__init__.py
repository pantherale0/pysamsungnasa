"""Protocol factory."""

import logging

from .messages import load_message_classes
from .messaging import BaseMessage, RawMessage
from ...helpers import bin2hex

MESSAGE_PARSERS: dict[int, BaseMessage] = load_message_classes()
SEND_MESSAGE_BASE_CONTENT = [
    "{SOURCE}",  # Source Address (Class 10, Chan 00, Addr 00)
    "{DESTINATION}",  # Destination Address (Class B0, Chan FF, Addr FF)
    "00",  # Packet Info/ProtoVer/Retry
    "14",  # PacketType (1=Normal), DataType (4=Notification)
    "{CUR_PACK_NUM}",  # Packet Number
    "01",  # Capacity (Number of Messages)
    "{MESSAGE_NUMBER}",  # Message Number (OUT_OPERATION_STATUS)
    "{PAYLOAD_HEX}",  # Message Payload
]
_LOGGER = logging.getLogger(__name__)


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


def build_message(source: str, destination: str, message_number: int, payload: bytes) -> str:
    """Build a message to send to a device."""
    msg = list(SEND_MESSAGE_BASE_CONTENT)
    msg[0] = source
    msg[1] = destination
    msg[6] = f"{message_number:04x}"  # Message Number (4 bytes)
    msg[7] = bin2hex(payload)  # Message Payload in hex
    return "".join(msg).upper()
