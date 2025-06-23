"""NASA Configuration."""

from dataclasses import dataclass

from .helpers import Address

@dataclass
class NasaConfig:
    """Represent a NASA configuration."""

    client_address: int = 0  # Represents the client address (this device's address)
    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[tuple[str, str]] | None = None
    max_buffer_size: int = 65536 # 64kb
    log_all_messages: bool = False # If set to true, log all messages including those not destined for this device.
    log_buffer_messages: bool = False # If set to true, messsages relating to the buffer are logged

    @property
    def address(self) -> Address:
        """Return address."""
        return Address(
            0x50,
            0xFF,
            self.client_address
        )
