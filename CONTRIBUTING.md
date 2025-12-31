# Contributing to pysamsungnasa

Thank you for your interest in contributing to pysamsungnasa! This document outlines the process for adding new features, particularly new message parsers for the Samsung NASA protocol.

## Adding New Message Parsers

All new message parsers **must** be added using the interactive `add_message.py` script. This ensures:

- Proper message class structure and naming conventions
- Correct positioning by MESSAGE_ID ordering
- Automatic code formatting with ruff
- Consistent documentation and attributes

### Quick Start

```bash
python3 scripts/add_message.py
```

The script will guide you through:

1. **Device Type**: Choose whether the message is for indoor or outdoor units
2. **Message Type**: Select from:
   - `BoolMessage` - Binary on/off states (e.g., heater on/off)
   - `EnumMessage` - Enumerated values with predefined states
   - `FloatMessage` - Numeric floating point values with units
   - `BasicTemperatureMessage` - Temperature values (automatically divided by 10)
   - `BasicPowerMessage` - Power state messages
   - `RawMessage` - Undocumented or unknown message types

3. **Message ID**: The 16-bit hex identifier (e.g., `0x4087`)
4. **Message Name**: Human-readable description (e.g., "Water Pump PWM %")
5. **Enum Name** (EnumMessage only): Reference to the enum definition in `pysamsungnasa/enum.py`
6. **Unit** (FloatMessage only): Unit of measurement (e.g., "%", "°C", "kW")

### Example Interaction

```
================================================================================
ADD NEW MESSAGE PARSER
================================================================================
Add to [i]ndoor or [o]utdoor device? [i/o]: i
Message types:
  1. BoolMessage      - Binary on/off state
  2. EnumMessage      - Enumerated value with defined states
  3. FloatMessage     - Numeric floating point value
  4. BasicTemperatureMessage - Temperature value (divided by 10)
  5. RawMessage       - Undocumented/unknown message
  6. BasicPowerMessage - Power state message

Select message type [1-6]: 3

Message ID (hex, e.g., 0x4087): 0x42AB
Message name (e.g., 'Water Pump PWM %'): Total Cooling Capacity
Unit of measurement (e.g., '%', '°C', or leave blank): kW

================================================================================
GENERATED CLASS:
================================================================================
class InTotalCoolingCapacityMessage(FloatMessage):
    """Parser for message 0x42AB (Total Cooling Capacity)."""

    MESSAGE_ID = 0x42AB
    MESSAGE_NAME = "Total Cooling Capacity"
    UNIT_OF_MEASUREMENT = "kW"

================================================================================

Add this message? [y/n]: y

✓ Added to indoor.py
✓ Applied ruff formatting

✓ Message added successfully!
```

## Pre-Commit Hooks (Required)

Before committing any code, you **must** install the pre-commit hooks. These ensure:

- All message parsers are sorted by MESSAGE_ID
- Code is properly formatted with ruff
- File organization remains consistent

### Installation

The hooks are automatically installed during project setup, but you can manually set them up:

```bash
chmod +x scripts/pre-commit-hook
cp scripts/pre-commit-hook .git/hooks/pre-commit
```

### Manual Organization

If needed, you can manually run the message sorting script:

```bash
python3 scripts/sort_messages.py
```

This will:
- Sort all message classes by MESSAGE_ID in both `indoor.py` and `outdoor.py`
- Apply ruff formatting for consistent code style
- Maintain proper spacing between class definitions

## Code Organization

### Message File Structure

- **`pysamsungnasa/protocol/factory/messages/indoor.py`**: Message parsers for indoor units (0x4000-0x4FFF)
- **`pysamsungnasa/protocol/factory/messages/outdoor.py`**: Message parsers for outdoor units (0x8000-0x8FFF)

Messages are organized by MESSAGE_ID in ascending order within each file.

### Enum Definitions

All enum values referenced by `EnumMessage` classes must be defined in `pysamsungnasa/enum.py`. Add your enum there before creating the message parser.

## Documentation

When adding new messages, ensure:

1. **Class docstring** describes the message purpose and range (if applicable)
2. **MESSAGE_NAME** is human-readable (e.g., "Water Pump PWM %" not "wpump_pwm")
3. **UNIT_OF_MEASUREMENT** is specified for numeric values
4. Comments are added for complex message types or unusual encoding

## Testing

After adding a new message, verify it works by:

1. Running the parser against known device responses
2. Checking that the value is correctly decoded
3. Confirming the message class appears in the correct position when sorted

## Committing Changes

1. Add your new messages using `scripts/add_message.py`
2. The pre-commit hook will automatically sort and format on commit
3. Write a clear commit message explaining what messages were added

Example commit message:
```
feat: add water system temperature sensor messages

- InWaterOutletTempMessage (0x4236)
- InWaterInletTempMessage (0x4237)
- InWaterTargetTempMessage (0x4238)

All messages added via add_message.py script with proper formatting.
```

## Guidelines

- **Always use the `add_message.py` script** - Don't manually edit message files
- **Keep message names descriptive** - Avoid abbreviations unless widely recognized
- **Match enum definitions** - EnumMessage classes must reference existing enums
- **Include units** - FloatMessage and similar types must specify units
- **Document unknowns** - Use RawMessage for undocumented message types and add context in docstring

## Getting Help

- Check existing messages in `indoor.py` or `outdoor.py` for examples
- Review `NASA.ptc` in the `info/snet/` folder for protocol documentation
- Refer to `NOTES.md` for additional message information and context

Thank you for contributing!
