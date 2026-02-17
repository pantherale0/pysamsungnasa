# Basic Usage

Learn how to use pysamsungnasa to communicate with your Samsung HVAC units.

## Core Concepts

### The NASA Protocol

The NASA protocol is Samsung's proprietary protocol for HVAC communication:

- **Packet-based** - Data is sent as packets with start/end markers
- **Addressed** - Each device has a unique address on the network
- **Bidirectional** - Devices can send requests and receive responses
- **Asynchronous** - Uses async/await for non-blocking I/O

### Components

1. **SamsungNasa** - Main entry point, manages connections and devices
2. **NasaClient** - Low-level TCP client for protocol communication
3. **NasaDevice** - Represents a single device and its attributes
4. **Controllers** - Control specific functions (Climate, DHW)
5. **NasaPacketParser** - Parses incoming NASA protocol packets

## Working with SamsungNasa

### Initialization

Create a SamsungNasa instance:

```python
from pysamsungnasa import SamsungNasa

nasa = SamsungNasa(
    host="192.168.1.100",           # IP address of NASA adapter
    port=8000,                       # NASA protocol port
    config={
        "client_address": 1,         # Your address on network
        "device_addresses": [],      # Known devices (optional)
    },
    new_device_event_handler=None,   # Callback for new devices (optional)
    disconnect_event_handler=None,   # Callback on disconnect (optional)
)
```

### Starting and Stopping

```python
# Connect to the unit
await nasa.start()

# ... do work ...

# Disconnect
await nasa.stop()
```

### Device Management

```python
# Get all devices
devices = nasa.devices
# Output: {"200000": NasaDevice, "200020": NasaDevice, ...}

# Get a specific device
outdoor = nasa.devices["100000"]
indoor = nasa.devices["200020"]

# List all device addresses
for address in nasa.devices:
    print(address)
```

## Working with Devices

### Device Attributes

Each device has attributes that represent its current state:

```python
device = nasa.devices["100000"]

# Access attributes
print(device.address)              # Device address string
print(device.device_type)          # AddressClass enum
print(device.last_packet_time)     # Last update timestamp
print(device.attributes)           # All attributes dict
print(device.config)               # Configuration object
```

### Reading Outdoor Unit Attributes

Use `get_attribute()` to read specific data from outdoor units:

```python
from pysamsungnasa.protocol.factory.messages.outdoor import (
    OutdoorAirTemperature,
    HeatPumpVoltage,
    OutdoorCompressorFrequency,
    OutdoorPowerConsumption,
    OutdoorPowerCurrent
)

outdoor = nasa.devices["100000"]

# Read temperature (automatically fetches if not cached)
temp_msg = await outdoor.get_attribute(OutdoorAirTemperature)
print(f"Outdoor temperature: {temp_msg.VALUE}°C")

# Read power consumption
power_msg = await outdoor.get_attribute(OutdoorPowerConsumption)
print(f"Power: {power_msg.VALUE}W")

# Read current draw
current_msg = await outdoor.get_attribute(OutdoorPowerCurrent)
print(f"Current: {current_msg.VALUE}A")

# Read compressor frequency
freq_msg = await outdoor.get_attribute(OutdoorCompressorFrequency)
print(f"Compressor: {freq_msg.VALUE}Hz")

# Read voltage
voltage_msg = await outdoor.get_attribute(HeatPumpVoltage)
print(f"Voltage: {voltage_msg.VALUE}V")
```

### Reading Indoor Unit Attributes

Read data from indoor (climate) units:

```python
from pysamsungnasa.protocol.factory.messages.indoor import (
    InCurrentTemperature,
    InTargetTemperature,
    InOperationPowerMessage,
    InOperationModeMessage,
    InFanSpeedMessage
)

indoor = nasa.devices["200020"]

# Read current temperature
current_temp = await indoor.get_attribute(InCurrentTemperature)
print(f"Current: {current_temp.VALUE}°C")

# Read target temperature  
target_temp = await indoor.get_attribute(InTargetTemperature)
print(f"Target: {target_temp.VALUE}°C")

# Read power state
power = await indoor.get_attribute(InOperationPowerMessage)
print(f"Power: {power.VALUE}")

# Read operation mode
mode = await indoor.get_attribute(InOperationModeMessage)
print(f"Mode: {mode.VALUE}")

# Force a fresh read (bypass cache)
fresh_temp = await indoor.get_attribute(
    InCurrentTemperature,
    requires_read=True
)
print(f"Fresh temperature: {fresh_temp.VALUE}°C")
```

## Callbacks and Events

### Device Callbacks

Get notified whenever any packet is received for a device:

```python
def on_device_changed(device):
    print(f"Device {device.address} was updated!")
    print(f"  Last update: {device.last_packet_time}")
    print(f"  Total attributes: {len(device.attributes)}")

device = nasa.devices["100000"]
device.add_device_callback(on_device_changed)

# Later, remove the callback
device.remove_device_callback(on_device_changed)
```

### Packet Callbacks

Listen for specific message types:

```python
from pysamsungnasa.protocol.factory.messages.indoor import InCurrentTemperature
from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorAirTemperature

def on_indoor_temp_changed(device, **kwargs):
    message = kwargs['packet']
    msg_number = kwargs['messageNumber']
    print(f"Indoor temp: {message.VALUE}°C (msg {msg_number})")

def on_outdoor_temp_changed(device, **kwargs):
    message = kwargs['packet']
    print(f"Outdoor temp: {message.VALUE}°C")

indoor = nasa.devices["200020"]
outdoor = nasa.devices["100000"]

# Add callbacks for specific message types
indoor.add_packet_callback(InCurrentTemperature, on_indoor_temp_changed)
outdoor.add_packet_callback(OutdoorAirTemperature, on_outdoor_temp_changed)

# Later, remove them
indoor.remove_packet_callback(InCurrentTemperature, on_indoor_temp_changed)
outdoor.remove_packet_callback(OutdoorAirTemperature, on_outdoor_temp_changed)
```

