# NASA Client API

Low-level TCP client for NASA protocol communication.

## Overview

The `NasaClient` handles all TCP communication with the NASA device. Most users won't interact with this directly - the `SamsungNasa` class provides a higher-level interface.

## Class Definition

```python
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.config import NasaConfig

client = NasaClient(
    host: str,
    port: int,
    config: NasaConfig,
    recv_event_handler: Callable | None = None,
    send_event_handler: Callable | None = None,
    disconnect_event_handler: Callable | None = None,
)
```

## Properties

### `is_connected: bool`

Read-only property indicating connection status.

```python
if client.is_connected:
    print("Connected to NASA device")
```

## Methods

### Connection Management

#### `async connect() -> bool`

Establish TCP connection to the NASA device.

```python
success = await client.connect()
if success:
    print("Connected successfully")
else:
    print("Connection failed")
```

**Returns:**
- `True` if connection successful
- `False` if connection failed

**Raises:**
- `ConnectionError` if unable to connect

#### `async disconnect()`

Close the TCP connection gracefully.

```python
await client.disconnect()
```

### Message Sending

#### `async send_message(destination, request_type, messages)`

Send a message to a device.

```python
from pysamsungnasa.protocol.factory import SendMessage
from pysamsungnasa.protocol.enum import DataType

await client.send_message(
    destination="200020",
    request_type=DataType.REQUEST,
    messages=[
        SendMessage(0x4000, b'\x01')  # Turn on
    ]
)
```

**Parameters:**
- `destination` (str | NasaDevice) - Target device address or NasaDevice object
- `request_type` (DataType) - Type of request (REQUEST, WRITE, READ, etc.)
- `messages` (list[SendMessage]) - Messages to send

#### `async nasa_read(msgs, destination)`

Send a read request to read device attributes.

```python
await client.nasa_read(
    msgs=[0x4000, 0x4001, 0x4203],
    destination="200020"
)
```

**Parameters:**
- `msgs` (list[int]) - List of message IDs to read
- `destination` (str) - Target device address

### Event Handlers

#### `set_receive_event_handler(handler: Callable)`

Set a callback for when data is received.

```python
def on_receive(packet_data):
    print(f"Received: {packet_data}")

client.set_receive_event_handler(on_receive)
```

### Internal Methods

These are typically used internally by `SamsungNasa`:

#### `_mark_read_received(packet_number, source, message_numbers)`

Mark pending read as received (internal).

#### `_handle_disconnection(ex: Exception | None)`

Handle connection loss (internal).

#### `_handle_connection()`

Handle successful connection (internal).

## Configuration

The client respects these configuration options:

```python
config = {
    # Retries
    "enable_read_retries": True,
    "read_retry_max_attempts": 3,
    "read_retry_interval": 1.0,
    "read_retry_backoff_factor": 1.1,

    "enable_write_retries": True,
    "write_retry_max_attempts": 3,
    "write_retry_interval": 1.0,
    "write_retry_backoff_factor": 1.1,

    # Buffer
    "max_buffer_size": 262144,
    "log_buffer_messages": False,
}

client = NasaClient(
    host="192.168.1.100",
    port=8000,
    config=NasaConfig(**config)
)
```

## Low-Level Usage Example

While typically you'd use `SamsungNasa`, here's direct client usage:

```python
import asyncio
from pysamsungnasa.nasa_client import NasaClient
from pysamsungnasa.config import NasaConfig
from pysamsungnasa.protocol.factory import SendMessage
from pysamsungnasa.protocol.enum import DataType

async def main():
    config = NasaConfig(
        client_address=1,
        enable_read_retries=True
    )

    client = NasaClient(
        host="192.168.1.100",
        port=8000,
        config=config
    )

    # Connect
    if not await client.connect():
        print("Failed to connect")
        return

    # Send a command
    await client.send_message(
        destination="200020",
        request_type=DataType.REQUEST,
        messages=[SendMessage(0x4000, b'\x01')]
    )

    # Wait for response
    await asyncio.sleep(2)

    # Disconnect
    await client.disconnect()

asyncio.run(main())
```

## Queue Management

The client uses internal queues for:

- **TX Queue** - Messages to send
- **RX Queue** - Packets received
- **Pending Reads** - Tracking read requests awaiting responses
- **Pending Writes** - Tracking write requests awaiting ACKs

These are managed automatically and not exposed to the user.

## Threading Model

- **Asynchronous** - Uses asyncio for all I/O operations
- **Single-threaded** - All operations run in a single event loop
- **Non-blocking** - Network I/O is non-blocking

## Error Handling

Connection errors are handled gracefully:

```python
try:
    await client.connect()
except ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Timeouts

Timeouts are managed based on configuration:

```python
config = {
    "read_retry_interval": 1.0,     # 1 second between retries
    "read_retry_max_attempts": 3,   # 3 attempts
    # Total timeout: ~3 seconds (with backoff)
}
```

## Performance Considerations

- **Buffer size** - Adjust `max_buffer_size` if handling many devices
- **Retry settings** - Balance responsiveness vs reliability
- **Message batching** - Send multiple messages in one packet for efficiency

```python
# Send multiple messages at once
await client.send_message(
    destination="200020",
    messages=[
        SendMessage(0x4000, b'\x01'),  # Power on
        SendMessage(0x4001, b'\x01'),  # Cool mode
        SendMessage(0x4201, (220).to_bytes(2, 'big'))  # 22°C
    ]
)
```

## Next Steps

- Read [SamsungNasa API](samsung-nasa.md)
- Check [NASA Device API](nasa-device.md)
- Learn [Basic Usage](../user-guide/basic-usage.md)
