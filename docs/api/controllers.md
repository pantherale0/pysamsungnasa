# Controllers API

Reference for ClimateController and DhwController classes.

## ClimateController

Controls heating, cooling, and ventilation for indoor units.

### Class Definition

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClimateController:
    address: str
    message_sender: Callable
    power: Optional[bool] = None
    current_mode: Optional[str] = None
    real_operation_mode: Optional[str] = None
    f_current_temperature: Optional[float] = None
    f_target_temperature: Optional[float] = None
    current_humidity: Optional[int] = None
    current_fan_mode: Optional[str] = None
    current_fan_speed: Optional[int] = None
    water_outlet_current_temperature: Optional[float] = None
    water_law_target_temperature: Optional[float] = None
    zone_1_status: Optional[bool] = None
    zone_2_status: Optional[bool] = None
```

### Properties

#### `power: bool | None`
Whether climate control is powered on.

```python
cc = indoor.climate_controller
if cc.power:
    print("Climate control is ON")
else:
    print("Climate control is OFF")
```

#### `current_mode: str | None`
Current operation mode.

```python
print(f"Mode: {cc.current_mode}")
# Output: "cool", "heat", "auto", "dry", "fan"
```

#### `real_operation_mode: str | None`
Actual current operation mode (read-only, reflects what unit is actually doing).

```python
print(f"Real mode: {cc.real_operation_mode}")
# May differ from current_mode during transitions
```

#### `f_current_temperature: float | None`
Current room temperature in °C.

```python
print(f"Room temperature: {cc.f_current_temperature}°C")
```

#### `f_target_temperature: float | None`
Target set temperature in °C.

```python
print(f"Target: {cc.f_target_temperature}°C")
```

#### `current_humidity: int | None`
Current humidity percentage (0-100).

```python
print(f"Humidity: {cc.current_humidity}%")
```

#### `current_fan_mode: str | None`
Current fan mode.

```python
print(f"Fan mode: {cc.current_fan_mode}")
```

#### `current_fan_speed: int | None`
Current fan speed (typically 1-4).

```python
print(f"Fan speed: {cc.current_fan_speed}")
```

#### `water_outlet_current_temperature: float | None`
Water outlet temperature for water-based systems.

#### `water_law_target_temperature: float | None`
Target temperature for water law heating mode.

### Control Methods

#### `async turn_on()`
Enable climate control.

```python
await cc.turn_on()
```

#### `async turn_off()`
Disable climate control.

```python
await cc.turn_off()
```

#### `async set_operation_mode(mode: str)`
Set the operation mode.

**Supported modes:**
- `"auto"` - Automatic mode
- `"cool"` - Cooling mode
- `"heat"` - Heating mode
- `"dry"` - Dehumidification mode
- `"fan"` - Fan only mode

```python
await cc.set_operation_mode("cool")
await cc.set_operation_mode("heat")
await cc.set_operation_mode("auto")
```

#### `async set_target_temperature(temperature: float)`
Set the target temperature in °C.

```python
# Set to 22°C
await cc.set_target_temperature(22.0)

# Set to 23.5°C
await cc.set_target_temperature(23.5)
```

**Range:** Typically 16-30°C (check your unit's limits)

#### `async set_fan_speed(speed: int)`
Set fan speed.

**Speed levels:**
- `1` - Low
- `2` - Medium
- `3` - High
- `4` - Very High
- `0` - Auto (if supported)

```python
await cc.set_fan_speed(1)  # Low
await cc.set_fan_speed(3)  # High
```

#### `async set_air_swing(direction: str)`
Set vertical air swing direction.

**Directions:**
- `"up"` - Swing up
- `"middle"` - Middle position
- `"down"` - Swing down
- `"swing"` - Continuous swing
- `"off"` - No swing

```python
await cc.set_air_swing("swing")
await cc.set_air_swing("down")
```

### Advanced Methods

#### `async set_target_humidity(humidity: int)`
Set target humidity (if supported).

```python
await cc.set_target_humidity(50)  # 50%
```

#### `async set_water_law_target_temperature(temp: float)`
Set temperature for water law heating mode.

```python
await cc.set_water_law_target_temperature(45)
```

#### `async set_water_outlet_target_temperature(temp: float)`
Set outlet water temperature (for water systems).

```python
await cc.set_water_outlet_target_temperature(50)
```

## DhwController

Controls domestic hot water heating.

### Class Definition

```python
@dataclass
class DhwController:
    address: str
    message_sender: Callable
    power: Optional[bool] = None
    operation_mode: Optional[str] = None
    reference_temp_source: Optional[str] = None
    target_temperature: Optional[float] = None
    current_temperature: Optional[float] = None
    outdoor_operation_status: Optional[str] = None
    outdoor_operation_mode: Optional[str] = None
    dhw_enable_status: Optional[bool] = None
