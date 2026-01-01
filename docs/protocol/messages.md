# Message Types

Reference for NASA protocol message types and their formats.

## Message Type System

Messages in the NASA protocol are identified by a **Message Number** - a 16-bit value that encodes both the message identity and its payload structure.

### Message Structure

The upper 2 bits of the message number define the payload type:

```
Message Number: 0xMMSS
               └──┬──┘
                  └─ S = Size type (bits 9-8)
                     M = Message ID (rest of bits)
```

**Size Types:**

| Value | Type | Size | Description |
|-------|------|------|-------------|
| 0 | Enum | 1 byte | Boolean or enumeration value (0-255) |
| 1 | Variable | 2 bytes | 16-bit unsigned integer (0-65535) |
| 2 | LongVariable | 4 bytes | 32-bit unsigned integer |
| 3 | Structure | Variable | Complex structured data |

## Common Message Categories

### Power & Operation (0x4000 range)

#### 0x4000 - Power Control
**Type:** Enum (1 byte)
**Values:** 0=Off, 1=On, 2=On (alt)

```python
# Turn on
SendMessage(0x4000, b'\x01')

# Turn off
SendMessage(0x4000, b'\x00')
```

#### 0x4001 - Operation Mode
**Type:** Enum (1 byte)
**Values:** 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat, 21=Cool Storage, 24=Hot Water

```python
# Set to cool mode
SendMessage(0x4001, b'\x01')

# Set to heat mode
SendMessage(0x4001, b'\x04')
```

#### 0x4002 - Real Operation Mode (Read-only)
**Type:** Enum (1 byte)
Returns the actual current mode the unit is operating in.

### Fan Control (0x4000 range)

#### 0x4006 - Fan Speed
**Type:** Enum (1 byte)
**Values:** 0=Off, 1=Low, 2=Mid, 3=High, 4=Very High

```python
# Set fan to high speed
SendMessage(0x4006, b'\x03')
```

#### 0x4008 - Fan Speed Real
**Type:** Enum (1 byte)
Read-only actual fan speed.

#### 0x4011 - Air Swing Up/Down
**Type:** Enum (1 byte)
**Values:** 0=Off, 1=Up, 2=Middle, 3=Down, 4=Swing

### Temperature Values (0x4200-0x4240)

#### 0x4201 - Target Temperature
**Type:** Variable (2 bytes)
**Encoding:** Integer value * 10, big-endian

```python
# Set target to 22°C
temp_c = 22
payload = int(temp_c * 10).to_bytes(2, 'big')
SendMessage(0x4201, payload)

# Set target to 72°F
temp_f = 72
# First convert F to C or use directly if unit supports F
payload = int(temp_f * 10).to_bytes(2, 'big')
SendMessage(0x4201, payload)
```

#### 0x4203 - Current Temperature
**Type:** Variable (2 bytes)
**Encoding:** Integer value * 10, big-endian
Read-only.

```python
# Reading example (automatically parsed)
current_temp_raw = int.from_bytes(payload, 'big')
current_temp_c = current_temp_raw / 10
```

#### 0x4238 - Water Outlet Temperature
**Type:** Variable (2 bytes)
Water outlet temperature (for water-based systems).

#### 0x4248 - Water Law Target Temperature
**Type:** Variable (2 bytes)
Target temperature for water law heating mode.

### Humidity Control (0x4030-0x4040)

#### 0x4038 - Current Humidity
**Type:** Enum (1 byte)
**Range:** 0-100 (percentage)
Read-only.

### Status Messages (0x8000+ range)

#### 0x8001 - Outdoor Operation Status
**Type:** Enum (1 byte)
Reflects outdoor unit operation status in indoor units.

#### 0x8003 - Outdoor Operation Mode
**Type:** Enum (1 byte)
Reflects outdoor unit operation mode in indoor units.

#### 0x8061 - Some Status (Implementation dependent)

### Error Codes (0x0200 range)

