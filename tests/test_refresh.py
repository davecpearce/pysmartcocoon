#!/usr/bin/env python3
"""Tests for polling support: refresh results, re-login, and payload types.

Home Assistant is moving from waiting for updates (which never arrived --
the callback the integration registered is never called) to polling the
fans endpoint. That needs three things the library did not do:

* say whether a refresh worked, rather than swallowing the failure;
* log in again when the session expires, rather than failing forever;
* read what the API actually sends: `speed_level`, and decimals as strings.

The payloads here copy the shape of a live response captured on 2026-11-02,
not the idealised floats older fixtures use.
"""

from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from pysmartcocoon import api as api_module
from pysmartcocoon.api import SmartCocoonAPI
from pysmartcocoon.errors import RequestError, UnauthorizedError
from pysmartcocoon.manager import SmartCocoonManager
from pysmartcocoon.room import Room


def _live_fan(**overrides: Any) -> dict[str, Any]:
    """A fan entry shaped like the live API's, values invented."""
    payload: dict[str, Any] = {
        "id": 129140,
        "fan_id": "4125f4",
        "mqtt_password": "p",
        "last_connection": "2026-11-02T11:34:26.017Z",
        "power": 3800,
        "speed_level": 2,
        "firmware_version": "20409",
        "fan_on": True,
        "mode": "eco",
        "mqtt_username": "1218_4125f4",
        "room_id": 51328,
        "predicted_room_temperature": "21.0",
        "is_room_estimating": False,
        "thermostat_vendor": "ecobee",
        "connected": True,
    }
    payload.update(overrides)
    return payload


class _CannedAPI:
    """Stands in for SmartCocoonAPI's request method.

    Arguments mirror SmartCocoonAPI and are deliberately unused.
    """

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


# --- payload types ----------------------------------------------------------


@pytest.mark.asyncio
async def test_speed_level_and_string_temperature_are_read() -> None:
    """The fields the app shows, in the form the API sends them."""
    manager = _manager({"fans": [_live_fan()]})
    assert await manager.async_refresh_fans()

    fan = manager.fans["4125f4"]
    assert fan.speed_level == 2
    assert fan.power == 3800
    assert fan.predicted_room_temperature == 21.0
    assert isinstance(fan.predicted_room_temperature, float)
    assert fan.thermostat_vendor == "ecobee"


@pytest.mark.asyncio
async def test_missing_or_bad_values_become_none_not_errors() -> None:
    """speed_level is optional; a junk temperature must not raise."""
    payload = _live_fan(predicted_room_temperature="n/a")
    del payload["speed_level"]
    manager = _manager({"fans": [payload]})
    assert await manager.async_refresh_fans()

    fan = manager.fans["4125f4"]
    assert fan.speed_level is None
    assert fan.predicted_room_temperature is None


def test_room_temperatures_are_numbers() -> None:
    """Room decimals arrive as strings too."""
    room = Room(
        {
            "id": 51328,
            "name": "Office",
            "desired_temperature": "30.0",
            "predicted_temperature": "21.0",
            "is_estimating": False,
            "hvac_mode": "heat",
            "hvac_state": None,
            "temperature": "22.8",
            "target_temperature": "21.5",
            "thermostat_id": 1956,
        }
    )
    assert room.temperature == 22.8
    assert room.predicted_temperature == 21.0
    assert room.desired_temperature == 30.0
    assert room.target_temperature == 21.5


# --- refresh results --------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_reports_success() -> None:
    """A good response is reported as a successful refresh."""
    assert await _manager({"fans": [_live_fan()]}).async_refresh_fans()


@pytest.mark.parametrize(
    "result",
    [RequestError("down"), UnauthorizedError("401"), None, {"other": []}],
)
@pytest.mark.asyncio
async def test_refresh_reports_failure_and_keeps_values(result: Any) -> None:
    """A failed refresh says so, and the fan keeps its previous values."""
    manager = _manager({"fans": [_live_fan(power=5000)]})
    assert await manager.async_refresh_fans()

    # pylint: disable=protected-access
    manager._api = _CannedAPI(result)  # type: ignore[assignment]
    assert await manager.async_refresh_fans() is False
    assert manager.fans["4125f4"].power == 5000


