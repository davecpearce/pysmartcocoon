# coding: utf-8
"""Tests SmartCocoon api module."""
import asyncio
import aiohttp 

import pytest

from pysmartcocoon import Client

# Enter correct real values here for the tests to complete successfully with real SmartCocoon Server calls.
#USERNAME = "user@domain.com"
#PASSWORD = "password"
#FAN_ID = "1abc23"  # This is the physical fan ID printed om the fan

@pytest.mark.skip("Not an automated test but an example of usage with real values.")
async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

    async with aiohttp.ClientSession() as session:
        # Init client
        client = Client(session=session)
        await client.authenticate( USERNAME, PASSWORD )
        await client.load_data()

        # Test fan controls
        await client.fan_turn_on(FAN_ID)
        await client.fan_set_speed(FAN_ID, 50)
        await client.fan_set_speed(FAN_ID, 100)
        await client.fan_turn_off(FAN_ID)

asyncio.run(test_integration_fan_control())