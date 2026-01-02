# Protocol Overview

The NASA protocol is Samsung's proprietary protocol for HVAC device communication. This document provides a high-level overview for developers working with pysamsungnasa.

## What is NASA?

**NASA** (Network Architecture for Samsung Appliances) is a protocol used by Samsung HVAC and heating systems for inter-device communication.

Key characteristics:
- **Packet-based** - Data transmitted as structured packets
- **Addressable** - Each device has a unique network address
- **Bidirectional** - Devices both send and receive messages
- **Message-oriented** - Data organized into typed messages
- **Acknowledged** - Critical operations are acknowledged

## Architecture

### Network Model

```
┌─────────────┐
│   Indoor    │
│    Units    │
└──────┬──────┘
       │
   RS485 Bus
   (F1/F2)
       │
┌──────┬──────┐
│ Outdoor     │
│    Unit     │
└─────────────┘
```

All devices are connected via RS485 (F1/F2 connectors) forming a shared bus network.

### Device Types

Common device types (Address Classes):

| Address Class | Hex  | Description |
|---------------|------|-------------|
| Outdoor       | 0x10 | Heat pump outdoor unit |
| HTU           | 0x11 | Heating/Cooling Unit |
| Indoor        | 0x20 | Wall-mounted indoor unit |
| ERV           | 0x30 | Energy Recovery Ventilation |
| Diffuser      | 0x35 | Air diffuser/controller |
| MCU           | 0x38 | Main Control Unit |
| RMC           | 0x40 | Remote Controller |
| WiredRemote   | 0x50 | Wired remote control |
| PIM           | 0x58 | Power Interface Module |

## Message Types

The protocol defines several message types used in different contexts:

### Data Types

- **Read** (0x01) - Request to read device state
- **Write** (0x02) - Request to change device state
- **Request** (0x03) - General request
- **Notification** (0x04) - Unsolicited status broadcast
- **Response** (0x05) - Answer to a request
- **Ack** (0x06) - Acknowledge receipt
- **Nack** (0x07) - Negative acknowledge

### Packet Types

- **StandBy** (0) - Standby/initialization
- **Normal** (1) - Normal data transmission
- **Gathering** (2) - Data gathering mode
- **Install** (3) - Installation/setup mode
- **Download** (4) - Firmware download

## Message Numbers

Messages are identified by a 16-bit message number that encodes both the message type and data structure.

Common message ranges:

| Range | Purpose |
|-------|---------|
| 0x0000-0x00FF | System messages |
| 0x0200-0x04FF | Configuration and status |
| 0x0400-0x07FF | Installation/setup |
| 0x0600-0x0FFF | Product options |
| 0x2000-0x2FFF | Network control |
| 0x4000-0x7FFF | Device operation |

Examples:
- `0x4000` - Power on/off
- `0x4001` - Operation mode
- `0x4203` - Current temperature
- `0x4201` - Target temperature

## Payload Structures

Messages contain payloads of different sizes:

### Enum (1 byte)
Represents an enumeration value (0-255). These can also be used to represent an integer such as for the PWM water pump sensor.

Example: Power state (0=Off, 1=On)

```python
SendMessage(0x4000, b'\x01')  # Turn on
```

### Variable (2 bytes)
Represents a 16-bit value (0-65535).

Example: Temperature * 10

```python
temp_c = 22
payload = int(temp_c * 10).to_bytes(2, 'big')
SendMessage(0x4201, payload)  # Set temperature
```

### LongVariable (4 bytes)
Represents a 32-bit value.

Example: Power consumption in watts

```python
power_w = 1500
payload = power_w.to_bytes(4, 'big')
SendMessage(0x0406, payload)
```

### Structure
Variable-length structured data.

Example: Product information, device configuration

```python
SendMessage(0x0600, struct_data)  # Product options
```

## Communication Flow

### Normal Request/Response

```
Client                          Device
  │                               │
  ├─ REQUEST (Read/Write) ───────>│
  │                               │
  │<─ ACK ─────────────────────── │
  │                               │
  │<─ RESPONSE ────────────────── │
  │                               │
  └─ (data received) ────────────>│
```

### Unsolicited Notification

```
Device                          Client
  │                               │
  ├─ NOTIFICATION (broadcast) ──>│
  │                               │
  │<─ ACK ─────────────────────── │
```

### Retry Logic

If no acknowledgment is received, the client retries:

```
Client                          Device
  │                               │
  ├─ REQUEST ────────────────────>│
  │                               │
  │ (wait, no ACK)                │
  │                               │
  ├─ REQUEST (retry) ────────────>│
  │                               │
  │<─ ACK ─────────────────────── │
```

## Addressing

Addresses are structured as three components:

```
Address Class | Channel | Address
```

For example:
- `100000` = Class 0x10 (Outdoor), Channel 0x00, Address 0x00
- `200000` = Class 0x20 (Indoor), Channel 0x00, Address 0x00

## Transmission Settings

### Retry Configuration

The library provides configurable retries:

```python
config = {
    "enable_read_retries": True,
    "read_retry_max_attempts": 3,
    "read_retry_interval": 1.0,
    "read_retry_backoff_factor": 1.1,
}
```

### Timeout

If no response is received after all retries, the request times out.

## Data Encoding

### Temperature Values

Temperatures are typically encoded as:
- Integer value multiplied by 10
- Sent as 2-byte big-endian integer

Example: 22.5°C = 225 = `0x00E1`

### Power Values

Power is typically encoded as:
- Watts as 4-byte big-endian integer

Example: 1500W = `0x000005DC`

### Humidity

Humidity is sent as percentage (0-100):
- 1-byte unsigned integer

Example: 55% = `0x37`

## Known Message Numbers

See the NOTES.md file in the project root for an extensive list of known message numbers with descriptions.

Key categories:
- **Error codes** (0x0202-0x0206) - Device error states
- **Installation counts** (0x0207-0x0211) - Number of connected units
- **Operation modes** (0x4000-0x4015) - Power, mode, fan, temperature, swing
- **Temperature values** (0x4200-0x4240) - Current and target temperatures
- **Power consumption** (0x0406-0x0442) - Energy monitoring

## Protocol Evolution

The protocol has evolved over time:

- **Original NASA** - Basic protocol from Samsung HVAC systems
- **Extended NASA** - Added message types and capabilities
- **S-Net** - Latest version with additional message types and features

pysamsungnasa supports messages from the latest S-Net version.

## Working with Raw Messages

For advanced users, you can work with raw messages:

```python
from pysamsungnasa.protocol.factory import SendMessage

# Create a raw message
msg = SendMessage(
    MESSAGE_ID=0x4000,      # Power control
    PAYLOAD=b'\x01'         # Turn on
)

# Send it
await nasa.send_message(
    destination="200020",
    messages=[msg]
)
```

## Further Reading

- [Packet Structure](packet-structure.md) - Detailed packet format
- [Message Types](messages.md) - Message definitions
- [Message Factory](message-factory.md) - Auto-generated message documentation

## References

The protocol documentation is based on:

1. **MyEHS Wiki** - Comprehensive protocol documentation
2. **NASA.prc** - SNET Pro service software protocol definitions
3. **NasaConst.java** - WiFiKit open-source message definitions
4. **ESPHome Samsung HVAC Bus** - Community protocol implementations
5. **OpenEnergyMonitor Forum** - Shared wisdom and discoveries
