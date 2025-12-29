#!/usr/bin/env python3
"""Debug script to check fan connection status from SmartCocoon API.

This script helps debug whether the cloud API is reporting a fan as connected
or if there's an issue in pysmartcocoon's handling of the connection status.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from pysmartcocoon import SmartCocoonManager

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

_LOGGER = logging.getLogger(__name__)


def load_env_file() -> bool:
    """Load .env file from various locations."""
    env_paths = [
        Path(__file__).parent / ".env",  # tests/.env (preferred)
        Path(__file__).parent.parent / ".env",  # project root .env
        Path.cwd() / ".env",
        Path.home() / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            _LOGGER.info("Loaded .env file from: %s", env_path)
            return True

    _LOGGER.info("No .env file found, using environment variables")
    load_dotenv()  # Try loading from current directory
    return False


def get_credentials() -> tuple[str, str]:
    """Get username and password from environment."""
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        _LOGGER.error(
            "Please set USERNAME and PASSWORD in .env file or "
            "environment variables"
        )
        _LOGGER.error("Create a .env file with:")
        _LOGGER.error('  USERNAME="your_username"')
        _LOGGER.error('  PASSWORD="your_password"')
        _LOGGER.error("Or see tests/template.env for an example")
        sys.exit(1)

    return username, password


def log_raw_api_data(raw_data: dict) -> None:
    """Log raw API response data."""
    _LOGGER.info("\n📡 RAW API RESPONSE:")
    _LOGGER.info(
        "  connected: %s (type: %s)",
        raw_data.get("connected"),
        type(raw_data.get("connected")),
    )
    _LOGGER.info("  last_connection: %s", raw_data.get("last_connection"))
    _LOGGER.info("  fan_on: %s", raw_data.get("fan_on"))
    _LOGGER.info("  mode: %s", raw_data.get("mode"))

    # Show full raw data
    _LOGGER.info("\n📋 FULL RAW API DATA:")
    for key, value in raw_data.items():
        _LOGGER.info("  %s: %s (type: %s)", key, value, type(value).__name__)


def log_processed_values(fan) -> None:
    """Log processed pysmartcocoon values."""
    _LOGGER.info("\n📦 PYSMARTCOCOON PROCESSED VALUES:")
    _LOGGER.info("  connected: %s", fan.connected)
    _LOGGER.info("  last_connection: %s", fan.last_connection)
    _LOGGER.info("  fan_on: %s", fan.fan_on)
    _LOGGER.info("  mode: %s", fan.mode)

    # Calculate time since last connection
    if fan.last_connection:
        time_since = (
            datetime.now(fan.last_connection.tzinfo) - fan.last_connection
        )
        _LOGGER.info("  time_since_connection: %s", time_since)


def log_analysis(fan) -> None:
    """Log analysis of connection status."""
    _LOGGER.info("\n🔍 ANALYSIS:")
    if fan.connected:
        if fan.last_connection:
            time_since = (
                datetime.now(fan.last_connection.tzinfo) - fan.last_connection
            )
            hours_ago = time_since.total_seconds() / 3600
            _LOGGER.info("  ⚠️  Fan is reported as CONNECTED")
            time_str = str(time_since)
            _LOGGER.info(
                "  Last seen: %s ago (%.1f hours)", time_str, hours_ago
            )
            if hours_ago > 24:
                _LOGGER.warning(
                    "  ⚠️  WARNING: Last connection was over 24 hours ago!"
                )
        else:
            _LOGGER.warning(
                "  ⚠️  Fan is reported as CONNECTED but "
                "last_connection is None!"
            )
    else:
        _LOGGER.info("  ✓ Fan is correctly reported as NOT CONNECTED")


async def debug_fan_connection(target_fan_id: str | None = None) -> None:
    """Debug fan connection status."""
    load_env_file()
    username, password = get_credentials()

    manager = SmartCocoonManager()

    _LOGGER.info("Authenticating with SmartCocoon API...")
    if not await manager.async_start_services(username, password):
        _LOGGER.error("Failed to authenticate")
        sys.exit(1)

    _LOGGER.info("Fetching fan data...")
    await manager.async_update_data()

    fans = manager.fans

    if not fans:
        _LOGGER.warning("No fans found")
        return

    separator = "=" * 80
    _LOGGER.info("\n%s", separator)
    _LOGGER.info("FAN CONNECTION STATUS DEBUG")
    _LOGGER.info("%s", separator)

    for fan_id_key, fan in fans.items():
        if target_fan_id and fan_id_key != target_fan_id:
            continue

        _LOGGER.info("\nFan ID: %s", fan.fan_id)
        _LOGGER.info("-" * 80)

        # Get raw API data by calling the API directly
        if fan.identifier:
            _LOGGER.info(
                "Fetching raw API data for fan identifier: %s", fan.identifier
            )
            # Access the API from the manager
            api = manager._api  # pylint: disable=protected-access
            raw_data = await api.async_get_fan(fan.identifier)

            if raw_data:
                log_raw_api_data(raw_data)

        log_processed_values(fan)
        log_analysis(fan)
        separator = "=" * 80
        _LOGGER.info("\n%s", separator)


if __name__ == "__main__":
    target_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(debug_fan_connection(target_id))
