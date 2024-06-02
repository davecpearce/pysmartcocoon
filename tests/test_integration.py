"""Tests SmartCocoon api module."""
import asyncio
import logging
import time
from os import environ
from os.path import dirname, join

import aiohttp
from dotenv import load_dotenv

from pysmartcocoon.manager import SmartCocoonManager

# Load the account information
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

USERNAME = environ.get("USERNAME")
PASSWORD = environ.get("PASSWORD")
FAN_ID = environ.get("FAN_ID")

logging.basicConfig(level=logging.DEBUG)
_LOGGER: logging.Logger = logging.getLogger(__name__)


async def test_integration_fan_control() -> None:
    """Test authentification then control fan."""

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


asyncio.run(test_integration_fan_control())
