#!/usr/bin/env python3
"""
Sort message class definitions in indoor.py and outdoor.py by MESSAGE_ID.
Can be used as a git pre-commit hook to keep message files organized.
"""

import re
import subprocess
from pathlib import Path


def extract_message_classes(content):
    """
    Extract message class definitions from Python source code.
    Returns list of (class_name, message_id, full_class_text) tuples.
    """
    classes = []
    # Pattern to match class definitions with MESSAGE_ID
    class_pattern = r"^(class\s+\w+\(.*?\):.*?)(?=^class\s+|\Z)"

    for match in re.finditer(class_pattern, content, re.MULTILINE | re.DOTALL):
        class_text = match.group(1)

        # Extract class name
        class_name_match = re.search(r"class\s+(\w+)\(", class_text)
        if not class_name_match:
            continue
        class_name = class_name_match.group(1)

        # Extract MESSAGE_ID
        msg_id_match = re.search(r"MESSAGE_ID\s*=\s*(0x[0-9a-fA-F]+|[0-9]+)", class_text)
        if not msg_id_match:
            continue

        msg_id_str = msg_id_match.group(1)
        msg_id = int(msg_id_str, 16) if msg_id_str.startswith("0x") else int(msg_id_str)

        classes.append((class_name, msg_id, class_text.rstrip()))

    return classes


def sort_message_file(file_path):
    """
    Read a message file, sort classes by MESSAGE_ID, and write back.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Split into header (imports, docstring) and classes
    # Find the first class definition
    first_class_match = re.search(r"^class\s+", content, re.MULTILINE)

    if not first_class_match:
        print(f"  No classes found in {file_path.name}")
        return False

    header_end = first_class_match.start()
    header = content[:header_end].rstrip()
    classes_content = content[header_end:]

    # Extract all classes
    classes = extract_message_classes(classes_content)

    if not classes:
        print(f"  No MESSAGE_ID classes found in {file_path.name}")
        return False

    # Sort by MESSAGE_ID
    classes.sort(key=lambda x: x[1])

    # Reconstruct file with proper spacing (two blank lines between classes)
    class_definitions = [class_text for _, _, class_text in classes]
    new_content = header + "\n\n\n" + "\n\n\n".join(class_definitions) + "\n"

    # Write back
    with open(file_path, "w") as f:
        f.write(new_content)

    print(f"  Sorted {len(classes)} classes in {file_path.name}")
    return True


def format_with_ruff(file_path):
    """
    Format file with ruff if available.
    """
    try:
        result = subprocess.run(["ruff", "format", str(file_path)], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  Formatted {file_path.name} with ruff")
            return True
        else:
            print(f"  Warning: ruff formatting had issues for {file_path.name}")
            if result.stderr:
                print(f"    {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"  Warning: ruff not found - skipping format step")
        return False
    except subprocess.TimeoutExpired:
        print(f"  Warning: ruff formatting timed out for {file_path.name}")
        return False


def main():
    """Sort message classes in all message files."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    messages_dir = project_root / "pysamsungnasa" / "protocol" / "factory" / "messages"

    print("=" * 80)
    print("SORTING MESSAGE CLASSES BY MESSAGE_ID")
    print("=" * 80)
    print()

    if not messages_dir.exists():
        print(f"Error: Messages directory not found: {messages_dir}")
        return 1

    files_to_sort = [
        messages_dir / "indoor.py",
        messages_dir / "outdoor.py",
    ]

    sorted_count = 0
    for file_path in files_to_sort:
        if file_path.exists():
            if sort_message_file(file_path):
                sorted_count += 1
                format_with_ruff(file_path)
        else:
            print(f"  Skipping {file_path.name} (not found)")

    print()
    print("=" * 80)
    print(f"Sorted {sorted_count} files successfully")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
