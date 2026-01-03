# Installation

## Requirements

- **Python 3.13+** - pysamsungnasa requires Python 3.13 or higher
- **Network access** - TCP connection to your Samsung HVAC unit's NASA network interface
- **RS485 interface** - F1/F2 connectors with appropriate network adapter

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

1. **F1/F2 Connectors** - Your Samsung unit has F1/F2 connectors for the NASA network
2. **RS485 Adapter** - Use an RS485 to Ethernet/TCP adapter (e.g., Tibbo or similar)
3. **Network Cable** - Connect the adapter to your network

### Configuration

1. **IP Address & Port** - Configure your RS485 adapter's network settings
   - Default port for NASA protocol is usually 8000
   - Note the IP address and port

2. **Network Access** - Ensure the device is on the same network as your Python application
   - Or that the device has network routes to reach it

3. **Firewall** - Allow TCP traffic on the configured port

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

The integrated CLI is available by default however additional dependancies are required for it to run, execute the below command before running:

```bash
pip install "pysamsungnasa[cli]"
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to the NASA device

**Solutions**:
1. Verify the host and port are correct
2. Check network connectivity: `ping <host>`
3. Verify TCP connection: `telnet <host> <port>`
4. Check firewall rules
5. Ensure the RS485 adapter is powered and configured

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
