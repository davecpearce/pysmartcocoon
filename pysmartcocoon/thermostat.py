"""Define a SmartCocoon Thermostat class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any, Dict

class Thermostat:  # pylint: disable=too-many-instance-attributes
    """Define the thermostat."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize."""
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.thermostat_id: id = data["thermostat_id"]
        self.token: str = data["token"]
        self.hvac_mode: str = data["hvac_mode"]
        self.hvac_state: str = data["hvac_state"]
        self.temperature: float = data["temperature"]
        self.target_temperature: float = data["target_temperature"]
        self.vendor: str = data["vendor"]