"""Tests SmartCocoon api module."""
import asyncio
import logging
import time

import aiohttp
import pytest

from pysmartcocoon.fan import Fan
from pysmartcocoon.manager import SmartCocoonManager

# Enter correct real values here for the tests to complete successfully
# with real SmartCocoon Server calls.
USERNAME = "user@domain.com"
PASSWORD = "password"
FAN_ID = "1abc23"  # This is the physical fan ID printed from the fan

logging.basicConfig(level=logging.DEBUG)
_LOGGER: logging.Logger = logging.getLogger(__name__)


@pytest.mark.skip(
    "Not an automated test but an example of usage with real values."
)
def async_fan_update_callback(fan: Fan) -> None:
    """Handle fan updates."""
    msg = (
        f"Received an update for Fan %s{fan.fan_id}: "
        f"fan_on = {fan.fan_on}, power: {fan.power}, "
        f"mode: {fan.mode}"
    )
    _LOGGER.debug(msg)


async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(session=session)

        if not await manager.async_start_services(USERNAME, PASSWORD):
            _LOGGER.debug("Authentication failed")
            return

        # Test fan controls
        wait_for = 5

        await manager.async_fan_turn_on(FAN_ID)
        time.sleep(wait_for)
        await manager.async_set_fan_speed(FAN_ID, 50)
        time.sleep(wait_for)
        await manager.async_set_fan_speed(FAN_ID, 100)
        time.sleep(wait_for)
        await manager.async_set_fan_auto(FAN_ID)
        time.sleep(wait_for)
        await manager.async_set_fan_eco(FAN_ID)
        time.sleep(wait_for)
        await manager.async_fan_turn_off(FAN_ID)
        time.sleep(wait_for)

        await manager.async_stop_services()


asyncio.run(test_integration_fan_control())
