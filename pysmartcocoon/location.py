"""Define a SmartCocoon Rocation class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any, Dict

class Location:  # pylint: disable=too-many-instance-attributes
    """Define the location."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize."""
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.street: str = data["location"]["street"]
        self.city: str = data["location"]["city"]
        self.state: str = data["location"]["state"]
        self.country: str = data["location"]["country"]
        self.postal_code: str = data["location"]["postal_code"]