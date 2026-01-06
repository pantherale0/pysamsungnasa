# Packet Structure

Detailed specification of the NASA protocol packet format.

## Overview

The NASA protocol uses a frame-based communication model:

```
┌─────┬────────┬────────┬─────────────┬──────┬──────┐
│STX  │  Size  │Address │  Packet &   │      │ ETX  │
│0x32 │(2 bytes)│ (6) │ Data Type │Messages│ 0x34 │
└─────┴────────┴────────┴─────────────┴──────┴──────┘
       └─────────────────────────────────────┘
                    Payload Size
```

## Packet Layout

Each NASA packet follows this structure:

| Bytes | Field | Value | Description |
|-------|-------|-------|-------------|
| 0 | Packet Start (STX) | 0x32 | Fixed start marker ('2') |
| 1-2 | Packet Size | 16-bit LE | Total packet size (including size field) |
| 3 | Source Address Class | Enum | Device type sending the packet |
| 4 | Source Channel | 8-bit | Channel number |
| 5 | Source Address | 8-bit | Device address |
| 6 | Dest Address Class | Enum | Destination device type |
| 7 | Dest Channel | 8-bit | Destination channel |
| 8 | Dest Address | 8-bit | Destination device address |
| 9 | Packet Information | Flags | Protocol version, retry count |
| 10 | Packet Type & Data Type | Nibbles | Message type and operation |
| 11 | Packet Number | 8-bit | Increasing packet counter |
| 12 | Capacity | 8-bit | Number of messages in packet |
| 13-14 | Message Number | 16-bit | First message identifier |
| 15... | Message Payload | Variable | Data for message |
| ... | (repeat for each message) | | Multiple messages per packet |
| -3 to -2 | CRC 16 | 16-bit | Checksum |
| -1 | Packet End (ETX) | 0x34 | Fixed end marker ('4') |

## Calculation Notes

```python
# Total packet length calculation
packet_size = data[1] | (data[2] << 8)  # 16-bit little-endian
total_length = packet_size + 2  # Size field is not included in size value

# CRC validation
crc_bytes = data[-3:-1]  # Two bytes before ETX
crc_value = crc_bytes[0] | (crc_bytes[1] << 8)
```

## Field Descriptions

### Packet Start & End

```python
PACKET_START = 0x32  # '2' - marks packet beginning
PACKET_END = 0x34    # '4' - marks packet end
```

These fixed markers frame every valid NASA protocol packet. Packets without these markers should be discarded.

### Packet Size

16-bit little-endian value representing packet length starting from the size field itself.

```python
size = data[1] | (data[2] << 8)  # Little-endian decoding
payload_start = 3
payload_length = size - 1  # Exclude size bytes
total_packet_len = size + 2  # Include the 2 size bytes plus payload
```

### Address Fields (Bytes 3-8)

Device communication requires a 6-byte address structure for both source and destination:

```
[Source Address Class (1)] [Source Channel (1)] [Source Address (1)]
[Dest Address Class (1)]   [Dest Channel (1)]   [Dest Address (1)]
```

**Address Class** enumeration:

| Class | Hex | Device Type | Notes |
|-------|-----|-------------|-------|
| Outdoor | 0x10 | Heat pump outdoor unit | Primary heat source |
| HTU | 0x11 | Heating/Cooling unit | Alternative outdoor |
| Indoor | 0x20 | Wall mounted unit | Single-zone terminal |
| ERV | 0x30 | Energy recovery ventilation | Fresh air handling |
| Diffuser | 0x35 | Air diffuser/controller | Duct outlet |
| MCU | 0x38 | Main control unit | Central distribution |
| RMC | 0x40 | Remote controller | Central thermostat |
| WiredRemote | 0x50 | Wired remote control | Wall panel |
| PIM | 0x58 | Power interface module | Electrical interface |
| SIM | 0x59 | Serial interface module | Communications |
| Peak | 0x5A | Peak power controller | Load balancing |
| PowerDivider | 0x5B | Power distribution | Multi-unit control |
| WiFiKit | 0x62 | WiFi interface module | Network connectivity |

**Channel** field further specifies the subsystem (typically 0x00 for main).

**Address** field identifies the specific device on that channel.

