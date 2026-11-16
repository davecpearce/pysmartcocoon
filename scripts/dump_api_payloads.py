#!/usr/bin/env python3
"""Dump the raw SmartCocoon API payloads, redacted, for diagnosing issues.

The library only reads the fields it knows about, so a field the API started
sending is invisible from the outside -- which is exactly what several open
issues turn on. This asks the API directly and reports **every** key it sent,
marking the ones no model consumes.

Credentials are read from the environment or a .env file, never from the
command line, so they do not land in shell history. Output goes through
`redact()`, the same function the debug logging uses, so credentials and
the home address (street, postal code, coordinates) are masked. It still
describes a real home -- room names, thermostat, equipment -- so read it
before attaching it to a public issue.

Usage:

    export SC_USERNAME='you@example.com'
    export SC_PASSWORD='...'
    python scripts/dump_api_payloads.py

or put SC_USERNAME / SC_PASSWORD in a .env file beside this repo and run the
same command. Add --verbose to also stream the library's own debug logging.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _sc_common import load_credentials  # noqa: E402  (sets up sys.path)

# pylint: disable=wrong-import-position
from pysmartcocoon.api import SmartCocoonAPI  # noqa: E402
from pysmartcocoon.const import API_URL, EntityType  # noqa: E402
from pysmartcocoon.redact import redact  # noqa: E402

# pylint: enable=wrong-import-position

_LOGGER = logging.getLogger("dump_api_payloads")

#: Keys each model actually reads today. Anything the API sends that is not
#: listed here is reported as unmodelled -- that is the interesting part.
MODELLED_KEYS: dict[str, frozenset[str]] = {
    "fans": frozenset(
        {
            "id",
            "fan_id",
            "mode",
            "fan_on",
            "firmware_version",
            "is_room_estimating",
            "connected",
            "last_connection",
            "power",
            "speed_level",
            "predicted_room_temperature",
            "room_id",
            "thermostat_vendor",
            "mqtt_username",
            "mqtt_password",
        }
    ),
    "rooms": frozenset(
        {
            "id",
            "name",
            "desired_temperature",
            "hvac_mode",
            "hvac_state",
            "is_estimating",
            "predicted_temperature",
            "target_temperature",
            "temperature",
            "thermostat_id",
            "external_sensor",
        }
    ),
}


def summarise_keys(label: str, items: list[dict[str, Any]]) -> list[str]:
    """Report which keys the API sent and which of them nothing reads."""
    known = MODELLED_KEYS.get(label)
    if known is None or not items:
        return []

    seen: set[str] = set()
    for item in items:
        seen.update(item.keys())

    lines = []
    unmodelled = sorted(seen - known)
    missing = sorted(known - seen)

    if unmodelled:
        lines.append(f"  !! {label}: keys the API sends that NOTHING reads:")
        for key in unmodelled:
            sample = next(
                (i[key] for i in items if i.get(key) not in (None, "")), None
            )
            lines.append(f"       {key} = {sample!r}")
    else:
        lines.append(f"  -- {label}: no unmodelled keys")

    if missing:
        lines.append(
            f"  !! {label}: keys the library expects but the API did NOT "
            f"send: {', '.join(missing)}"
        )

    return lines


def endpoint_report(name: str, response: Any) -> tuple[Any, list[str]]:
    """Redact one endpoint's response and describe its keys.

    The key report prints sample values to the terminal, so it must be built
    from the redacted copy. It once sampled the raw response, and a fan's
    `mqtt_password` -- nested inside `rooms` -- was printed in clear while
    the JSON file beside it was correctly masked.
    """
    redacted = redact(response)
    items = (redacted or {}).get(name) or []
    return redacted, summarise_keys(name, items)


def summarise_fans(fans: list[dict[str, Any]]) -> list[str]:
    """Print the fields issue #421 turns on, per fan."""
    lines = ["", "Fan speed check (issue #421)", "-" * 60]
    for fan in fans:
        power = fan.get("power")
        speed_pct = (
            int(power / 100) if isinstance(power, (int, float)) else "?"
        )
        lines.extend(
            [
                f"  fan_id            {fan.get('fan_id')}",
                f"    mode            {fan.get('mode')}",
                f"    fan_on          {fan.get('fan_on')}",
                f"    connected       {fan.get('connected')}",
                f"    power (raw)     {power}",
                f"    -> HA shows     {speed_pct}%",
                "",
            ]
        )
    lines.append("  Compare 'HA shows' against the speed in the mobile app.")
    lines.append("  If they differ, the app's value is coming from somewhere")
    lines.append("  other than `power` -- check the unmodelled keys above.")
    return lines


async def main() -> int:
    """Authenticate, fetch every endpoint, and write a redacted dump."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Where to write the redacted JSON "
            "(default: ./sc-api-dump-<timestamp>.json)"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also stream the library's own debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    if not args.verbose:
        logging.getLogger("pysmartcocoon").setLevel(logging.WARNING)

    username, password = load_credentials()

    api = SmartCocoonAPI()
    try:
        if not await api.async_authenticate(username, password):
            _LOGGER.error("Authentication failed -- check the credentials.")
            return 1
        _LOGGER.info("Authenticated.")

        dump: dict[str, Any] = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "endpoints": {},
        }
        report: list[str] = ["", "=" * 60, "Payload key report", "=" * 60]

        for entity in EntityType:
            name = entity.value
            try:
                response = await api.async_request("GET", f"{API_URL}{name}")
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("GET %s failed: %s", name, err)
                dump["endpoints"][name] = {"error": str(err)}
                continue

            dump["endpoints"][name], lines = endpoint_report(name, response)
            items = (dump["endpoints"][name] or {}).get(name) or []
            _LOGGER.info("GET %-16s %d item(s)", name, len(items))
            report.extend(lines)

        fans = (dump["endpoints"].get("fans") or {}).get("fans") or []
        if fans:
            report.extend(summarise_fans(fans))

        out = args.output or Path.cwd() / (
            f"sc-api-dump-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        out.write_text(json.dumps(dump, indent=2, default=str))

        print("\n".join(report))
        print()
        print(f"Redacted dump written to: {out}")
        print(
            "Credentials and the home address are masked. Room names and "
            "equipment are not -- read it before attaching it to an issue."
        )
        return 0
    finally:
        await api.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
