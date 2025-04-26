"""Define a SmartCocoon Rocation class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any


class Location:  # pylint: disable=too-many-instance-attributes
    """Define the location."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize."""
        self._identifier: int = data["id"]
        self._postal_code: str = data["location"]["postal_code"]

    @property
    def identifier(self) -> str:
        """Return location id"""
        return self._identifier

    @property
    def postal_code(self) -> str:
        """Return postal code"""
        return self._postal_code
