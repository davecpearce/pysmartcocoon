"""Define a SmartCocoon Rocation class."""
# pylint: disable=too-few-public-methods,too-many-instance-attributes

from typing import Any


class Location:  # pylint: disable=too-many-instance-attributes
    """Define the location."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize."""
        self._identifier: int = data["id"]
        self._name: str = data["name"]
        self._street: str = data["location"]["street"]
        self._city: str = data["location"]["city"]
        self._state: str = data["location"]["state"]
        self._country: str = data["location"]["country"]
        self._postal_code: str = data["location"]["postal_code"]

    @property
    def identifier(self) -> str:
        """Return location id"""
        return self._identifier

    @property
    def name(self) -> str:
        """Return location mame"""
        return self._name

    @property
    def street(self) -> str:
        """Return street"""
        return self._street

    @property
    def city(self) -> str:
        """Return city"""
        return self._city

    @property
    def country(self) -> str:
        """Return country"""
        return self._country

    @property
    def postal_code(self) -> str:
        """Return postal code"""
        return self._postal_code
