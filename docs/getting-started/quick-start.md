# Quick Start

Get up and running with pysamsungnasa in 5 minutes!

## CLI

You can launch the interactive CLI as a main module:

```bash
python -m pysamsungnasa
```

The CLI automatically connects using environment variables (set individually or via a `.env` file):

```bash
# .env file
SAMSUNG_HP_HOST=192.168.1.100
SAMSUNG_HP_PORT=8000
SAMSUNG_HP_DEVICE_PNP=true
```

Or set environment variables:

```bash
export SAMSUNG_HP_HOST=192.168.1.100
export SAMSUNG_HP_PORT=8000

python -m pysamsungnasa
```

## Basic Setup

The simplest way to connect to your Samsung HVAC unit:

```python
import asyncio
from pysamsungnasa import SamsungNasa

async def main():
    # Create a NASA protocol instance
    nasa = SamsungNasa(
        host="192.168.1.100",      # IP of your NASA network adapter
        port=8000,                  # NASA protocol port
        config={
            "client_address": 1,    # Your client address on the network
        }
    )

    # Connect to the unit
    await nasa.start()

    # Your code here...

    # Disconnect when done
    await nasa.stop()

asyncio.run(main())
```

## Discovering Devices

By default, pysamsungnasa discovers devices automatically. Once connected, new devices will appear in `nasa.devices`:

```python
async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    # Wait for device discovery
    await asyncio.sleep(2)

    # List all discovered devices
    print(f"Discovered {len(nasa.devices)} devices:")
    for address, device in nasa.devices.items():
        print(f"  {address}: {device.device_type}")

    await nasa.stop()
```

## Accessing Known Devices

If you know your device addresses, add them to the configuration:

```python
nasa = SamsungNasa(
    host="192.168.1.100",
    port=8000,
    config={
        "client_address": 1,
        "device_addresses": [
            "100000",    # Outdoor unit
            "200020",    # Indoor unit 1
        ]
    }
)
```

## Reading Device Data

Once connected, access device information:

```python
async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000"]
        }
    )

    await nasa.start()

    # Get the outdoor unit
    outdoor = nasa.devices["100000"]

    # Read attributes
    print(f"Outdoor temperature: {outdoor.outdoor_temperature}°C")
    print(f"Power consumption: {outdoor.power_consumption}W")
    print(f"Compressor frequency: {outdoor.compressor_frequency}Hz")

    await nasa.stop()

asyncio.run(main())
```

## Controlling Devices (Indoor Unit)

Control climate and DHW systems:

```python
async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200020"]  # Indoor unit
        }
    )

    await nasa.start()

    indoor = nasa.devices["200020"]

    # Control climate
    if indoor.climate_controller:
        # Turn on
        await indoor.climate_controller.turn_on()

        # Set mode (auto, cool, heat, dry, fan)
        await indoor.climate_controller.set_operation_mode("cool")

        # Set target temperature
        await indoor.climate_controller.set_target_temperature(22)

        # Set fan speed
        await indoor.climate_controller.set_fan_speed(1)

    # Control DHW (if available)
    if indoor.dhw_controller:
        await indoor.dhw_controller.turn_on()
        await indoor.dhw_controller.set_target_temperature(45)

    await nasa.stop()

asyncio.run(main())
```

## Listening to Device Events

Register callbacks to be notified of changes:

```python
async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000"]
        }
    )

    def device_updated(device):
        print(f"Device {device.address} updated!")
        print(f"  Outdoor temp: {device.outdoor_temperature}°C")

    await nasa.start()

    outdoor = nasa.devices["100000"]
    outdoor.add_device_callback(device_updated)

    # Device callback will be triggered whenever data is received
    await asyncio.sleep(60)

    await nasa.stop()

asyncio.run(main())
```

## Error Handling

Always wrap your code in proper error handling:

```python
async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    try:
        await nasa.start()

        # Your code here

    except ConnectionError as e:
        print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await nasa.stop()

asyncio.run(main())
```

## Full Example

Here's a complete example that brings it all together:

```python
import asyncio
import logging
from pysamsungnasa import SamsungNasa

# Enable logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000", "200020"]
        }
    )

    def on_device_update(device):
        print(f"✓ {device.address} updated")

    try:
        # Connect
        print("Connecting...")
        await nasa.start()
        print("Connected!")

        # Wait for initial data
        await asyncio.sleep(2)

        # Register callbacks
        for address, device in nasa.devices.items():
            device.add_device_callback(on_device_update)
            print(f"Registered callback for {address}")

        # Monitor for 30 seconds
        print("Monitoring for 30 seconds...")
        await asyncio.sleep(30)

        # Display data
        for address, device in nasa.devices.items():
            print(f"\n{address}:")
            if hasattr(device, 'outdoor_temperature'):
                print(f"  Outdoor temp: {device.outdoor_temperature}°C")
            if hasattr(device, 'power_consumption'):
                print(f"  Power: {device.power_consumption}W")

    finally:
        print("Disconnecting...")
        await nasa.stop()
        print("Done!")

asyncio.run(main())
```

## Next Steps

- Learn about [Configuration](../user-guide/configuration.md) options
- Read the [User Guide](../user-guide/basic-usage.md) for more detailed usage
- Check the [API Reference](../api/samsung-nasa.md) for all available methods
- Explore [Examples](../examples.md) for more use cases