Example address in HVAC system:
```
Address Class: 0x10 (Outdoor)
Channel: 0x00
Address: 0x00
```

This represents the primary outdoor unit.

### Packet Information (Byte 9)

This byte packs multiple control fields using bit masking:

```python
byte_9 = data[9]

# Bit 7: Packet Information flag (1 = contains control info)
packet_info_flag = (byte_9 & 0x80) >> 7

# Bits 6-5: Protocol Version (0-3)
protocol_version = (byte_9 & 0x60) >> 5

# Bits 4-3: Retry Count (0-3, number of retries)
retry_count = (byte_9 & 0x18) >> 3

# Bits 2-0: Reserved (not used)
```

- **Packet Information**: Indicates if packet is informational vs control
- **Protocol Version**: NASA protocol version (allows future compatibility)
- **Retry Count**: Tracks retry attempts for reliability

### Packet Type & Data Type (Byte 10)

This byte contains two 4-bit fields:

```python
byte_10 = data[10]

# High nibble (bits 7-4): Packet Type
packet_type = (byte_10 & 0xF0) >> 4

# Low nibble (bits 3-0): Data Type
data_type = byte_10 & 0x0F
```

**Packet Type values:**
- 0 = **StandBy** - Device in standby mode
- 1 = **Normal** - Normal operation
- 2 = **Gathering** - Data collection mode
- 3 = **Install** - Installation/setup mode
- 4 = **Download** - Firmware download/configuration

**Data Type values:**
- 0 = **Undefined** - Invalid or unknown type
- 1 = **Read** - Request to read data
- 2 = **Write** - Command to write data
- 3 = **Request** - Service request
- 4 = **Notification** - Status notification
- 5 = **Response** - Reply to read request
- 6 = **Ack** - Acknowledgment of command
- 7 = **Nack** - Negative acknowledgment (error)

### Packet Number (Byte 11)

```python
packet_number = data[11]
```

An incrementing counter for packet ordering and duplicate detection. Wraps from 255 back to 0.

### Message Capacity (Byte 12)

```python
capacity = data[12]
```

Specifies how many messages are encoded in this packet. Allows multiple independent messages in a single packet for efficiency.

### Message Number (Bytes 13-14)

The message number field encodes both the message identifier and its payload type:

```python
msg_num = data[13] | (data[14] << 8)  # 16-bit little-endian

# Extract message type from bits 10-9
msg_type = (msg_num & 0x0600) >> 9

# Message payload types:
# 0 = Enum (1 byte payload)
# 1 = Variable (2 bytes payload)
# 2 = LongVariable (4 bytes payload)
# 3 = Structure (remaining bytes)
```

## Message Payload Structure

For packets with multiple messages, each message follows this pattern:

```
Message 1:
[Message Number (2)] [Payload (variable)]

Message 2:
[Message Number (2)] [Payload (variable)]

... repeat for capacity count ...
```

The payload size is determined by the message number encoding:
- **Type 0 (Enum):** 1 byte
- **Type 1 (Variable):** 2 bytes
- **Type 2 (LongVariable):** 4 bytes
- **Type 3 (Structure):** All remaining bytes minus CRC and ETX

## CRC Validation

The last 3 bytes of the packet contain checksum and end marker:

```python
crc_high = data[-3]
crc_low = data[-2]
end_marker = data[-1]

crc_value = crc_low | (crc_high << 8)  # Little-endian CRC16
assert end_marker == 0x34  # Verify ETX
```

The CRC-16 covers the entire packet from STX through the last data byte.

## Packet Validation Checklist

When receiving a packet:

1. ✓ Verify `data[0] == 0x32` (STX)
2. ✓ Check `data[-1] == 0x34` (ETX)
3. ✓ Validate packet length matches size field
4. ✓ Verify CRC-16 checksum
5. ✓ Ensure capacity count is valid
6. ✓ Parse messages according to their types
7. ✓ Handle address routing correctly

## Example Packet Breakdown

