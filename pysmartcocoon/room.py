"""Define a SmartCocoon Room class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any, Dict

class Room:  # pylint: disable=too-many-instance-attributes
    """Define the room."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize."""
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.desired_temperature: float = data["desired_temperature"]
        self.hvac_mode: str = data["hvac_mode"]
        self.hvac_state: str = data["hvac_state"]
        self.is_estimating: bool = data["is_estimating"]
        self.predicted_temperature: float = data["predicted_temperature"]
        self.target_temperature: float = data["target_temperature"]
        self.temperature: float = data["temperature"]
        self.thermostat_id: int = data["thermostat_id"]