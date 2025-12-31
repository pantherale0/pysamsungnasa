# Git Pre-Commit Hook Setup

This directory contains a script that automatically reorganizes message class definitions by MESSAGE_ID.

## Installation

### Automatic Setup
```bash
chmod +x scripts/pre-commit-hook
cp scripts/pre-commit-hook .git/hooks/pre-commit
```

### Manual Setup
Copy the content of `pre-commit-hook` to `.git/hooks/pre-commit` and make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## What It Does

The pre-commit hook will:
1. Run `sort_messages.py` before each commit
2. Automatically reorganize message classes in `indoor.py` and `outdoor.py` by MESSAGE_ID
3. Detect any changes and automatically stage them
4. Ensure your message files are always organized consistently

## Usage

Once installed, the hook runs automatically on every `git commit`. No additional action needed!

### Manual Run
To manually reorganize messages without committing:
```bash
python3 scripts/sort_messages.py
```

## What Gets Sorted

- **indoor.py**: 174+ message classes
- **outdoor.py**: 255+ message classes

Classes are sorted by MESSAGE_ID value in ascending order (0x0 to 0xFFFF).
