#!/usr/bin/env python3
"""Tests for credential redaction in debug logging.

The point of these tests is not that `redact` transforms dicts correctly in
the abstract -- it is that a password enabled at DEBUG level never reaches a
log file. Several tests therefore assert on captured log output rather than
on return values.
"""

import json
import logging

import pytest

from pysmartcocoon.const import API_AUTH_URL, API_HEADERS
from pysmartcocoon.redact import REDACTED, mask_identifier, redact

SECRET = "hunter2-correct-horse"


def test_password_is_redacted() -> None:
    """A request body's password must never survive redaction."""
    body = {"email": "dave@example.com", "password": SECRET}
    assert redact(body)["password"] == REDACTED


def test_redaction_does_not_mutate_input() -> None:
    """Redaction must not corrupt the payload actually sent to the API."""
    body = {"email": "dave@example.com", "password": SECRET}
    redact(body)
    assert body["password"] == SECRET


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "Password",
        "mqtt_password",
        "access-token",
        "refresh_token",
        "TOKEN",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "client",
    ],
)
def test_sensitive_keys_are_redacted(key: str) -> None:
    """Credential-bearing keys are matched case-insensitively."""
    assert redact({key: SECRET})[key] == REDACTED


def test_auth_triple_is_fully_covered() -> None:
    """access-token, client and uid together are this API's credential.

    Redacting only the token would still leak two thirds of it.
    """
    headers = {
        **API_HEADERS,
        "access-token": "tok",
        "client": "cli",
        "uid": "dave@example.com",
    }
    result = redact(headers)
    assert result["access-token"] == REDACTED
    assert result["client"] == REDACTED
    assert "dave" not in result["uid"]


def test_non_sensitive_values_are_preserved() -> None:
    """Redaction must leave ordinary debugging detail intact."""
    payload = {"fan_id": "abc123", "mode": "always_on", "power": 33}
    assert redact(payload) == payload


def test_nested_and_listed_secrets_are_redacted() -> None:
    """Secrets nested in lists and sub-dicts are still found."""
    payload = {
        "data": {"fans": [{"fan_id": "a", "mqtt_password": SECRET}]},
    }
    assert (
        redact(payload)["data"]["fans"][0]["mqtt_password"] == REDACTED
    )
    assert redact(payload)["data"]["fans"][0]["fan_id"] == "a"


def test_email_is_masked_but_domain_kept() -> None:
    """Enough is kept to tell accounts apart; the local part is not."""
    masked = mask_identifier("dave@example.com")
    assert masked == "d***@example.com"
    assert "dave@example.com" not in masked


def test_mask_identifier_handles_odd_values() -> None:
    """Masking must not raise on empty or non-string input."""
    assert mask_identifier("") == ""
    assert mask_identifier(None) is None
    assert mask_identifier(12345) == 12345
    assert mask_identifier("nodomain") == "n***"


def test_password_absent_from_serialised_debug_output() -> None:
    """The realistic failure: a password reaching a pasted log."""
    body = {"email": "dave@example.com", "password": SECRET}
    rendered = json.dumps(redact(body), indent=2)
    assert SECRET not in rendered


@pytest.mark.asyncio
async def test_authenticate_does_not_log_password(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """End-to-end guard over the actual logging path.

    Exercises SmartCocoonAPI.async_request with DEBUG enabled and asserts the
    password never appears in emitted records. The request itself is expected
    to fail -- no network here -- which is fine, because the request body is
    logged before the call is made.
    """
    from pysmartcocoon.api import SmartCocoonAPI

    caplog.set_level(logging.DEBUG, logger="pysmartcocoon")

    api = SmartCocoonAPI(request_timeout=1)
    with pytest.raises(Exception):
        await api.async_request(
            "POST",
            API_AUTH_URL,
            json={"email": "dave@example.com", "password": SECRET},
        )

    assert SECRET not in caplog.text
    assert REDACTED in caplog.text
