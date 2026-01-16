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

### Outdoor Unit Attributes

Access data from outdoor units:

```python
outdoor = nasa.devices["100000"]

# Temperature
outdoor_temp = outdoor.outdoor_temperature  # °C
water_outlet_temp = outdoor.water_outlet_temperature  # °C

# Power
power = outdoor.power_consumption  # W
power_current = outdoor.power_current  # A

# Performance
cop = outdoor.cop_rating  # Coefficient of Performance
frequency = outdoor.compressor_frequency  # Hz
fan_speed = outdoor.fan_speed  # RPM

# Energy
cumulative = outdoor.cumulative_energy  # kWh
produced = outdoor.power_produced  # W
generated = outdoor.power_generated_last_minute  # W

# Status
voltage = outdoor.heatpump_voltage  # V
```

### Indoor Unit Attributes

Work with indoor (climate) units:

```python
indoor = nasa.devices["200020"]

# Check what controllers are available
has_climate = indoor.climate_controller is not None
has_dhw = indoor.dhw_controller is not None

if has_climate:
    # Access climate attributes
    power = indoor.climate_controller.power  # bool
    mode = indoor.climate_controller.current_mode  # str
    temp = indoor.climate_controller.f_current_temperature  # °C
    target_temp = indoor.climate_controller.f_target_temperature  # °C
    humidity = indoor.climate_controller.current_humidity  # %
    fan_mode = indoor.climate_controller.current_fan_mode  # str
```

## Callbacks and Events

### Device Callbacks

Get notified when a device is updated:

```python
def on_device_changed(device):
    print(f"Device {device.address} was updated!")
    print(f"  Last update: {device.last_packet_time}")

device = nasa.devices["100000"]
device.add_device_callback(on_device_changed)

# Later, remove the callback
device.remove_device_callback(on_device_changed)
```

### Packet Callbacks

Listen for specific message types:

```python
from pysamsungnasa.protocol.factory.messages.indoor import IndoorCurrentTemperature

def on_outdoor_temp_changed(device, **kwargs):
    print(f"Message received: {kwargs['packet']}")

indoor = nasa.devices["200020"]
indoor.add_packet_callback(IndoorCurrentTemperature, on_outdoor_temp_changed)

# Later, remove it
indoor.remove_packet_callback(IndoorCurrentTemperature, on_outdoor_temp_changed)
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

### Using Controllers

The easiest way to send commands is through device controllers:

```python
indoor = nasa.devices["200020"]

# Climate control
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

# DHW control
if indoor.dhw_controller:
    dhw = indoor.dhw_controller

    await dhw.turn_on()
    await dhw.turn_off()
    await dhw.set_target_temperature(45.0)
```

### Direct Message Sending

For advanced usage, send raw messages:

```python
from pysamsungnasa.protocol.factory import SendMessage
from pysamsungnasa.protocol.enum import DataType

await nasa.send_message(
    destination="200020",
    request_type=DataType.REQUEST,
    messages=[
        SendMessage(0x4000, b'\x01'),  # Turn on
    ]
)
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
async def monitor():
    def log_changes(device):
        print(f"[{device.last_packet_time}] {device.address} updated")

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    for device in nasa.devices.values():
        device.add_device_callback(log_changes)

    # Monitor for 60 seconds
    await asyncio.sleep(60)
    await nasa.stop()
```

### Polling for Data

```python
async def poll_every_30_seconds():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    try:
        while True:
            print("\n=== Current Status ===")
            for address, device in nasa.devices.items():
                if hasattr(device, 'outdoor_temperature'):
                    print(f"{address}: {device.outdoor_temperature}°C")
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
