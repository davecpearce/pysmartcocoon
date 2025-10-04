"""TypedDicts for SmartCocoon API payloads."""

from typing import NotRequired, TypedDict


class FanPayload(TypedDict):
    """Fan payload fields returned by API."""

    id: int
    fan_id: str
    mode: str
    fan_on: bool
    firmware_version: str
    is_room_estimating: bool
    connected: bool
    last_connection: NotRequired[str]
    power: int
    predicted_room_temperature: float
    room_id: int
    thermostat_vendor: int
    mqtt_username: str
    mqtt_password: str


class FansResponse(TypedDict):
    """Response shape for listing fans."""

    fans: list[FanPayload]