```

### Properties

#### `power: bool | None`
Whether DHW is powered on.

```python
dhw = indoor.dhw_controller
if dhw.power:
    print("Hot water heating is ON")
```

#### `operation_mode: str | None`
Current DHW operation mode.

```python
print(f"Mode: {dhw.operation_mode}")
```

#### `target_temperature: float | None`
Target water temperature in °C.

```python
print(f"Target: {dhw.target_temperature}°C")
```

#### `current_temperature: float | None`
Current water temperature in °C.

```python
print(f"Current: {dhw.current_temperature}°C")
```

#### `reference_temp_source: str | None`
Source for reference temperature.

#### `outdoor_operation_status: str | None`
Status reflected from outdoor unit.

#### `outdoor_operation_mode: str | None`
Mode reflected from outdoor unit.

#### `dhw_enable_status: bool | None`
Whether DHW is enabled in system settings.

### Control Methods

#### `async turn_on()`
Enable DHW heating.

```python
await dhw.turn_on()
```

#### `async turn_off()`
Disable DHW heating.

```python
await dhw.turn_off()
```

#### `async set_target_temperature(temperature: float)`
Set target water temperature in °C.

```python
await dhw.set_target_temperature(45)
await dhw.set_target_temperature(50)
```

**Typical range:** 30-55°C (check your unit's limits)

#### `async set_operation_mode(mode: str)`
Set DHW operation mode.

**Common modes:**
- `"normal"` - Normal heating
- `"eco"` - Energy-saving mode
- `"comfort"` - Comfort mode

```python
await dhw.set_operation_mode("normal")
await dhw.set_operation_mode("eco")
```

## Usage Examples

### Simple Climate Control

```python
indoor = nasa.devices["200020"]
cc = indoor.climate_controller

# Turn on and set to 22°C in cool mode
await cc.turn_on()
await cc.set_operation_mode("cool")
await cc.set_target_temperature(22)
await cc.set_fan_speed(2)

print(f"Set to {cc.f_target_temperature}°C in {cc.current_mode} mode")
```

### Simple DHW Control

```python
indoor = nasa.devices["200020"]
dhw = indoor.dhw_controller

# Turn on hot water and set to 45°C
await dhw.turn_on()
await dhw.set_target_temperature(45)

print(f"Hot water set to {dhw.target_temperature}°C")
```

### Monitoring with Callbacks

```python
cc = indoor.climate_controller

def on_temp_change(device):
    current = cc.f_current_temperature
    target = cc.f_target_temperature
    print(f"Temp: {current}°C (target {target}°C)")

indoor.add_device_callback(on_temp_change)
```

### Conditional Control

```python
async def smart_cooling():
    """Cool room when temperature exceeds threshold."""

    cc = indoor.climate_controller
    target = 22
    threshold = 24

    def control_temp(device):
        current = cc.f_current_temperature

        if current > threshold and cc.current_mode != "cool":
            # Too hot, start cooling
            asyncio.create_task(cc.set_operation_mode("cool"))
            asyncio.create_task(cc.set_target_temperature(target))

        elif current < target - 0.5 and cc.power:
            # Cool enough, turn off
            asyncio.create_task(cc.turn_off())

    indoor.add_device_callback(control_temp)
```

### Temperature Ramping

```python
async def ramp_temperature(cc, target_temp, step=1, delay=30):
    """Gradually change temperature."""

    current = cc.f_target_temperature or 20

    if target_temp > current:
        # Ramp up
        while current < target_temp:
            current += step
            await cc.set_target_temperature(min(current, target_temp))
            await asyncio.sleep(delay)
    else:
        # Ramp down
        while current > target_temp:
            current -= step
            await cc.set_target_temperature(max(current, target_temp))
            await asyncio.sleep(delay)

# Usage
await ramp_temperature(cc, target_temp=24, step=0.5, delay=60)
```

### Multi-Device Synchronization

```python
async def sync_controllers(devices, property_name, value):
    """Set same property on multiple devices."""

    for device in devices:
        if not device.climate_controller:
            continue

        cc = device.climate_controller

        if property_name == "temperature":
            await cc.set_target_temperature(value)
        elif property_name == "mode":
            await cc.set_operation_mode(value)
        elif property_name == "fan":
            await cc.set_fan_speed(value)
        elif property_name == "power":
            if value:
                await cc.turn_on()
            else:
                await cc.turn_off()

# Usage
indoor_units = [d for d in nasa.devices.values() if hasattr(d, 'climate_controller')]
await sync_controllers(indoor_units, "temperature", 22)
await sync_controllers(indoor_units, "mode", "cool")
```

## Error Handling

```python
try:
    await cc.set_target_temperature(22)
except AttributeError:
    print("Climate controller not available")
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

- Read [User Guide Controllers](../user-guide/controllers.md)
- Check [Basic Usage](../user-guide/basic-usage.md)
- Explore [Examples](../examples.md)
