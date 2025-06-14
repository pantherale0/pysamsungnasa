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
