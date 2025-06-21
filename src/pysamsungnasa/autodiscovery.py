"""NASA Device Autodiscovery."""

from .nasa import SamsungNasa
from .nasa_client import NasaClient
from .device import NasaDevice
from .protocol.enum import DataType



async def autodiscover_devices(client: NasaClient):
    """Send auto disocvery packets to the client."""

async def nasa_poke(client: SamsungNasa):
    """Send poke packets to the client."""
    await client.send_message(
        0x4242,
        payload=bytes.fromhex("FFFF"),
        destination="200000",
        request_type=DataType.REQUEST
    )
