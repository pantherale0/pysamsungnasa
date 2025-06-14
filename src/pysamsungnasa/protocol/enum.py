"""Protocol enums."""

from enum import StrEnum


class PacketTypes(StrEnum):
    """NASA Packet Types"""

    GATHERING = "gathering"
    NORMAL = "normal"
    STANDBY = "standby"
    INSTALL = "install"
    DOWNLOAD = "download"


class PayloadTypes(StrEnum):
    """NASA Payload Types."""

    UNDEF = "undef"
    READ = "read"
    WRITE = "write"
    REQUEST = "request"
    NOTIFICATION = "notification"
    RESPONSE = "response"
    ACK = "ack"
    NACK = "nack"
