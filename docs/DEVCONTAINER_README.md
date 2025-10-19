# Devcontainer Setup for pysmartcocoon

This devcontainer is configured to provide a complete development environment for the pysmartcocoon project, including the ability to run GitHub Actions locally.

## 🚀 Features

### Development Tools

- **Python 3.13.2** - Matches Home Assistant requirements
- **Docker CLI** - Required for running GitHub Actions locally
- **act** - Tool for running GitHub Actions locally
- **Pre-commit hooks** - Automated code quality checks
- **All Python dependencies** - From requirements.txt and requirements_test.txt

### VS Code Extensions

- Python development tools (Pylance, Black formatter, Pylint, MyPy)
- YAML support for GitHub Actions workflows
- Docker support
- GitHub Pull Request integration
- Makefile tools

### Testing & Quality Tools

- **pytest** - Testing framework
- **mypy** - Static type checking
- **black** - Code formatting
- **pylint** - Code linting
- **isort** - Import sorting
- **bandit** - Security linting
- **pre-commit** - Git hooks

## 🛠️ Running GitHub Actions Locally

### Quick Start

```bash
# Run the tests workflow (linting, pre-commit, mypy)
./scripts/run-github-actions.sh tests

# List available workflows
./scripts/run-github-actions.sh list

# Get help
./scripts/run-github-actions.sh help
```

### Manual act Commands

```bash
# Run the tests workflow
act -W .github/workflows/tests.yaml

# Run with verbose output
act -W .github/workflows/tests.yaml --verbose

# List all available workflows
act --list
```

## 🔧 Development Workflow

### 1. Code Quality Checks

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run individual tools
black .
isort .
pylint pysmartcocoon/
mypy pysmartcocoon/const.py pysmartcocoon/types.py
```

### 2. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pysmartcocoon

# Run integration tests (requires credentials)
export RUN_INTEGRATION=1
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
```

### 3. Debug Logging Testing

```bash
# Run the comprehensive test script
python tests/test_smoke_test.py

# Run specific debug test
pytest tests/test_fan_control.py::test_integration_debug_logging -v -s
```

## 📁 Project Structure

```
pysmartcocoon/
├── .devcontainer/           # Devcontainer configuration
│   ├── Dockerfile          # Container definition
│   └── devcontainer.json   # VS Code settings
├── .github/workflows/       # GitHub Actions workflows
│   └── tests.yaml          # Main CI workflow
├── pysmartcocoon/          # Main package code
├── tests/                  # Test files
├── scripts/                # Development utility scripts
│   ├── run-github-actions.sh   # Helper script for local GitHub Actions
│   └── run-local-checks.sh     # Manual local checks script
└── requirements*.txt       # Python dependencies
```

## 🐛 Troubleshooting

### act Issues

- **Docker not available**: Ensure Docker is running and accessible
- **First run slow**: act downloads Docker images on first use
- **Permission issues**: Make sure the script is executable (`chmod +x scripts/run-github-actions.sh`)

### Development Issues

- **Missing dependencies**: Run `pip install -e .[test]` to install all dependencies
- **Pre-commit fails**: Run `pre-commit install` to set up git hooks
- **Type checking errors**: Check mypy configuration in pyproject.toml
- **Pre-commit Node.js errors**: The container includes `libatomic1` for Node.js compatibility

### VS Code Issues

- **Extensions not loading**: Reload the window (Ctrl+Shift+P → "Developer: Reload Window")
- **Python interpreter**: Should auto-detect `/usr/local/bin/python`
- **Formatting not working**: Check that Black formatter is enabled in settings

## 🔄 Rebuilding the Devcontainer

If you make changes to the devcontainer configuration:

1. **Command Palette** (Ctrl+Shift+P)
2. **Dev Containers: Rebuild Container**
3. Wait for the rebuild to complete

This will install all the new tools and dependencies.

## 📚 Additional Resources

- [act Documentation](https://github.com/nektos/act)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)
- [Pre-commit Hooks](https://pre-commit.com/)
- [pytest Documentation](https://docs.pytest.org/)
