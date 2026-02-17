# Device Management

Manage and interact with discovered and known Samsung HVAC devices.

## Device Types

### NasaDevice

The base class for all devices:

```python
device = nasa.devices["100000"]

print(device.address)           # Device address (string)
print(device.device_type)       # Device type (AddressClass enum)
print(device.last_packet_time)  # Last update time
print(device.attributes)        # All attributes dict
print(device.config)            # Configuration object
```

### OutdoorNasaDevice

Represents outdoor units (typically address `100000`):

```python
outdoor = nasa.devices["100000"]

# Check if it's an outdoor device
if isinstance(outdoor, OutdoorNasaDevice):
    # Access outdoor-specific attributes
    print(outdoor.outdoor_temperature)
    print(outdoor.power_consumption)
```

### IndoorNasaDevice

Represents indoor units (typically addresses `200020`, `200021`, etc.):

```python
indoor = nasa.devices["200020"]

# Check if it's an indoor device
if isinstance(indoor, IndoorNasaDevice):
    # Access indoor-specific attributes
    if indoor.climate_controller:
        print(indoor.climate_controller.current_mode)
    if indoor.dhw_controller:
        print(indoor.dhw_controller.target_temperature)
```

## Discovering Devices

### Automatic Discovery

When you start the connection, devices advertise themselves:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={"client_address": 1}
)

await nasa.start()

# Wait for devices to appear
await asyncio.sleep(2)

# List discovered devices
for address, device in nasa.devices.items():
    print(f"{address}: {device.device_type}")
```

### Known Devices

Pre-configure devices you want to monitor:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={
        "client_address": 1,
        "device_addresses": ["200000", "200020"]
    }
)

await nasa.start()

# Devices will be immediately available
outdoor = nasa.devices["100000"]
indoor = nasa.devices["200020"]
```

### New Device Handler

Get notified when new devices appear:

```python
async def on_new_device(device):
    print(f"New device found: {device.address}")
    print(f"Type: {device.device_type}")

    # Request its configuration
    await device.get_configuration()

nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={"client_address": 1},
    new_device_event_handler=on_new_device
)

await nasa.start()
```

## Device Attributes

### Universal Attributes

All devices have:

```python
device = nasa.devices["100000"]

device.address           # Address string (e.g., "100000")
device.device_type      # AddressClass enum
device.last_packet_time # datetime of last update
device.attributes       # Dict of all attributes
device.config           # NasaConfig object
device.fsv_config       # FSV configuration dict
```

## Reading Device Attributes

### Using get_attribute()

Read specific attributes from a device. If the attribute isn't cached, it will be automatically requested:

```python
from pysamsungnasa.protocol.factory.messages.outdoor import (
    OutdoorAirTemperature,
    HeatPumpVoltage,
    OutdoorCompressorFrequency
)
from pysamsungnasa.protocol.factory.messages.indoor import (
    InTargetTemperature,
    InCurrentTemperature,
    InOperationPowerMessage
)

outdoor = nasa.devices["100000"]

# Read outdoor temperature (will fetch if not cached)
temp_msg = await outdoor.get_attribute(OutdoorAirTemperature)
print(f"Outdoor temperature: {temp_msg.VALUE}°C")

# Read voltage
voltage_msg = await outdoor.get_attribute(HeatPumpVoltage)
print(f"Voltage: {voltage_msg.VALUE}V")

# Force a fresh read even if cached
freq_msg = await outdoor.get_attribute(
    OutdoorCompressorFrequency,
    requires_read=True
)
print(f"Compressor frequency: {freq_msg.VALUE}Hz")
```

### Reading Indoor Unit Attributes

```python
indoor = nasa.devices["200020"]

# Get current temperature
current_temp = await indoor.get_attribute(InCurrentTemperature)
print(f"Current temperature: {current_temp.VALUE}°C")

# Get target temperature
target_temp = await indoor.get_attribute(InTargetTemperature)
print(f"Target temperature: {target_temp.VALUE}°C")

# Get power state
power = await indoor.get_attribute(InOperationPowerMessage)
print(f"Power: {power.VALUE}")
```

### Accessing Cached Attributes

Access previously received attributes directly from the cache:

