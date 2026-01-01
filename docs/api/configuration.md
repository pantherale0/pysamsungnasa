# Configuration API

Reference for NasaConfig and configuration management.

## NasaConfig

Configuration dataclass for pysamsungnasa.

### Class Definition

```python
from dataclasses import dataclass, field
from pysamsungnasa.config import NasaConfig

@dataclass
class NasaConfig:
    """Represent a NASA configuration."""

    client_address: int = 1
    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[str] = field(default_factory=list)
    max_buffer_size: int = 262144
    log_all_messages: bool = False
    devices_to_log: list[str] = field(default_factory=list)
    log_buffer_messages: bool = False
    enable_read_retries: bool = True
    read_retry_max_attempts: int = 3
    read_retry_interval: float = 1.0
    read_retry_backoff_factor: float = 1.1
    enable_write_retries: bool = True
    write_retry_max_attempts: int = 3
    write_retry_interval: float = 1.0
    write_retry_backoff_factor: float = 1.1
```

## Configuration Properties

### Network Configuration

#### `client_address: int = 1`
Your client's address on the NASA network.

**Default:** 1
**Valid range:** 1-255
**Purpose:** Identifies your application on the bus

```python
config = {"client_address": 1}
```

#### `device_addresses: list[str] = []`
Pre-configured device addresses to monitor.

```python
config = {
    "device_addresses": [
        "100000  # Outdoor unit
        "200020",  # Indoor unit 1
        "200021",  # Indoor unit 2
    ]
}
```

### Device Discovery

#### `device_pnp: bool = False`
Enable Plug and Play device auto-discovery.

**Default:** False (disabled)
**Note:** If enabled, devices are automatically discovered

```python
config = {"device_pnp": True}
```

#### `device_dump_only: bool = False`
Only listen to messages without active device management.

**Default:** False

```python
config = {"device_dump_only": True}
```

### Buffer Management

#### `max_buffer_size: int = 262144`
Maximum size of the receive buffer (bytes).

**Default:** 256 KB
**Note:** Increase if you experience buffer overflows with many devices

```python
config = {"max_buffer_size": 524288}  # 512 KB
```

### Logging Configuration

#### `log_all_messages: bool = False`
Log every message received, not just relevant ones.

**Default:** False
**Warning:** Very verbose, use only for debugging

```python
config = {"log_all_messages": True}
```

#### `devices_to_log: list[str] = []`
Specific devices to log messages from (ignored if `log_all_messages=True`).

```python
config = {
    "devices_to_log": ["200000", "200020"]
}
```

#### `log_buffer_messages: bool = False`
Log buffer-related diagnostic messages.

**Default:** False
**Purpose:** Debugging connection issues

```python
config = {"log_buffer_messages": True}
```

### Retry Configuration - Read

#### `enable_read_retries: bool = True`
Automatically retry failed read requests.

**Default:** True

#### `read_retry_max_attempts: int = 3`
Maximum number of read retry attempts.

**Default:** 3 attempts
**Valid range:** 1-10

#### `read_retry_interval: float = 1.0`
Initial wait time between read retries (seconds).

**Default:** 1.0 second

#### `read_retry_backoff_factor: float = 1.1`
Multiply retry interval by this factor after each attempt.

**Default:** 1.1
**Calculation:** Each retry waits `interval * (backoff_factor ^ attempt)`

**Example with defaults:**
- Attempt 1: Immediate
- Attempt 2: Wait 1.0s
- Attempt 3: Wait 1.1s
- Attempt 4: Wait 1.21s

```python
config = {
    "enable_read_retries": True,
    "read_retry_max_attempts": 3,
    "read_retry_interval": 1.0,
    "read_retry_backoff_factor": 1.1,
}
```

### Retry Configuration - Write

#### `enable_write_retries: bool = True`
Automatically retry failed write requests.

**Default:** True

#### `write_retry_max_attempts: int = 3`
Maximum number of write retry attempts.

**Default:** 3 attempts

#### `write_retry_interval: float = 1.0`
Initial wait time between write retries (seconds).

**Default:** 1.0 second

#### `write_retry_backoff_factor: float = 1.1`
Multiply retry interval by this factor after each attempt.

**Default:** 1.1

```python
config = {
    "enable_write_retries": True,
    "write_retry_max_attempts": 3,
    "write_retry_interval": 1.0,
    "write_retry_backoff_factor": 1.1,
}
```

## Properties (Read-only)

### `address: Address`
Returns the client's address as an Address object.

```python
nasa = SamsungNasa(...)
client_addr = nasa.config.address
print(client_addr)  # 0x80FF01
```

## Creating Configuration

### From Dictionary

