# NASA Device API

Reference for NasaDevice and its subclasses.

## NasaDevice (Base Class)

The base class for all devices discovered on the NASA network.

### Class Definition

```python
class NasaDevice:
    """Represents a NASA protocol device."""

    def __init__(
        self,
        address: str,
        device_type: AddressClass,
        packet_parser: NasaPacketParser,
        config: NasaConfig,
        client: NasaClient,
    ) -> None:
        ...
```

### Properties

#### `address: str`
The device's network address (e.g., "100000").

```python
device = nasa.devices["100000"]
print(device.address)  # "100000"
```

#### `device_type: AddressClass`
The type of device (enumeration).

```python
from pysamsungnasa.protocol.enum import AddressClass

if device.device_type == AddressClass.OUTDOOR:
    print("This is an outdoor unit")
elif device.device_type == AddressClass.INDOOR:
    print("This is an indoor unit")
```

#### `attributes: dict[int, BaseMessage]`
All received message attributes, indexed by message ID.

```python
# Check what attributes we have
for msg_id, msg_data in device.attributes.items():
    print(f"Message 0x{msg_id:04X}: {msg_data}")

# Access specific attribute
if 0x4203 in device.attributes:
    temp_data = device.attributes[0x4203]
```

#### `last_packet_time: datetime | None`
Timestamp of the last received packet.

```python
from datetime import datetime, timezone, timedelta

if device.last_packet_time:
    elapsed = datetime.now(timezone.utc) - device.last_packet_time
    print(f"Last update: {elapsed.total_seconds():.1f} seconds ago")
else:
    print("Device has not sent any data yet")
```

#### `config: NasaConfig`
Reference to the active configuration object.

```python
print(f"Client address: {device.config.client_address}")
print(f"Retry enabled: {device.config.enable_read_retries}")
```

#### `fsv_config: dict`
FSV (Feature/Setting/Value) configuration for the device.

```python
# Get all FSV settings
for msg_id, value in device.fsv_config.items():
    print(f"FSV 0x{msg_id:04X}: {value}")
```

### Methods

#### `add_device_callback(callback: Callable) -> None`

Register a callback to be called whenever the device is updated.

```python
def on_update(device):
    print(f"Device {device.address} was updated!")
    print(f"Attributes: {len(device.attributes)}")

device.add_device_callback(on_update)
```

The callback receives the device object as its only parameter.

#### `remove_device_callback(callback: Callable) -> None`

Unregister a device callback.

```python
device.remove_device_callback(on_update)
```

#### `add_packet_callback(message: type[BaseMessage], callback: Callable) -> None`

Register a callback for a specific message type.

```python
from pysamsungnasa.protocol.factory.messages.indoor import IndoorCurrentTemperature

def on_temp_change(device, **kwargs):
    message = kwargs['packet']
    print(f"Temperature: {message.VALUE}°C")

# Listen for temperature messages
device.add_packet_callback(IndoorCurrentTemperature, on_temp_change)
```

The callback receives:
- `device` - The device object
- `**kwargs` - Additional data including `packet` and `messageNumber`

#### `remove_packet_callback(message: type[BaseMessage], callback: Callable) -> None`

Unregister a packet-specific callback.

```python
from pysamsungnasa.protocol.factory.messages.indoor import IndoorCurrentTemperature

device.remove_packet_callback(IndoorCurrentTemperature, on_temp_change)
```

#### `async get_configuration() -> None`

Request device FSV configuration from the device.

```python
# Request configuration
await device.get_configuration()

# Wait for response
await asyncio.sleep(2)

# Check configuration
print(device.fsv_config)
```

This is typically called automatically for newly discovered indoor units.

#### `handle_packet(**kwargs) -> None`

Internal method called by the packet parser when data is received. Users should not call this directly.

### Monitoring Device Health

```python
async def check_device_health(device):
    """Check if a device is responsive."""

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

# Check all devices
for device in nasa.devices.values():
    await check_device_health(device)
```

## OutdoorNasaDevice

Subclass for outdoor heat pump units (typically address `100000`).

### Additional Properties

#### `outdoor_temperature: float | None`
Outside air temperature (°C).

```python
outdoor = nasa.devices["100000"]
if hasattr(outdoor, 'outdoor_temperature'):
    print(f"Outside: {outdoor.outdoor_temperature}°C")
```