```
Hex: 32 0B 00 10 00 00 20 00 00 81 50 01 02 00 42
     |  |     |        |        |  |  |  |  |     |
     |  |     |        |        |  |  |  |  |     +-- Message payload
     |  |     |        |        |  |  |  |  +-- Message number
     |  |     |        |        |  |  |  +-- Capacity (2 messages)
     |  |     |        |        |  |  +-- Packet number
     |  |     |        |        |  +-- Data type (5=Response), Packet type (1=Normal)
     |  |     |        |        +-- Packet info/version/retry
     |  |     |        +-- Destination: Indoor unit, ch 0, addr 0
     |  |     +-- Source: Outdoor unit, ch 0, addr 0
     |  +-- Size: 11 bytes
     +-- STX (0x32)
```


Each address has three components:

```
Address Class | Channel | Address
  (byte 0)    | (byte 1)| (byte 2)
```

**Address Class** values:

| Class | Hex | Device Type |
|-------|-----|-------------|
| Outdoor | 0x10 | Outdoor unit |
| HTU | 0x11 | Heating/Cooling unit |
| Indoor | 0x20 | Wall mounted unit |
| ERV | 0x30 | Ventilation |
| Diffuser | 0x35 | Air diffuser |
| MCU | 0x38 | Main control unit |
| RMC | 0x40 | Remote controller |
| WiredRemote | 0x50 | Wired remote |
| PIM | 0x58 | Power interface |

Example address: `100000`
- Class: `0x10` (Outdoor)
- Channel: `0x00`
- Address: `0x00`

### Packet Information (Byte 9)

This byte contains multiple fields:

```python
byte_9 = data[9]

# Bit 7: Packet Information flag
packet_info = (byte_9 & 0x80) >> 7

# Bits 6-5: Protocol Version
protocol_version = (byte_9 & 0x60) >> 5

# Bits 4-3: Retry Count
retry_count = (byte_9 & 0x18) >> 3
```

- **Packet Information**: 1 if packet contains control information, 0 otherwise
- **Protocol Version**: Version number of the NASA protocol
- **Retry Count**: How many times this packet has been retried

### Packet Type & Data Type (Bytes 10-11)

```python
byte_10 = data[10]
byte_11 = data[11]

# Byte 10, high nibble: Packet Type
packet_type = (byte_10 & 0xF0) >> 4

# Byte 10, low nibble: Data Type
data_type = byte_10 & 0x0F

# Byte 11: Packet Number
packet_number = byte_11
```

**Packet Types:**
- 0 = StandBy
- 1 = Normal
- 2 = Gathering
- 3 = Install
- 4 = Download

**Data Types:**
- 0 = Undefined
- 1 = Read
- 2 = Write
- 3 = Request
- 4 = Notification
- 5 = Response
- 6 = Ack
- 7 = Nack

### Message Capacity

Byte 13 indicates how many messages are included in this packet.

```python
capacity = data[13]  # Number of messages
```

### Message Number (Bytes 14-15)

The message number is a 16-bit identifier that encodes the message type and payload size:

```python
msg_num = data[14] * 256 + data[15]

# Extract message type from upper 2 bits
msg_type = (msg_num & 0x0600) >> 9

# Message types:
# 0 = Enum (1 byte)
# 1 = Variable (2 bytes)
# 2 = LongVariable (4 bytes)
# 3 = Structure (variable)
```

### Message Payloads

Messages are stored sequentially. The number of bytes for each message depends on its type:

- **Enum**: 1 byte
- **Variable**: 2 bytes
- **LongVariable**: 4 bytes
- **Structure**: All remaining bytes (until CRC)

```python
# Parse messages
messages = []
offset = 16  # Start after header

for i in range(capacity):
    msg_num = data[offset] * 256 + data[offset + 1]
    msg_type = (msg_num & 0x0600) >> 9

    if msg_type == 0:  # Enum
        payload = data[offset + 2:offset + 3]
        offset += 3
    elif msg_type == 1:  # Variable
        payload = data[offset + 2:offset + 4]
        offset += 4
    elif msg_type == 2:  # LongVariable
        payload = data[offset + 2:offset + 6]
        offset += 6
    elif msg_type == 3:  # Structure
        # Rest of data until CRC
        payload = data[offset + 2:-3]
        offset = len(data) - 3

    messages.append((msg_num, payload))
```

### CRC (Cyclic Redundancy Check)

The last 3 bytes before end marker contain CRC and end marker:

