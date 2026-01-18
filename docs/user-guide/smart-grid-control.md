# Smart Grid Control

Enable your heat pump to participate in grid demand response programs and optimize energy consumption based on grid signals.

## Overview

Smart Grid Control (FSV #5091) allows Samsung heat pumps to respond to external signals from utility companies or grid aggregators. The system can:

- **Reduce heating/DHW capacity** during peak demand periods (load shedding)
- **Increase heating/DHW** during off-peak hours (load shifting)
- **Adjust compressor speed** for frequency regulation
- **Support renewable energy** by shifting loads to high-generation periods

This leads to:
- Lower energy costs through automated off-peak consumption
- Reduced demand charges from the utility
- Grid stability support and renewable integration
- Energy savings of 10-15% in typical demand response scenarios

## Architecture

Smart Grid Control operates through four distinct operating modes, controlled exclusively via two physical terminals:

| **Mode** | **Terminal 1** | **Terminal 2** | **Behavior** |
|----------|---|---|---|
| **1: Forced Off** | Short (0V) | Open | All system components stop (thermostat off) |
| **2: Normal** | Open | Open | System operates normally with user setpoints |
| **3: Load Increase** | Open | Short (0V) | Temperature setpoints raised (+FSV #5092, +FSV #5093) |
| **4: Load Reduction** | Short (0V) | Short (0V) | Temperature adjusted per FSV #5094 settings |

**Important**: The four modes are controlled via physical terminal connections, NOT via Modbus messages. Message 0x4124 is only used to enable/disable SG Ready mode.

## Configuration

### Enable Smart Grid Control

First, enable the feature via FSV #5091:

```python
# FSV #5091 = 1 to enable Smart Grid Control
# This allows the system to receive and respond to external signals
```

### Related Settings

Once enabled, configure the system's response behavior using:

| **FSV** | **Message ID** | **Purpose** | **Default** | **Range** |
|---------|---|---|---|---|
| **#5092** | `0x42DD` | Heating temperature shift during Mode 3/4 | 2°C | 2-5°C (0.5°C steps) |
| **#5093** | `0x42DE` | DHW temperature shift during Mode 3 | 5°C | 2-5°C (0.5°C steps) |
| **#5094** | `0x411D` | DHW priority during Mode 4 (demand response) | 0 (Comfort) | 0-1 |

### Control Methods

#### Physical Terminal Control (Primary Method)

Connect your grid signal controller to the two physical terminals for mode selection:
- Use relay outputs or open-collector circuits
- Short = 0V (terminal active), Open = floating (terminal inactive)
- Switch between modes by changing terminal configurations
- This is the standard way Samsung heat pumps control SG modes

**Terminal Connection Guide** (from manufacturer):
- Terminal 1 & 2 to Digital Input port on indoor controller
- System samples terminal state to determine current mode
- Changes take effect immediately upon terminal state change

#### Software Enable/Disable (0x4124)

Message 0x4124 (SG Ready Mode State) provides a software on/off switch for the SG Ready system:

| **Value** | **Enum Name** | **Effect** |
|---|---|---|
| `0` | `OFF` | SG Ready disabled - physical terminal inputs are ignored |
| `1` | `ON` | SG Ready enabled - physical terminal inputs are processed |

Use this message to globally enable or disable SG Ready responsiveness without physically disconnecting terminals:

```python
# Recommended approach: Use write_attribute() method for clean, supported API
from pysamsungnasa.protocol.factory.messages.indoor import InSgReadyModeStateMessage
from pysamsungnasa.protocol.enum import InSgReadyModeState

# Get your device from SamsungNasa instance
device = nasa.devices.get("200020")  # Indoor unit 1

# Enable SG Ready mode (allows terminal inputs to control modes):
await device.write_attribute(InSgReadyModeStateMessage, InSgReadyModeState.ON)

# Disable SG Ready mode (ignores terminal inputs, system operates normally):
await device.write_attribute(InSgReadyModeStateMessage, InSgReadyModeState.OFF)
```

**Note**: The `write_attribute()` method is the recommended, supported API for all message sending. This handles message encoding, addressing, and transmission automatically. Avoid calling `to_bytes()` directly - it's internal framework code.

## Operational Scenarios

````

## Operational Scenarios

### Scenario 1: Comfort-Focused Home

Prioritize user comfort, use grid response for heating only:

```python
# FSV #5091 = 1  (Enable smart grid)
# FSV #5092 = 2  (Minimal heating shift)
# FSV #5093 = 5  (Keep DHW stable)
# FSV #5094 = 0  (Comfort mode: DHW continues regardless of grid signal)
```

**Response**: During peak demand when Mode 1 (terminal signals) is active, heating stops but DHW continues normally. Users always have hot water.

### Scenario 2: Aggressive Load Shedding

Maximize grid participation, reduce all loads during peak demand:

```python
# FSV #5091 = 1  (Enable smart grid)
# FSV #5092 = 5  (Maximum heating reduction)
# FSV #5093 = 5  (Reduce DHW more aggressively)
# FSV #5094 = 1  (Demand response mode: DHW stops when signaled)
```

**Response**: During peak demand when Mode 1 (terminal signals) is active, both heating and DHW stop. All compressor loads shed. Best for areas with tight grid constraints.

### Scenario 3: Time-of-Use Optimization

Shift loads to low-cost hours, pre-heat during abundance periods:

```python
# FSV #5091 = 1  (Enable smart grid)
# FSV #5092 = 4  (Moderate heating increase during off-peak)
# FSV #5093 = 5  (Pre-heat DHW during surplus periods)
# FSV #5094 = 0  (Maintain comfort)
```

**Response**: During off-peak periods when Mode 3 (terminal signals) is active, heating and DHW targets increase. System pre-stores thermal energy to minimize peak-hour operation.

## Message Details

### FSV #5091: Smart Grid Control Application

**Message ID**: `0x411C` | **Type**: Boolean | **Default**: 0 | **Range**: 0-1

Enables/disables the entire smart grid coordination feature.

- **0 (Disabled)**: System operates independently based on user setpoints
- **1 (Enabled)**: System receives and responds to external control signals

### FSV #5092: Smart Grid Heating Temperature Shift

**Message ID**: `0x42DD` | **Type**: Float | **Unit**: °C | **Default**: 2°C | **Range**: 2-5°C (0.5°C steps)

Temperature increase offset during Smart Grid Mode 3 and 4 (load increase):

- **Mode 3 (BOOST)**: All heating modes (room sensor, outlet, water law) = Current setpoint + FSV #5092
- **Mode 4 (LOAD_REDUCTION)**: Similar to Mode 3 with additional adjustments for room sensor (+3°C more)

**Typical values**:
- 2°C - Minimal load increase, less impact on comfort
- 3°C - Moderate load increase, balanced response
- 4-5°C - Aggressive load increase, maximizes energy storage

### FSV #5093: Smart Grid DHW Temperature Shift

**Message ID**: `0x42DE` | **Type**: Float | **Unit**: °C | **Default**: 5°C | **Range**: 2-5°C (0.5°C steps)

Temperature increase offset for DHW during Smart Grid Mode 3 (BOOST - load increase):

- **Mode 3 (BOOST)**: DHW setpoint = Current setpoint + FSV #5093
- **Mode 4 (LOAD_REDUCTION)**: DHW controlled by FSV #5094 instead

**Typical values**:
- 2°C - Minimal pre-heating, energy savings ~2-3%
- 3-4°C - Moderate pre-heating, energy savings ~4-8%
- 5°C - Aggressive pre-heating, maximum energy storage (default)

### FSV #5094: Smart Grid DHW Mode

**Message ID**: `0x411D` | **Type**: Enum | **Default**: 0 | **Range**: 0-1

Controls DHW behavior during Smart Grid Mode 4 (LOAD_REDUCTION - demand response):

- **0 (Comfort Mode)**: DHW heating continues normally, heating may be deferred instead
  - DHW always available at target temperature
  - System prioritizes user comfort
  - Better for residential users

- **1 (Demand Response Mode)**: DHW heating stops/reduces when grid signal active
  - Maximum demand reduction during peak periods
  - Tank may cool during extended demand response
  - Better for grid-sensitive areas, requires backup heating

**Safety Notes**:
- Even in Mode 1 (demand response), system maintains minimum tank temperature to prevent bacterial growth
- If equipped with backup electric booster heater, it can provide emergency DHW
- Does not run indefinitely cold

## Code Examples

### Reading Smart Grid Settings

```python
from pysamsungnasa import SamsungNasa

async def read_smart_grid_settings():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    # Get indoor unit
    indoor = nasa.devices.get("200020")
    if not indoor:
        print("No indoor unit found")
        return

    # Read smart grid attributes (if available through device)
    print(f"Device: {indoor.device_type}")
    print(f"Attributes: {indoor.attributes}")

    # Look for FSV 5091-5094 in attributes
    for attr_name, attr_value in indoor.attributes.items():
        if "5091" in attr_name or "5092" in attr_name or \
           "5093" in attr_name or "5094" in attr_name:
            print(f"  {attr_name}: {attr_value}")

    await nasa.stop()
```

### Enabling/Disabling SG Ready via Software

```python
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.indoor import InSgReadyModeStateMessage
from pysamsungnasa.protocol.enum import InSgReadyModeState

async def enable_sg_ready(nasa, target_address):
    """
    Enable SG Ready mode via software message (0x4124).

    When enabled, the system will respond to physical terminal input signals to control
    the four Smart Grid operation modes. When disabled, terminal inputs are ignored.

    Args:
        nasa: SamsungNasa instance
        target_address: Device address (e.g., "200020" for indoor unit 1)
    """
    device = nasa.devices.get(target_address)
    if not device:
        print(f"Device {target_address} not found")
        return False

    try:
        # Enable SG Ready mode
        await device.write_attribute(InSgReadyModeStateMessage, InSgReadyModeState.ON)
        print(f"Enabled SG Ready mode on {target_address}")
        return True
    except Exception as e:
        print(f"Failed to enable SG Ready: {e}")
        return False

async def disable_sg_ready(nasa, target_address):
    """
    Disable SG Ready mode via software message (0x4124).

    When disabled, the system ignores physical terminal input signals and operates
    normally based on user setpoints.

    Args:
        nasa: SamsungNasa instance
        target_address: Device address (e.g., "200020" for indoor unit 1)
    """
    device = nasa.devices.get(target_address)
    if not device:
        print(f"Device {target_address} not found")
        return False

    try:
        # Disable SG Ready mode
        await device.write_attribute(InSgReadyModeStateMessage, InSgReadyModeState.OFF)
        print(f"Disabled SG Ready mode on {target_address}")
        return True
    except Exception as e:
        print(f"Failed to disable SG Ready: {e}")
        return False
```

### Configuring Smart Grid Response Settings

```python
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.indoor import (
    InFsv5091Message,
    InFsv5092,
    InFsv5093,
    InFsv5094Message,
)

async def enable_smart_grid(nasa, target_address):
    """Enable FSV #5091 (Smart Grid Control Application)"""
    device = nasa.devices.get(target_address)
    if not device:
        return False

    try:
        await device.write_attribute(InFsv5091Message, 1)  # 1 = enabled
        print(f"Enabled Smart Grid Control on {target_address}")
        return True
    except Exception as e:
        print(f"Failed to enable smart grid: {e}")
        return False

async def configure_smart_grid_response(
    nasa,
    target_address,
    heating_shift=2.0,  # FSV #5092 in °C
    dhw_shift=5.0,      # FSV #5093 in °C
    dhw_mode=0          # FSV #5094: 0=Comfort, 1=Demand Response
):
    """
    Configure how system responds to grid signals via terminal mode changes.

    These settings only take effect when the system enters Mode 3 or Mode 4
    based on physical terminal inputs.

    Uses write_attribute for all message sending - the recommended approach.

    Args:
        nasa: SamsungNasa instance
        target_address: Device address
        heating_shift: Temperature increase for heating in Mode 3/4 (2-5°C)
        dhw_shift: Temperature increase for DHW in Mode 3 (2-5°C)
        dhw_mode: 0=Comfort (DHW continues in Mode 4), 1=Demand Response (DHW stops)
    """

    device = nasa.devices.get(target_address)
    if not device:
        return False

    try:
        # Configure heating response
        await device.write_attribute(InFsv5092, heating_shift)

        # Configure DHW pre-heating
        await device.write_attribute(InFsv5093, dhw_shift)

        # Configure DHW mode priority
        await device.write_attribute(InFsv5094Message, dhw_mode)

        print(f"Configured smart grid response on {target_address}")
        return True
    except Exception as e:
        print(f"Failed to configure smart grid: {e}")
        return False
```

**Important**: Always use `write_attribute()` method for sending messages to devices. The internal `to_bytes()` methods are for framework use only and should not be called directly.

### Monitoring Grid Response Status

```python
import asyncio
from pysamsungnasa import SamsungNasa

async def monitor_smart_grid_response():
    """Monitor how system responds to grid signals"""

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    async def on_device_update(device):
        """Called whenever device updates"""
        if device.address == "200020":  # Indoor unit
            print(f"Smart Grid Status Update:")
            # Check for operation mode, temperature, status
            print(f"  Power: {device.climate_controller.power if device.climate_controller else 'N/A'}")
            print(f"  Mode: {device.climate_controller.current_mode if device.climate_controller else 'N/A'}")
            print(f"  Temp: {device.climate_controller.f_current_temperature if device.climate_controller else 'N/A'}°C")

    # Register update callback
    indoor = nasa.devices.get("200020")
    if indoor:
        indoor.add_device_callback(on_device_update)

    # Monitor for 1 hour
    await asyncio.sleep(3600)
    await nasa.stop()

asyncio.run(monitor_smart_grid_response())
```

## Troubleshooting

### Smart Grid Mode Not Triggering

1. **Check FSV #5091**: Verify smart grid is enabled (value = 1)
2. **Verify signal**: Confirm grid signal is being sent to terminals or via Modbus
3. **Check terminal connections**: Ensure terminals are properly connected and shorts/opens match mode requirements
4. **Review configuration**: Verify FSV #5092, #5093, #5094 are set correctly
5. **Check logs**: Enable debug logging to see if messages are being received

### System Not Responding to Mode Changes

1. **Verify messaging**: Confirm Modbus commands are reaching the device
2. **Check addressing**: Ensure target device address is correct
3. **Review state**: Some modes may not be available depending on current operation state
4. **Temperature constraints**: FSV values must be within allowed ranges (2-5°C)

### Unexpected Temperature Changes

1. **Review FSV #5092/5093**: Verify temperature shift values are as intended
2. **Check current setpoints**: Shifts are relative to current user setpoint
3. **Monitor FSV #5094**: In demand response mode, DHW may reduce unexpectedly
4. **Check operation mode**: Temperature behavior differs between Mode 3 and Mode 4

## Related Settings

For comprehensive demand-side management, also consider:

- **FSV #5081**: PV Control Application (solar optimization)
- **FSV #5082/5083**: PV temperature shifts (solar-aware setpoints)
- **FSV #5041/5042/5043**: Power Peak Control (simpler load shedding)
- **FSV #5051**: Frequency Ratio Control (compressor frequency limiting)
- **FSV #5022**: DHW Saving Mode (energy-saving offset)

## Standards and Regulations

Smart Grid Control implementations support:

- **OpenADR 2.0**: Open Automated Demand Response protocol
- **Utility Demand Response Programs**: Peak time rebates (PTR), critical peak pricing (CPP)
- **Local regulations**: Compliant with grid integration requirements in EU, US, and other regions
- **SG-Ready**: Samsung complies with SG-Ready protocol for heat pump demand response

## See Also

- [Smart Thermostat Example](../examples.md#smart-thermostat)
- [Configuration Guide](./configuration.md)
- [Message Reference](../protocol/messages-reference.md)
- [Protocol Overview](../protocol/overview.md)
