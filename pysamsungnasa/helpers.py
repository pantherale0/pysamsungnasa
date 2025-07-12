import binascii
import re


def bin2hex(bin):
    return binascii.hexlify(bin).decode("utf-8")


def hex2bin(hex):
    return binascii.unhexlify(re.sub(r"\s", "", hex))


_NONCE = 0xA4


def getnonce():
    global _NONCE
    _NONCE += 1
    _NONCE %= 256
    return _NONCE


def resetnonce():
    global _NONCE
    _NONCE = 0


class Address:
    """Class to represent a device address."""

    def __init__(self, class_id: int, channel: int, address: int):
        self.class_id = class_id
        self.channel = channel
        self.address = address

    def __str__(self):
        return f"{self.class_id:02X}{self.channel:02X}{self.address:02X}"

    def __repr__(self):
        return f"Address(class_id={self.class_id}, channel={self.channel}, address={self.address})"

    @classmethod
    def parse(cls, data: str):
        """Parse into a address object."""
        return cls(
            class_id=int(data[0:2], 16),
            channel=int(data[2:4], 16),
            address=int(data[4:6], 16),
        )
