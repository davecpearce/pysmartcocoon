# Debug Logging Guide

This comprehensive guide explains how to enable and use debug logging for the PySmartCocoon library in both development and Home Assistant environments.

## Table of Contents

- [Overview](#overview)
- [Development Testing](#development-testing)
- [Home Assistant Integration](#home-assistant-integration)
- [Debug Output Examples](#debug-output-examples)
- [Troubleshooting](#troubleshooting)
- [Performance Considerations](#performance-considerations)

## Overview

Debug logging provides detailed information about API requests, responses, and internal operations. This is essential for troubleshooting integration issues and understanding how the library interacts with the SmartCocoon API.

### What Debug Logging Shows

- **API Requests**: Method, URL, headers, and request body
- **API Responses**: Status code, response headers, and response body
- **Authentication**: User details and token information
- **Fan Operations**: Mode changes, speed adjustments, and status updates
- **Error Details**: Comprehensive error information for troubleshooting

## Development Testing

### Prerequisites

1. **Set up environment variables**:

   ```bash
   # Copy the template and fill in your credentials
   cp tests/template.env tests/.env
   # Edit tests/.env with your actual credentials
   ```

2. **Set the integration test flag**:
   ```bash
   export RUN_INTEGRATION=1
   ```

### Testing Methods

#### Method 1: Using the Smoke Test Script (Recommended)

```bash
# Run the smoke test with debug output
python tests/test_smoke_test.py
```

This will:

- Test authentication with detailed debug output
- Test all API calls (locations, rooms, thermostats, fans) with debug output
- Show comprehensive results summary
- Demonstrate the full async_update_data() functionality

#### Method 2: Using pytest

```bash
# Run just the debug logging test
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s

# Run all fan control tests (includes debug test)
pytest tests/test_fan_control.py -v -s

# Run all tests with debug output
pytest -v -s
```

#### Method 3: Manual Execution

```bash
# Run the test file directly
python tests/test_integration.py
```

### Test Functions

#### `test_integration_debug_logging()`

- **Purpose**: Specifically tests debug logging functionality
- **What it does**:
  - Creates a SmartCocoonManager
  - Attempts authentication (triggers debug logging)
  - Retrieves fan data (triggers more debug logging)
  - Provides guidance on what debug output to expect

#### Enhanced Existing Tests

- All existing integration tests now benefit from debug logging
- The `logging.basicConfig(level=logging.DEBUG)` ensures debug output is shown

## Home Assistant Integration

### Method 1: Using Home Assistant Logger Integration

Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    pysmartcocoon: debug
    custom_components.smartcocoon: debug # if using as custom component
```

### Method 2: Using Home Assistant Developer Tools

1. Go to **Settings** → **System** → **Logs**
2. Click **Load Full Home Assistant Log**
3. In the filter box, enter: `pysmartcocoon`
4. Set the log level to **DEBUG**

### Method 3: Using Logger Service

You can also control logging dynamically using the logger service:

```yaml
# In an automation or script
service: logger.set_level
data:
  pysmartcocoon: debug
```

### Disabling Debug Logging in Home Assistant

To disable debug logging, either:

1. Remove the logger configuration from `configuration.yaml`
2. Set the log level back to `info` or `warning`
3. Use the logger service: `service: logger.set_level` with `pysmartcocoon: info`

## Debug Output Examples

### Development Environment

When debug logging is enabled in development, you'll see output like:

```
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] ┌─ API REQUEST ──────────────────────────────────────────────
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] │ Method: POST
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] │ URL: https://app.mysmartcocoon.com/api/auth/sign_in
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] │ Headers: {'Content-Type': 'application/json', 'User-Agent': '...'}
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] │ Request body (JSON): {'email': 'user@example.com', 'password': 'password'}
2024-01-15 10:30:15 DEBUG [pysmartcocoon.api] └─────────────────────────────────────────────────────────────

2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] ┌─ API RESPONSE ─────────────────────────────────────────────
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ Status: 200
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ Headers: {'access-token': '...', 'client': '...', 'uid': '...'}
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ Response body: {'data': {'id': 123, 'email': 'user@example.com', ...}}
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] └────────────────────────────────────────────────────────────

2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] ┌─ AUTHENTICATION SUCCESS ────────────────────────────────
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ User ID: 123
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ Email: user@example.com
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] │ Token expires in: 3600 seconds
2024-01-15 10:30:16 DEBUG [pysmartcocoon.api] └─────────────────────────────────────────────────────────
```

### Home Assistant Environment

In Home Assistant, the output will include the thread information:

```
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] ┌─ API REQUEST ──────────────────────────────────────────────
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] │ Method: POST
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] │ URL: https://app.mysmartcocoon.com/api/auth/sign_in
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] │ Headers: {'Content-Type': 'application/json', 'User-Agent': '...'}
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] │ Request body (JSON): {'email': 'user@example.com', 'password': 'password'}
2024-01-15 10:30:15 DEBUG (MainThread) [pysmartcocoon.api] └─────────────────────────────────────────────────────────────
```

## Troubleshooting

### No Debug Output

- Ensure `RUN_INTEGRATION=1` is set (for development testing)
- Check that your `.env` file has valid credentials
- Verify logging level is set to DEBUG
- Check that the logger configuration is correct in Home Assistant

### Authentication Errors

- Check your credentials in `tests/.env` or Home Assistant configuration
- Look at the debug output for specific error details
- Verify your SmartCocoon account is active
- Check for missing required headers in API responses

### Missing Dependencies

- Install test dependencies: `pip install -r requirements_test.txt`
- Ensure all required packages are installed
- For Home Assistant: Ensure the custom component is properly installed

### API Connection Issues

- Check network connectivity
- Verify the SmartCocoon API is accessible
- Look for rate limiting or authentication token expiration
- Check for changes in the API endpoints

## Performance Considerations

Debug logging generates a lot of output and may impact performance:

- **Development**: Debug logging is fine for testing and development
- **Home Assistant**: Only enable when troubleshooting issues
- **Production**: Disable debug logging in production environments
- **Log Rotation**: Consider log rotation for long-running systems

### Recommended Usage

1. **Enable** debug logging when:

   - Setting up the integration for the first time
   - Troubleshooting connection or authentication issues
   - Investigating unexpected behavior
   - Testing new features

2. **Disable** debug logging when:
   - Everything is working correctly
   - Running in production
   - Performance is a concern
   - Log files are getting too large

## Integration with Development Workflow

The same debug logging that works in these tests will work in Home Assistant when you configure:

```yaml
logger:
  logs:
    pysmartcocoon: debug
```

This makes it easy to troubleshoot HA integration issues using the same debug output you see in development tests.

## Additional Resources

- [Home Assistant Logger Integration](https://www.home-assistant.io/integrations/logger/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [PySmartCocoon Development Guide](DEVCONTAINER_README.md)
