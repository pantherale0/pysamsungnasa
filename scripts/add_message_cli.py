#!/usr/bin/env python3
"""Script to add a new message parser to indoor.py or outdoor.py.

This version supports both interactive and non-interactive (CLI argument) modes.

Usage:
    Interactive: python3 scripts/add_message.py
    Non-interactive: python3 scripts/add_message.py --device-type DEVICE --message-type TYPE --message-id ID --message-name NAME [--enum-name NAME] [--unit UNIT]

Arguments:
    --device-type: 'indoor' or 'outdoor'
    --message-type: Message type (1-6 or name)
    --message-id: Hex message ID (e.g., 0x4087)
    --message-name: Human-readable message name
    --enum-name: Enum name (required for EnumMessage)
    --unit: Unit of measurement (optional)
"""

import subprocess
from pathlib import Path
import re
import sys
import argparse


def get_file_choice():
    """Get whether to add to indoor or outdoor."""
    while True:
        choice = input("Add to [i]ndoor or [o]utdoor device? [i/o]: ").lower().strip()
        if choice in ("i", "indoor"):
            return "indoor"
        elif choice in ("o", "outdoor"):
            return "outdoor"
        print("  Invalid choice. Please enter 'i' or 'o'")


def get_message_type():
    """Get the message type."""
    print("\nMessage types:")
    print("  1. BoolMessage      - Binary on/off state")
    print("  2. EnumMessage      - Enumerated value with defined states")
    print("  3. FloatMessage     - Numeric floating point value")
    print("  4. BasicTemperatureMessage - Temperature value (divided by 10)")
    print("  5. RawMessage       - Undocumented/unknown message")
    print("  6. BasicPowerMessage - Power state message")

    while True:
        choice = input("\nSelect message type [1-6]: ").strip()
        types = {
            "1": "BoolMessage",
            "2": "EnumMessage",
            "3": "FloatMessage",
            "4": "BasicTemperatureMessage",
            "5": "RawMessage",
            "6": "BasicPowerMessage",
        }
        if choice in types:
            return types[choice]
        print("  Invalid choice. Please enter 1-6")


def parse_message_type(message_type):
    """Parse message type from string (number or name)."""
    type_map = {
        "1": "BoolMessage",
        "2": "EnumMessage",
        "3": "FloatMessage",
        "4": "BasicTemperatureMessage",
        "5": "RawMessage",
        "6": "BasicPowerMessage",
        "boolmessage": "BoolMessage",
        "enummessage": "EnumMessage",
        "floatmessage": "FloatMessage",
        "basictemperaturemessage": "BasicTemperatureMessage",
        "rawmessage": "RawMessage",
        "basicpowermessage": "BasicPowerMessage",
    }
    normalized = message_type.lower().replace("-", "")
    if normalized in type_map:
        return type_map[normalized]
    raise ValueError(f"Invalid message type: {message_type}")


def get_message_id():
    """Get the message ID in hex."""
    while True:
        msg_id = input("\nMessage ID (hex, e.g., 0x4087): ").strip()
        if msg_id.startswith("0x"):
            msg_id = msg_id[2:]
        try:
            value = int(msg_id, 16)
            if 0 <= value <= 0xFFFF:
                return f"0x{msg_id.upper()}"
            print("  Message ID must be between 0x0000 and 0xFFFF")
        except ValueError:
            print("  Invalid hex value. Use format like '4087' or '0x4087'")


def parse_message_id(message_id):
    """Parse message ID from string."""
    msg_id = message_id.strip()
    if msg_id.startswith("0x"):
        msg_id = msg_id[2:]
    try:
        value = int(msg_id, 16)
        if 0 <= value <= 0xFFFF:
            return f"0x{msg_id.upper()}"
        raise ValueError(f"Message ID must be between 0x0000 and 0xFFFF")
    except ValueError:
        raise ValueError(f"Invalid hex value: {message_id}")


def get_message_name():
    """Get the human-readable message name."""
    while True:
        name = input("\nMessage name (e.g., 'Water Pump PWM %'): ").strip()
        if name:
            return name
        print("  Name cannot be empty")


def get_enum_name(device_type):
    """Get the enum name for EnumMessage."""
    prefix = "In" if device_type == "indoor" else "Out"
    return input(f"\nEnum name (e.g., '{prefix}OperationMode'): ").strip()


def get_unit():
    """Get the unit of measurement."""
    unit = input("\nUnit of measurement (e.g., '%', '°C', or leave blank): ").strip()
    return unit if unit else "N/A"


def generate_class(device_type, message_type, message_id, message_name, enum_name=None, unit="N/A"):
    """Generate the message class code."""
    prefix = "In" if device_type == "indoor" else "Out"

    # Generate class name from message name
    class_name = "".join(word.capitalize() for word in message_name.split())
    class_name = f"{prefix}{class_name}Message"

    docstring = f'"""Parser for message {message_id} ({message_name})."""'

    if message_type == "EnumMessage":
        code = f"""class {class_name}(EnumMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}"
    MESSAGE_ENUM = {enum_name}"""
    elif message_type == "BoolMessage":
        code = f"""class {class_name}(BoolMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}" """
    elif message_type == "FloatMessage":
        code = f"""class {class_name}(FloatMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}"
    UNIT_OF_MEASUREMENT = "{unit}" """
    elif message_type == "BasicTemperatureMessage":
        code = f"""class {class_name}(BasicTemperatureMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}" """
    elif message_type == "RawMessage":
        code = f"""class {class_name}(RawMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}" """
    else:  # BasicPowerMessage
        code = f"""class {class_name}(BasicPowerMessage):
    {docstring}

    MESSAGE_ID = {message_id}
    MESSAGE_NAME = "{message_name}" """

    return code


