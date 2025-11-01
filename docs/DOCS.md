# PySmartCocoon Documentation

Welcome to the PySmartCocoon documentation! This guide will help you get started with the library and find the information you need.

## 📚 Documentation Overview

### Getting Started

- **[README.md](README.md)** - Main project overview, installation, and quick start guide
- **[Installation Guide](#installation)** - Detailed installation instructions
- **[Quick Start Guide](#quick-start)** - Get up and running in minutes

### User Guides

- **[Debug Guide](DEBUG_GUIDE.md)** - Comprehensive debug logging documentation
- **[Home Assistant Integration](#home-assistant-integration)** - HA setup and configuration
- **[API Reference](#api-reference)** - Complete API documentation

### Development

- **[Development Guide](DEVCONTAINER_README.md)** - Development environment setup
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](#testing)** - Running tests and debugging

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install pysmartcocoon

# Or install from source
git clone https://github.com/davecpearce/pysmartcocoon.git
cd pysmartcocoon
pip install -e .
```

### Basic Usage

```python
import asyncio
from pysmartcocoon import SmartCocoonManager

async def main():
    manager = SmartCocoonManager()

    # Authenticate
    await manager.async_start_services(
        username="your_email@example.com",
        password="your_password"
    )

    # Get fan data
    await manager.async_update_data()

    # Control fans
    for fan_id, fan in manager.fans.items():
        print(f"Fan {fan.name}: {fan.mode} at {fan.speed_pct}%")
        await fan.async_set_fan_mode("auto")

    await manager._api.close()

asyncio.run(main())
```

## 📖 Detailed Guides

### Debug Logging

The [Debug Guide](DEBUG_GUIDE.md) provides comprehensive information about:

- Enabling debug logging in development
- Configuring debug logging in Home Assistant
- Understanding debug output
- Troubleshooting common issues
- Performance considerations

### Home Assistant Integration

#### Installation

1. Copy the `custom_components/smartcocoon` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

#### Configuration

```yaml
# configuration.yaml
smartcocoon:
  username: "your_email@example.com"
  password: "your_password"

# Enable debug logging
logger:
  logs:
    pysmartcocoon: debug
```

### Development Environment

The [Development Guide](DEVCONTAINER_README.md) covers:

- VS Code Dev Container setup
- Running GitHub Actions locally
- Code quality tools
- Testing framework
- Debug logging setup

## 🔧 API Reference

### SmartCocoonManager

The main class for interacting with the SmartCocoon API.

```python
from pysmartcocoon import SmartCocoonManager

manager = SmartCocoonManager()
```

#### Methods

- `async_start_services(username, password)` - Authenticate with the API
- `async_update_data()` - Refresh all data from the API
- `fans` - Dictionary of discovered fans
- `rooms` - Dictionary of discovered rooms
- `thermostats` - Dictionary of discovered thermostats

### Fan Control

```python
# Get a fan
fan = manager.fans["fan_id"]

# Control the fan
await fan.async_set_fan_mode("auto")  # auto, eco, always_on, always_off
await fan.async_set_fan_speed(75)     # 0-100%

# Get fan status
print(f"Fan: {fan.name}")
print(f"Mode: {fan.mode}")
print(f"Speed: {fan.speed_pct}%")
print(f"Connected: {fan.connected}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with debug output
pytest -v -s

# Run integration tests (requires credentials)
export RUN_INTEGRATION=1
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
```

### Debug Logging Tests

```bash
# Run comprehensive test script
python tests/test_smoke_test.py

# Run specific debug test
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check your credentials
   - Enable debug logging to see detailed error information
   - Verify your SmartCocoon account is active

2. **No Debug Output**
   - Ensure `RUN_INTEGRATION=1` is set (for development)
   - Check logging level is set to DEBUG
   - Verify logger configuration in Home Assistant

3. **Fan Control Not Working**
   - Check if the fan is connected
   - Verify the fan ID is correct
   - Enable debug logging to see API responses

### Getting Help

- Check the [Debug Guide](DEBUG_GUIDE.md) for troubleshooting
- Review the [Development Guide](DEVCONTAINER_README.md) for setup issues
- Open an issue on GitHub for bugs or feature requests

## 🤝 Contributing

We welcome contributions! See the [Contributing Guide](CONTRIBUTING.md) for:

- Development environment setup
- Code style guidelines
- Testing requirements
- Pull request process
- Bug reporting guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/davecpearce/pysmartcocoon
- **PyPI Package**: https://pypi.org/project/pysmartcocoon/
- **Home Assistant Community**: https://community.home-assistant.io/
- **SmartCocoon Website**: https://mysmartcocoon.com/

---

**Need help?** Check the [Debug Guide](DEBUG_GUIDE.md) for troubleshooting or open an issue on GitHub!
