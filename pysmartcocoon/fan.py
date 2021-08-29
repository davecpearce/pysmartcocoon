"""Define a SmartCocoon Fan class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any, Dict
from datetime import datetime

class Fan:  # pylint: disable=too-many-instance-attributes
    """Define the fan."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize."""
        self.id: int = data["id"]
        self.fan_id: int = data["fan_id"]
        self.fan_on: bool = data["fan_on"]
        self.firmware_version: str = data["firmware_version"]
        self.is_room_estimating: bool = data["is_room_estimating"]
        self.connected: bool = data["connected"]
        self.last_connection: datetime = data["last_connection"]
        self.mode: str = data["mode"]
        self.mqtt_username: str = data["mqtt_username"]
        self.mqtt_password: str = data["mqtt_password"]
        self.power: int = data["power"]
        self.predicted_room_temperature: float = data["predicted_room_temperature"]
        self.room_id: int = data["room_id"]
        self.thermostat_vendor: int = data["thermostat_vendor"]