"""Tests SmartCocoon api module."""

import asyncio
import logging
from os import environ
from os.path import dirname, join

import aiohttp
import pytest
from dotenv import load_dotenv

from pysmartcocoon.const import FanMode
from pysmartcocoon.manager import SmartCocoonManager

# Load the account information
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

USERNAME = environ.get("USERNAME")
PASSWORD = environ.get("PASSWORD")
FAN_ID = environ.get("FAN_ID")

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


if __name__ == "__main__":
    # Allow manual execution outside pytest
    asyncio.run(_fan_control())
    asyncio.run(_fan_modes())
