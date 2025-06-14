"""NASA Configuration."""

from dataclasses import dataclass


@dataclass
class NasaConfig:
    """Represent a NASA configuration."""

    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[tuple[str, str]] | None = None
