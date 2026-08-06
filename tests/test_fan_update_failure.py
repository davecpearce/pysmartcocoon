#!/usr/bin/env python3
"""Tests that a rejected fan update is reported as a failure.

`SmartCocoonAPI.async_request` returns None for a response it could not use,
without raising. The fan previously ignored that and returned True regardless,
so Home Assistant displayed a speed the fan had never accepted.
"""

from typing import Any, Optional

import pytest

from pysmartcocoon.fan import Fan
from pysmartcocoon.manager import SmartCocoonManager

FAN_ID = "abc123"


def _api_payload(power: int = 3300, mode: str = "always_on") -> dict[str, Any]:
    """A fan payload shaped like the API's, for seeding state."""
    return {
        "id": 42,
        "fan_id": FAN_ID,
        "mode": mode,
        "fan_on": True,
        "firmware_version": "1.0.0",
        "is_room_estimating": False,
        "connected": True,
        "last_connection": None,
        "power": power,
        "predicted_room_temperature": 21.0,
        "room_id": 7,
        "thermostat_vendor": None,
        "mqtt_username": "u",
        "mqtt_password": "p",
    }


class _StubAPI:
    """Stands in for SmartCocoonAPI with a controllable update result.

    The signatures mirror SmartCocoonAPI, so the arguments are deliberately
    accepted and ignored.
    """

    # pylint: disable=unused-argument

    def __init__(self, update_result: Optional[dict[str, Any]]) -> None:
        self._update_result = update_result
        self.update_calls = 0

    async def async_update_fan(
        self, fan_identifier: int, mode: str, power: int
    ) -> Optional[dict[str, Any]]:
        """Return the configured result, standing in for the real call."""
        self.update_calls += 1
        return self._update_result

    async def async_get_fan(
        self, fan_identifier: int
    ) -> Optional[dict[str, Any]]:
        """Return a fixed payload; the refresh path is not under test."""
        return _api_payload()


async def _seeded_fan(api: Any) -> Fan:
    fan = Fan(FAN_ID, api)
    await fan.async_update_api_data(_api_payload())
    return fan


@pytest.mark.asyncio
async def test_rejected_update_reports_failure() -> None:
    """Regression test: API returns None, so this must not claim success."""
    api = _StubAPI(update_result=None)
    fan = await _seeded_fan(api)

    result = await fan.async_set_fan_modes(fan_speed_pct=50)

    assert api.update_calls == 1
    assert result is False


@pytest.mark.asyncio
async def test_accepted_update_reports_success() -> None:
    """An accepted update still reports success."""
    api = _StubAPI(update_result=_api_payload())
    fan = await _seeded_fan(api)

    assert await fan.async_set_fan_modes(fan_speed_pct=50) is True


@pytest.mark.asyncio
async def test_manager_propagates_failure() -> None:
    """The manager must not swallow the result.

    It previously returned None from these methods, so a caller could not
    distinguish a rejected update from an applied one.
    """
    api = _StubAPI(update_result=None)
    manager = SmartCocoonManager()
    # pylint: disable=protected-access
    manager._fans[FAN_ID] = await _seeded_fan(api)

    assert await manager.async_set_fan_speed(FAN_ID, 50) is False
    assert await manager.async_fan_turn_on(FAN_ID) is False
    assert await manager.async_set_fan_auto(FAN_ID) is False


@pytest.mark.asyncio
async def test_manager_propagates_success() -> None:
    """And reports success when the fan accepts the change."""
    api = _StubAPI(update_result=_api_payload())
    manager = SmartCocoonManager()
    # pylint: disable=protected-access
    manager._fans[FAN_ID] = await _seeded_fan(api)

    assert await manager.async_set_fan_speed(FAN_ID, 50) is True


@pytest.mark.parametrize("speed", [101, 150, -1, -100])
def test_out_of_range_speed_is_rejected(speed: int) -> None:
    """Out-of-range speeds must not be applied.

    The previous implementation logged that the value was invalid and then
    set it anyway, so 150 became a power of 15000.
    """
    fan = Fan(FAN_ID, _StubAPI(update_result=None))
    fan.set_speed_pct(40)
    assert fan.power == 4000

    assert fan.set_speed_pct(speed) is False
    assert fan.power == 4000  # unchanged


@pytest.mark.parametrize("speed", [0, 1, 50, 99, 100])
def test_in_range_speed_is_applied(speed: int) -> None:
    """Boundary values are accepted."""
    fan = Fan(FAN_ID, _StubAPI(update_result=None))
    assert fan.set_speed_pct(speed) is True
    assert fan.power == speed * 100
