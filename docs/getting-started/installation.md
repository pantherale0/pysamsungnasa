# Installation

## Requirements

- **Python 3.13+** - pysamsungnasa requires Python 3.13 or higher
- **Serial connection** - Connection to your Samsung HVAC unit's NASA RS485 bus via serial port or network serial bridge using SerialX
- **RS485 interface** - Connection to F1/F2 connectors using an RS485 adapter (USB, serial, or TCP/socket bridge)

## Installation Methods

### From PyPI (Recommended)

Install the latest version from the Python Package Index:

```bash
pip install pysamsungnasa
```

### From GitHub

For the latest development version:

```bash
pip install git+https://github.com/pantherale0/pysamsungnasa.git
```

### From Source

Clone the repository and install:

```bash
git clone https://github.com/pantherale0/pysamsungnasa.git
cd pysamsungnasa
pip install -e .
```

## Development Installation

If you want to contribute to pysamsungnasa, install with development dependencies:

```bash
pip install -e ".[test]"
```

This includes testing frameworks and linting tools.

## Network Requirements

### Hardware Setup

1. **F1/F2 Connectors** - Your Samsung unit has F1/F2 connectors for the NASA network.
2. **RS485 Adapter** - Use an RS485 adapter (USB serial dongle or TCP/socket serial bridge) to connect your computer or server to the F1/F2 RS485 bus.

### Configuration

1. **Connection URL / Device Path** - Note the path to the RS485 interface:
   - For direct USB adapters, this might be `/dev/ttyUSB0` (Linux) or `COM3` (Windows).
   - For network serial bridges, this can be a socket URL supported by SerialX, e.g. `socket://192.168.1.100:8000`.
2. **Baudrate** - The standard baudrate for Samsung NASA communication is `9600`.
3. **Encryption Key** - If using an adapter that requires a secure key (e.g., some hardware bridges), set it via the `SAMSUNG_HP_DEVICE_KEY` environment variable.

## Verifying Installation

Test that pysamsungnasa is correctly installed:

```bash
python -c "import pysamsungnasa; print(pysamsungnasa.__version__)"
```

Or check from Python:

```python
import pysamsungnasa
from pysamsungnasa import SamsungNasa, NasaClient
print("pysamsungnasa is installed!")
```

## Optional Dependencies

### CLI Usage

The integrated CLI is available by default however additional dependencies are required for it to run, execute the below command before running:

```bash
pip install "pysamsungnasa[cli]"
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to the NASA device

**Solutions**:
1. Verify the device path (`device_path`) and baudrate (`client_baudrate`) are correct in your configuration.
2. If using a network socket URL (e.g., `socket://192.168.1.100:8000`), check network connectivity (`ping <host>`) and TCP connection (`telnet <host> <port>`).
3. If using a local serial port (e.g. `/dev/ttyUSB0`), ensure your user has appropriate permissions to read/write the serial device (e.g. `sudo usermod -a -G dialout $USER`).
4. Ensure the RS485 adapter is powered and correctly wired to the F1/F2 bus.

### Import Errors

**Problem**: ModuleNotFoundError when importing pysamsungnasa

**Solutions**:
1. Verify installation: `pip list | grep pysamsungnasa`
2. Check Python version: `python --version` (must be 3.13+)
3. Reinstall: `pip install --upgrade --force-reinstall pysamsungnasa`

### Version Compatibility

Ensure you have the compatible Python version:

```bash
# Check your Python version
python --version

# Should show Python 3.13.x or higher
```

## Next Steps

Once installed, proceed to the [Quick Start](quick-start.md) guide to get your first connection working!
