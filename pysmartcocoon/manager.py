"""Define a manager to interact with SmartCocoon"""

import asyncio
import logging
from typing import Any, Optional

from aiohttp import ClientSession

from pysmartcocoon.api import SmartCocoonAPI
from pysmartcocoon.const import API_URL, DEFAULT_TIMEOUT, EntityType, FanMode
from pysmartcocoon.errors import RequestError, UnauthorizedError
from pysmartcocoon.fan import Fan
from pysmartcocoon.location import Location
from pysmartcocoon.room import Room
from pysmartcocoon.thermostat import Thermostat

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SmartCocoonManager:
    """Define the main controller class to communicate with the
    SmartCocoon cloud API
    """

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._api = SmartCocoonAPI(session, request_timeout)

        self._api_connected: bool = False

        """Variables to store SmartCocoon response data"""
        self._locations: dict[int, Location] = {}
        self._thermostats: dict[int, Thermostat] = {}
        self._rooms: dict[int, Room] = {}
        self._fans: dict[str, Fan] = {}

    @property
    def locations(self) -> dict[int, Any]:
        """Return list of Locations."""
        return self._locations

    @property
    def thermostats(self) -> dict[int, Any]:
        """Return list of Thermostats."""
        return self._thermostats

    @property
    def rooms(self) -> dict[int, Any]:
        """Return list of Rooms."""
        return self._rooms

    @property
    def fans(self) -> dict[str, Any]:
        """Return list of Fans."""
        return self._fans

    async def async_start_services(self, username: str, password: str) -> bool:
        """Start services"""

        _LOGGER.debug("Starting services")

        # Authenticate with the API
        self._api_connected = await self._api.async_authenticate(
            username, password
        )  # pylint: disable=line-too-long

        if self._api_connected:
            # Make API calls to initial data
            await self.async_update_data()

        return self._api_connected

    async def async_update_data(self) -> None:
        """Update data from SmartCocoon API"""
        tasks: list[Any] = []
        tasks.append(self.async_update_locations())
        tasks.append(self.async_update_thermostats())
        tasks.append(self.async_update_rooms())
        await asyncio.gather(*tasks)
        await self.async_update_fans()

    async def async_update_locations(self) -> dict[int, Location]:
        """Update location data"""
        entity = EntityType.LOCATIONS.value
        try:
            response = await self._api.async_request(
                "GET", f"{API_URL}{entity}"
            )
        except (UnauthorizedError, RequestError) as err:
            _LOGGER.debug("Failed to update locations: %s", err)
            return self._locations

        if response and entity in response:
            for item in response[entity]:
                location = Location(data=item)
                self._locations[location.identifier] = location

        return self._locations

    async def async_update_thermostats(self) -> dict[int, Thermostat]:
        """Update thermostate data"""
        entity = EntityType.THERMOSTATS.value
        try:
            response = await self._api.async_request(
                "GET", f"{API_URL}{entity}"
            )
        except (UnauthorizedError, RequestError) as err:
            _LOGGER.debug("Failed to update thermostats: %s", err)
            return self._thermostats

        if response and entity in response:
            for item in response[entity]:
                thermostat = Thermostat(data=item)
                self._thermostats[thermostat.identifier] = thermostat

        return self._thermostats

    async def async_update_rooms(self) -> dict[int, Room]:
        """Update rooms data"""
        entity = EntityType.ROOMS.value
        try:
            response = await self._api.async_request(
                "GET", f"{API_URL}{entity}"
            )
        except (UnauthorizedError, RequestError) as err:
            _LOGGER.debug("Failed to update rooms: %s", err)
            return self._rooms

        if response and entity in response:
            for item in response[entity]:
                room = Room(data=item)
                self._rooms[room.identifier] = room

        return self._rooms

    async def async_update_fans(self) -> dict[str, Fan]:
        """Update fans data"""
        entity = EntityType.FANS.value
        try:
            response = await self._api.async_request(
                "GET", f"{API_URL}{entity}"
            )
        except (UnauthorizedError, RequestError) as err:
            _LOGGER.debug("Failed to update fans: %s", err)
            return self._fans

        if response and entity in response:
            for data in response[entity]:
                # Check to see if Fan exists in _fans
                fan_id = data["fan_id"]

                if fan_id not in self._fans:
                    fan = Fan(fan_id=fan_id, api=self._api)
                    self._fans[fan_id] = fan

                await self._fans[fan_id].async_update_api_data(data)
                room_id = self._fans[fan_id].room_id
                if room_id is not None:
                    room_name = await self.async_get_room_name(room_id)
                    self._fans[fan_id].set_room_name(room_name)

        return self._fans

    async def async_get_room_name(self, room_id: int) -> str:
        """Get room name from room"""
        if room_id in self._rooms:
            room_name = self._rooms[room_id].name

            _LOGGER.debug(
                "In async_get_room_name for room_id: %s, found room name: %s",
                room_id,
                room_name,
            )
            return room_name

        msg = f"In async_get_room_name, room_id: {room_id} was not found"
        _LOGGER.debug(msg)
        return "Unknown"

    async def async_fan_turn_on(self, fan_id: str) -> None:
        """Turn on fan."""

        await self._fans[fan_id].async_set_fan_modes(fan_mode=FanMode.ON)

    async def async_fan_turn_off(self, fan_id: str) -> None:
        """Turn on fan."""

        await self._fans[fan_id].async_set_fan_modes(fan_mode=FanMode.OFF)

    async def async_set_fan_auto(self, fan_id: str) -> None:
        """Enable auto mode on fan."""

        await self._fans[fan_id].async_set_fan_modes(fan_mode=FanMode.AUTO)

    async def async_set_fan_eco(self, fan_id: str) -> None:
        """Enable eco mode on fan."""

        await self._fans[fan_id].async_set_fan_modes(fan_mode=FanMode.ECO)

    async def async_set_fan_modes(
        self, fan_id: str, fan_mode: FanMode, fan_speed_pct: int
    ) -> None:
        """Set fan mode and speed."""

        await self._fans[fan_id].async_set_fan_modes(
            fan_mode=fan_mode, fan_speed_pct=fan_speed_pct
        )

    async def async_set_fan_speed(
        self, fan_id: str, fan_speed_pct: int
    ) -> None:
        """Set fan speed."""

        await self._fans[fan_id].async_set_fan_modes(
            fan_speed_pct=fan_speed_pct
        )
