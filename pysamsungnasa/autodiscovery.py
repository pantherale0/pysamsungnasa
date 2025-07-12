"""NASA Device Autodiscovery."""

from .nasa import SamsungNasa
from .nasa_client import NasaClient
from .protocol.enum import DataType
from .protocol.factory import build_message, SendMessage


async def request_network_address(client: NasaClient):
    """Request a network address from the client."""
    await client.send_command(
        message=[
            build_message(
                source="500000",
                destination="B0FFFF",
                messages=[SendMessage(MESSAGE_ID=hex(0x10000 + 0x210)[-4:], PAYLOAD=bytes.fromhex(hex(0x10000)[-4:]))],
            )
        ]
    )


async def autodiscover_devices(client: NasaClient):
    """Send auto disocvery packets to the client."""


async def nasa_poke(client: SamsungNasa):
    """Send poke packets to the client."""
    await client.send_message(
        0x4242, payload=bytes.fromhex("FFFF"), destination="200000", request_type=DataType.REQUEST
    )
