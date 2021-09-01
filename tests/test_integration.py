# coding: utf-8
"""Tests SmartCocoon api module."""
import asyncio
import aiohttp 

import pytest

from pysmartcocoon.manager import SmartCocoonManager

# Enter correct real values here for the tests to complete successfully with real SmartCocoon Server calls.
USERNAME = "user@domain.com"
PASSWORD = "password"
FAN_ID = "1abc23"  # This is the physical fan ID printed from the fan

@pytest.mark.skip("Not an automated test but an example of usage with real values.")
async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init manager
        manager = SmartCocoonManager(session=session)

        if not await manager.authenticate( USERNAME, PASSWORD ):
            return

        await manager.load_data()

        # Test fan controls
        await manager.fan_turn_on(FAN_ID)
        await manager.fan_set_speed(FAN_ID, 50)
        await manager.fan_set_speed(FAN_ID, 100)
        await manager.fan_turn_off(FAN_ID)
        await manager.fan_auto(FAN_ID)
        await manager.fan_eco(FAN_ID)

asyncio.run(test_integration_fan_control())