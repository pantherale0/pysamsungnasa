# CLI Reference

pysamsungnasa includes an interactive command-line interface for testing and managing your Samsung HVAC units.

## Launching the CLI

### Using the run.py Script

The project includes a `run.py` script that launches the interactive CLI:

```bash
python run.py
```

### Configuration

The CLI reads configuration from environment variables and a `.env` file:

```bash
# .env file
NASA_HOST=192.168.1.100
NASA_PORT=8000
NASA_CLIENT_ADDRESS=1
NASA_DEBUG=false
```

Or set environment variables:

```bash
export NASA_HOST=192.168.1.100
export NASA_PORT=8000
export NASA_CLIENT_ADDRESS=1

python run.py
```

## Commands

### Help

```
> help
```

Displays all available commands.

### Device Information

#### list
List all discovered devices.

```
> list
```

Shows all devices currently connected:
```
Device 100000 (Outdoor):
  Address: 100000
  Type: AddressClass.OUTDOOR
  Attributes: 45
  Last update: 2024-01-01 12:34:56

Device 200020 (Indoor):
  Address: 200020
  Type: AddressClass.INDOOR
  Attributes: 38
  Last update: 2024-01-01 12:34:55
```

#### device
Display detailed information about a specific device.

```
> device 100000
```

Shows:
- Device address and type
- Last packet time
- Configuration settings
- FSV configuration
- Controller status
- All attributes

Example output:
```
Device 100000:
  Last seen: 2024-01-01 12:34:56
  Address: 100000
  Device Type: AddressClass.OUTDOOR
  Total attributes: 45

  Outdoor air temp: 8.5°C
  Heatpump voltage: 380V
  Power consumption: 1200W
  Compressor frequency: 45Hz
```

#### attributes
Show all attributes for a device.

```
> attributes 100000
```

Lists all message numbers and values received from the device.

### Climate Control

#### set-mode
Set the operation mode.

```
> set-mode 200020 cool
> set-mode 200020 heat
> set-mode 200020 auto
> set-mode 200020 dry
> set-mode 200020 fan
```

#### set-temp
Set target temperature.

```
> set-temp 200020 22
```

Temperature in Celsius (or Fahrenheit, depending on unit configuration).

#### set-fan
Set fan speed.

```
> set-fan 200020 1
> set-fan 200020 2
> set-fan 200020 3
> set-fan 200020 4
```

Fan speeds:
- 1 = Low
- 2 = Mid
- 3 = High
- 4 = Very High

#### power-on / power-off
Turn climate control on or off.

```
> power-on 200020
> power-off 200020
```

### DHW (Domestic Hot Water) Control

#### dhw-on / dhw-off
Turn DHW on or off.

```
> dhw-on 200020
> dhw-off 200020
```

#### set-dhw-temp
Set DHW target temperature.

```
> set-dhw-temp 200020 45
```

### Monitoring

#### follow
Continuously display updates as data is received.

```
> follow
```

Displays real-time updates to the console. Press Ctrl+C to stop.

#### logs
Show last 20 lines of log output.

```
> logs
```

Displays NASA protocol debug logs.

### Connection

#### status
Show connection status.

```
> status
```

Output:
```
Connection: Connected
Host: 192.168.1.100
Port: 8000
Devices: 2
```

#### reconnect
Reconnect to the NASA network.

```
> reconnect
```

Closes the current connection and establishes a new one.

### Utility Commands

#### clear
Clear the screen.

```
> clear
```

#### quit / exit
Exit the CLI.

```
> quit
> exit
```

## Interactive Usage Examples

### Monitoring Session

```
> list
Device 100000 (Outdoor)
Device 200020 (Indoor)

> device 100000
Device 100000:
  Outdoor air temp: 8.5°C
  Power consumption: 1200W

> set-temp 200020 22
Setting target temperature to 22°C...

> set-mode 200020 heat
Setting operation mode to heat...

> follow
[Real-time updates display]
2024-01-01 12:35:01 - Device 100000 updated
2024-01-01 12:35:02 - Device 200020 updated
```

### Temperature Control

```
> device 200020
Device 200020:
  Climate power: true
  Climate mode: auto
  Current temp: 19.5°C
  Target temp: 20°C

> set-temp 200020 22
Target temperature set to 22°C

> follow
[Monitor temperature rise...]
12:35:10 - Current: 19.5°C
12:35:20 - Current: 19.7°C
12:35:30 - Current: 19.9°C
12:35:40 - Current: 20.2°C
```

### Multi-Zone Control

```
> device 200020
Device 200020 (Living Room)
  Current: 21°C, Target: 22°C

> device 200021
Device 200021 (Bedroom)
  Current: 18°C, Target: 20°C

> set-temp 200020 23
> set-temp 200021 19
> set-fan 200020 3
> set-fan 200021 1

> follow
[Both zones controlled independently]
```

### DHW Setup

```
> dhw-on 200020
DHW power: ON

> set-dhw-temp 200020 45
DHW target temperature: 45°C

> device 200020
  DHW Controller: Yes
  DHW power: true
  DHW target temp: 45.0°C
  DHW current temp: 38.2°C
```

## Troubleshooting CLI Issues

### Connection Problems

**Error: "Connection refused"**

1. Check host and port in environment variables
2. Verify the NASA adapter is powered and connected
3. Test network connectivity: `ping <host>`

**Error: "No devices found"**

1. Wait 2-3 seconds for devices to be discovered
2. Use `device_addresses` in configuration
3. Check `logs` command for connection errors

### Command Not Found

**Error: "Unknown command: ..."**

Type `help` to see valid commands.

### Device Not Responding

**Error: "Device not found: ..."**

Use `list` to see currently connected devices.

Devices may take time to respond. Try:

```
> follow
[Wait for device to appear]
> device <address>
```

## Log Output

CLI logs are saved to `nasa.log`:

```bash
tail -f nasa.log
```

Log level can be controlled via `NASA_DEBUG` environment variable:

```bash
export NASA_DEBUG=true
python run.py
```

## Batch Operations

While the CLI is interactive, you can create scripts to automate operations:

```bash
#!/bin/bash

# Set both zones to 22°C
(
  echo "set-temp 200020 22"
  echo "set-temp 200021 22"
  echo "follow"
  sleep 30
  echo "quit"
) | python run.py
```

## Next Steps

- Learn about [Basic Usage](../user-guide/basic-usage.md) in Python
- Read the [API Reference](../api/samsung-nasa.md)
- Check [Examples](../examples.md) for programmatic usage
