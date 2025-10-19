"""Tests SmartCocoon api module."""

import asyncio
import logging
from os import environ
from os.path import dirname, join
from typing import cast

import aiohttp
import pytest
from dotenv import load_dotenv

from pysmartcocoon.const import FanMode
from pysmartcocoon.manager import SmartCocoonManager

# Load the account information
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Get environment variables with proper type handling
_username = environ.get("USERNAME")
_password = environ.get("PASSWORD")
_fan_id = environ.get("FAN_ID")

# Type guards to ensure we have the required values
if not _username or not _password or not _fan_id:
    raise ValueError(
        "Missing required environment variables: USERNAME, PASSWORD, FAN_ID"
    )

# Cast to str after confirming they're not None
USERNAME = cast(str, _username)
PASSWORD = cast(str, _password)
FAN_ID = cast(str, _fan_id)

logging.basicConfig(level=logging.DEBUG)
_LOGGER: logging.Logger = logging.getLogger(__name__)


if environ.get("RUN_INTEGRATION") != "1":
    pytestmark = pytest.mark.skip(
        reason="Set RUN_INTEGRATION=1 to run integration tests"
    )


async def _fan_control() -> None:
    """Test authentication then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(session=session)

        if not await manager.async_start_services(
            username=USERNAME, password=PASSWORD
        ):
            _LOGGER.debug("Authentication failed")
            return

        # Test fan controls
        wait_for = 5

        await manager.async_fan_turn_on(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_speed(FAN_ID, 50)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_speed(FAN_ID, 100)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_auto(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_eco(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_fan_turn_off(FAN_ID)
        await asyncio.sleep(wait_for)


@pytest.mark.integration
def test_integration_fan_control() -> None:
    """Integration smoke: fan control flow."""
    asyncio.run(_fan_control())


async def _fan_modes() -> None:
    """Smoke test: set fan modes and verify reported state."""

    async with aiohttp.ClientSession() as session:
        manager = SmartCocoonManager(session=session)

        if not await manager.async_start_services(
            username=USERNAME, password=PASSWORD
        ):
            _LOGGER.debug("Authentication failed")
            return

        wait_for = int(environ.get("INTEGRATION_WAIT", 3))

        await manager.async_fan_turn_on(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[FAN_ID].mode_enum == FanMode.ON

        await manager.async_set_fan_speed(FAN_ID, 33)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        # Mode should remain ON when changing speed
        assert manager.fans[FAN_ID].mode_enum == FanMode.ON

        await manager.async_set_fan_auto(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[FAN_ID].mode_enum == FanMode.AUTO

        await manager.async_set_fan_eco(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[FAN_ID].mode_enum == FanMode.ECO

        await manager.async_fan_turn_off(FAN_ID)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[FAN_ID].mode_enum == FanMode.OFF


@pytest.mark.integration
def test_integration_fan_modes() -> None:
    """Integration smoke: verify fan mode transitions."""
    asyncio.run(_fan_modes())


async def _test_debug_logging() -> None:
    """Test debug logging functionality."""
    _LOGGER.info("=== Testing Debug Logging Functionality ===")

    async with aiohttp.ClientSession() as session:
        manager = SmartCocoonManager(session=session)

        _LOGGER.info(
            "Manager created - debug logging should show detailed API calls"
        )
        _LOGGER.info("Attempting authentication (watch for debug output)...")

        # This should trigger debug logging for the authentication API call
        auth_result = await manager.async_start_services(
            username=USERNAME, password=PASSWORD
        )

        if auth_result:
            _LOGGER.info(
                "Authentication successful - debug logging should have shown:"
            )
            _LOGGER.info("- API REQUEST details (method, URL, headers, body)")
            _LOGGER.info("- API RESPONSE details (status, headers, body)")
            _LOGGER.info("- AUTHENTICATION SUCCESS details (user info, token)")

            # Test a simple API call to show more debug output
            _LOGGER.info(
                "Testing fan data retrieval (watch for more debug output)..."
            )
            await manager.async_update_fans()
            _LOGGER.info(
                "Fan data retrieved - debug logging should have shown details"
            )
        else:
            _LOGGER.warning(
                "Authentication failed - check debug output for error details"
            )


@pytest.mark.integration
def test_integration_debug_logging() -> None:
    """Integration test: verify debug logging functionality."""
    asyncio.run(_test_debug_logging())


if __name__ == "__main__":
    # Allow manual execution outside pytest
    asyncio.run(_test_debug_logging())
    asyncio.run(_fan_control())
    asyncio.run(_fan_modes())
