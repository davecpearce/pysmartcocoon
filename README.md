# SmartCocoon Python API

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![logo](logo.png)

A Python library for controlling [SmartCocoon smart vents](https://mysmartcocoon.com/) with comprehensive debug logging and Home Assistant integration support.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Home Assistant Integration](#home-assistant-integration)
- [Debug Logging](#debug-logging)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Overview

This library provides a Python interface to the SmartCocoon cloud service, allowing you to control smart vents programmatically. It's designed primarily for Home Assistant integration but can be used independently for any Python project.

### Status

This is not an official API from SmartCocoon and is in active development. The library is stable for basic operations but may have breaking changes as the API evolves.

### Supported Devices

- SmartCocoon Smart Vents (all models)

## Installation

### From PyPI (Recommended)

```bash
pip install pysmartcocoon
```

### From Source

```bash
git clone https://github.com/davecpearce/pysmartcocoon.git
cd pysmartcocoon
pip install -e .
```

### For Development

```bash
git clone https://github.com/davecpearce/pysmartcocoon.git
cd pysmartcocoon
pip install -e .[test]
```

## Quick Start

```python
import asyncio
from pysmartcocoon import SmartCocoonManager

async def main():
    # Initialize the manager
    manager = SmartCocoonManager()

    # Authenticate with your SmartCocoon account
    await manager.async_start_services(
        username="your_email@example.com",
        password="your_password"
    )

    # Update data from the API
    await manager.async_update_data()

    # Access your fans
    for fan_id, fan in manager.fans.items():
        print(f"Fan {fan_id}: {fan.name} - {fan.mode}")

        # Control the fan
        await fan.async_set_fan_mode("auto")
        await fan.async_set_fan_speed(50)  # 50% speed

    # Clean up
    await manager._api.close()

# Run the example
asyncio.run(main())
```

## Features

### Core Functionality

- **Cloud Integration**: Connect to SmartCocoon cloud service
- **Device Discovery**: Automatically discover and configure fans
- **Fan Control**: Complete control over fan operations
- **Real-time Updates**: Get current fan status and settings
- **Error Handling**: Robust error handling and retry logic

### Fan Control Capabilities

- **Power Control**: Turn fans on/off
- **Speed Control**: Set fan speed (0-100%)
- **Mode Control**:
  - `auto` - Automatic mode based on temperature
  - `eco` - Energy-efficient mode
  - `always_on` - Always running
  - `always_off` - Always off
- **Status Monitoring**: Real-time fan status and connection state

### Advanced Features

- **Debug Logging**: Comprehensive debug output for troubleshooting
- **Type Hints**: Full type annotation support
- **Async Support**: Built for async/await patterns
- **Home Assistant Ready**: Designed for seamless HA integration

## Usage Examples

### Basic Fan Control

```python
import asyncio
from pysmartcocoon import SmartCocoonManager

async def control_fan():
    manager = SmartCocoonManager()

    try:
        # Authenticate
        await manager.async_start_services("user@example.com", "password")

        # Get fan data
        await manager.async_update_data()

        # Find a specific fan
        fan = next(iter(manager.fans.values()))

        # Turn on and set to auto mode
        await fan.async_set_fan_mode("auto")
        await fan.async_set_fan_speed(75)

        print(f"Fan {fan.name} is now {fan.mode} at {fan.speed_pct}%")

    finally:
        await manager._api.close()

asyncio.run(control_fan())
```

### Monitoring Fan Status

```python
async def monitor_fans():
    manager = SmartCocoonManager()

    try:
        await manager.async_start_services("user@example.com", "password")

        while True:
            await manager.async_update_data()

            for fan_id, fan in manager.fans.items():
                status = "🟢 Connected" if fan.connected else "🔴 Disconnected"
                print(f"{fan.name}: {status} - {fan.mode} at {fan.speed_pct}%")

            await asyncio.sleep(30)  # Check every 30 seconds

    finally:
        await manager._api.close()
```

## Home Assistant Integration

### Installation

1. Copy the `custom_components/smartcocoon` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

### Configuration

```yaml
# configuration.yaml
smartcocoon:
  username: "your_email@example.com"
  password: "your_password"
```

### Debug Logging in Home Assistant

Add to your `configuration.yaml`:

```yaml
logger:
  logs:
    pysmartcocoon: debug
```

For detailed debug information, see the [Debug Guide](docs/DEBUG_GUIDE.md).

## Debug Logging

The library includes comprehensive debug logging to help troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Your code here - debug output will be shown
```

Debug output includes:

- API requests and responses
- Authentication details
- Fan control operations
- Error information

See the [Debug Guide](docs/DEBUG_GUIDE.md) for complete documentation.

## Development

### Prerequisites

- Python 3.13.2+
- Git
- Docker (for running GitHub Actions locally)

### Development Environment

This project includes a complete development environment using VS Code Dev Containers:

1. Open the project in VS Code
2. When prompted, reopen in container
3. The devcontainer will automatically set up all dependencies

See [docs/DEVCONTAINER_README.md](docs/DEVCONTAINER_README.md) for detailed setup instructions.

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

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **pylint**: Code linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

Run all checks:

```bash
pre-commit run --all-files
```

## Documentation

- [📚 Complete Documentation](docs/DOCS.md) - Comprehensive documentation index
- [🐛 Debug Guide](docs/DEBUG_GUIDE.md) - Debug logging and troubleshooting
- [🛠️ Development Guide](docs/DEVCONTAINER_README.md) - Development environment setup
- [🤝 Contributing Guide](docs/CONTRIBUTING.md) - How to contribute to the project
- [📜 Development Scripts](scripts/README.md) - Utility scripts for development

## Contributing

Contributions are welcome! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Quick Contribution Checklist

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## Work to do

- [ ] MQTT integration for real-time updates
- [ ] Device discovery implementation
- [ ] WebSocket support for live updates
- [ ] Additional fan control features
- [ ] Performance optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/davepearce
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/davecpearce/pysmartcocoon.svg?style=for-the-badge
[commits]: https://github.com/davecpearce/pymywatertoronto/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/davecpearce/pysmartcocoon.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40davecpearce-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/davecpearce/pysmartcocoon.svg?style=for-the-badge
[releases]: https://github.com/davecpearce/pysmartcocoon/releases
[user_profile]: https://github.com/davecpearce
