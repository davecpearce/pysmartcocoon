# Contributing to PySmartCocoon

Thank you for your interest in contributing to PySmartCocoon! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [License](#license)

## Getting Started

### Prerequisites

- Python 3.13.2+
- Git
- VS Code (recommended)
- Docker (for running GitHub Actions locally)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/pysmartcocoon.git
   cd pysmartcocoon
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/davecpearce/pysmartcocoon.git
   ```

## Development Environment

### Using VS Code Dev Container (Recommended)

The project includes a complete development environment using VS Code Dev Containers:

1. Open the project in VS Code
2. When prompted, reopen in container
3. The devcontainer will automatically set up all dependencies

See [DEVCONTAINER_README.md](DEVCONTAINER_README.md) for detailed setup instructions.

### Manual Setup

If you prefer to set up the environment manually:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .[test]

# Install pre-commit hooks
pre-commit install
```

## Code Style

This project uses several tools to maintain consistent code style:

- **Black**: Code formatting
- **isort**: Import sorting
- **pylint**: Code linting
- **mypy**: Type checking

### Running Code Quality Checks

```bash
# Run all checks
pre-commit run --all-files

# Run individual tools
black .
isort .
pylint pysmartcocoon/
mypy pysmartcocoon/
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed when you run `pre-commit install`. These hooks will run automatically on every commit to ensure code quality.

To run pre-commit on all files:

```bash
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v -s

# Run with coverage
pytest --cov=pysmartcocoon

# Run specific test file
pytest tests/test_fan_control.py -v -s
```

### Integration Tests

Integration tests require valid SmartCocoon credentials:

1. Copy `tests/template.env` to `tests/.env`
2. Fill in your credentials:
   ```bash
   USERNAME="your_email@example.com"
   PASSWORD="your_password"
   FAN_ID="your_fan_id"
   ```
3. Set the integration test flag:
   ```bash
   export RUN_INTEGRATION=1
   ```
4. Run integration tests:
   ```bash
   pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
   ```

### Debug Logging Tests

To test debug logging functionality:

```bash
# Run the comprehensive test script
python tests/test_smoke_test.py

# Run specific debug test
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
```

## Submitting Changes

### Creating a Pull Request

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write your code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**:

   ```bash
   # Run all tests
   pytest

   # Run code quality checks
   pre-commit run --all-files
   ```

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

### Pull Request Guidelines

- **Clear title**: Use a descriptive title
- **Description**: Explain what changes you made and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update documentation if needed
- **Breaking changes**: Clearly mark any breaking changes

## Bug Reports

### Before Reporting

1. Check if the issue has already been reported
2. Try the latest version
3. Enable debug logging to gather more information

### Reporting a Bug

Use GitHub's [issue tracker](https://github.com/davecpearce/pysmartcocoon/issues) to report bugs.

**Great Bug Reports** include:

- **Summary**: Brief description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, library version
- **Debug logs**: Include relevant debug output (see [DEBUG_GUIDE.md](DEBUG_GUIDE.md))
- **Code sample**: Minimal code that reproduces the issue

### Example Bug Report

```markdown
## Bug Report

**Summary**: Fan control fails with authentication error

**Steps to reproduce**:

1. Install pysmartcocoon
2. Set up credentials in .env file
3. Run: `python tests/test_smoke_test.py`
4. See authentication error

**Expected behavior**: Should authenticate successfully

**Actual behavior**: Gets KeyError: 'access-token'

**Environment**:

- Python: 3.13.2
- OS: Ubuntu 22.04
- pysmartcocoon: 0.1.0

**Debug logs**:
[Include relevant debug output here]
```

## Feature Requests

### Before Requesting

1. Check if the feature has already been requested
2. Consider if it fits the project's scope
3. Think about the implementation approach

### Requesting a Feature

Use GitHub's [issue tracker](https://github.com/davecpearce/pysmartcocoon/issues) with the "enhancement" label.

**Good Feature Requests** include:

- **Clear description**: What you want to achieve
- **Use case**: Why this feature would be useful
- **Proposed solution**: How you think it should work
- **Alternatives**: Other approaches you've considered

## Code Review Process

1. **Automated checks**: All PRs must pass automated tests and code quality checks
2. **Manual review**: A maintainer will review your code
3. **Feedback**: Address any feedback from reviewers
4. **Merge**: Once approved, your changes will be merged

## Development Workflow

### Running GitHub Actions Locally

You can run the same checks that run in GitHub Actions locally:

```bash
# Run the tests workflow
./scripts/run-github-actions.sh tests

# List available workflows
./scripts/run-github-actions.sh list
```

### Debugging

For debugging issues, see the [Debug Guide](DEBUG_GUIDE.md) for comprehensive information about debug logging.

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE.md).

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the "question" label
- Check the [Debug Guide](DEBUG_GUIDE.md) for troubleshooting
- Review the [Development Guide](DEVCONTAINER_README.md) for setup help

Thank you for contributing to PySmartCocoon! 🎉
