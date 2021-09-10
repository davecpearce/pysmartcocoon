"""Define a SmartCocoon Room class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any, Dict

class Room:  # pylint: disable=too-many-instance-attributes
    """Define the room."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize."""
        self._id: int = data["id"]
        self._name: str = data["name"]
        self._desired_temperature: float = data["desired_temperature"]
        self._hvac_mode: str = data["hvac_mode"]
        self._hvac_state: str = data["hvac_state"]
        self._is_estimating: bool = data["is_estimating"]
        self._predicted_temperature: float = data["predicted_temperature"]
        self._target_temperature: float = data["target_temperature"]
        self._temperature: float = data["temperature"]
        self._thermostat_id: int = data["thermostat_id"]

    @property
    def id(self) -> str: 
        """Return Room id.
          
           This is a numerical ID generated by SmartCocoon
           This value can change if the room is re-added to 
           an cloud account
        """
        return self._id


    @property
    def name(self) -> str: 
        """Return Room name"""
        return self._name