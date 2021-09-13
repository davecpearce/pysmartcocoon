# coding: utf-8
"""Tests SmartCocoon api module."""
import asyncio

import aiohttp 
import time
import logging

import pytest

from pysmartcocoon.manager import SmartCocoonManager
from pysmartcocoon.fan import Fan
from pysmartcocoon.const import (
    FanMode,
)

# Enter correct real values here for the tests to complete successfully with real SmartCocoon Server calls.
USERNAME = "user@domain.com"
PASSWORD = "password"
FAN_ID = "1abc23"  # This is the physical fan ID printed from the fan

logging.basicConfig(level=logging.DEBUG)
_LOGGER: logging.Logger = logging.getLogger(__name__)

@pytest.mark.skip("Not an automated test but an example of usage with real values.")


async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(
            session=session
        )

        if not await manager.async_start_services( USERNAME, PASSWORD ):
            _LOGGER.debug("Authentication failed")
            return

        # Test fan controls
        WAIT_FOR = 5

        await manager.async_fan_turn_off(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_speed(FAN_ID, 0)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_modes(
            fan_id=FAN_ID,
            fan_mode = FanMode.ON, 
            fan_speed_pct = 100)        
        time.sleep(WAIT_FOR)
        await manager.async_fan_turn_off(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_fan_turn_on(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_speed(FAN_ID, 0)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_modes(
            fan_id=FAN_ID,
            fan_mode = FanMode.ON, 
            fan_speed_pct = 33)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_speed(FAN_ID, 33)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_speed(FAN_ID, 101)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_auto(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_eco(FAN_ID)
        time.sleep(WAIT_FOR)
        await manager.async_set_fan_modes(
            fan_id=FAN_ID,
            fan_mode = None, 
            fan_speed_pct = None)
        time.sleep(WAIT_FOR)
        await manager.async_fan_turn_off(FAN_ID)
        time.sleep(WAIT_FOR)

        await manager.async_stop_services()
        logging.info("Successfully shutdown the service.")        

asyncio.run(test_integration_fan_control())