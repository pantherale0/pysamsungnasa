# Controllers

Control device functions using the ClimateController and DhwController classes.

## Overview

Controllers provide a high-level interface to control specific device functions:

- **ClimateController** - Control heating and cooling (indoor units)
- **DhwController** - Control domestic hot water (indoor units)

## Climate Controller

The `ClimateController` manages heating, cooling, and fan control for indoor units.

### Checking Availability

```python
indoor = nasa.devices["200020"]

if indoor.climate_controller:
    print("Climate controller is available")
    await indoor.climate_controller.turn_on()
else:
    print("No climate controller on this unit")
```

### Power Control

```python
cc = indoor.climate_controller

# Turn on
await cc.turn_on()

# Turn off
await cc.turn_off()

# Check current state
power_on = cc.power  # True or False
```

### Mode Control

Set the operation mode:

```python
# Available modes depend on your unit
await cc.set_operation_mode("cool")
await cc.set_operation_mode("heat")
await cc.set_operation_mode("dry")
await cc.set_operation_mode("fan")
await cc.set_operation_mode("auto")

# Check current mode
current = cc.current_mode  # Returns mode string
```

### Temperature Control

```python
# Set target temperature
await cc.set_target_temperature(22.0)  # 22°C
await cc.set_target_temperature(72.0)  # 72°F

# Read temperatures
target = cc.f_target_temperature
current = cc.f_current_temperature

print(f"Target: {target}°C, Current: {current}°C")
```

### Fan Control

```python
# Set fan speed (typically 1-4)
await cc.set_fan_speed(1)  # Low
await cc.set_fan_speed(2)  # Medium
await cc.set_fan_speed(3)  # High
await cc.set_fan_speed(4)  # Very High

# Check current speed
speed = cc.current_fan_speed
mode = cc.current_fan_mode

print(f"Fan speed: {speed}, Mode: {mode}")
```

### Air Swing Control

Control vertical air direction (if supported):

```python
# Set air swing
await cc.set_air_swing("up")
await cc.set_air_swing("middle")
await cc.set_air_swing("down")
await cc.set_air_swing("swing")
await cc.set_air_swing("off")
```

### Reading Status

```python
cc = indoor.climate_controller

# Power status
print(f"Power: {cc.power}")

# Temperatures
print(f"Current: {cc.f_current_temperature}°C")
print(f"Target: {cc.f_target_temperature}°C")

# Mode
print(f"Mode: {cc.current_mode}")
print(f"Real Mode: {cc.real_operation_mode}")

# Fan
print(f"Fan Mode: {cc.current_fan_mode}")
print(f"Fan Speed: {cc.current_fan_speed}")

# Humidity
print(f"Humidity: {cc.current_humidity}%")

# Water
if hasattr(cc, 'water_outlet_current_temperature'):
    print(f"Water outlet: {cc.water_outlet_current_temperature}°C")
```

### Humidity Control

Some units support humidity control:

```python
# Set target humidity
if hasattr(cc, 'set_target_humidity'):
    await cc.set_target_humidity(50)  # 50%
```

### Zone Control

Multi-zone units support zone selection:

```python
# Check zone status
if hasattr(cc, 'zone_1_status'):
    print(f"Zone 1: {cc.zone_1_status}")
if hasattr(cc, 'zone_2_status'):
    print(f"Zone 2: {cc.zone_2_status}")

# Control zones (implementation varies by unit)
# Refer to your specific unit's documentation
```

## DHW (Domestic Hot Water) Controller

The `DhwController` manages hot water heating.

### Checking Availability

```python
indoor = nasa.devices["200020"]

if indoor.dhw_controller:
    print("DHW controller is available")
    await indoor.dhw_controller.turn_on()
else:
    print("No DHW on this unit")
```

### Power Control

```python
dhw = indoor.dhw_controller

# Turn on
await dhw.turn_on()

# Turn off
await dhw.turn_off()

# Check current state
power_on = dhw.power  # True or False
```

### Temperature Control

```python
# Set target temperature
await dhw.set_target_temperature(45.0)  # 45°C
await dhw.set_target_temperature(110.0)  # 110°F

# Read temperatures
target = dhw.target_temperature
current = dhw.current_temperature

print(f"Target: {target}°C, Current: {current}°C")
```

### Operation Mode

```python
# Set DHW operation mode
modes = ["normal", "eco", "comfort"]  # Varies by unit
await dhw.set_operation_mode("normal")

# Check current mode
mode = dhw.operation_mode
```

### Reading DHW Status

```python
dhw = indoor.dhw_controller

# Power status
print(f"Power: {dhw.power}")

# Temperatures
print(f"Target: {dhw.target_temperature}°C")
print(f"Current: {dhw.current_temperature}°C")

# Mode
print(f"Mode: {dhw.operation_mode}")

# Outdoor status (reflected from outdoor unit)
print(f"Outdoor op status: {dhw.outdoor_operation_status}")
print(f"Outdoor mode: {dhw.outdoor_operation_mode}")
```

