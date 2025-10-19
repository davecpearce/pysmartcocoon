# Development Scripts

This directory contains utility scripts for development and testing.

## 📜 Available Scripts

### `run-github-actions.sh`

Helper script to run GitHub Actions workflows locally using `act`.

**Usage:**

```bash
# Run the tests workflow
./scripts/run-github-actions.sh tests

# List available workflows
./scripts/run-github-actions.sh list

# Get help
./scripts/run-github-actions.sh help
```

**Requirements:**

- `act` tool installed
- Docker running
- GitHub Actions workflow files in `.github/workflows/`

### `run-local-checks.sh`

Manual script to run the same checks as GitHub Actions locally without Docker.

**Usage:**

```bash
# Run all local checks
./scripts/run-local-checks.sh
```

**What it does:**

- Environment setup verification
- Python dependency installation
- Code quality checks (pre-commit, mypy, pylint, black, isort)
- Test execution
- Summary report

**Requirements:**

- Python 3.13.2+
- All dependencies installed (`pip install -e .[test]`)

## 🚀 Quick Start

1. **For GitHub Actions simulation:**

   ```bash
   ./scripts/run-github-actions.sh tests
   ```

2. **For local development checks:**
   ```bash
   ./scripts/run-local-checks.sh
   ```

## 🔧 Troubleshooting

### Permission Issues

```bash
chmod +x scripts/*.sh
```

### Script Not Found

Make sure you're running from the project root directory.

### Docker Issues (for GitHub Actions script)

- Ensure Docker is running
- Check if you're in a container with Docker-in-Docker support

## 📚 Related Documentation

- [Development Guide](../docs/DEVCONTAINER_README.md) - Complete development setup
- [Contributing Guide](../docs/CONTRIBUTING.md) - Contribution workflow
- [Debug Guide](../docs/DEBUG_GUIDE.md) - Debugging and troubleshooting
