#!/usr/bin/env python3
"""Script to add a new message parser to indoor.py or outdoor.py.

Usage:
    python3 scripts/add_message.py

Prompts for message details and adds the parser class to the appropriate file.
Automatically sorts by MESSAGE_ID and applies ruff formatting.
"""

import subprocess
from pathlib import Path
import re


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


def main():
    """Main script flow."""
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


if __name__ == "__main__":
    main()
