# Tests for pysamsungnasa

This directory contains comprehensive unit tests for the pysamsungnasa library.

## Test Coverage

The test suite covers the following modules:

- **test_helpers.py** - Tests for helper functions (bin2hex, hex2bin, Address class, nonce functions)
- **test_enum.py** - Tests for protocol enums (AddressClass, PacketType, DataType, and various operational enums)
- **test_config.py** - Tests for the NasaConfig dataclass
- **test_parser.py** - Tests for NasaPacketParser (packet parsing, device handlers, packet listeners)
- **test_factory.py** - Tests for message factory functions (build_message, parse_message, message name lookups)

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

Or install the package with test dependencies:

```bash
pip install -e ".[test]"
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run without coverage reporting
pytest tests/ --no-cov

# Run specific test file
pytest tests/test_helpers.py

# Run specific test class
pytest tests/test_parser.py::TestNasaPacketParser

# Run specific test
pytest tests/test_helpers.py::TestAddress::test_address_parse
```

### Run Tests with Coverage

```bash
# Run tests with coverage report
pytest tests/ --cov=pysamsungnasa --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Test Structure

Each test file follows this structure:

```python
import pytest
from pysamsungnasa.module import ClassToTest


class TestClassName:
    """Tests for ClassName."""

    def test_feature_name(self):
        """Test specific feature."""
        # Arrange
        obj = ClassToTest()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected_value
```

## Async Tests

Tests for async functions use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function(self):
    """Test async function."""
    result = await async_function()
    assert result == expected
```

## Mocking

The test suite uses mocking to:
- Mock unavailable dependencies (e.g., aiotelnet which requires Python 3.13+)
- Isolate tests from external dependencies
- Test callbacks and event handlers

See `conftest.py` for global fixtures and mocks.

## Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Use descriptive test names that explain what is being tested
3. Include docstrings for test classes and methods
4. Group related tests in the same test class
5. Ensure tests are isolated and don't depend on execution order
6. Add async tests with proper `@pytest.mark.asyncio` decorator

## Test Markers

Tests can be marked with the following markers (defined in pyproject.toml):

- `integration` - Integration tests (skipped by default)
- `unit` - Fast offline unit tests
- `slow` - Tests that take longer to run
- `spark` - Tests requiring Spark
- `gpu` - Tests requiring GPU
- `notebooks` - Notebook tests

Example:

```python
@pytest.mark.unit
def test_fast_unit_test(self):
    """Fast unit test."""
    pass
```

Run only unit tests:

```bash
pytest tests/ -m unit
```
