"""Protocol factory."""

from .messaging import BaseMessage, InOperationModeMessage, InFanModeRealMessage, BoolMessage

MESSAGE_PARSERS = {
    0x4001: InOperationModeMessage,
    0x4007: InFanModeRealMessage,
    0x4065: BoolMessage,
    # Add more mappings here
}


def parse_message(message_number: int, payload: bytes, description: str) -> BaseMessage:
    parser_class = MESSAGE_PARSERS.get(message_number)
    if not parser_class:
        raise ValueError(f"No parser defined for message number: {hex(message_number)}")
    parser = parser_class(message_number, payload, description)
    return parser
