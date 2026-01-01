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

### Outdoor Unit Attributes

```python
outdoor = nasa.devices["100000"]

# Temperature
outdoor.outdoor_temperature         # Outdoor air temperature (°C)
outdoor.water_outlet_temperature    # Water outlet temp (°C)

# Power
outdoor.power_consumption           # Instantaneous power (W)
outdoor.power_current               # Current draw (A)
outdoor.power_produced              # Power produced (W)
outdoor.power_generated_last_minute # Power in last minute (W)
outdoor.cumulative_energy           # Total energy (kWh)

# Performance
outdoor.cop_rating                  # Efficiency rating
outdoor.compressor_frequency        # Compressor speed (Hz)
outdoor.fan_speed                   # Fan speed (RPM)

# Status
outdoor.heatpump_voltage           # Operating voltage (V)
```

### Indoor Unit Attributes

```python
indoor = nasa.devices["200020"]

# Check if controllers are available
has_climate = indoor.climate_controller is not None
has_dhw = indoor.dhw_controller is not None

# Climate control
if has_climate:
    cc = indoor.climate_controller
    cc.power                       # On/off status
    cc.current_mode                # Current mode (cool, heat, etc)
    cc.f_current_temperature       # Current room temp (°C)
    cc.f_target_temperature        # Target temp (°C)
    cc.current_humidity            # Humidity (%)
    cc.current_fan_mode            # Fan mode
    cc.current_fan_speed           # Fan speed (1-4)

# DHW control
if has_dhw:
    dhw = indoor.dhw_controller
    dhw.power                      # On/off status
    dhw.target_temperature         # Target temp (°C)
    dhw.current_temperature        # Current temp (°C)
    dhw.operation_mode             # Operating mode
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

# Request configuration
await device.get_configuration()
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

Register functions to be called when device data changes:

```python
def on_update(device):
    print(f"Device {device.address} updated at {device.last_packet_time}")

device = nasa.devices["100000"]
device.add_device_callback(on_update)

# Later, remove it
device.remove_device_callback(on_update)
```

### Message-Specific Callbacks

Listen for specific message types:

```python
def on_temp_message(device, **kwargs):
    message = kwargs['packet']
    print(f"Temperature update: {message.VALUE}")

indoor = nasa.devices["200020"]

# Add callback for message 0x4203 (current temp)
indoor.add_packet_callback(0x4203, on_temp_message)

# Later, remove it
indoor.remove_packet_callback(0x4203, on_temp_message)
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
def check_attributes(device):
    """Verify expected attributes exist."""
    expected = {0x4203: "Current Temperature", 0x4201: "Target Temperature"}

    for msg_id, name in expected.items():
        if msg_id in device.attributes:
            print(f"✓ {name} present")
        else:
            print(f"✗ {name} MISSING")

    # Request configuration to fill missing values
    if len(device.attributes) < len(expected):
        print("Requesting configuration...")
        await device.get_configuration()

await check_attributes(indoor)
```

## Next Steps

- Learn how to control devices with [Controllers](controllers.md)
- Read about [Basic Usage](basic-usage.md)
- Check the [API Reference](../api/nasa-device.md)