```python
device = nasa.devices["100000"]

# Check if attribute exists in cache
if OutdoorAirTemperature.MESSAGE_ID in device.attributes:
    cached_msg = device.attributes[OutdoorAirTemperature.MESSAGE_ID]
    print(f"Cached temperature: {cached_msg.VALUE}°C")
else:
    print("Temperature not yet received")

# Or use get_attribute which handles this automatically
temp_msg = await device.get_attribute(OutdoorAirTemperature)
print(f"Temperature: {temp_msg.VALUE}°C")
```

## Writing Device Attributes

### Using write_attribute()

Write a single attribute to a device:

```python
from pysamsungnasa.protocol.factory.messages.indoor import (
    InTargetTemperature,
    InOperationPowerMessage,
    InOperationModeMessage,
    InFanSpeedMessage
)
from pysamsungnasa.protocol.enum import DataType

indoor = nasa.devices["200020"]

# Set target temperature to 22°C
await indoor.write_attribute(InTargetTemperature, 22.0)

# Turn on the device
await indoor.write_attribute(InOperationPowerMessage, 1)  # 1 = On, 0 = Off

# Set operation mode
from pysamsungnasa.protocol.enum import InOperationMode
await indoor.write_attribute(InOperationModeMessage, InOperationMode.COOL)

# Set fan speed (1-4)
await indoor.write_attribute(InFanSpeedMessage, 3)
```

### Using write_attributes()

Write multiple attributes in a single packet (up to 10 messages):

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
    InOperationModeMessage: InOperationMode.COOL,  # Set to cooling mode
    InTargetTemperature: 22.0,  # Set temperature
    InFanSpeedMessage: 3,  # Set fan speed
})
```

### Using Different Write Modes

Some attributes require a REQUEST mode instead of WRITE:

```python
from pysamsungnasa.protocol.enum import DataType

# Some messages may require DataType.REQUEST
await indoor.write_attribute(
    InTargetTemperature,
    22.0,
    mode=DataType.REQUEST
)

# Default is DataType.WRITE
await indoor.write_attribute(InTargetTemperature, 22.0)  # Uses WRITE mode
```

## Accessing Device Configuration

Get the FSV (Feature/Setting/Value) configuration:

```python
device = nasa.devices["200020"]

# Get all FSV settings
fsv_config = device.fsv_config

# FSV is a dictionary of message ID to values
for msg_id, value in fsv_config.items():
    print(f"Message 0x{msg_id:04X}: {value}")
```

## Device State Management

### Getting Raw Attributes

Access the raw attribute dictionary:

```python
device = nasa.devices["100000"]

# Get all attributes
all_attrs = device.attributes
print(f"Total attributes: {len(all_attrs)}")

# Access a specific attribute by message ID
if 0x4203 in device.attributes:
    value = device.attributes[0x4203]
    print(f"Message 0x4203: {value}")
```

### Checking Last Update

Monitor device responsiveness:

```python
import time
from datetime import datetime, timezone

device = nasa.devices["100000"]

# Check when last updated
if device.last_packet_time:
    elapsed = datetime.now(timezone.utc) - device.last_packet_time
    print(f"Last update: {elapsed.total_seconds():.1f} seconds ago")
else:
    print("No data yet")
```

## Device Callbacks

### Device Update Callbacks

Register functions to be called whenever any packet is received for a device:

```python
def on_update(device):
    print(f"Device {device.address} updated at {device.last_packet_time}")
    print(f"Total attributes: {len(device.attributes)}")

device = nasa.devices["100000"]
device.add_device_callback(on_update)

# Later, remove it
device.remove_device_callback(on_update)
```

### Message-Specific Callbacks

Listen for specific message types using packet callbacks:

```python
from pysamsungnasa.protocol.factory.messages.indoor import InCurrentTemperature
from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorAirTemperature

def on_indoor_temp(device, **kwargs):
    """Called when indoor temperature message is received."""
    message = kwargs['packet']
    msg_number = kwargs['messageNumber']
    print(f"Indoor temp update: {message.VALUE}°C (msg {msg_number})")

def on_outdoor_temp(device, **kwargs):
    """Called when outdoor temperature message is received."""
    message = kwargs['packet']
    print(f"Outdoor temp: {message.VALUE}°C")

indoor = nasa.devices["200020"]
outdoor = nasa.devices["100000"]

# Add callback for specific message type
indoor.add_packet_callback(InCurrentTemperature, on_indoor_temp)
outdoor.add_packet_callback(OutdoorAirTemperature, on_outdoor_temp)

