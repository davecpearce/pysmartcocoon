#!/usr/bin/env python3
"""Tests for aiohttp session ownership and reuse.

Two distinct bugs are covered here:

1. The retry loop closed its session inside the loop body, so attempts 2 and
   3 ran against a closed session. Retries silently never worked for anyone
   not supplying their own session.
2. `close()` closed the caller's session. Home Assistant passes its shared
   session, so calling it would have taken down every other integration.
"""

import asyncio

import pytest
from aiohttp import ClientSession

from pysmartcocoon.api import SmartCocoonAPI


@pytest.mark.asyncio
async def test_caller_supplied_session_is_not_closed() -> None:
    """close() must leave a session it did not create alone.

    Home Assistant shares one aiohttp session across all integrations.
    """
    session = ClientSession()
    try:
        api = SmartCocoonAPI(session)
        await api.close()
        assert not session.closed
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_owned_session_is_closed() -> None:
    """A session the API created itself is closed by close()."""
    api = SmartCocoonAPI()
    created = api._ensure_session()  # pylint: disable=protected-access
    assert not created.closed

    await api.close()
    assert created.closed


@pytest.mark.asyncio
async def test_session_is_reused_across_requests() -> None:
    """The same session is returned each time, not recreated per request.

    This is what makes retries work: a second attempt must not find the
    session closed underneath it.
    """
    api = SmartCocoonAPI()
    try:
        first = api._ensure_session()  # pylint: disable=protected-access
        second = api._ensure_session()  # pylint: disable=protected-access
        assert first is second
        assert not first.closed
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_caller_session_is_returned_unchanged() -> None:
    """A supplied session is used as-is rather than replaced."""
    session = ClientSession()
    try:
        api = SmartCocoonAPI(session)
        in_use = api._ensure_session()  # pylint: disable=protected-access
        assert in_use is session
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_session_survives_failed_attempts() -> None:
    """The regression test for the retry bug.

    Previously the session was closed in a `finally` inside the retry loop,
    so it was already closed once the request returned. Drive a request that
    fails against an unroutable address and assert the session is still
    usable afterwards.
    """
    api = SmartCocoonAPI(request_timeout=1)
    try:
        session = api._ensure_session()  # pylint: disable=protected-access

        with pytest.raises(Exception):
            await api.async_request(
                "GET", "http://127.0.0.1:9/never-listening"
            )

        assert not session.closed
        after = api._ensure_session()  # pylint: disable=protected-access
        assert after is session
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_close_is_idempotent() -> None:
    """Calling close() twice must not raise."""
    api = SmartCocoonAPI()
    api._ensure_session()  # pylint: disable=protected-access
    await api.close()
    await api.close()


@pytest.mark.asyncio
async def test_context_manager_closes_owned_session() -> None:
    """__aexit__ closes a session the API owns."""
    async with SmartCocoonAPI() as api:
        created = api._ensure_session()  # pylint: disable=protected-access
    assert created.closed


@pytest.mark.asyncio
async def test_context_manager_leaves_caller_session_open() -> None:
    """__aexit__ must not close a caller-supplied session either."""
    session = ClientSession()
    try:
        async with SmartCocoonAPI(session):
            pass
        assert not session.closed
    finally:
        await session.close()


def test_no_event_loop_needed_to_construct() -> None:
    """Constructing the API must not create a session eagerly.

    aiohttp requires a running loop to create a ClientSession, so building
    one in __init__ would make SmartCocoonAPI unusable outside async code.
    """
    api = SmartCocoonAPI()
    assert api._session is None  # pylint: disable=protected-access

    async def _use() -> None:
        api._ensure_session()  # pylint: disable=protected-access
        await api.close()

    asyncio.run(_use())
