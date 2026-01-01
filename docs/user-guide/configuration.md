# Configuration

Configure pysamsungnasa to match your network setup and requirements.

## NasaConfig Object

All configuration is managed through the `NasaConfig` class, passed as a dictionary to `SamsungNasa`:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={
        # Configuration options here
    }
)
```

## Basic Configuration

### Client Address

Your device's address on the NASA network:

```python
config = {
    "client_address": 1,  # Default: 1
}
```

The client address identifies your Python application on the network. Must be unique among all clients.

### Device Addresses

Specify devices you want to monitor:

```python
config = {
    "client_address": 1,
    "device_addresses": [
        "100000  # Outdoor unit (standard format)
        "200020",    # Indoor unit 1
        "200021",    # Indoor unit 2
    ]
}
```

**Address Format**: Addresses are strings representing the device's network address.

Common addresses:
- `100000  # Outdoor unit (standard)
- `200020` - Indoor unit 1
- `200021` - Indoor unit 2
- See your unit's documentation for specific addresses

## Buffer Management

### Max Buffer Size

Control the maximum size of the receive buffer:

```python
config = {
    "max_buffer_size": 262144,  # Default: 256KB
}
```

Increase if you experience buffer overflow errors. Decrease if memory is limited.

### Buffer Logging

Enable logging of buffer-related messages:

```python
config = {
    "log_buffer_messages": False,  # Default: False
}
```

Useful for debugging connection issues.

## Logging Configuration

### Log All Messages

Log every message received, not just those for your devices:

```python
config = {
    "log_all_messages": False,  # Default: False
}
```

**Warning**: Generates very verbose output. Use only for debugging.

### Device-Specific Logging

Log messages only from specific devices:

```python
config = {
    "devices_to_log": [
        "100000",  # Only log outdoor unit
        "200020",  # And indoor unit 1
    ]
}
```

Useful for debugging specific devices without verbose output.

## Retry Configuration

### Read Retries

Automatically retry failed read requests:

```python
config = {
    "enable_read_retries": True,      # Default: True
    "read_retry_max_attempts": 3,     # Default: 3
    "read_retry_interval": 1.0,       # Default: 1.0 seconds
    "read_retry_backoff_factor": 1.1, # Default: 1.1
}
```

- **enable_read_retries**: Turn retry logic on/off
- **read_retry_max_attempts**: How many times to retry
- **read_retry_interval**: Wait time between attempts (increases with backoff factor)
- **read_retry_backoff_factor**: Multiply interval by this after each attempt

Example: With interval=1.0 and backoff=1.1:
- Attempt 1: immediate
- Attempt 2: wait 1.0s
- Attempt 3: wait 1.1s

### Write Retries

Retry failed write requests (commands):

```python
config = {
    "enable_write_retries": True,       # Default: True
    "write_retry_max_attempts": 3,      # Default: 3
    "write_retry_interval": 1.0,        # Default: 1.0 seconds
    "write_retry_backoff_factor": 1.1,  # Default: 1.1
}
```

## PNP (Plug and Play)

### Auto-Discovery

Enable automatic device discovery:

```python
config = {
    "device_pnp": False,  # Default: False (disabled)
}
```

When enabled, devices are automatically discovered without specifying addresses.

## Device Dump Mode

### Dump Only Mode

Receive all messages without filtering:

```python
config = {
    "device_dump_only": False,  # Default: False
}
```

Useful for analyzing all network traffic.

## Complete Configuration Example

Here's a realistic configuration:

```python
config = {
    # Network
    "client_address": 1,
    "device_addresses": ["200000", "200020"],

    # Buffer
    "max_buffer_size": 262144,
    "log_buffer_messages": False,

    # Logging
    "log_all_messages": False,
    "devices_to_log": [],

    # Retries
    "enable_read_retries": True,
    "read_retry_max_attempts": 3,
    "read_retry_interval": 1.0,
    "read_retry_backoff_factor": 1.1,

    "enable_write_retries": True,
    "write_retry_max_attempts": 3,
    "write_retry_interval": 1.0,
    "write_retry_backoff_factor": 1.1,

    # Discovery
    "device_pnp": False,
    "device_dump_only": False,
}

nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config=config
)
```

## Environment-Based Configuration

Load configuration from environment variables:

```python
import os

config = {
    "client_address": int(os.getenv("NASA_CLIENT_ADDRESS", "1")),
    "device_addresses": os.getenv("NASA_DEVICES", "200000,200020").split(","),
    "log_all_messages": os.getenv("NASA_DEBUG", "false").lower() == "true",
}

nasa = SamsungNasa(
    host=os.getenv("NASA_HOST", "192.168.1.100"),
    port=int(os.getenv("NASA_PORT", "8000")),
    config=config
)
```

Usage:
```bash
export NASA_HOST=192.168.1.100
export NASA_PORT=8000
export NASA_CLIENT_ADDRESS=1
export NASA_DEVICES=200000,200020
export NASA_DEBUG=false

python your_script.py
```

## Configuration for Different Setups

### Single Outdoor Unit

```python
config = {
    "client_address": 1,
    "device_addresses": ["100000"],
}
```

### Multiple Indoor Units

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

### Debug Mode

```python
config = {
    "client_address": 1,
    "device_addresses": ["100000"],
    "log_all_messages": True,
    "devices_to_log": ["100000"],
    "log_buffer_messages": True,
}
```

### Production Mode

```python
config = {
    "client_address": 1,
    "device_addresses": ["200000", "200020"],
    "enable_read_retries": True,
    "enable_write_retries": True,
    "read_retry_max_attempts": 5,
    "write_retry_max_attempts": 5,
}
```

## Accessing Configuration

Access the active configuration:

```python
nasa = SamsungNasa(...)
await nasa.start()

# Get the config object
cfg = nasa.config

print(f"Client address: {cfg.client_address}")
print(f"Retry enabled: {cfg.enable_read_retries}")
```

## Configuration Validation

The `NasaConfig` class validates configuration on creation:

```python
try:
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "invalid_option": True,  # Will raise an error
        }
    )
except TypeError as e:
    print(f"Configuration error: {e}")
```

## Next Steps

- Learn about [Device Management](device-management.md)
- Explore [Controllers](controllers.md)
- Read the [API Reference](../api/configuration.md)