# Later, remove them
indoor.remove_packet_callback(InCurrentTemperature, on_indoor_temp)
outdoor.remove_packet_callback(OutdoorAirTemperature, on_outdoor_temp)
```

### Complete Example with Callbacks

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.indoor import (
    InCurrentTemperature,
    InTargetTemperature
)

async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    def on_temp_change(device, **kwargs):
        message = kwargs['packet']
        print(f"Temperature changed to {message.VALUE}°C")

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    indoor = nasa.devices["200020"]
    
    # Listen for temperature changes
    indoor.add_packet_callback(InCurrentTemperature, on_temp_change)

    # Set new target temperature
    await indoor.write_attribute(InTargetTemperature, 23.0)

    # Keep running to receive updates
    await asyncio.sleep(60)
    await nasa.stop()

asyncio.run(main())
```

## Multiple Device Management

### Iterate Over All Devices

```python
for address, device in nasa.devices.items():
    print(f"\nDevice: {address}")
    print(f"  Type: {device.device_type}")
    print(f"  Last update: {device.last_packet_time}")

    # Register callbacks
    device.add_device_callback(lambda d: print(f"  Updated: {d.address}"))
```

### Find Devices by Type

```python
from pysamsungnasa.device import OutdoorNasaDevice, IndoorNasaDevice

outdoor_units = [d for d in nasa.devices.values() if isinstance(d, OutdoorNasaDevice)]
indoor_units = [d for d in nasa.devices.values() if isinstance(d, IndoorNasaDevice)]

print(f"Outdoor units: {len(outdoor_units)}")
print(f"Indoor units: {len(indoor_units)}")
```

### Synchronize Multiple Devices

```python
async def set_all_targets(nasa, temperature):
    """Set target temperature on all indoor units."""
    for device in nasa.devices.values():
        if isinstance(device, IndoorNasaDevice):
            if device.climate_controller:
                await device.climate_controller.set_target_temperature(temperature)
                print(f"Set {device.address} to {temperature}°C")
```

## Device Information Display

### Print Device Summary

```python
def print_device_summary(device):
    print(f"Device: {device.address}")
    print(f"  Type: {device.device_type}")
    print(f"  Attributes: {len(device.attributes)}")
    print(f"  Last update: {device.last_packet_time}")

    if hasattr(device, 'outdoor_temperature'):
        print(f"  Outdoor temp: {device.outdoor_temperature}°C")

    if hasattr(device, 'climate_controller') and device.climate_controller:
        cc = device.climate_controller
        print(f"  Climate power: {cc.power}")
        print(f"  Current mode: {cc.current_mode}")
        print(f"  Target temp: {cc.f_target_temperature}°C")

for device in nasa.devices.values():
    print_device_summary(device)
    print()
```

## Troubleshooting Device Issues

### Device Not Responding

```python
async def check_device_health(device):
    """Check if a device is responding."""
    if device.last_packet_time is None:
        print(f"{device.address}: Never received data")
        return False

    from datetime import datetime, timezone, timedelta
    elapsed = datetime.now(timezone.utc) - device.last_packet_time

    if elapsed > timedelta(minutes=5):
        print(f"{device.address}: No update for {elapsed.total_seconds():.0f}s")
        return False

    print(f"{device.address}: OK (updated {elapsed.total_seconds():.0f}s ago)")
    return True

for device in nasa.devices.values():
    await check_device_health(device)
```

### Missing Attributes

```python
from pysamsungnasa.protocol.factory.messages.indoor import (
    InCurrentTemperature,
    InTargetTemperature
)

async def check_attributes(device):
    """Verify expected attributes exist and request if missing."""
    try:
        # Try to get current temperature (will fetch if not cached)
        current = await device.get_attribute(InCurrentTemperature)
        print(f"✓ Current Temperature: {current.VALUE}°C")
    except TimeoutError:
        print("✗ Current Temperature: TIMEOUT")

    try:
        # Try to get target temperature
        target = await device.get_attribute(InTargetTemperature)
        print(f"✓ Target Temperature: {target.VALUE}°C")
    except TimeoutError:
        print("✗ Target Temperature: TIMEOUT")

    # Check cached attributes
    print(f"\nTotal cached attributes: {len(device.attributes)}")

await check_attributes(indoor)
```

## Next Steps

- Learn how to control devices with [Controllers](controllers.md)
- Read about [Basic Usage](basic-usage.md)
- Check the [API Reference](../api/nasa-device.md)