def find_insertion_point(file_path, message_id):
    """Find where to insert the message in order by MESSAGE_ID."""
    with open(file_path) as f:
        content = f.read()

    # Find all MESSAGE_ID values
    pattern = r"MESSAGE_ID = (0x[0-9A-F]+)"
    matches = list(re.finditer(pattern, content))

    if not matches:
        return len(content)

    target_id = int(message_id, 16)
    insert_pos = len(content)

    for match in matches:
        current_id = int(match.group(1), 16)
        if current_id > target_id:
            # Find the start of this class
            class_start = content.rfind("class ", 0, match.start())
            insert_pos = class_start
            break

    return insert_pos


def add_to_file(device_type, class_code):
    """Add the class to the appropriate file."""
    file_name = "indoor.py" if device_type == "indoor" else "outdoor.py"
    file_path = Path(__file__).parent.parent / "pysamsungnasa" / "protocol" / "factory" / "messages" / file_name

    with open(file_path) as f:
        content = f.read()

    # Find insertion point based on MESSAGE_ID ordering
    message_id_match = re.search(r"MESSAGE_ID = (0x[0-9A-F]+)", class_code)
    if message_id_match:
        insert_pos = find_insertion_point(file_path, message_id_match.group(1))
    else:
        insert_pos = len(content)

    # Insert with proper spacing
    new_content = content[:insert_pos] + class_code + "\n\n\n" + content[insert_pos:]

    with open(file_path, "w") as f:
        f.write(new_content)

    print(f"\n✓ Added to {file_name}")
    return file_path


def format_with_ruff(file_path):
    """Format file with ruff."""
    try:
        result = subprocess.run(
            ["ruff", "format", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✓ Applied ruff formatting")
            return True
        else:
            print("⚠ ruff formatting had issues")
            return False
    except FileNotFoundError:
        print("⚠ ruff not found - skipping formatting")
        return False
    except subprocess.TimeoutExpired:
        print("⚠ ruff formatting timed out")
        return False


def interactive_mode():
    """Interactive script flow."""
    print("=" * 80)
    print("ADD NEW MESSAGE PARSER")
    print("=" * 80)

    try:
        device_type = get_file_choice()
        message_type = get_message_type()
        message_id = get_message_id()
        message_name = get_message_name()

        enum_name = None
        if message_type == "EnumMessage":
            enum_name = get_enum_name(device_type)

        unit = ""
        if message_type in ("FloatMessage", "BasicTemperatureMessage"):
            unit = get_unit()

        # Generate and display the class
        class_code = generate_class(device_type, message_type, message_id, message_name, enum_name, unit)

        print("\n" + "=" * 80)
        print("GENERATED CLASS:")
        print("=" * 80)
        print(class_code)
        print("=" * 80)

        confirm = input("\nAdd this message? [y/n]: ").lower().strip()
        if confirm == "y":
            file_path = add_to_file(device_type, class_code)
            format_with_ruff(file_path)
            print("\n✓ Message added successfully!")
        else:
            print("✗ Cancelled")

    except KeyboardInterrupt:
        print("\n✗ Cancelled by user")


def non_interactive_mode(args):
    """Non-interactive mode using command-line arguments."""
    try:
        # Validate and parse arguments
        device_type = args.device_type.lower()
        if device_type not in ("indoor", "outdoor"):
            raise ValueError(f"Invalid device type: {device_type}. Must be 'indoor' or 'outdoor'")

        message_type = parse_message_type(args.message_type)
        message_id = parse_message_id(args.message_id)
        message_name = args.message_name.strip()

        if not message_name:
            raise ValueError("Message name cannot be empty")

        enum_name = None
        if message_type == "EnumMessage":
            if not args.enum_name:
                raise ValueError("Enum name is required for EnumMessage")
            enum_name = args.enum_name.strip()

        unit = "N/A"
        if message_type in ("FloatMessage", "BasicTemperatureMessage"):
            if args.unit:
                unit = args.unit.strip()

        # Generate and add the class
        class_code = generate_class(device_type, message_type, message_id, message_name, enum_name, unit)

        print("=" * 80)
        print("GENERATED CLASS:")
        print("=" * 80)
        print(class_code)
        print("=" * 80)

        file_path = add_to_file(device_type, class_code)
        format_with_ruff(file_path)
        print("\n✓ Message added successfully!")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-type", help="Device type: 'indoor' or 'outdoor'")
    parser.add_argument("--message-type", help="Message type (1-6 or name)")
    parser.add_argument("--message-id", help="Message ID in hex (e.g., 0x4087)")
    parser.add_argument("--message-name", help="Human-readable message name")
    parser.add_argument("--enum-name", help="Enum name (required for EnumMessage)")
    parser.add_argument("--unit", help="Unit of measurement (optional)")

    args = parser.parse_args()

    # Determine if running in interactive or non-interactive mode
    if args.device_type or args.message_type or args.message_id or args.message_name:
        # Non-interactive mode - all required args must be provided
        if not all([args.device_type, args.message_type, args.message_id, args.message_name]):
            print("Error: When using non-interactive mode, you must provide all required arguments:", file=sys.stderr)
            print("  --device-type, --message-type, --message-id, --message-name", file=sys.stderr)
            sys.exit(1)
        non_interactive_mode(args)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
