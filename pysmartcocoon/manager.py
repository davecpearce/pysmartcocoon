"""Define a manager to interact with SmartCocoon"""
import asyncio
import paho.mqtt.client as mqtt

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
import async_timeout

from datetime import datetime, timedelta
import logging

from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Optional,
)

from pysmartcocoon.const import (
    API_HEADERS,
    API_URL,
    API_AUTH_URL,
    API_FANS_URL,
    DEFAULT_TIMEOUT,
    FanMode,
    EntityType,
    MQTT_BROKER,
    MQTT_CLIENT,
    MQTT_KEEPALIVE,
    MQTT_PORT,
)

from pysmartcocoon.errors import RequestError, SmartCocoonError
from pysmartcocoon.errors import UnauthorizedError
from pysmartcocoon.errors import TokenExpiredError

from pysmartcocoon.location import Location
from pysmartcocoon.thermostat import Thermostat
from pysmartcocoon.room import Room
from pysmartcocoon.fan import Fan

logging.basicConfig(level=logging.DEBUG)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SmartCocoonManager:
    """Define the main controller class to communicate with the SmartCocoon cloud API"""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        async_update_fan_callback: Optional[Callable[[str, Any], None]] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self._session = session
        self._request_timeout = request_timeout
        self._async_update_fan_callback = async_update_fan_callback

        self._headersAuth = API_HEADERS
        self._authenticated = False

        """Variables to store SmartCocoon response data"""
        self._locations: Dict[int, Location] = {}
        self._thermostats: Dict[int, Thermostat] = {}
        self._rooms: Dict[int, Room] = {}
        self._fans: Dict[int, Fan] = {}
        self._mqttc: mqtt.Client = None
        self._mqtt_username: str = None
        self._mqtt_password: str = None
        self._loop = asyncio.get_running_loop()


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


    async def async_authenticate(
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

        response = await self._async_request("POST", API_AUTH_URL, **request_body)

        return self._authenticated
        

    async def _async_request(self, method: str, url: str, **kwargs) -> dict:
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

        data = None

        try:
            #async with async_timeout.timeout(self._request_timeout):
            async with session.request(method, url, ssl=False, headers=self._headersAuth, **kwargs) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
        except ClientError as err:
            if "401" in str(err):
                # Authentication failed
                return None        
            elif "403" in str(err):
                # Forbidden error - likely needs to re-authenticate
                return None        
        except asyncio.TimeoutError as err:
            _LOGGER.error("API call to SmartCocoon timed out")
            return None
        except:
            _LOGGER.error("API call to SmartCocoon failed")
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

        if data is not None:
            return cast(Dict[str, Any], data)
        else:
            _LOGGER.error("Response data is None")
            return

    async def async_update_data(self) -> None:
        tasks = []
        tasks.append(self.async_update_locations())
        tasks.append(self.async_update_thermostats())
        tasks.append(self.async_update_rooms())
        tasks.append(self.async_update_fans())

        await asyncio.gather(*tasks)

    async def async_update_locations(
        self
    ) -> Dict[int, Location]:

        entity = EntityType.LOCATIONS.value
        response = await self._async_request(
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
        response = await self._async_request(
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
        response = await self._async_request(
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
        response = await self._async_request(
            "GET", 
            f"{API_URL}{entity}"
        )

        if len(response) != 0:
            if self._mqtt_username is None:
                self._mqtt_username = response[entity][0]["mqtt_username"]
                self._mqtt_password = response[entity][0]["mqtt_password"]

            for item in response[entity]:
                fan = Fan(data=item)
                self._fans[fan.fan_id] = fan

        return self._fans


    async def _async_update_fan(
        self,
        fan_id: str
    ) -> Fan:

        entity = EntityType.FANS.value
        response = await self._async_request(
            "GET",
            f"{API_URL}{entity}/{self._fans[fan_id].id}"
        )

        if len(response) != None:
            fan: Fan = Fan(response)
            self._fans[fan.fan_id] = fan

        if self._async_update_fan_callback:
            await self._async_update_fan_callback(self._fans[fan.fan_id])

        return self._fans[fan.fan_id]


    async def _set_fan_mode(self, fan_id: str, fan_mode: FanMode ) -> None:
        """Set the fan mode."""

        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["mode"] = fan_mode.value

        fan = self._fans[fan_id]
        response = await self._async_request(
            "PUT", 
            f"{API_FANS_URL}{fan.id}", **request_body
        )

        if fan_mode == FanMode.ON:
            fan.fan_on = True
        elif fan_mode == FanMode.OFF:
            fan.fan_on = False


    async def async_fan_turn_on(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._set_fan_mode(fan_id, FanMode.ON)

        _LOGGER.debug("Fan %s was turned on", fan_id)


    async def async_fan_turn_off(self, fan_id: str) -> None:
        """Turn on fan."""
        await self._set_fan_mode(fan_id, FanMode.OFF)

        _LOGGER.debug("Fan %s was turned off", fan_id)


    async def async_fan_auto(self, fan_id: str) -> None:
        """Enable auto mode on fan."""
        await self._set_fan_mode(fan_id, FanMode.AUTO)

        _LOGGER.debug("Fan %s was set to auto", fan_id)


    async def async_fan_eco(self, fan_id: str) -> None:
        """Enable eco mode on fan."""
        await self._set_fan_mode(fan_id, FanMode.ECO)

        _LOGGER.debug("Fan %s was set to eco", fan_id)


    async def async_fan_set_speed(self, fan_id: str, fan_speed: int) -> None:
        """Set fan speed."""

        if fan_speed > 100:
            _LOGGER.debug("Fan speed of %s is invalid, must be between 0 and 100", fan_speed)
            return

        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["power"] = fan_speed * 100

        fan = self._fans[fan_id]
        response = await self._async_request(
            "PUT", 
            f"{API_FANS_URL}{fan.id}", **request_body
        )

        _LOGGER.debug("Fan %s speed was set to %d percent", fan_id, fan_speed)


    def _mqtt_on_connect(self, _mqttc, userdata, flags, rc: int):
        if rc == 0:
            _LOGGER.debug("MQTT connection successful")
        else:
            _LOGGER.debug("MQTT connection failed %i", rc)


    def _mqtt_on_message_status(self, _mqttc, userdata, message):
        _LOGGER.debug("MQTT message received: %s", message.payload)

        # Format of topic should be "nnnn_fan_id/status"
        # Where nnnn = location_id

        topic_l1 = message.topic.split("/")[0]
        fan_id = topic_l1.split("_")[1]

        asyncio.run_coroutine_threadsafe(self._async_update_fan(fan_id),self._loop)


    async def async_start_mqtt(self) -> bool:
        """Start MQTT subscriptions."""

        self._mqttc = mqtt.Client(MQTT_CLIENT, protocol=mqtt.MQTTv311)
        self._mqttc.username_pw_set(self._mqtt_username, password=self._mqtt_password)
        self._mqttc.on_connect = self._mqtt_on_connect
        self._mqttc.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)

        for fan in self._fans:
            self._mqttc.message_callback_add(f"{self._mqtt_username}/status",self._mqtt_on_message_status)
        self._mqttc.subscribe(f"{self._mqtt_username}/#")

        self._mqttc.loop_start()


    async def async_stop_mqtt(self) -> bool:
        """Stop MQTT subscriptions."""

        self._mqttc.disconnect()
        self._mqttc.loop_stop()
