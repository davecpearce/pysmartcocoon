#!/usr/bin/env python3
"""Tests for paired external sensors (ha-smartcocoon#422).

SmartCocoon's temperature and humidity sensor is reported inside the room
it is paired to, as an `external_sensor` object in the `rooms` response.
The payloads copy the shape of a live response captured on 2026-11-12;
the values and MAC addresses are invented.
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from pysmartcocoon.errors import RequestError, UnauthorizedError
from pysmartcocoon.external_sensor import ExternalSensor
from pysmartcocoon.manager import SmartCocoonManager
from pysmartcocoon.room import Room


def _sensor(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": 13004,
        "mac_address": "AA:BB:CC:00:11:22",
        "temperature": 19.85,
        "humidity": 52.95,
        "battery_level": 3002.0,
        "created_at": "2026-07-05T13:51:10.977Z",
        "updated_at": "2026-11-12T01:49:23.736Z",
        "last_connection": "2026-11-12T01:49:15.000Z",
    }
    payload.update(overrides)
    return payload


def _room(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": 93694,
        "name": "Main Bathroom",
        "desired_temperature": "21.0",
        "predicted_temperature": "21.5",
        "is_estimating": False,
        "hvac_mode": "cool",
        "hvac_state": None,
        "temperature": None,
        "target_temperature": None,
        "thermostat_id": 79390,
        "vendor": "nonsmart",
        "fans": [],
        "external_sensor": _sensor(),
    }
    payload.update(overrides)
    return payload


class _CannedAPI:
    """Stands in for SmartCocoonAPI's request method."""

    # pylint: disable=unused-argument,too-few-public-methods

    def __init__(self, result: Any) -> None:
        self._result = result

    async def async_request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Return or raise the configured result."""
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def _manager(result: Any) -> SmartCocoonManager:
    manager = SmartCocoonManager()
    # pylint: disable=protected-access
    manager._api = _CannedAPI(result)  # type: ignore[assignment]
    return manager


# --- the model --------------------------------------------------------------


def test_room_reads_its_paired_sensor() -> None:
    """Every field of the live payload is read, with the right types."""
    sensor = Room(_room()).external_sensor

    assert sensor is not None
    assert sensor.identifier == 13004
    assert sensor.room_id == 93694
    assert sensor.mac_address == "AA:BB:CC:00:11:22"
    assert sensor.temperature == 19.85
    assert sensor.humidity == 52.95
    assert sensor.battery_level == 3002.0
    assert sensor.battery_voltage == 3.002
    assert sensor.last_connection == datetime(
        2026, 11, 12, 1, 49, 15, tzinfo=timezone.utc
    )
    assert sensor.updated_at is not None and sensor.updated_at.tzinfo


def test_room_without_a_sensor() -> None:
    """Rooms with no sensor paired, and older payloads, have none."""
    assert Room(_room(external_sensor=None)).external_sensor is None
    payload = _room()
    del payload["external_sensor"]
    assert Room(payload).external_sensor is None


def test_readings_sent_as_strings_are_converted() -> None:
    """The rest of the API sends decimals as strings; accept that here too."""
    sensor = ExternalSensor(
        _sensor(temperature="19.85", humidity="52.95"), room_id=1
    )
    assert sensor.temperature == 19.85
    assert sensor.humidity == 52.95


def test_missing_or_garbled_readings_are_none() -> None:
    """A partial payload must not raise; the missing values are None."""
    sensor = ExternalSensor(
        {"id": 1, "temperature": None, "last_connection": "not a date"},
        room_id=1,
    )
    assert sensor.temperature is None
    assert sensor.humidity is None
    assert sensor.battery_level is None
    assert sensor.battery_voltage is None
    assert sensor.last_connection is None
    assert sensor.mac_address is None


# --- refreshing -------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_rooms_updates_sensor_readings() -> None:
    """A refresh replaces the room, so the new readings are visible."""
    manager = _manager({"rooms": [_room()]})
    assert await manager.async_refresh_rooms() is True
    assert manager.external_sensors[93694].temperature == 19.85

    # pylint: disable=protected-access
    manager._api = _CannedAPI(  # type: ignore[assignment]
        {"rooms": [_room(external_sensor=_sensor(temperature=22.5))]}
    )
    assert await manager.async_refresh_rooms() is True
    assert manager.external_sensors[93694].temperature == 22.5


@pytest.mark.asyncio
async def test_external_sensors_lists_only_rooms_with_one() -> None:
    """Rooms without a paired sensor are left out."""
    manager = _manager(
        {
            "rooms": [
                _room(),
                _room(id=93695, name="Main Bedroom", external_sensor=None),
            ]
        }
    )
    assert await manager.async_refresh_rooms() is True
    assert set(manager.rooms) == {93694, 93695}
    assert set(manager.external_sensors) == {93694}


@pytest.mark.asyncio
async def test_failed_refresh_keeps_previous_readings() -> None:
    """A failed request returns False and changes nothing."""
    manager = _manager({"rooms": [_room()]})
    await manager.async_refresh_rooms()

    # pylint: disable=protected-access
    manager._api = _CannedAPI(RequestError("boom"))  # type: ignore[assignment]
    assert await manager.async_refresh_rooms() is False
    assert manager.external_sensors[93694].temperature == 19.85

    manager._api = _CannedAPI(None)  # type: ignore[assignment]
    assert await manager.async_refresh_rooms() is False
    assert manager.external_sensors[93694].temperature == 19.85


@pytest.mark.asyncio
async def test_rejected_credentials_are_raised() -> None:
    """Like async_refresh_fans, a rejected login is not a plain False."""
    manager = _manager(UnauthorizedError("401"))
    with pytest.raises(UnauthorizedError):
        await manager.async_refresh_rooms()


@pytest.mark.asyncio
async def test_one_malformed_room_does_not_block_the_others() -> None:
    """An unreadable entry is skipped; the rest still update."""
    broken = _room(id=1)
    del broken["name"]
    manager = _manager({"rooms": [broken, _room()]})
    assert await manager.async_refresh_rooms() is True
    assert set(manager.rooms) == {93694}
