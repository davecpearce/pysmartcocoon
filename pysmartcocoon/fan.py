"""Define a SmartCocoon Fan class."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Optional

import paho.mqtt.client as mqtt

from pysmartcocoon.api import SmartCocoonAPI
from pysmartcocoon.const import (
    API_FANS_URL,
    API_URL,
    DEFAULT_FAN_POWER_PCT,
    MQTT_BROKER,
    MQTT_KEEPALIVE,
    MQTT_PORT,
    EntityType,
    FanMode,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Fan:
    """Define the fan."""

    def __init__(
        self,
        fan_id: str,
        api: SmartCocoonAPI,
        async_update_fan_callback: Optional[Callable[[str, Any], None]] = None,
    ) -> None:
        """Initialize."""

        # Fan attributes from SmartCocoon
        self._fan_id: int = fan_id
        self._id: int = None
        self._fan_on: bool = None
        self._firmware_version: str = None
        self._is_room_estimating: bool = None
        self._connected: bool = None
        self._last_connection: datetime = None
        self._mode: str = None
        self._power: int = None
        self._predicted_room_temperature: float = None
        self._room_id: int = None
        self._thermostat_vendor: int = None
        self._mqtt_username: str = None
        self._mqtt_password: str = None

        # Extra attributes not provided by API
        self._room_name: str = None

        self._api = api

        # MQTT attributes
        self._async_update_fan_callback = async_update_fan_callback
        self._mqtt_connected = False
        self._mqttc: mqtt.Client = None
        self._loop = asyncio.get_running_loop()

    @property
    def id(self) -> str:
        """Return Fan id.

        This is a numerical ID generated by SmartCocoon
        This value can change if the fan is re-added to
        an cloud account
        """
        return self._id

    @property
    def fan_id(self) -> str:
        """Return Fan fan_id.

        This is the physical ID printed on the fan
        """
        return self._fan_id

    @property
    def fan_on(self) -> str:
        """Return a bool indicating if the fan is on or off
        On = True
        Off = False
        """
        return self._fan_on

    @property
    def firmware_version(self) -> str:
        """Return the firmware version of the fan"""
        return self._firmware_version

    @property
    def is_room_estimating(self) -> bool:
        """Return value to indicate if the room is estimating temp
        Estimating = True
        Not Estimating = False
        """
        return self._is_room_estimating

    @property
    def connected(self) -> bool:
        """Return a bool indicating if the fan is connected
        Connected = True
        Not Connected = False
        """
        return self._connected

    @property
    def last_connection(self) -> datetime:
        """Return a bool indicating if the fan is connected
        Connected = True
        Not Connected = False
        """
        return self._last_connection

    @property
    def mode(self) -> str:
        """Return the current mode setting of the fan"""
        return self._mode

    @property
    def mode_enum(self) -> FanMode:
        """Return the current mode setting of the fan"""
        return FanMode(self._mode)

    @property
    def power(self) -> int:
        """Return the current power setting of the fan
        % value is multiplied by 100
        100% = power level of 10000
        """
        return self._power

    @property
    def speed_pct(self) -> int:
        """Return the current power setting of the fan
        by %
        """
        return self._power / 100

    @property
    def predicted_room_temperature(self) -> float:
        """Return the predicted room temperature of the fan"""
        return self._predicted_room_temperature

    @property
    def room_name(self) -> str:
        """Return the room name of the fan"""
        return self._room_name

    def set_speed_pct(self, fan_speed_pct: int) -> bool:
        """Update the power of the fan"""

        if fan_speed_pct > 100:
            _LOGGER.debug(
                "Fan ID: %s - Fan speed of %s%% is invalid, must be "
                "between 0%% and 100%%",
                self.fan_id,
                str(fan_speed_pct),
            )

        _LOGGER.debug(
            "Fan ID: %s - Updating fan speed to %s%%", self.fan_id, str(fan_speed_pct)
        )

        self._power = fan_speed_pct * 100
        return True

    def set_room_name(self, room_name: str) -> bool:
        """Update the room_name"""

        _LOGGER.debug("Fan ID: %s - Updating room_name to '%s'", self.fan_id, room_name)

        self._room_name = room_name
        return True

    @property
    def room_id(self) -> str:
        """Return the room id of the fan"""
        return self._room_id

    @property
    def thermostat_vendor(self) -> str:
        """Return the thermostat vendor of the fan"""
        return self._thermostat_vendor

    @property
    def mqtt_username(self) -> str:
        """Return the MQTT username of the fan"""
        return self._mqtt_username

    @property
    def mqtt_password(self) -> str:
        """Return the MQTT password of the fan"""
        return self._mqtt_password

    async def async_set_fan_modes(
        self, fan_mode: FanMode = None, fan_speed_pct: int = None
    ) -> bool:
        """Set the fan mode and speed."""

        _LOGGER.debug(
            "Fan ID: %s - In async_set_fan_mode with fan_mode: "
            "%s and fan_speed: %s%%",
            self.fan_id,
            fan_mode,
            str(fan_speed_pct),
        )

        if fan_mode is None and fan_speed_pct is None:
            _LOGGER.debug(
                "async_set_fan_modes must provide a value for "
                "fan_mode and/or fan_speed"
            )
            return False

        if fan_mode is None:
            # Determine value for fan_mode
            if fan_speed_pct == 0:
                if self.mode_enum is FanMode.ON:
                    fan_mode = FanMode.OFF
                else:
                    fan_mode = self.mode_enum
            else:
                if self.mode_enum is FanMode.OFF:
                    fan_mode = FanMode.ON
                else:
                    fan_mode = self.mode_enum

        # Update fan mode if changed
        if self.mode_enum != fan_mode:
            self._mode = fan_mode.value

        if fan_speed_pct is None:
            if fan_mode is FanMode.OFF:
                fan_speed_pct = self.speed_pct
            elif fan_mode is FanMode.ON and self.speed_pct == 0:
                fan_speed_pct = DEFAULT_FAN_POWER_PCT
            else:
                fan_speed_pct = self.speed_pct
        else:
            if fan_speed_pct > 100:
                _LOGGER.debug(
                    "Fan ID: %s - Fan speed of %s%% is invalid, "
                    "must be between 0%% and 100%%",
                    self.fan_id,
                    str(fan_speed_pct),
                )
                return False

        # Update power if changed
        if self.speed_pct != fan_speed_pct:
            self.set_speed_pct(fan_speed_pct)

        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["mode"] = self.mode
        request_body["json"]["power"] = self.power

        await self._api.async_request("PUT", f"{API_FANS_URL}{self.id}", **request_body)

        _LOGGER.debug(
            "Fan ID: %s - Fan Mode was set to %s, speed to %s",
            self.fan_id,
            self.mode,
            self.speed_pct,
        )

        if fan_mode == FanMode.ON.value and not self.fan_on:
            _LOGGER.debug("Fan ID: %s - Changing fan_on to 'True'", self.fan_id)
            self._fan_on = True
        elif fan_mode == FanMode.OFF.value:
            _LOGGER.debug("Fan ID: %s - Changing fan_on to 'False'", self.fan_id)
            self._fan_on = False

    async def async_update_api_data(
        self,
        data: dict[str, Any],
    ) -> bool:
        """Selectively update the fan attributes with API data"""

        _LOGGER.debug("Fan ID: %s - In async_update_api_data", data["fan_id"])

        self._id: int = data["id"]
        self._fan_id: str = data["fan_id"]

        # Fan attributes from SmartCocoon
        self._mode: str = data["mode"]

        # fan_on does not always reflect the current mode, mode is more
        # accurate if set to always_on or always_off

        if self._mode == FanMode.ON.value:
            self._fan_on = True
        elif self._mode == FanMode.OFF.value:
            self._fan_on = False
        else:
            self._fan_on: bool = data["fan_on"]

        self._firmware_version = data["firmware_version"]
        self._is_room_estimating = data["is_room_estimating"]
        self._connected = data["connected"]
        self._last_connection = data["last_connection"]
        self._power = data["power"]
        self._predicted_room_temperature = data["predicted_room_temperature"]
        self._room_id = data["room_id"]
        self._thermostat_vendor = data["thermostat_vendor"]
        self._mqtt_username = data["mqtt_username"]
        self._mqtt_password = data["mqtt_password"]

    async def async_set_async_update_fan_callback(
        self, async_update_fan_callback: Callable[[str, Any], None]
    ) -> None:

        self._async_update_fan_callback = async_update_fan_callback

    async def _async_update_fan(self) -> bool:

        _LOGGER.debug("Fan ID: %s - Updating fan attributes from cloud", self.fan_id)

        entity = EntityType.FANS.value
        response = await self._api.async_request("GET", f"{API_URL}{entity}/{self._id}")

        if len(response) is not None:
            await self.async_update_api_data(response)

            if self._async_update_fan_callback:
                _LOGGER.debug(
                    "Fan ID: %s - Executing callback for fan update", self.fan_id
                )
                await self._async_update_fan_callback()
                _LOGGER.debug(
                    "Fan ID: %s - Completed callback for fan update", self.fan_id
                )

        return True

    def _mqtt_on_connect(self, _mqttc, userdata, flags, rc: int):
        if rc == 0:
            _LOGGER.debug("Fan ID: %s - MQTT connection successful", self.fan_id)
            self._mqtt_connected = True
        else:
            _LOGGER.debug("Fan ID: %s - MQTT connection failed %i", self.fan_id, rc)
            self._mqtt_connected = False

    def _mqtt_on_disconnect(self, _mqttc, userdata, rc: int):
        if rc == 0:
            _LOGGER.debug(
                "Fan ID: %s - MQTT has been successfully" "disconnected", self.fan_id
            )
        else:
            _LOGGER.debug(
                "Fan ID: %s - MQTT unexpected disconnect: %i", self.fan_id, rc
            )
            asyncio.run_coroutine_threadsafe(self._async_start_mqtt(), self._loop)

        self._mqtt_connected = False

    def _mqtt_on_message_status(self, _mqttc, userdata, message: mqtt.MQTTMessage):
        payload = str(message.payload)
        _LOGGER.debug("Fan ID: %s - MQTT message received: %s", self.fan_id, payload)

        # Format of topic should be "nnnn_fan_id/status"
        # Where nnnn = location_id

        # Ignore if payload contains 'sendKeepAlive'
        if payload.find("sendKeepAlive"):
            asyncio.run_coroutine_threadsafe(self._async_update_fan(), self._loop)

    async def _async_start_mqtt(self) -> bool:
        """Start MQTT subscriptions."""

        _LOGGER.debug("Fan ID: %s - In async_start_mqtt", self.fan_id)

        if self.mqtt_username is None:
            _LOGGER.debug("Fan ID: %s - MQTT username is not provided", self.fan_id)
            return False

        client_id = mqtt.base62(uuid.uuid4().int, padding=22)
        self._mqttc = mqtt.Client(client_id, protocol=mqtt.MQTTv311)
        self._mqttc.username_pw_set(self.mqtt_username, password=self.mqtt_password)
        self._mqttc.on_connect = self._mqtt_on_connect
        self._mqttc.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_KEEPALIVE)
        self._mqttc.on_disconnect = self._mqtt_on_disconnect
        self._mqttc.message_callback_add(
            f"{self._mqtt_username}/status", self._mqtt_on_message_status
        )
        self._mqttc.subscribe(f"{self._mqtt_username}/status")
        self._mqttc.loop_start()
        return True

    async def _async_stop_mqtt(self) -> bool:
        """Stop MQTT subscriptions."""

        _LOGGER.debug("Fan ID: %s - Stopping MQTT", self.fan_id)

        self._mqttc.disconnect()
        self._mqttc.loop_stop()

    async def async_start_services(self) -> bool:
        """Start all services."""

        _LOGGER.debug("Fan ID: %s - Starting services", self.fan_id)
        await self._async_start_mqtt()

    async def async_stop_services(self) -> bool:
        """Stop all services."""

        _LOGGER.debug("Fan ID: %s - Stopping services", self.fan_id)
        await self._async_stop_mqtt()
