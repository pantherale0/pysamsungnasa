"""NASA Device Autodiscovery."""

from .nasa import SamsungNasa
from .nasa_client import NasaClient
from .protocol.enum import DataType
from .protocol.factory import SendMessage, build_message


async def request_network_address(client: NasaClient):
    """Request a network address from the client."""
    await client.send_command(
        message=[
            build_message(
                source="500000",
                destination="B0FFFF",
                data_type=DataType.REQUEST,
                messages=[SendMessage(MESSAGE_ID=0x0210, PAYLOAD=bytes.fromhex("0000"))],
            )
        ]
    )


async def autodiscover_devices(client: NasaClient):
    """Send auto disocvery packets to the client."""


async def nasa_poke(client: SamsungNasa):
    """Send poke packets to the client."""
    await client.send_message(
        destination="200000",
        request_type=DataType.REQUEST,
        messages=[SendMessage(MESSAGE_ID=0x4242, PAYLOAD=bytes.fromhex("FFFF"))],
    )
