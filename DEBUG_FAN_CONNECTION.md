# Debugging Fan Connection Status

This guide helps you debug why a fan that's not plugged in appears as connected in Home Assistant.

## Quick Debug Steps

### Option 1: Use the Debug Script (Recommended)

Run the debug script to see the raw API response:

**Using .env file (recommended):**

1. The script is in the `tests/` folder and will use `tests/.env`:

```bash
# Edit tests/.env with your credentials (or use tests/template.env as a template)
# Then run from the project root:
python tests/debug_fan_connection.py

# Or for a specific fan
python tests/debug_fan_connection.py YOUR_FAN_ID
```

2. Or run from the tests directory:

```bash
cd tests
python debug_fan_connection.py
```

**Or using environment variables:**

```bash
export USERNAME=your_username
export PASSWORD=your_password
python debug_fan_connection.py
```

This will show:

- Raw API response with the `connected` value from the cloud
- Processed values in pysmartcocoon
- Analysis of the connection status

### Option 2: Enable Debug Logging in Home Assistant

1. Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    pysmartcocoon: debug
    custom_components.smartcocoon: debug
```

2. Restart Home Assistant

3. Check the logs - you'll see:
   - Raw API responses with the `connected` value
   - Log messages like: `Fan ID: XXX - Raw API 'connected' value: True (type: bool)`

### Option 3: Check Logs Directly

Look for these log messages in your Home Assistant logs:

```
Fan ID: XXX - Raw API 'connected' value: <value> (type: <type>)
```

This tells you exactly what the cloud API is returning.

## What to Look For

1. **Raw API `connected` value**: This is what the SmartCocoon cloud API is reporting
   - If this is `True` but the fan is unplugged, the issue is with the cloud API
   - If this is `False` but Home Assistant shows it as connected, the issue is in the integration

2. **`last_connection` timestamp**: Check when the fan was last seen
   - If `last_connection` is very old (days/weeks), but `connected` is `True`, the cloud API may have stale data

3. **Compare values**:
   - Raw API `connected` vs pysmartcocoon `connected` property
   - They should match - if they don't, there's a bug in pysmartcocoon

## Understanding the Code

The `connected` status is set directly from the API response in `fan.py` line 344:

```python
self._connected = data["connected"]
```

There's no transformation - pysmartcocoon reports exactly what the cloud API returns.

## Expected Behavior

- **Fan plugged in and online**: `connected = True`, recent `last_connection`
- **Fan unplugged**: `connected = False`, `last_connection` may be old or None
- **Fan offline but plugged in**: `connected = False`, recent `last_connection`

If you see `connected = True` for an unplugged fan, the SmartCocoon cloud API is reporting incorrect data.
