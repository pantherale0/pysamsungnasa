# pysamsungnasa Documentation

Welcome to the pysamsungnasa documentation! This library provides a Python interface to communicate with Samsung HVAC/EHS (Heat Pump) units over the NASA protocol via RS485 connection.

## What is pysamsungnasa?

**pysamsungnasa** is a Python library that enables you to:

- **Connect** to Samsung heat pumps and air conditioning units via TCP socket over F1/F2 connectors using the NASA protocol
- **Discover** new devices on the NASA network and manage known devices
- **Send commands** to devices and handle their responses
- **Parse** incoming data packets from devices in real-time
- **Monitor** device attributes and receive callbacks for changes
- **Control** DHW (Domestic Hot Water) settings including power, operation mode, and target temperature
- **Control** climate settings including power, mode, target temperature, fan speed, and more
- **Configure** devices and access their settings

## Key Features

✅ **Async-first design** - Built on asyncio for responsive applications
✅ **Device discovery** - Automatically detect new devices on the network
✅ **Rich device control** - Control climate and DHW systems
✅ **Message parsing** - Automatic NASA protocol packet parsing
✅ **Callback system** - Register callbacks for device and packet updates
✅ **Configuration management** - Read and manage device configurations
✅ **CLI interface** - Interactive command-line tool for manual control and monitoring
✅ **Comprehensive API** - Well-documented Python API for integration

## Supported Units

- **EHS Mono**

### Adding device support

This library is compatible with all Samsung NASA heat pumps and AC units, to add specific device support install the CLI and execute `device dump` from the interactive console session. This will produce a hex file for each known device address which can be uploaded to a new issue in the repository.

## Quick Start

```python
import asyncio
from pysamsungnasa import SamsungNasa

async def main():
    # Initialize the NASA protocol
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000"]  # Outdoor unit
        }
    )

    # Start the connection
    await nasa.start()

    # Get the device
    device = nasa.devices["100000"]

    # Access device attributes
    print(f"Outdoor temperature: {device.outdoor_temperature}")
    print(f"Power consumption: {device.power_consumption}")

    # Control climate (if indoor unit)
    if hasattr(device, 'climate_controller'):
        await device.climate_controller.turn_on()
        await device.climate_controller.set_target_temperature(22)

    # Stop when done
    await nasa.stop()

asyncio.run(main())
```

## Contents

- **[Getting Started](getting-started/installation.md)** - Installation and basic setup
- **[User Guide](user-guide/basic-usage.md)** - How to use the library
- **[API Reference](api/samsung-nasa.md)** - Detailed API documentation
- **[Protocol Documentation](protocol/overview.md)** - NASA protocol details
- **[CLI Reference](cli/reference.md)** - Command-line interface guide
- **[Examples](examples.md)** - Code examples and use cases

## Installation

Install the latest version from PyPI:

```bash
pip install pysamsungnasa
```

## Acknowledgments

This project builds upon the excellent work from:

- [ESPHome Samsung HVAC Bus](https://github.com/omerfaruk-aran/esphome_samsung_hvac_bus/)
- [Samsung NASA MQTT Bridge](https://github.com/70p4z/samsung-nasa-mqtt/)
- Community contributions from OpenEnergyMonitoring Forum
- [EHS Wiki](https://wiki.myehs.eu/wiki/Main_Page)

## License

MIT License - see LICENSE file for details

## Support

- 📚 [Full Documentation](https://github.com/pantherale0/pysamsungnasa)
- 🐛 [Issue Tracker](https://github.com/pantherale0/pysamsungnasa/issues)
- 💬 [GitHub Discussions](https://github.com/pantherale0/pysamsungnasa/discussions)
