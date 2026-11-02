"""TypedDicts for SmartCocoon API payloads."""

from typing import NotRequired, TypedDict


class FanPayload(TypedDict):
    """Fan payload fields returned by API.

    Checked against a live response on 2026-11-02. Decimals arrive as
    strings, and `thermostat_vendor` is a name, not a number; the models
    convert on read (see convert.py).
    """

    id: int
    fan_id: str
    mode: str
    fan_on: bool
    firmware_version: str
    is_room_estimating: bool
    connected: bool
    last_connection: NotRequired[str]
    power: int
    speed_level: NotRequired[int]
    predicted_room_temperature: str
    room_id: int
    thermostat_vendor: str
    mqtt_username: str
    mqtt_password: str


class FansResponse(TypedDict):
    """Response shape for listing fans."""

    fans: list[FanPayload]
