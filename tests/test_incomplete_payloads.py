#!/usr/bin/env python3
"""Tests for handling fan payloads that are missing fields.

Two behaviours matter here:

1. A payload missing required fields must not be applied piecemeal. Assigning
   field by field raised partway through and left the fan holding a mix of
   old and new values.
2. One unusable entry in the fan list must not abandon the whole refresh,
   which previously took every other fan's update with it.
"""

from typing import Any, Optional

import pytest

from pysmartcocoon.fan import Fan
from pysmartcocoon.manager import SmartCocoonManager

FAN_ID = "abc123"


def _payload(**overrides: Any) -> dict[str, Any]:
    """A complete fan payload, with optional overrides."""
    data: dict[str, Any] = {
        "id": 42,
        "fan_id": FAN_ID,
        "mode": "always_on",
        "fan_on": True,
        "firmware_version": "1.0.0",
        "is_room_estimating": False,
        "connected": True,
        "last_connection": "2026-08-06T12:00:00Z",
        "power": 3300,
        "predicted_room_temperature": 21.0,
        "room_id": 7,
        "thermostat_vendor": None,
        "mqtt_username": "u",
        "mqtt_password": "p",
    }
    data.update(overrides)
    return data


class _StubAPI:
    """Minimal stand-in; these tests never reach the network."""

    # Arguments mirror SmartCocoonAPI and are deliberately unused.
    # pylint: disable=unused-argument,too-few-public-methods

    async def async_get_fan(
        self, fan_identifier: int
    ) -> Optional[dict[str, Any]]:
        """Unused here, present to match the real interface."""
        return None


@pytest.mark.asyncio
async def test_complete_payload_is_applied() -> None:
    """The happy path still works."""
    fan = Fan(FAN_ID, _StubAPI())
    assert await fan.async_update_api_data(_payload()) is True
    assert fan.power == 3300
    assert fan.mode == "always_on"


@pytest.mark.asyncio
async def test_missing_last_connection_is_tolerated() -> None:
    """last_connection is NotRequired in FanPayload, so it may be absent.

    It was previously read with data["last_connection"], which raised.
    """
    data = _payload()
    del data["last_connection"]

    fan = Fan(FAN_ID, _StubAPI())
    assert await fan.async_update_api_data(data) is True
    assert fan.last_connection is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    ["id", "mode", "power", "connected", "mqtt_password", "room_id"],
)
async def test_missing_required_field_is_rejected(field: str) -> None:
    """A payload missing a required field is refused, not half-applied."""
    fan = Fan(FAN_ID, _StubAPI())
    await fan.async_update_api_data(_payload())

    data = _payload(power=9900, mode="eco")
    del data[field]

    assert await fan.async_update_api_data(data) is False


@pytest.mark.asyncio
async def test_rejected_payload_leaves_previous_values_intact() -> None:
    """The point of rejecting up front: no partial application.

    Assigning field by field would have set the earlier attributes before
    reaching the missing one.
    """
    fan = Fan(FAN_ID, _StubAPI())
    await fan.async_update_api_data(_payload(power=3300, mode="always_on"))

    broken = _payload(power=9900, mode="eco")
    del broken["mqtt_password"]  # late in the assignment order

    assert await fan.async_update_api_data(broken) is False
    assert fan.power == 3300
    assert fan.mode == "always_on"


class _ListAPI:
    """Returns a fan list containing good and broken entries."""

    # Arguments mirror SmartCocoonAPI and are deliberately unused.
    # pylint: disable=unused-argument,too-few-public-methods

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self._entries = entries

    async def async_request(
        self, method: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Return the canned fan list."""
        return {"fans": self._entries}


@pytest.mark.asyncio
async def test_one_bad_entry_does_not_block_the_others() -> None:
    """A malformed entry must not cost the remaining fans their update."""
    good = _payload(fan_id="good-fan", power=5000)
    broken = _payload(fan_id="broken-fan")
    del broken["power"]
    no_id = _payload()
    del no_id["fan_id"]

    manager = SmartCocoonManager()
    # pylint: disable=protected-access
    manager._api = _ListAPI([broken, no_id, good])  # type: ignore[assignment]

    fans = await manager.async_update_fans()

    assert "good-fan" in fans
    assert fans["good-fan"].power == 5000
