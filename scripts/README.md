# Development Scripts

This directory contains utility scripts for development and testing.

## 📜 Available Scripts

### `dump_api_payloads.py`

Fetches every API endpoint for your account and writes the responses to
`sc-api-dump-<timestamp>.json`, passed through the same `redact()` as debug logging.
It also lists every key the API sent that the library does not read, which is the
quickest way to spot a new or renamed field.

**Usage:**

```bash
export SC_USERNAME='you@example.com'
read -s SC_PASSWORD && export SC_PASSWORD   # keeps it out of shell history
python scripts/dump_api_payloads.py         # add --verbose for library debug logs
```

`SC_USERNAME` and `SC_PASSWORD` can also go in a `.env` file. Credentials are never
accepted as arguments. Credentials and your street address, postal code and
coordinates are masked, but room names and equipment are not, so read the file before
attaching it to an issue. Dump files are git-ignored.

### `check_tool_pins.py`

Runs as a pre-commit hook. Fails when a tool pinned in both `requirements_test.txt`
and `.pre-commit-config.yaml` has a different version in each.
`python scripts/check_tool_pins.py --fix` rewrites `requirements_test.txt` to match
the pre-commit revs. The monthly autoupdate workflow does this automatically.

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
- All dependencies installed (`pip install -r requirements_test.txt && pip install -e .`)

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
