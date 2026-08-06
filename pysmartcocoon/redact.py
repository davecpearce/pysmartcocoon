"""Redaction helpers for debug logging.

This library logs whole API requests and responses at DEBUG level, and the
README tells Home Assistant users to turn that logging on when something is
wrong. Those logs routinely get pasted into public GitHub issues, so nothing
written at DEBUG may contain a usable credential.

Everything here is about what reaches a log file. None of it changes what is
sent to the API.
"""

from typing import Any

REDACTED = "**REDACTED**"

# Matched case-insensitively as a substring of the key, so "access-token",
# "mqtt_password" and "refresh_token" are all covered without having to
# enumerate every spelling the API might introduce later.
_SECRET_KEY_PARTS: tuple[str, ...] = (
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "apikey",
)

# Keys whose exact name identifies a credential, but which contain no
# substring worth matching on. `client` is one third of this API's auth
# triple (access-token + client + uid), so it is a credential, not metadata.
_SECRET_KEY_EXACT: frozenset[str] = frozenset({"client"})

# Account identifiers rather than credentials. Partially masked instead of
# removed, so debug output can still tell two accounts apart -- which is the
# reason someone would want the value in the first place.
_IDENTIFIER_KEY_EXACT: frozenset[str] = frozenset({"email", "uid"})


def _is_secret(key: str) -> bool:
    lowered = key.lower()
    if lowered in _SECRET_KEY_EXACT:
        return True
    return any(part in lowered for part in _SECRET_KEY_PARTS)


def mask_identifier(value: Any) -> Any:
    """Mask an account identifier, keeping just enough to tell accounts apart.

    Email addresses keep their first character and domain, since the domain
    is often the useful part when diagnosing a login problem and is not
    secret. Anything else keeps only its first character.
    """
    if not isinstance(value, str) or not value:
        return value

    if "@" in value:
        local, _, domain = value.partition("@")
        head = local[0] if local else ""
        return f"{head}***@{domain}"

    return f"{value[0]}***"


def redact(obj: Any) -> Any:
    """Return a copy of ``obj`` with credentials replaced.

    Recurses through dicts and lists. The input is never mutated, so callers
    can pass request bodies and API responses directly without risk of
    corrupting the data actually in flight.
    """
    if isinstance(obj, dict):
        result: dict[Any, Any] = {}
        for key, value in obj.items():
            if isinstance(key, str) and _is_secret(key):
                result[key] = REDACTED
            elif isinstance(key, str) and key.lower() in _IDENTIFIER_KEY_EXACT:
                result[key] = mask_identifier(value)
            else:
                result[key] = redact(value)
        return result

    if isinstance(obj, (list, tuple)):
        redacted = [redact(item) for item in obj]
        return type(obj)(redacted) if isinstance(obj, tuple) else redacted

    return obj