@pytest.mark.asyncio
async def test_update_fans_keeps_its_old_contract() -> None:
    """Existing callers still get the fan dict back, even on failure."""
    manager = _manager(RequestError("down"))
    assert not await manager.async_update_fans()
    manager = _manager({"fans": [_live_fan()]})
    assert "4125f4" in await manager.async_update_fans()


# --- re-login on 401 --------------------------------------------------------


def _auth_server(state: dict[str, Any], accept_login: bool = True) -> Any:
    """A local stand-in for the SmartCocoon API.

    The first fans request gets a 401 (an expired session); after a fresh
    login it succeeds. Counts logins so the tests can check there is
    exactly one retry, not a loop.
    """

    async def sign_in(_request: web.Request) -> web.Response:
        state["logins"] += 1
        if not accept_login:
            return web.json_response({"errors": ["bad"]}, status=401)
        token = f"token-{state['logins']}"
        return web.json_response(
            {"data": {"id": 1, "email": "dave@example.com"}},
            headers={"access-token": token, "expiry": "1", "client": "c"},
        )

    async def fans(request: web.Request) -> web.Response:
        state["fan_requests"] += 1
        if request.headers.get("access-token") != "token-2":
            return web.json_response({"errors": ["expired"]}, status=401)
        return web.json_response({"fans": [_live_fan()]})

    app = web.Application()
    app.router.add_post("/auth/sign_in", sign_in)
    app.router.add_get("/fans", fans)
    return app


@pytest.mark.asyncio
async def test_expired_session_logs_in_again_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A 401 triggers one fresh login and one retry, then succeeds."""
    state = {"logins": 0, "fan_requests": 0}
    async with TestServer(_auth_server(state)) as server:
        monkeypatch.setattr(
            api_module, "API_AUTH_URL", str(server.make_url("/auth/sign_in"))
        )
        client = SmartCocoonAPI(request_timeout=5)
        try:
            assert await client.async_authenticate("dave@example.com", "pw")
            data = await client.async_request(
                "GET", str(server.make_url("/fans"))
            )
        finally:
            await client.close()

    assert data is not None and data["fans"][0]["fan_id"] == "4125f4"
    assert state == {"logins": 2, "fan_requests": 2}


@pytest.mark.asyncio
async def test_failed_relogin_raises_instead_of_looping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If the fresh login is refused, the 401 surfaces; no retry storm.

    Stands for a password changed since Home Assistant logged in.
    """
    state = {"logins": 0, "fan_requests": 0}
    async with TestServer(_auth_server(state, accept_login=False)) as server:
        monkeypatch.setattr(
            api_module, "API_AUTH_URL", str(server.make_url("/auth/sign_in"))
        )
        client = SmartCocoonAPI(request_timeout=5)
        # pylint: disable=protected-access
        client._credentials = ("dave@example.com", "pw")
        try:
            with pytest.raises(UnauthorizedError):
                await client.async_request(
                    "GET", str(server.make_url("/fans"))
                )
        finally:
            await client.close()

    assert state == {"logins": 1, "fan_requests": 1}


@pytest.mark.asyncio
async def test_no_relogin_without_stored_credentials() -> None:
    """Never logged in: a 401 is raised as before, with no login attempt."""
    state = {"logins": 0, "fan_requests": 0}
    async with TestServer(_auth_server(state)) as server:
        client = SmartCocoonAPI(request_timeout=5)
        try:
            with pytest.raises(UnauthorizedError):
                await client.async_request(
                    "GET", str(server.make_url("/fans"))
                )
        finally:
            await client.close()

    assert state == {"logins": 0, "fan_requests": 1}
