"""NASA Configuration."""

from dataclasses import dataclass, field

from .helpers import Address


@dataclass
class NasaConfig:
    """Represent a NASA configuration."""

    client_address: int = 1  # Represents the client address (this device's address)
    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[str] = field(default_factory=list)
    max_buffer_size: int = 262144  # 256kb
    log_all_messages: bool = False  # If set to true, log all messages including those not destined for this device.
    devices_to_log: list[str] = field(
        default_factory=list
    )  # Optional: add the device address here to only log messages for a specific device
    messages_to_log: list[int] = field(
        default_factory=list
    )  # Optional: add message IDs here to only log specific messages
    log_buffer_messages: bool = False  # If set to true, messsages relating to the buffer are logged
    enable_read_retries: bool = True  # Enable automatic retry of read requests that don't get responses
    read_retry_max_attempts: int = 3  # Maximum number of retry attempts for read requests
    read_retry_interval: float = 1.0  # Interval in seconds between retry attempts
    read_retry_backoff_factor: float = 1.1  # Multiply retry interval by this factor after each attempt
    enable_write_retries: bool = True  # Enable automatic retry of write requests that don't get ACKs
    write_retry_max_attempts: int = 3  # Maximum number of retry attempts for write requests
    write_retry_interval: float = 1.0  # Interval in seconds between retry attempts
    write_retry_backoff_factor: float = 1.1  # Multiply retry interval by this factor after each attempt

    @property
    def address(self) -> Address:
        """Return address."""
        return Address(0x80, 0xFF, self.client_address)