```python
crc_high = data[-3]
crc_low = data[-2]
end_marker = data[-1]  # Should be 0x34

crc_16 = crc_high * 256 + crc_low

# CRC algorithm (CRC-16-CCITT)
# Implementation specific to NASA protocol
```

## Complete Parsing Example

```python
def parse_nasa_packet(data: bytes):
    """Parse a complete NASA packet."""

    if data[0] != 0x32:
        raise ValueError("Invalid packet start")
    if data[-1] != 0x34:
        raise ValueError("Invalid packet end")

    # Header
    size = data[1] | (data[2] << 8)
    src_class, src_chan, src_addr = data[3], data[4], data[5]
    dst_class, dst_chan, dst_addr = data[6], data[7], data[8]

    # Info byte
    packet_info = (data[9] & 0x80) >> 7
    protocol_ver = (data[9] & 0x60) >> 5
    retry_count = (data[9] & 0x18) >> 3

    # Type byte
    packet_type = (data[10] & 0xF0) >> 4
    data_type = data[10] & 0x0F
    packet_num = data[11]

    # Messages
    capacity = data[12]
    messages = []
    offset = 13

    for i in range(capacity):
        msg_num = data[offset] * 256 + data[offset + 1]
        msg_type = (msg_num & 0x0600) >> 9

        if msg_type == 0:
            payload = data[offset + 2:offset + 3]
            offset += 3
        elif msg_type == 1:
            payload = data[offset + 2:offset + 4]
            offset += 4
        elif msg_type == 2:
            payload = data[offset + 2:offset + 6]
            offset += 6
        elif msg_type == 3:
            payload = data[offset + 2:len(data) - 3]
            offset = len(data) - 3

        messages.append({
            'number': msg_num,
            'type': msg_type,
            'payload': payload
        })

    # CRC
    crc = data[-3] * 256 + data[-2]

    return {
        'source': f'{src_class:02X}{src_chan:02X}{src_addr:02X}',
        'destination': f'{dst_class:02X}{dst_chan:02X}{dst_addr:02X}',
        'packet_type': packet_type,
        'data_type': data_type,
        'messages': messages,
        'crc': crc
    }
```

## Building a Packet

To send a packet:

```python
def build_nasa_packet(
    source: str,          # e.g., "800001"
    destination: str,     # e.g., "100000"
    messages: list,       # [(msg_num, payload), ...]
    packet_type: int = 1, # Normal
    data_type: int = 3,   # Request
):
    """Build a NASA packet."""

    # Parse addresses
    src_class = int(source[0:2], 16)
    src_chan = int(source[2:4], 16)
    src_addr = int(source[4:6], 16)

    dst_class = int(destination[0:2], 16)
    dst_chan = int(destination[2:4], 16)
    dst_addr = int(destination[4:6], 16)

    # Build header
    packet = bytearray()
    packet.append(0x32)  # STX

    # Size placeholder (will update later)
    size_offset = len(packet)
    packet.append(0x00)
    packet.append(0x00)

    # Addresses
    packet.append(src_class)
    packet.append(src_chan)
    packet.append(src_addr)
    packet.append(dst_class)
    packet.append(dst_chan)
    packet.append(dst_addr)

    # Info byte
    packet.append(0x20)  # Protocol version 1

    # Type byte
    packet.append((packet_type << 4) | data_type)

    # Packet number
    packet.append(0x01)  # Placeholder

    # Capacity
    packet.append(len(messages))

    # Messages
    for msg_num, payload in messages:
        packet.append((msg_num >> 8) & 0xFF)
        packet.append(msg_num & 0xFF)
        packet.extend(payload)

    # CRC (placeholder)
    crc = calculate_crc(packet)
    packet.extend([
        (crc >> 8) & 0xFF,
        crc & 0xFF
    ])

    # ETX
    packet.append(0x34)

    # Update size
    size = len(packet) - 3  # Excluding STX and size field
    packet[size_offset] = size & 0xFF
    packet[size_offset + 1] = (size >> 8) & 0xFF

    return bytes(packet)
```

## Notes

- All multi-byte values are in **little-endian** format unless otherwise noted
- The CRC algorithm is **CRC-16-CCITT**
- Packet numbers wrap around from 0-255
- Messages within a packet are processed in order
- Structure messages consume all remaining payload bytes
