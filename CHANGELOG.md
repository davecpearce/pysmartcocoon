# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.5] - 2026-08-06

### Fixed

- **Fan updates the API rejects are no longer reported as successful** - `_async_set_fan` discarded the API response and always returned success. The API can return no usable response without raising an error, so a rejected change was indistinguishable from an applied one: Home Assistant would show the fan at a speed it never accepted.
- **Out-of-range fan speeds are rejected instead of applied** - `set_speed_pct` logged that a value outside 0-100 was invalid and then applied it anyway, so a speed of 150 became a power of 15000. It now leaves the speed unchanged and returns `False`.

- **`__version__` now matches the released version** - It was hardcoded in `__init__.py` while `bumpver` only rewrote `pyproject.toml`, so it reported `1.4.2` throughout the 1.4.3 and 1.4.4 releases. `bumpver` now updates both.

### Changed

- **Fan control methods on `SmartCocoonManager` now return `bool`** instead of `None`, so callers can tell an applied change from a rejected one: `async_fan_turn_on`, `async_fan_turn_off`, `async_set_fan_auto`, `async_set_fan_eco`, `async_set_fan_modes`, `async_set_fan_speed`. Callers that ignore the return value are unaffected.

## [1.4.4] - 2026-08-06

### Fixed

- **Retries now actually retry** - The retry loop closed its HTTP session inside the loop body, which also runs when continuing to the next attempt. When no session was supplied by the caller, attempt 1 closed it and the remaining attempts ran against a closed session, so every transient rate-limit, server error or timeout became an immediate failure. Home Assistant was unaffected, as it supplies its own session.
- **`close()` no longer closes a session it does not own** - It closed `self._session` unconditionally, which only ever held the caller's session. Home Assistant shares one HTTP session across every integration, so a call to `close()` would have disrupted unrelated integrations. Sessions created by the library are still closed as before.

### Changed

- The HTTP session is now created on first use and reused for the object's lifetime rather than per request, so connections are pooled.

## [1.4.3] - 2026-08-06

### Security

- **Credentials no longer written to debug logs** - The debug logging added for troubleshooting dumped whole API requests and responses verbatim, which meant enabling `pysmartcocoon: debug` (as the README instructs) wrote the account password, bearer token, API client id, account email and per-fan `mqtt_password` into `home-assistant.log` in plaintext. Those logs are routinely pasted into public GitHub issues. All credentials are now replaced with `**REDACTED**` before logging, and email addresses are masked to `d***@example.com` so accounts can still be told apart.

  **If you enabled debug logging for this integration, treat your SmartCocoon password as exposed** - rotate it, and check any logs you have shared publicly.

## [1.4.2] - 2025-12-29

### Fixed

- **Connection status correction** - Fixed issue where fans that were unplugged or offline for more than 15 minutes were incorrectly reported as connected. The library now automatically corrects stale connection status from the SmartCocoon API by checking the `last_connection` timestamp.

### Added

- **Debug logging** - Added debug logging to show raw API `connected` values for troubleshooting connection status issues
- **Debug script** - Added `tests/debug_fan_connection.py` script to help diagnose connection status issues by comparing raw API data with processed values
- **Debug documentation** - Added `DEBUG_FAN_CONNECTION.md` guide for troubleshooting connection status problems

## [1.4.1] - 2025-12-14

### Added

- **`__version__` attribute** in package `__init__.py` for easier version checking

### Fixed

- **Devcontainer build error** - Fixed setuptools package discovery to exclude `node_modules` directory
- **Pre-commit prettier hook** - Replaced unstable alpha version with stable v3.1.0

### Changed

- **Dependency updates**:
  - Bumped aiohttp from 3.13.1 to 3.13.2
  - Bumped actions/checkout from 5 to 6 in GitHub Actions workflows
  - Bumped peter-evans/create-pull-request from 7 to 8 in GitHub Actions workflows
- **Pre-commit hooks**: Autoupdated to latest versions

### Maintenance

- Added `node_modules/` to `.gitignore` to prevent cache files from being committed
- Removed accidentally committed prettier cache file

## [1.4.0] - 2025-10-19

### Added

- **Comprehensive test suite** with 8 test files
  - Unit tests for basic functionality without API calls
  - Integration tests for real API testing (marked with `@pytest.mark.integration`)
  - Connection monitoring tests
  - Extra state attributes tests
  - Fan control tests with debug logging
  - Smoke tests for comprehensive API testing
- **Debug logging system** with detailed API request/response information
  - Box-drawing characters for better log formatting
  - Request/response headers and body logging
  - Authentication success/failure logging
  - Defensive programming for missing API headers
- **Local development scripts** in `scripts/` directory
  - `run-local-checks.sh` - Run all quality checks locally
  - `run-github-actions.sh` - Run GitHub Actions workflows locally
- **Organized documentation structure** in `docs/` directory
  - `DEBUG_GUIDE.md` - Comprehensive debug logging guide
  - `DEVCONTAINER_README.md` - Development environment setup
  - `CONTRIBUTING.md` - Contribution guidelines
  - `DOCS.md` - Documentation index
- **Custom pytest markers** for test categorization
  - `@pytest.mark.integration` for integration tests
  - Proper test exclusion from CI for integration tests
- **Enhanced error handling** and defensive programming
- **Comprehensive README** with table of contents and usage examples

### Changed

- **Updated devcontainer** for Python 3.13.2 with all necessary tools
- **Enhanced GitHub Actions workflow** to exclude integration tests
- **Improved code quality** with comprehensive linting and type checking
- **Updated pre-commit hooks** with latest tool versions
- **Enhanced API error handling** with null checks for critical headers

### Fixed

- **All MyPy type checking errors** with proper type annotations
- **All pylint warnings** with appropriate suppressions
- **Code formatting issues** with black and isort
- **Import organization** and code structure
- **Line length violations** and code style issues

### Removed

- Old `test_integration.py` file (replaced with modular test files)

### Security

- Enhanced API response validation with defensive programming
- Added null checks for critical authentication headers

## [1.3.1] - Previous Release

### Added

- Basic SmartCocoon API integration
- Fan control functionality
- Room and thermostat management
- Basic error handling

---

## Development

### Testing

- **Unit Tests**: Run with `pytest tests/ -k "not integration"`
- **Integration Tests**: Run with `pytest tests/ -k "integration"` (requires API credentials)
- **All Tests**: Run with `pytest tests/`

### Code Quality

- **Pre-commit hooks**: Run with `pre-commit run --all-files`
- **Local checks**: Run with `./scripts/run-local-checks.sh`
- **GitHub Actions**: Run with `./scripts/run-github-actions.sh`

### Documentation

- See `docs/` directory for comprehensive guides
- README.md for quick start and overview