### Heating Law Control

Advanced DHW modes based on heating law:

```python
# Check if water law is active
if hasattr(dhw, 'water_law_mode'):
    print(f"Water law mode: {dhw.water_law_mode}")

# Set water law temperature
if hasattr(dhw, 'set_water_law_target_temperature'):
    await dhw.set_water_law_target_temperature(40.0)

# Set water outlet target (for water law)
if hasattr(dhw, 'set_water_outlet_target_temperature'):
    await dhw.set_water_outlet_target_temperature(50.0)
```

## Error Handling

Always handle errors when controlling devices:

```python
try:
    cc = indoor.climate_controller
    await cc.set_target_temperature(22)
    print("Temperature set successfully")
except AttributeError:
    print("No climate controller on this device")
except Exception as e:
    print(f"Error setting temperature: {e}")
```

## Practical Examples

### Simple Thermostat

```python
async def simple_thermostat():
    """Maintain temperature at 22°C."""
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200020"]
        }
    )

    await nasa.start()
    indoor = nasa.devices["200020"]
    cc = indoor.climate_controller

    TARGET = 22

    async def maintain_temperature(device):
        if cc.f_current_temperature < TARGET:
            if cc.current_mode != "heat":
                await cc.set_operation_mode("heat")
        elif cc.f_current_temperature > TARGET + 1:
            if cc.current_mode != "cool":
                await cc.set_operation_mode("cool")

    indoor.add_device_callback(maintain_temperature)

    try:
        await asyncio.sleep(3600)  # Run for 1 hour
    finally:
        await nasa.stop()
```

### DHW Schedule

```python
import asyncio
from datetime import datetime

async def scheduled_dhw():
    """Turn on DHW at specific times."""
    nasa = SamsungNasa(...)
    await nasa.start()

    indoor = nasa.devices["200020"]
    dhw = indoor.dhw_controller

    while True:
        now = datetime.now().hour

        if now in [7, 18]:  # 7 AM and 6 PM
            await dhw.turn_on()
            print("DHW enabled")
        elif now in [12, 22]:  # 12 PM and 10 PM
            await dhw.turn_off()
            print("DHW disabled")

        await asyncio.sleep(3600)  # Check every hour
```

### Multi-Zone Control

```python
async def control_multiple_zones():
    """Control climate in multiple zones."""
    nasa = SamsungNasa(...)
    await nasa.start()

    zone1 = nasa.devices["200020"]  # Living room
    zone2 = nasa.devices["200021"]  # Bedroom

    # Set different targets
    await zone1.climate_controller.set_target_temperature(22)
    await zone2.climate_controller.set_target_temperature(18)

    # Different fan speeds
    await zone1.climate_controller.set_fan_speed(3)
    await zone2.climate_controller.set_fan_speed(1)
```

### Combined Climate and DHW

```python
async def full_control():
    """Control both climate and DHW."""
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1, "device_addresses": ["200020"]}
    )

    await nasa.start()
    indoor = nasa.devices["200020"]

    # Turn on everything
    if indoor.climate_controller:
        await indoor.climate_controller.turn_on()
        await indoor.climate_controller.set_operation_mode("cool")
        await indoor.climate_controller.set_target_temperature(22)

    if indoor.dhw_controller:
        await indoor.dhw_controller.turn_on()
        await indoor.dhw_controller.set_target_temperature(45)

    print("System activated")
```

## Controller Attributes

### ClimateController Attributes

```python
@dataclass
class ClimateController:
    address: str                          # Device address
    power: Optional[bool]                 # Power state
    current_mode: Optional[str]           # Current mode
    real_operation_mode: Optional[str]    # Real mode (read-only)
    f_current_temperature: Optional[float]# Room temperature
    f_target_temperature: Optional[float] # Target temperature
    current_humidity: Optional[int]       # Humidity %
    current_fan_mode: Optional[str]       # Fan mode
    current_fan_speed: Optional[int]      # Fan speed
    water_outlet_current_temperature: Optional[float]
    water_law_target_temperature: Optional[float]
    zone_1_status: Optional[bool]         # Zone 1 on/off
    zone_2_status: Optional[bool]         # Zone 2 on/off
```

### DhwController Attributes

```python
@dataclass
class DhwController:
    address: str                          # Device address
    power: Optional[bool]                 # Power state
    operation_mode: Optional[str]         # Operation mode
    target_temperature: Optional[float]   # Target temperature
    current_temperature: Optional[float]  # Current temperature
    reference_temp_source: Optional[str]  # Reference source
    outdoor_operation_status: Optional[str]
    outdoor_operation_mode: Optional[str]
    dhw_enable_status: Optional[bool]     # Is DHW enabled
```

## Next Steps

- Learn about [Device Management](device-management.md)
- Read [Basic Usage](basic-usage.md)
- Check the [API Reference](../api/controllers.md)