#### `water_outlet_temperature: float | None`
Water outlet temperature (°C) - for water-based systems.

#### `power_consumption: float | None`
Current instantaneous power consumption (W).

#### `power_current: float | None`
Current draw (Amps).

#### `power_produced: float | None`
Power being generated/produced (W).

#### `power_generated_last_minute: float | None`
Energy generated in the last minute (Wh).

#### `cumulative_energy: float | None`
Total cumulative energy usage/generation (kWh).

#### `heatpump_voltage: float | None`
Operating voltage (V).

#### `compressor_frequency: float | None`
Compressor speed (Hz).

#### `fan_speed: float | None`
Fan speed (RPM).

#### `cop_rating: float | None`
Coefficient of Performance - efficiency metric.

### Example Usage

```python
outdoor = nasa.devices["100000"]

print(f"Temperature: {outdoor.outdoor_temperature}°C")
print(f"Power: {outdoor.power_consumption}W")
print(f"Frequency: {outdoor.compressor_frequency}Hz")
print(f"Efficiency: {outdoor.cop_rating}")
print(f"Total Energy: {outdoor.cumulative_energy}kWh")
```

## IndoorNasaDevice

Subclass for indoor wall-mounted units (typically addresses `200020` and above).

### Additional Properties

#### `climate_controller: ClimateController | None`
Climate/HVAC control interface (if available).

#### `dhw_controller: DhwController | None`
Domestic hot water control interface (if available).

### Example Usage

```python
indoor = nasa.devices["200020"]

# Check what's available
if indoor.climate_controller:
    cc = indoor.climate_controller
    print(f"Climate: {cc.current_mode} mode, {cc.f_current_temperature}°C")

if indoor.dhw_controller:
    dhw = indoor.dhw_controller
    print(f"DHW: {dhw.target_temperature}°C")
```

## Message Attributes

The `attributes` dictionary contains parsed messages from the device. Each entry maps a message ID to a message object:

```python
device = nasa.devices["200020"]

for msg_id, msg_object in device.attributes.items():
    # msg_object has properties like:
    # - msg_object.VALUE - The actual value
    # - msg_object.is_fsv_message - Whether it's an FSV config message
    # - str(msg_object) - Human readable representation

    if hasattr(msg_object, 'VALUE'):
        print(f"Message 0x{msg_id:04X}: {msg_object.VALUE}")
```

## Type Checking

Use isinstance() to check device types:

```python
from pysamsungnasa.device import OutdoorNasaDevice, IndoorNasaDevice

for device in nasa.devices.values():
    if isinstance(device, OutdoorNasaDevice):
        print(f"Outdoor unit: {device.address}")
    elif isinstance(device, IndoorNasaDevice):
        print(f"Indoor unit: {device.address}")
    else:
        print(f"Other device: {device.address} ({device.device_type})")
```

## Practical Examples

### Monitor All Outdoor Units

```python
async def monitor_outdoor():
    """Monitor all outdoor units."""

    from pysamsungnasa.device import OutdoorNasaDevice

    nasa = SamsungNasa(...)
    await nasa.start()

    outdoor_units = [
        d for d in nasa.devices.values()
        if isinstance(d, OutdoorNasaDevice)
    ]

    def log_outdoor(device):
        print(f"\n{device.address}:")
        print(f"  Temp: {device.outdoor_temperature}°C")
        print(f"  Power: {device.power_consumption}W")
        print(f"  COP: {device.cop_rating}")

    for unit in outdoor_units:
        unit.add_device_callback(log_outdoor)

    await asyncio.sleep(300)
    await nasa.stop()

asyncio.run(monitor_outdoor())
```

### Sync All Indoor Units

```python
async def sync_all_zones():
    """Synchronize all zones to same temperature."""

    from pysamsungnasa.device import IndoorNasaDevice

    nasa = SamsungNasa(...)
    await nasa.start()

    target_temp = 22

    for device in nasa.devices.values():
        if not isinstance(device, IndoorNasaDevice):
            continue

        if device.climate_controller:
            await device.climate_controller.set_target_temperature(target_temp)
            print(f"{device.address}: Set to {target_temp}°C")

    await nasa.stop()

asyncio.run(sync_all_zones())
```

## Next Steps

- Read [Basic Usage](../user-guide/basic-usage.md)
- Learn about [Device Management](../user-guide/device-management.md)
- Check [Controllers](controllers.md)
