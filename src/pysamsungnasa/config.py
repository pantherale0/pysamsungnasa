"""NASA Configuration."""

from dataclasses import dataclass


@dataclass
class NasaConfig:
    """Represent a NASA configuration."""

    client_address: int = 0  # Represents the client address (this device's address)
    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[tuple[str, str]] | None = None