#### 0x0202 - Error Code 1
**Type:** Variable (2 bytes)
Error code from outdoor unit.

#### 0x0203-0x0206 - Error Codes 2-5
Similar error codes.

### Device Configuration (0x0600 range)

#### 0x0600 - Product Options
**Type:** Structure
Basic device configuration and capabilities.

#### 0x0601 - Installation Options
**Type:** Structure
Installation settings.

#### 0x0605 - Device Position/Name
**Type:** Structure
Device location information.

#### 0x0607 - Serial Number
**Type:** Structure
Device serial number.

#### 0x060C - EEPROM Code Version
**Type:** Structure
EEPROM database version.

### Installation Count (0x0200 range)

#### 0x0207 - Indoor Unit Count
**Type:** Variable (2 bytes)
Number of indoor units connected.

#### 0x0208 - ERV Unit Count
**Type:** Variable (2 bytes)

#### 0x0209 - EHS Unit Count
**Type:** Variable (2 bytes)

#### 0x0211 - MCU Count
**Type:** Variable (2 bytes)
Number of connected MCUs.

### Power Consumption (0x0400 range)

#### 0x0406 - Total Power Consumption
**Type:** LongVariable (4 bytes)
**Encoding:** Watts, big-endian

```python
# Reading example
power_w = int.from_bytes(payload, 'big')
```

#### 0x0407 - Cumulative Power Consumption
**Type:** LongVariable (4 bytes)
**Encoding:** kWh or Wh (implementation-dependent)

#### 0x041C-0x0423 - Channel Power Values
**Type:** LongVariable (4 bytes) each
Individual channel power consumption.

### Water Heater Control (Indoor units)

#### 0x4065 - DHW Power
**Type:** Enum (1 byte)
**Values:** 0=Off, 1=On

#### 0x4066 - DHW Operation Mode
**Type:** Enum (1 byte)
Hot water operation mode.

#### 0x4235 - DHW Target Temperature
**Type:** Variable (2 bytes)
Hot water target temperature * 10.

#### 0x4237 - DHW Current Temperature
**Type:** Variable (2 bytes)
Hot water current temperature * 10.

### Network & Addressing (0x0400 range)

#### 0x0401 - Main Address
**Type:** LongVariable (4 bytes)
Primary device address.

#### 0x0402 - RMC Address
**Type:** LongVariable (4 bytes)
Remote controller address.

#### 0x0408 - Setup Address
**Type:** LongVariable (4 bytes)

## Message Discovery

Find all messages for a specific device:

```python
def list_device_messages(device):
    """List all messages received from a device."""
    for msg_id, attribute in device.attributes.items():
        print(f"0x{msg_id:04X}: {attribute}")

list_device_messages(nasa.devices["100000"])
```

## Decoding Message Payloads

```python
def decode_message(msg_number: int, payload: bytes) -> object:
    """Decode a message payload based on its type."""

    msg_type = (msg_number & 0x0600) >> 9

    if msg_type == 0:  # Enum
        return payload[0]

    elif msg_type == 1:  # Variable (2 bytes)
        return int.from_bytes(payload, 'big')

    elif msg_type == 2:  # LongVariable (4 bytes)
        return int.from_bytes(payload, 'big')

    elif msg_type == 3:  # Structure
        return payload  # Raw bytes

    return None

# Example: Decode temperature
temp_raw = decode_message(0x4203, payload)
temp_c = temp_raw / 10
```

## Known Message Ranges

Refer to the NOTES.md file in the project repository for a comprehensive table of all known message numbers.

## Extended Messages

The library supports newer S-Net protocol messages that extend the original NASA protocol with additional device types and capabilities.

### Modern Message Ranges (S-Net)

- **0x2000-0x2FFF** - Network layer messages
- **0x4000-0x7FFF** - Device operation (extended)
- **0x8000-0xBFFF** - Nested message structures

## Next Steps

- Read [Protocol Overview](overview.md)
- Study [Packet Structure](packet-structure.md)
- Explore [Message Factory](message-factory.md)
