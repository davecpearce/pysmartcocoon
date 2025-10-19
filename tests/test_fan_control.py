"""Tests SmartCocoon api module.

Note: Integration tests in this file are marked with @pytest.mark.integration
and will NOT run in GitHub Actions CI. They require real API credentials
and are only intended for local development and testing.
"""

import asyncio
import logging
import sys
from os import environ
from os.path import dirname, join

import aiohttp
import pytest
from dotenv import load_dotenv

from pysmartcocoon.const import FanMode
from pysmartcocoon.manager import SmartCocoonManager

# Removed unused cast import


# Load the account information
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Environment variables will be checked inside test functions

logging.basicConfig(level=logging.DEBUG)
_LOGGER: logging.Logger = logging.getLogger(__name__)


if environ.get("RUN_INTEGRATION") != "1":
    pytestmark = pytest.mark.skip(
        reason="Set RUN_INTEGRATION=1 to run integration tests"
    )


async def _fan_control(user: str, pwd: str, fid: str) -> None:
    """Test authentication then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(session=session)

        if not await manager.async_start_services(username=user, password=pwd):
            _LOGGER.debug("Authentication failed")
            return

        # Test fan controls
        wait_for = 5

        await manager.async_fan_turn_on(fid)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_speed(fid, 50)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_speed(fid, 100)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_auto(fid)
        await asyncio.sleep(wait_for)
        await manager.async_set_fan_eco(fid)
        await asyncio.sleep(wait_for)
        await manager.async_fan_turn_off(fid)
        await asyncio.sleep(wait_for)


@pytest.mark.integration
def test_integration_fan_control() -> None:
    """Integration smoke: fan control flow."""
    # Check for required environment variables
    test_username = environ.get("USERNAME")
    test_password = environ.get("PASSWORD")
    test_fan_id = environ.get("FAN_ID")

    if not test_username or not test_password or not test_fan_id:
        pytest.skip(
            "Missing required environment variables: "
            "USERNAME, PASSWORD, FAN_ID"
        )

    asyncio.run(_fan_control(test_username, test_password, test_fan_id))


async def _fan_modes(user: str, pwd: str, fid: str) -> None:
    """Smoke test: set fan modes and verify reported state."""

    async with aiohttp.ClientSession() as session:
        manager = SmartCocoonManager(session=session)

        if not await manager.async_start_services(username=user, password=pwd):
            _LOGGER.debug("Authentication failed")
            return

        wait_for = int(environ.get("INTEGRATION_WAIT", 3))

        await manager.async_fan_turn_on(fid)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[fid].mode_enum == FanMode.ON

        await manager.async_set_fan_speed(fid, 33)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        # Mode should remain ON when changing speed
        assert manager.fans[fid].mode_enum == FanMode.ON

        await manager.async_set_fan_auto(fid)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[fid].mode_enum == FanMode.AUTO

        await manager.async_set_fan_eco(fid)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[fid].mode_enum == FanMode.ECO

        await manager.async_fan_turn_off(fid)
        await asyncio.sleep(wait_for)
        await manager.async_update_fans()
        assert manager.fans[fid].mode_enum == FanMode.OFF


@pytest.mark.integration
def test_integration_fan_modes() -> None:
    """Integration smoke: verify fan mode transitions."""
    # Check for required environment variables
    test_username = environ.get("USERNAME")
    test_password = environ.get("PASSWORD")
    test_fan_id = environ.get("FAN_ID")

    if not test_username or not test_password or not test_fan_id:
        pytest.skip(
            "Missing required environment variables: "
            "USERNAME, PASSWORD, FAN_ID"
        )

    asyncio.run(_fan_modes(test_username, test_password, test_fan_id))


async def _test_debug_logging(user: str, pwd: str) -> None:
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
            username=user, password=pwd
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
    # Check for required environment variables
    test_username = environ.get("USERNAME")
    test_password = environ.get("PASSWORD")
    test_fan_id = environ.get("FAN_ID")

    if not test_username or not test_password or not test_fan_id:
        pytest.skip(
            "Missing required environment variables: "
            "USERNAME, PASSWORD, FAN_ID"
        )

    asyncio.run(_test_debug_logging(test_username, test_password))


if __name__ == "__main__":
    # Allow manual execution outside pytest
    username = environ.get("USERNAME")
    password = environ.get("PASSWORD")
    fan_id = environ.get("FAN_ID")

    if not username or not password or not fan_id:
        print(
            "Missing required environment variables: "
            "USERNAME, PASSWORD, FAN_ID"
        )
        sys.exit(1)

    asyncio.run(_test_debug_logging(username, password))
    asyncio.run(_fan_control(username, password, fan_id))
    asyncio.run(_fan_modes(username, password, fan_id))
