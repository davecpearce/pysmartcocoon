"""Define a SmartCocoon external sensor.

SmartCocoon sells a temperature and humidity sensor that is paired to a
room. The API reports it inside that room's entry in the `rooms` response,
as an `external_sensor` object (ha-smartcocoon#422):

    "external_sensor": {
      "id": 13004,
      "mac_address": "BC:57:29:..",
      "temperature": 19.85,
      "humidity": 52.95,
      "battery_level": 3002.0,
      "created_at": "2026-07-05T13:51:10.977Z",
      "updated_at": "2026-11-12T01:49:23.736Z",
      "last_connection": "2026-11-12T01:49:15.000Z"
    }

Unlike most of this API, the readings arrive as numbers rather than
strings, but they are coerced the same way in case that changes.
"""

# pylint: disable=too-few-public-methods,too-many-instance-attributes

from datetime import datetime
from typing import Any, Optional

from pysmartcocoon.convert import as_float, as_int


def _as_datetime(value: Any) -> Optional[datetime]:
    """Return an ISO 8601 timestamp as an aware datetime, or None."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class ExternalSensor:
    """A temperature and humidity sensor paired to a room."""

    def __init__(self, data: dict[str, Any], room_id: int) -> None:
        """Initialize from the `external_sensor` object of a room."""
        self._identifier: Optional[int] = as_int(data.get("id"))
        self._room_id: int = room_id
        self._mac_address: Optional[str] = data.get("mac_address") or None
        self._temperature: Optional[float] = as_float(data.get("temperature"))
        self._humidity: Optional[float] = as_float(data.get("humidity"))
        self._battery_level: Optional[float] = as_float(
            data.get("battery_level")
        )
        self._updated_at: Optional[datetime] = _as_datetime(
            data.get("updated_at")
        )
        self._last_connection: Optional[datetime] = _as_datetime(
            data.get("last_connection")
        )

    @property
    def identifier(self) -> Optional[int]:
        """Return the sensor's numeric id."""
        return self._identifier

    @property
    def room_id(self) -> int:
        """Return the id of the room the sensor is paired to."""
        return self._room_id

    @property
    def mac_address(self) -> Optional[str]:
        """Return the sensor's MAC address."""
        return self._mac_address

    @property
    def temperature(self) -> Optional[float]:
        """Return the temperature in degrees Celsius."""
        return self._temperature

    @property
    def humidity(self) -> Optional[float]:
        """Return the relative humidity in percent."""
        return self._humidity

    @property
    def battery_level(self) -> Optional[float]:
        """Return the battery level exactly as the API reports it.

        Not documented. Live values sit around 3000 for sensors on fresh
        batteries, which reads as millivolts; see battery_voltage.
        """
        return self._battery_level

    @property
    def battery_voltage(self) -> Optional[float]:
        """Return the battery level in volts, assuming millivolts.

        Inferred, not documented: sensors on fresh batteries report about
        3000, consistent with a 3 V cell measured in millivolts.
        """
        if self._battery_level is None:
            return None
        return round(self._battery_level / 1000, 3)

    @property
    def updated_at(self) -> Optional[datetime]:
        """Return when the cloud last updated this sensor's record."""
        return self._updated_at

    @property
    def last_connection(self) -> Optional[datetime]:
        """Return when the sensor last reported in."""
        return self._last_connection
