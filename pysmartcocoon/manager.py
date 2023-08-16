"""Define a manager to interact with SmartCocoon"""
import asyncio
import logging
from typing import Optional

from aiohttp import ClientSession

from pysmartcocoon.api import SmartCocoonAPI
from pysmartcocoon.const import API_URL, DEFAULT_TIMEOUT, EntityType, FanMode
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
        self._fans: dict[int, Fan] = {}
        self._use_mqtt = None

    @property
    def locations(self):
        """Return list of Locations."""
        return self._locations

    @property
    def thermostats(self):
        """Return list of Thermostats."""
        return self._thermostats

    @property
    def rooms(self):
        """Return list of Rooms."""
        return self._rooms

    @property
    def fans(self):
        """Return list of Fans."""
        return self._fans

    async def async_start_services(
        self, username: str, password: str, use_mqtt: bool = True
    ) -> bool:
        """Start services"""

        _LOGGER.debug("Starting services")

        # Authenticate with the API
        self._api_connected = await self._api.async_authenticate(
            username, password
        )  # pylint: disable=line-too-long

        if self._api_connected:
            # Make API calls to initial data
            await self.async_update_data()

        # Start Fan services if enabled
        self._use_mqtt = use_mqtt
        if self._use_mqtt:
            for (
                fan_id
            ) in self._fans:  # pylint: disable=consider-using-dict-items
                _LOGGER.debug("Starting services for fan: %s", fan_id)
                await self._fans[fan_id].async_start_services()
        else:
            _LOGGER.debug("Fan services have been disabled")

        return self._api_connected

    async def async_stop_services(self) -> bool:
        """Stop servicez"""
        _LOGGER.debug("Stopping services")

        # Close the MQTT sessions managed by the fans if enabled

        if self._use_mqtt:
            for (
                fan_id
            ) in self._fans:  # pylint: disable=consider-using-dict-items
                _LOGGER.debug("Stopping services for fan: %s", fan_id)
                await self._fans[fan_id].async_stop_services()

        return True

    async def async_update_data(self) -> None:
        """Update data from SmartCocoon API"""
        tasks = []
        tasks.append(self.async_update_locations())
        tasks.append(self.async_update_thermostats())
        tasks.append(self.async_update_rooms())
        await asyncio.gather(*tasks)
        await self.async_update_fans()

    async def async_update_locations(self) -> dict[int, Location]:
        """Update location data"""
        entity = EntityType.LOCATIONS.value
        response = await self._api.async_request("GET", f"{API_URL}{entity}")

        if len(response) != 0:
            for item in response[entity]:
                location = Location(data=item)
                self._locations[location.identifier] = location

        return self._locations

    async def async_update_thermostats(self) -> dict[int, Thermostat]:
        """Update thermostate data"""
        entity = EntityType.THERMOSTATS.value
        response = await self._api.async_request("GET", f"{API_URL}{entity}")

        if len(response) != 0:
            for item in response[entity]:
                thermostat = Thermostat(data=item)
                self._thermostats[thermostat.identifier] = thermostat

        return self._thermostats

    async def async_update_rooms(self) -> dict[int, Room]:
        """Update rooms data"""
        entity = EntityType.ROOMS.value
        response = await self._api.async_request("GET", f"{API_URL}{entity}")

        if len(response) != 0:
            for item in response[entity]:
                room = Room(data=item)
                self._rooms[room.identifier] = room

        return self._rooms

    async def async_update_fans(self) -> dict[int, Fan]:
        """Update fans data"""
        entity = EntityType.FANS.value
        response = await self._api.async_request("GET", f"{API_URL}{entity}")

        if len(response) != 0:
            for data in response[entity]:
                # Check to see if Fan exists in _fans
                fan_id = data["fan_id"]

                if fan_id not in self._fans:
                    fan = Fan(fan_id=fan_id, api=self._api)
                    self._fans[fan_id] = fan

                await self._fans[fan_id].async_update_api_data(data)
                room_id = self._fans[fan_id].room_id
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
        else:
            room_name = None
            msg = f"In async_get_room_name, room_id: {room_id} was not found"
            _LOGGER.debug(msg)

        return room_name

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
