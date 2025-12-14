# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-12-14

### Added

- **`__version__` attribute** in package `__init__.py` for easier version checking

### Fixed

- **Silent fan update failure bug** - Fan updates now properly report failures
- **Authentication bug** - Improved authentication error handling and code quality
- **\_async_update_fan method** - Fixed to properly handle failure cases
- **Pre-commit prettier hook** - Replaced unstable alpha version with stable v3.1.0

### Changed

- **Dependency updates**:
  - Bumped aiohttp from 3.13.1 to 3.13.2
  - Bumped actions/checkout from 5 to 6 in GitHub Actions workflows
  - Bumped peter-evans/create-pull-request from 7 to 8 in GitHub Actions workflows
- **Pre-commit hooks**: Autoupdated to latest versions

### Documentation

- Added integration test documentation

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