The most common way - pass a dictionary to SamsungNasa:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={
        "client_address": 1,
        "device_addresses": ["200000", "200020"],
        "enable_read_retries": True,
    }
)
```

### From NasaConfig Object

Create a NasaConfig object first:

```python
from pysamsungnasa.config import NasaConfig

config = NasaConfig(
    client_address=1,
    device_addresses=["200000", "200020"],
    log_all_messages=False
)

nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config=config.dict()  # Convert to dict
)
```

### From Environment Variables

```python
import os
from pysamsungnasa.config import NasaConfig

config_dict = {
    "client_address": int(os.getenv("NASA_CLIENT_ADDR", "1")),
    "device_addresses": os.getenv("NASA_DEVICES", "100000").split(","),
    "log_all_messages": os.getenv("NASA_LOG_ALL", "false").lower() == "true",
    "enable_read_retries": os.getenv("NASA_RETRIES", "true").lower() == "true",
}

nasa = SamsungNasa(..., config=config_dict)
```

### From File

```python
import json
from pysamsungnasa import SamsungNasa

# Load from JSON file
with open("nasa_config.json") as f:
    config = json.load(f)

nasa = SamsungNasa(..., config=config)
```

Example `nasa_config.json`:
```json
{
    "client_address": 1,
    "device_addresses": ["200000", "200020"],
    "log_all_messages": false,
    "enable_read_retries": true,
    "read_retry_max_attempts": 3,
    "enable_write_retries": true,
    "write_retry_max_attempts": 3
}
```

## Configuration Presets

### Development/Debug

```python
debug_config = {
    "client_address": 1,
    "device_addresses": ["200000", "200020"],
    "log_all_messages": True,
    "log_buffer_messages": True,
    "enable_read_retries": True,
    "read_retry_max_attempts": 5,
    "enable_write_retries": True,
    "write_retry_max_attempts": 5,
}
```

### Production

```python
prod_config = {
    "client_address": 1,
    "device_addresses": ["200000", "200020"],
    "log_all_messages": False,
    "log_buffer_messages": False,
    "enable_read_retries": True,
    "read_retry_max_attempts": 3,
    "enable_write_retries": True,
    "write_retry_max_attempts": 3,
}
```

### Minimal

```python
minimal_config = {
    "client_address": 1,
}
```

### High-Reliability

```python
reliable_config = {
    "client_address": 1,
    "device_addresses": ["200000", "200020"],
    "enable_read_retries": True,
    "read_retry_max_attempts": 5,
    "read_retry_interval": 0.5,
    "read_retry_backoff_factor": 1.3,
    "enable_write_retries": True,
    "write_retry_max_attempts": 5,
    "write_retry_interval": 0.5,
    "write_retry_backoff_factor": 1.3,
}
```

## Accessing Configuration

After creating SamsungNasa, access the config:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={"client_address": 1}
)

# Read configuration
cfg = nasa.config

print(f"Client address: {cfg.client_address}")
print(f"Max buffer: {cfg.max_buffer_size} bytes")
print(f"Retries: {cfg.enable_read_retries}")
print(f"Devices: {cfg.device_addresses}")
```

## Validation

Configuration is validated when passed to SamsungNasa:

```python
try:
    nasa = SamsungNasa(
        ...,
        config={"invalid_key": "value"}  # Will raise error
    )
except TypeError as e:
    print(f"Configuration error: {e}")
```

## Configuration for Different Scenarios

### Single Device Monitoring

```python
config = {
    "client_address": 1,
    "device_addresses": ["100000"],
    "log_all_messages": False,
}
```

### Multiple Devices

```python
config = {
    "client_address": 1,
    "device_addresses": [
        "100000  # Outdoor
        "200020",  # Indoor 1
        "200021",  # Indoor 2
        "200022",  # Indoor 3
    ],
}
```

### Auto-Discovery

```python
config = {
    "client_address": 1,
    "device_pnp": True,  # Enable PnP
}
```

### Slow Network

```python
config = {
    "client_address": 1,
    "enable_read_retries": True,
    "read_retry_max_attempts": 5,
    "read_retry_interval": 2.0,  # Longer delays
    "read_retry_backoff_factor": 1.5,  # Steeper backoff
}
```

### Network Dump/Analysis

```python
config = {
    "client_address": 1,
    "device_dump_only": True,  # Don't manage devices
    "log_all_messages": True,   # Log everything
    "log_buffer_messages": True,
}
```

## Next Steps

- Read [Configuration Guide](../user-guide/configuration.md)
- Check [Basic Usage](../user-guide/basic-usage.md)
- Learn about [SamsungNasa](samsung-nasa.md)
