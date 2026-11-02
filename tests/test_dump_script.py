#!/usr/bin/env python3
"""The dump script's terminal report must be as redacted as its file.

The report prints sample values for keys nothing reads. It once sampled the
raw response, and a fan's `mqtt_password` -- nested inside `rooms` -- was
printed in clear while the JSON file beside it was correctly masked. The
terminal is the part people screen-share and paste.
"""

import importlib.util
import pathlib
import sys
from types import ModuleType

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
SECRET = "920ff2-not-a-real-password"
POSTAL = "K1A0B1"


def _load_script() -> ModuleType:
    """Import scripts/dump_api_payloads.py, which is not a package module."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "dump_api_payloads", SCRIPTS / "dump_api_payloads.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nested_password_never_reaches_the_report() -> None:
    """The case that leaked: a fan record nested inside a room."""
    dump = _load_script()
    response = {
        "rooms": [
            {
                "id": 2346,
                "name": "Bedroom",
                "fans": [
                    {
                        "fan_id": "6fcf50",
                        "mqtt_username": "1218_6fcf50",
                        "mqtt_password": SECRET,
                    }
                ],
            }
        ]
    }

    redacted, lines = dump.endpoint_report("rooms", response)
    report = "\n".join(lines)

    assert "fans" in report  # the nested key is still reported...
    assert SECRET not in report  # ...but never its secret
    assert SECRET not in repr(redacted)


def test_home_address_never_reaches_the_report() -> None:
    """Location values are masked in the report as in the file."""
    dump = _load_script()
    response = {
        "client_systems": [
            {"id": 1, "location": {"id": 1, "postal_code": POSTAL}}
        ]
    }

    _, lines = dump.endpoint_report("client_systems", response)
    assert POSTAL not in "\n".join(lines)
