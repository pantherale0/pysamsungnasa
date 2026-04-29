"""Message parser for NASA protocol."""

import logging
import struct
from . import MESSAGE_PARSERS
from .types import BaseMessage, RawMessage
from ...helpers import bin2hex

_LOGGER = logging.getLogger(__name__)

STX_BYTE = 0x32
ETX_BYTE = 0x34
MALFORMED_PACKET_LENGTH_THRESHOLD = 2000
MALFORMED_PACKET_MIN_BUFFER = 500
MALFORMED_PACKET_NEXT_STX_WINDOW = 300


def parse_message(
    message_number: int, payload: bytes, message_parsers: dict[int, BaseMessage] | None = None
) -> BaseMessage:
    """Parse a message from its payload.

    Args:
        message_number: The message ID to parse
        payload: The raw message payload bytes
        message_parsers: Dictionary mapping message numbers to parser classes.
                        If None, will attempt to use the global MESSAGE_PARSERS.

    Returns:
        Parsed message instance
    """
    if message_parsers is None:
        message_parsers = MESSAGE_PARSERS

    parser_class = message_parsers.get(message_number)
    if not parser_class:
        parser_class = RawMessage
    try:
        parser = parser_class.parse_payload(payload)
    except Exception as e:
        _LOGGER.exception(
            "Error parsing packet for %s (%s): %s",
            message_number,
            bin2hex(payload) if isinstance(payload, bytes) else str(payload),
            e,
        )
        parser = RawMessage.parse_payload(payload)
    return parser


def parse_tlv_structure(struct_payload: bytes) -> dict:
    """Parse TLV-encoded structure data from raw bytes.

    Extracts each TLV entry and attempts to parse each sub-message.
    As a best effort, joins all sub-message values into a single string representation.

    Args:
        struct_payload: Raw bytes containing TLV-encoded sub-messages

    Returns:
        Dictionary with parsed structure containing _submessages and _joined keys
    """
    submessages = {}
    submessage_strings = []
    struct_offset = 0

    while struct_offset < len(struct_payload):
        if struct_offset + 1 >= len(struct_payload):
            break

        # First byte contains length
        message_length = struct_payload[struct_offset]
        struct_offset += 1

        if struct_offset + 2 > len(struct_payload):
            break

        # Next two bytes are message ID
        try:
            sub_message_number = struct.unpack(">H", struct_payload[struct_offset : struct_offset + 2])[0]
        except struct.error:
            break
        struct_offset += 2

        # Remaining bytes are the value
        if message_length >= 2:
            value_length = message_length - 2
            if struct_offset + value_length > len(struct_payload):
                value = struct_payload[struct_offset:]
                struct_offset = len(struct_payload)
            else:
                value = struct_payload[struct_offset : struct_offset + value_length]
                struct_offset += value_length
        else:
            value = b""

        # Parse the submessage using the standard parse_message function
        try:
            parsed_submessage = parse_message(sub_message_number, value)
            submessages[sub_message_number] = parsed_submessage
            # Collect string representations for joining
            if hasattr(parsed_submessage, "VALUE"):
                submessage_strings.append(str(parsed_submessage.VALUE))
        except Exception as e:
            _LOGGER.debug("Failed to parse submessage 0x%04x in structure: %s", sub_message_number, e)
            # Store raw hex if parsing fails
            submessages[sub_message_number] = value.hex() if value else ""
            submessage_strings.append(value.hex() if value else "")

    # Attempt to create a joined string representation
    joined_value = None
    if submessage_strings:
        try:
            # Try to join as a concatenated hex string first
            joined_hex = ""
            for s in submessage_strings:
                if isinstance(s, bytes):
                    joined_hex += s.hex()
                elif isinstance(s, str):
                    if len(s) % 2 != 0:
                        _LOGGER.warning("Skipping odd-length string in structure joining: %r", s)
                        continue
                    joined_hex += s
                else:
                    continue
            # Try to decode as UTF-8
            decoded = bytes.fromhex(joined_hex).decode("utf-8").rstrip("\x00")
            if decoded and all(32 <= ord(c) <= 126 or c in "\n\r\t" for c in decoded):
                joined_value = decoded
            else:
                joined_value = joined_hex
        except (ValueError, UnicodeDecodeError):
            # If joining fails, use raw hex
            joined_value = "".join(submessage_strings)

    # Return with both the detailed submessages dict and the joined string
    value_dict = {"_submessages": submessages, "_joined": joined_value}
    return value_dict


def extract_packets_from_buffer(
    buffer: bytes,
    *,
    max_buffer_size: int,
    log_buffer_messages: bool = False,
    logger: logging.Logger | None = None,
) -> tuple[list[bytes], bytes]:
    """Extract complete NASA packets from a byte buffer.

    Args:
        buffer: Current stream buffer including newly received data.
        max_buffer_size: Max allowed in-memory buffer size.
        log_buffer_messages: Enable verbose parser diagnostics.
        logger: Optional logger for diagnostics.

    Returns:
        A tuple of ``(packets, remaining_buffer)``.
    """
    log = logger or _LOGGER
    packets: list[bytes] = []

    if len(buffer) > max_buffer_size:
        log.error("Max buffer size reached %s/%s", len(buffer), max_buffer_size)
        return packets, b""

    while buffer:
        stx_index = buffer.find(bytes((STX_BYTE,)))

        if stx_index == -1:
            if log_buffer_messages:
                log.debug("No STX found, clearing buffer")
            return packets, b""

        if stx_index > 0:
            if log_buffer_messages:
                log.debug("Skipping %d bytes of garbage", stx_index)
            buffer = buffer[stx_index:]

        if len(buffer) < 3:
            if log_buffer_messages:
                log.debug("Not enough data for header, waiting for more.")
            break

        try:
            _, packet_len_val = struct.unpack_from(">BH", buffer)
        except struct.error:
            log.debug("Struct unpack failed. Discarding STX and continuing.")
            buffer = buffer[1:]
            continue

        if packet_len_val > max_buffer_size:
            log.debug(
                "Parsed packet length %d exceeds max size %d. Assuming parse error.",
                packet_len_val,
                max_buffer_size,
            )
            buffer = buffer[1:]
            continue

        expected_packet_len = packet_len_val + 2  # STX + ETX
        if len(buffer) < expected_packet_len:
            if expected_packet_len > MALFORMED_PACKET_LENGTH_THRESHOLD and len(buffer) > MALFORMED_PACKET_MIN_BUFFER:
                next_stx = buffer.find(bytes((STX_BYTE,)), 1)
                if 0 < next_stx < MALFORMED_PACKET_NEXT_STX_WINDOW:
                    buffer = buffer[next_stx:]
                    continue

            if log_buffer_messages:
                log.debug(
                    "Incomplete packet. Have %d, need %d. Waiting for more data.",
                    len(buffer),
                    expected_packet_len,
                )
            break

        packet = buffer[:expected_packet_len]
        if packet[-1] != ETX_BYTE:
            if log_buffer_messages:
                log.debug("Invalid ETX. Got 0x%02x, expected 0x%02x.", packet[-1], ETX_BYTE)
            buffer = buffer[1:]
            continue

        packets.append(packet)
        buffer = buffer[expected_packet_len:]

    return packets, buffer
