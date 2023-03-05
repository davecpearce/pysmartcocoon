"""Define a client to interact with SmartCocoon"""
import asyncio

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
import async_timeout

from datetime import datetime, timedelta
import logging

from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

from pysmartcocoon.const import API_HEADERS
from pysmartcocoon.const import API_URL
from pysmartcocoon.const import API_AUTH_URL
from pysmartcocoon.const import API_FANS_URL
from pysmartcocoon.const import DEFAULT_TIMEOUT
from pysmartcocoon.const import FanMode
from pysmartcocoon.const import EntityType

from pysmartcocoon.errors import RequestError, SmartCocoonError
from pysmartcocoon.errors import UnauthorizedError
from pysmartcocoon.errors import TokenExpiredError

from pysmartcocoon.location import Location
from pysmartcocoon.thermostat import Thermostat
from pysmartcocoon.room import Room
from pysmartcocoon.fan import Fan

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Client:
    """Define the main controller class to communicate with the SmartCocoon cloud API"""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self._session = session
        self._request_timeout = request_timeout

        self._headersAuth = API_HEADERS
        self._authenticated = False

        """Variables to store SmartCocoon response data"""
        self.locations: Dict[int, Location] = {}
        self.thermostats: Dict[int, Thermostat] = {}
        self.rooms: Dict[int, Room] = {}
        self.fans: Dict[int, Fan] = {}


    async def authenticate(
        self,
        username: str,
        password: str
    ) -> bool:

        self._authenticated = False

        # Authenticate with user and pass
        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["email"] = username
        request_body["json"]["password"] = password

        response = await self._request("POST", API_AUTH_URL, **request_body)

        return self._authenticated
        

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        """Make a request using token authentication.
        Args:
            method: Method for the HTTP request (example "GET" or "POST").
            path: path of the REST API endpoint.
        Returns:
            the Response object corresponding to the result of the API request.
        """

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        assert session

        try:
            async with async_timeout.timeout(self._request_timeout):
                async with session.request(method, url, ssl=False, headers=self._headersAuth, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except ClientError as err:
            if "401" in str(err):
                # Authentication failed
                return None        
        except asyncio.TimeoutError as err:
            _LOGGER.error("API call to SmartCocoon timed out")
            return None
        finally:
            if not use_running_session:
                await session.close()

        # If this request is for authorization, save auth data
        if url == API_AUTH_URL:
            self._bearerToken: str = response.headers["access-token"]
            self._bearerTokenExpiration: datetime = datetime.now() + timedelta(
                seconds=int(response.headers["expiry"]) - 10
                )
            self._apiClient: str = response.headers["client"]

            self._headersAuth["access-token"] = self._bearerToken
            self._headersAuth["client"] = self._apiClient
            self._headersAuth["uid"] = data["data"]["email"]

            self._user_id: str = data["data"]["id"]
            self._authenticated = True

        return cast(Dict[str, Any], data)

    async def load_data(self) -> None:
        tasks = []
        tasks.append(self._load_locations())
        tasks.append(self._load_thermostats())
        tasks.append(self._load_rooms())
        tasks.append(self._load_fans())

        await asyncio.gather(*tasks)

    async def _load_locations(
        self ) -> Dict[int, Location]:

        # Init locations
        self.locations : Dict[int, Location] = {}

        entity = EntityType.LOCATIONS.value
        response = await self._request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                location = Location(data=item)
                self.locations[location.id] = location

        return self.locations


    async def _load_thermostats(
        self ) -> Dict[int, Thermostat]:

        # Init thermostats
        self.thermostats : Dict[int, Thermostat] = {}

        entity = EntityType.THERMOSTATS.value
        response = await self._request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                thermostat = Thermostat(data=item)
                self.thermostats[thermostat.id] = thermostat

        return self.thermostats


    async def _load_rooms(
        self ) -> Dict[int, Room]:

        # Init rooms
        self.rooms : Dict[int, Room] = {}

        entity = EntityType.ROOMS.value
        response = await self._request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                room = Room(data=item)
                self.rooms[room.id] = room

        return self.rooms


    async def _load_fans(
        self ) -> Dict[int, Fan]:

        # Init fans
        self.fans : Dict[int, Fan] = {}

        entity = EntityType.FANS.value
        response = await self._request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            for item in response[entity]:
                fan = Fan(data=item)
                self.fans[fan.fan_id] = fan

        return self.fans


    async def _set_fan_mode(self, fan_id: str, fan_mode: FanMode ) -> None:
        """Set the fan mode."""

        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["mode"] = fan_mode.value

        fan = self.fans[fan_id]
        response = await self._request(
            "PUT", 
            f"{API_FANS_URL}{fan.id}", **request_body
        )

        if fan_mode == FanMode.ON:
            fan.fan_on = True
        elif fan_mode == FanMode.OFF:
            fan.fan_on = False


    async def fan_turn_on(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._set_fan_mode(fan_id, FanMode.ON)

        _LOGGER.debug("Fan %s was turned on", fan_id)


    async def fan_turn_off(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._set_fan_mode(fan_id, FanMode.OFF)

        _LOGGER.debug("Fan %s was turned off", fan_id)


    async def fan_auto(self, fan_id: str) -> None:
        """Enable auto mode on fan."""
        await self._set_fan_mode(fan_id, FanMode.AUTO)

        _LOGGER.debug("Fan %s was set to auto", fan_id)

    async def fan_eco(self, fan_id: str) -> None:
        """Enable eco mode on fan."""
        await self._set_fan_mode(fan_id, FanMode.ECO)

        _LOGGER.debug("Fan %s was set to eco", fan_id)


    async def fan_set_speed(self, fan_id: str, fan_speed: int) -> None:
        """Set fan speed."""

        if fan_speed > 100:
            _LOGGER.debug("Fan speed of %s is invalid, must be between 0 and 100", fan_speed)
            return

        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["power"] = fan_speed * 100

        fan = self.fans[fan_id]
        response = await self._request(
            "PUT", 
            f"{API_FANS_URL}{fan.id}", **request_body
        )

        _LOGGER.debug("Fan %s speed was set to %s%", fan_id, fan_speed)