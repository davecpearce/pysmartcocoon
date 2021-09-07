# coding: utf-8
"""Tests SmartCocoon api module."""
import asyncio
import aiohttp 
import time
import logging

import pytest

from pysmartcocoon.manager import SmartCocoonManager
from pysmartcocoon.fan import Fan

# Enter correct real values here for the tests to complete successfully with real SmartCocoon Server calls.
USERNAME = "user@domain.com"
PASSWORD = "password"
FAN_ID = "1abc23"  # This is the physical fan ID printed from the fan

_LOGGER: logging.Logger = logging.getLogger(__name__)

@pytest.mark.skip("Not an automated test but an example of usage with real values.")

def async_fan_update_callback(fan: Fan) -> None:
    """Handle fan updates."""
    _LOGGER.debug(f"Received an update for Fan {fan.fan_id}: fan_on = {fan.fan_on}, power: {fan.power}, mode: {fan.mode}")


async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(
            session=session,
            async_update_fan_callback=async_fan_update_callback
        )

        if not await manager.async_authenticate( USERNAME, PASSWORD ):
            return

        await manager.async_update_data()

        await manager.async_start_mqtt()

        await manager.async_update_fans()

        # Test fan controls
        WAIT_FOR = 5

        await manager.async_fan_turn_on(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_fan_set_speed(FAN_ID, 50)
        time.sleep(WAIT_FOR)
        await manager.async_fan_set_speed(FAN_ID, 100)
        time.sleep(WAIT_FOR)
        await manager.async_fan_auto(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_fan_eco(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_fan_turn_off(FAN_ID)
        time.sleep(WAIT_FOR)

        await manager.async_stop_mqtt()

asyncio.run(test_integration_fan_control())