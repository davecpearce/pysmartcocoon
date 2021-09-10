"""Define a manager to interact with SmartCocoon"""
import asyncio
import paho.mqtt.client as mqtt
import uuid
import traceback

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
import async_timeout

from datetime import datetime, timedelta
import logging

from typing import (
    Any,
    cast,
    Dict,
    Optional,
)

from pysmartcocoon.const import (
    API_URL,
    API_FANS_URL,
    DEFAULT_TIMEOUT,
    FanMode,
    EntityType,
)

from pysmartcocoon.errors import RequestError, SmartCocoonError
from pysmartcocoon.errors import UnauthorizedError
from pysmartcocoon.errors import TokenExpiredError

from pysmartcocoon.api import SmartCocoonAPI
from pysmartcocoon.location import Location
from pysmartcocoon.thermostat import Thermostat
from pysmartcocoon.room import Room
from pysmartcocoon.fan import Fan

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SmartCocoonManager:
    """Define the main controller class to communicate with the SmartCocoon cloud API"""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self._api = SmartCocoonAPI(
            session,
            request_timeout
        )

        self._api_connected: bool = False

        """Variables to store SmartCocoon response data"""
        self._locations: Dict[int, Location] = {}
        self._thermostats: Dict[int, Thermostat] = {}
        self._rooms: Dict[int, Room] = {}
        self._fans: Dict[int, Fan] = {}


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
        self,
        username: str,
        password: str
    ) -> bool:
    
        _LOGGER.debug("Starting services")

        # Authenticate with the API
        self._api_connected = await self._api.async_authenticate( username, password )

        if self._api_connected:
            # Make API calls to initial data
            await self.async_update_data()

        # Start Fan services
        _LOGGER.debug("Starting fan services")
        for fan_id in self._fans:
            await self._fans[fan_id].async_start_services()

        return self._api_connected


    async def async_stop_services(
        self
    ) -> bool:
    
        _LOGGER.debug("Stopping services")

        # Close the MQTT sessions managed by the fans

        for fan_id in self._fans:
            _LOGGER.debug("Stopping services for fan: %s", fan_id)
            await self._fans[fan_id].async_stop_services()

        return True


    async def async_update_data(self) -> None:
        tasks = []
        tasks.append(self.async_update_locations())
        tasks.append(self.async_update_thermostats())
        tasks.append(self.async_update_rooms())
        await asyncio.gather(*tasks)

        """Fans requires rooms to be loaded in order to add the 
           room_name to the fan
        """           
        await self.async_update_fans()


    async def async_update_locations(
        self
    ) -> Dict[int, Location]:

        entity = EntityType.LOCATIONS.value
        response = await self._api.async_request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                location = Location(data=item)
                self._locations[location.id] = location

        return self._locations


    async def async_update_thermostats(
        self
    ) -> Dict[int, Thermostat]:

        entity = EntityType.THERMOSTATS.value
        response = await self._api.async_request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                thermostat = Thermostat(data=item)
                self._thermostats[thermostat.id] = thermostat

        return self._thermostats


    async def async_update_rooms(
        self
    ) -> Dict[int, Room]:

        entity = EntityType.ROOMS.value
        response = await self._api.async_request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                room = Room(data=item)
                self._rooms[room.id] = room

        return self._rooms


    async def async_update_fans(
        self
    ) -> Dict[int, Fan]:

        entity = EntityType.FANS.value
        response = await self._api.async_request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for data in response[entity]:
                # Check to see if Fan exists in _fans
                fan_id = data["fan_id"]

                if fan_id not in self._fans:
                    fan = Fan(fan_id=fan_id, api=self._api)
                    self._fans[fan_id] = fan

                await self._fans[fan_id].async_update_api_data( data )
                room_name = await self.async_get_room_name(self._fans[fan_id].room_id)
                self._fans[fan_id].update_room_name(room_name)

        return self._fans


    async def async_get_room_name(
        self,
        room_id: int
    ) -> str:

        if room_id in self._rooms:
            room_name = self.rooms[room_id].name

            _LOGGER.debug("In async_get_room_name for room_id: %s, found room nane: %s",
                room_id,
                room_name
            )
        else:
            room_name = None
            _LOGGER.debug("In async_get_room_name, room_id: %s was not nout",
                room_id
            )

        return room_name


    async def async_fan_turn_on(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._fans[fan_id].async_set_fan_mode(FanMode.ON)


    async def async_fan_turn_off(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._fans[fan_id].async_set_fan_mode(FanMode.OFF)


    async def async_fan_auto(self, fan_id: str) -> None:
        """Enable auto mode on fan."""
        await self._fans[fan_id].async_set_fan_mode(FanMode.AUTO)


    async def async_fan_eco(self, fan_id: str) -> None:
        """Enable eco mode on fan."""
        await self._fans[fan_id].async_set_fan_mode(FanMode.ECO)


    async def async_fan_set_speed(self, fan_id: str, fan_speed: int) -> None:
        """Set fan speed."""

        await self._fans[fan_id].async_fan_set_speed(fan_speed)
