# SmartCocoon Python API

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![logo](logo.png)

A Python library for the [SmartCocoon](https://mysmartcocoon.com/) cloud API. It is the
library behind the [SmartCocoon integration for Home Assistant](https://github.com/davecpearce/ha-smartcocoon),
and can be used on its own from any async Python code.

This is not an official SmartCocoon API. It talks to the same cloud service as the
SmartCocoon app, which is undocumented and can change without notice.

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [What the library gives you](#what-the-library-gives-you)
- [Keeping state current](#keeping-state-current)
- [Errors](#errors)
- [Debug logging](#debug-logging)
- [Development](#development)
- [Documentation](#documentation)

## Installation

```bash
pip install pysmartcocoon
```

Requires Python 3.13.2 or later.

## Quick start

```python
import asyncio

import aiohttp

from pysmartcocoon import SmartCocoonManager
from pysmartcocoon.const import FanMode


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        manager = SmartCocoonManager(session)

        # Logs in and loads locations, thermostats, rooms and fans.
        if not await manager.async_start_services("you@example.com", "password"):
            raise SystemExit("Login failed")

        for fan_id, fan in manager.fans.items():
            print(fan_id, fan.room_name, fan.mode, f"{fan.speed_pct}%")

        fan_id = next(iter(manager.fans))
        # Every control method returns False if SmartCocoon did not accept it.
        if not await manager.async_set_fan_speed(fan_id, 50):
            print("Speed change was not accepted")
        await manager.async_set_fan_modes(fan_id, FanMode.ECO, 50)


asyncio.run(main())
```

Pass your own `aiohttp.ClientSession` when you have one. The library never closes a
session it did not create, because Home Assistant shares one session across every
integration. If you pass none, the library creates its own.

## What the library gives you

`SmartCocoonManager` is the entry point. After `async_start_services()` it holds
`locations`, `thermostats`, `rooms` and `fans`, each a dict keyed by ID.

**Controlling a fan**: all of these take a `fan_id` and return `bool`:

| Method                                   | Effect                                              |
| ---------------------------------------- | --------------------------------------------------- |
| `async_fan_turn_on(fan_id)`              | Always on (`FanMode.ON`)                            |
| `async_fan_turn_off(fan_id)`             | Always off (`FanMode.OFF`)                          |
| `async_set_fan_auto(fan_id)`             | Auto mode, configured in the SmartCocoon app        |
| `async_set_fan_eco(fan_id)`              | Eco mode                                            |
| `async_set_fan_speed(fan_id, pct)`       | Speed, 0–100. Values outside that range are refused |
| `async_set_fan_modes(fan_id, mode, pct)` | Mode and speed together                             |

**Reading a fan**: the main `Fan` properties:

| Property                                                        | Meaning                                                                                                                                                                                    |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `mode`                                                          | `auto`, `eco`, `always_on` or `always_off`                                                                                                                                                 |
| `fan_on`                                                        | Whether the fan is currently running                                                                                                                                                       |
| `speed_pct` / `power`                                           | The **manual** speed setting, as a percentage / raw value (×100)                                                                                                                           |
| `speed_level`                                                   | The speed the fan is **actually** running at, 1–12. In eco and auto modes the cloud picks the speed itself, so this differs from `speed_pct`. The SmartCocoon app shows `speed_level / 12` |
| `connected`, `last_connection`                                  | Cloud connection state. A fan silent for more than 15 minutes is reported as disconnected even if the cloud still says connected                                                           |
| `predicted_room_temperature`, `is_room_estimating`              | SmartCocoon's room temperature estimate                                                                                                                                                    |
| `room_id`, `room_name`, `firmware_version`, `thermostat_vendor` | Descriptive details                                                                                                                                                                        |

The 1–12 range of `speed_level` is inferred from live data, not documented.

## Keeping state current

The API does not push changes to clients, so poll. `async_refresh_fans()` refreshes
every fan in one request and returns whether it worked:

```python
while True:
    if not await manager.async_refresh_fans():
        print("Refresh failed; fans keep their previous values")
    await asyncio.sleep(60)
```

Home Assistant polls this way every 60 seconds. `async_update_fans()` does the same
refresh but returns the fan dict and swallows every failure, so you cannot tell fresh
data from stale with it.

Each fan also carries `mqtt_username` and `mqtt_password`. **Do not connect to the
SmartCocoon broker with them.** They are the fan's own identity: connecting with them
takes over the fan's session, and the real fan drops offline until it reconnects.

## Errors

All errors derive from `pysmartcocoon.errors.SmartCocoonError`.

- **`UnauthorizedError`**: SmartCocoon rejected the credentials. Expired sessions are
  handled for you: on a 401 the library logs in again once and retries the request.
  You only see this error when that fresh login is refused too, which normally means
  the password changed. `async_refresh_fans()` raises it so you can ask for a new
  password; it returns `False` for every other failure.
- **`RequestError`**: network failures, timeouts and server errors, after up to three
  attempts with backoff. Rate limiting honours `Retry-After`.

## Debug logging

Enable the `pysmartcocoon` logger at `DEBUG` to log every API request and response.
Passwords, tokens, MQTT credentials and your home address are masked before they are
logged, and email addresses are partly masked, so the output is safe to attach to an
issue. In Home Assistant:

```yaml
logger:
  logs:
    pysmartcocoon: debug
```

To see every field the API sends, including ones the library doesn't read yet, run
[`scripts/dump_api_payloads.py`](scripts/README.md#dump_api_payloadspy). See the
[Debug Guide](docs/DEBUG_GUIDE.md) for more.

## Development

```bash
git clone https://github.com/davecpearce/pysmartcocoon.git
cd pysmartcocoon
pip install -r requirements_test.txt && pip install -e .

pytest -m "not integration"   # integration tests use your real account
mypy pysmartcocoon
pre-commit run --all-files    # the same lint gate CI runs
```

A VS Code dev container is included; see
[docs/DEVCONTAINER_README.md](docs/DEVCONTAINER_README.md). Releases are published to
PyPI automatically when a version tag is pushed; see
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md#releasing).

## Documentation

- [CHANGELOG.md](CHANGELOG.md): what changed in each release
- [Debug Guide](docs/DEBUG_GUIDE.md): debug logging and troubleshooting
- [Debugging fan connection status](DEBUG_FAN_CONNECTION.md)
- [Contributing](docs/CONTRIBUTING.md): code style, tests and releases
- [Dev container](docs/DEVCONTAINER_README.md)
- [Scripts](scripts/README.md)

## License

MIT. See [LICENSE.md](LICENSE.md).

[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/davepearce
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/davecpearce/pysmartcocoon.svg?style=for-the-badge
[commits]: https://github.com/davecpearce/pysmartcocoon/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/davecpearce/pysmartcocoon.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40davecpearce-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/davecpearce/pysmartcocoon.svg?style=for-the-badge
[releases]: https://github.com/davecpearce/pysmartcocoon/releases
[user_profile]: https://github.com/davecpearce
