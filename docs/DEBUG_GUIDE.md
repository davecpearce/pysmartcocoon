# Debug Logging Guide

How to turn on debug logging for pysmartcocoon, what it shows, and what it hides.

## What gets logged

With the `pysmartcocoon` logger at `DEBUG`, every API call logs its method, URL, headers
and request body, followed by the response status, headers and body. Fan updates log
the mode and speed being sent.

**Credentials and your address are masked before anything is written.** This matters
because these logs end up pasted into public GitHub issues.

| Masked completely (`**REDACTED**`)                 | Partly masked                                          | Kept                           |
| -------------------------------------------------- | ------------------------------------------------------ | ------------------------------ |
| password, access token, client ID, `mqtt_password` | email addresses (`y***@example.com`), the `uid` header | city, state, country           |
| street address, postal or zip code, coordinates    |                                                        | room, fan and thermostat names |

Room names and the equipment in your home are still visible, so read a log before
posting it.

## Home Assistant

The quickest way is **Settings → Devices & services → SmartCocoon → ⋮ → Enable debug
logging**. Reproduce the problem, then choose **Disable debug logging**, and Home
Assistant downloads the log. This toggle covers the library (`pysmartcocoon`) only.

To include the integration's own logs as well, or to keep debug logging on across
restarts, add this to `configuration.yaml` and restart:

```yaml
logger:
  default: info
  logs:
    pysmartcocoon: debug
    custom_components.smartcocoon: debug
```

You can also change the level without restarting:

```yaml
action: logger.set_level
data:
  pysmartcocoon: debug
```

Turn it back off when you are done. Each poll, every 60 seconds, logs the full fan
payload, so the log grows quickly.

## Standalone Python

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pysmartcocoon").setLevel(logging.DEBUG)
```

## Example output

A login, as the library logs it:

```text
DEBUG [pysmartcocoon.api] ┌─ API REQUEST ──────────────────────────────────────────────
DEBUG [pysmartcocoon.api] │ Method: POST
DEBUG [pysmartcocoon.api] │ URL: https://app.mysmartcocoon.com/api/auth/sign_in
DEBUG [pysmartcocoon.api] │ Request body (JSON):
{
  "email": "y***@example.com",
  "password": "**REDACTED**"
}
DEBUG [pysmartcocoon.api] └────────────────────────────────────────────────────────────
DEBUG [pysmartcocoon.api] ┌─ API RESPONSE ─────────────────────────────────────────────
DEBUG [pysmartcocoon.api] │ Status: 200
DEBUG [pysmartcocoon.api] │ Headers:
{
  "access-token": "**REDACTED**",
  "expiry": "1767225600",
  "client": "**REDACTED**",
  "uid": "y***@example.com",
  ...
}
DEBUG [pysmartcocoon.api] ┌─ AUTHENTICATION SUCCESS ──────────────────────────────
DEBUG [pysmartcocoon.api] │ User ID: 1218
DEBUG [pysmartcocoon.api] │ Email: y***@example.com
```

If you ever see a password or token in plain text, that is a bug. Please report it
without attaching the log.

## Seeing everything the API sends

The library reads only the fields it knows about, so a field the API has started
sending never shows up in a fan's properties. To see the raw payloads, redacted the
same way, run:

```bash
export SC_USERNAME='you@example.com'
read -s SC_PASSWORD && export SC_PASSWORD
python scripts/dump_api_payloads.py
```

It writes `sc-api-dump-<timestamp>.json` and lists every key the library doesn't use.
See [scripts/README.md](../scripts/README.md#dump_api_payloadspy).

## Running the integration tests

Integration tests log in to your real SmartCocoon account and **change your fans'
settings**. They are skipped by default.

```bash
cp tests/template.env tests/.env    # then fill in USERNAME, PASSWORD, FAN_ID
RUN_INTEGRATION=1 pytest -m integration -v -s
```

For everyday work, run only the unit tests:

```bash
pytest -m "not integration"
```

## Troubleshooting

- **No debug output in Home Assistant:** check that the logger name is
  `pysmartcocoon`. The integration's domain, `smartcocoon`, matches no logger.
- **`UnauthorizedError` after it was working:** an expired session is renewed
  automatically, once. Seeing this error means the fresh login was refused too, which
  usually means the password changed. Home Assistant will ask you to re-enter it.
- **A fan shows as disconnected but the app shows it online:** see
  [DEBUG_FAN_CONNECTION.md](../DEBUG_FAN_CONNECTION.md).