### New Device Handler

Handle newly discovered devices:

```python
async def on_new_device(device):
    print(f"New device discovered: {device.address}")
    print(f"Type: {device.device_type}")

nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={"client_address": 1},
    new_device_event_handler=on_new_device
)
```

### Disconnect Handler

Handle connection loss:

```python
async def on_disconnect():
    print("Connection lost! Attempting to reconnect...")

nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={"client_address": 1},
    disconnect_event_handler=on_disconnect
)
```

## Sending Commands

### Writing Single Attributes

Use `write_attribute()` to write a single value to a device:

```python
from pysamsungnasa.protocol.factory.messages.indoor import (
    InTargetTemperature,
    InOperationPowerMessage,
    InOperationModeMessage,
    InFanSpeedMessage
)
from pysamsungnasa.protocol.enum import InOperationMode

indoor = nasa.devices["200020"]

# Set target temperature
await indoor.write_attribute(InTargetTemperature, 22.0)

# Turn on the device
await indoor.write_attribute(InOperationPowerMessage, 1)  # 1=On, 0=Off

# Set cooling mode
await indoor.write_attribute(InOperationModeMessage, InOperationMode.COOL)

# Set fan speed (1-4)
await indoor.write_attribute(InFanSpeedMessage, 3)
```

### Writing Multiple Attributes

Use `write_attributes()` to write multiple values in a single packet (up to 10):

```python
from pysamsungnasa.protocol.factory.messages.indoor import (
    InTargetTemperature,
    InOperationPowerMessage,
    InOperationModeMessage,
    InFanSpeedMessage
)
from pysamsungnasa.protocol.enum import InOperationMode

indoor = nasa.devices["200020"]

# Set multiple attributes at once
await indoor.write_attributes({
    InOperationPowerMessage: 1,  # Turn on
    InOperationModeMessage: InOperationMode.COOL,  # Cooling
    InTargetTemperature: 22.0,  # Temperature
    InFanSpeedMessage: 3,  # Fan speed
})
```

### Using Controllers (Alternative)

For convenience, you can also use device controllers if available:

```python
indoor = nasa.devices["200020"]

# Climate control (if controller exists)
if indoor.climate_controller:
    cc = indoor.climate_controller
    
    # Power commands
    await cc.turn_on()
    await cc.turn_off()
    
    # Mode (auto, cool, heat, dry, fan)
    await cc.set_operation_mode("cool")
    
    # Temperature
    await cc.set_target_temperature(22.0)
    
    # Fan
    await cc.set_fan_speed(3)

# DHW control (if controller exists)
if indoor.dhw_controller:
    dhw = indoor.dhw_controller
    
    await dhw.turn_on()
    await dhw.turn_off()
    await dhw.set_target_temperature(45.0)
```

### Using Different Write Modes

Some operations may require `DataType.REQUEST` instead of the default `DataType.WRITE`:

```python
from pysamsungnasa.protocol.enum import DataType

# Use REQUEST mode
await indoor.write_attribute(
    InTargetTemperature,
    22.0,
    mode=DataType.REQUEST
)

# Default is WRITE mode
await indoor.write_attribute(InTargetTemperature, 22.0)
```

## Error Handling

Always handle potential errors:

```python
async def safe_control():
    try:
        indoor = nasa.devices["200020"]
        await indoor.climate_controller.set_target_temperature(22)
    except KeyError:
        print("Device not found!")
    except Exception as e:
        print(f"Error sending command: {e}")
```

## Common Patterns

### Monitor Device Changes

```python
import asyncio
from pysamsungnasa import SamsungNasa

async def monitor():
    def log_changes(device):
        print(f"[{device.last_packet_time}] {device.address} updated")
        print(f"  Attributes: {len(device.attributes)}")

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    for device in nasa.devices.values():
        device.add_device_callback(log_changes)

    # Monitor for 60 seconds
    await asyncio.sleep(60)
    await nasa.stop()
```

### Read and Display Data

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.outdoor import (
    OutdoorAirTemperature,
    OutdoorPowerConsumption,
    OutdoorCompressorFrequency
)

async def read_outdoor_data():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    outdoor = nasa.devices["100000"]

    # Read multiple attributes
    temp = await outdoor.get_attribute(OutdoorAirTemperature)
    power = await outdoor.get_attribute(OutdoorPowerConsumption)
    freq = await outdoor.get_attribute(OutdoorCompressorFrequency)

    print(f"Temperature: {temp.VALUE}°C")
    print(f"Power: {power.VALUE}W")
    print(f"Compressor: {freq.VALUE}Hz")

    await nasa.stop()
```

### Polling for Data

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorAirTemperature

async def poll_every_30_seconds():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    try:
        outdoor = nasa.devices["100000"]
        while True:
            # Force fresh read
            temp = await outdoor.get_attribute(
                OutdoorAirTemperature,
                requires_read=True
            )
            print(f"\n=== Current Status ===")
            print(f"Temperature: {temp.VALUE}°C")
            await asyncio.sleep(30)
    finally:
        await nasa.stop()
```

### Controlled Shutdown

```python
async def graceful_shutdown():
    nasa = SamsungNasa(...)

    try:
        await nasa.start()
        # Your code
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await nasa.stop()
        print("Cleanup complete")
```

## Next Steps

- Learn more about [Configuration](configuration.md)
- Explore [Device Management](device-management.md)
- Read about [Controllers](controllers.md)
- Check the [API Reference](../api/samsung-nasa.md)
