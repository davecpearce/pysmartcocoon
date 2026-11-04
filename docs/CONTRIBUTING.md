# Contributing to PySmartCocoon

Bug reports, fixes and features are all welcome.

## Setting up

You need Python 3.13.2 or later.

```bash
git clone https://github.com/<you>/pysmartcocoon.git
cd pysmartcocoon
python3 -m venv venv && source venv/bin/activate
pip install -r requirements_test.txt && pip install -e .
pre-commit install
```

A VS Code dev container is included as an alternative; see
[DEVCONTAINER_README.md](DEVCONTAINER_README.md).

## Code style

CI runs the pre-commit hooks, then mypy, then the tests. Run the same locally:

```bash
pre-commit run --all-files
mypy pysmartcocoon
```

The hooks run black (line length 79), isort, pyupgrade, pylint, bandit and prettier. Read the hook arguments from `.pre-commit-config.yaml` rather than
running the tools with their defaults. pylint here does **not** disable
`unused-argument`, so stub classes in tests need an explicit
`# pylint: disable=unused-argument`.

black, isort, bandit and pylint are pinned in both `requirements_test.txt` and
`.pre-commit-config.yaml`. The two must agree, and the
`tools pinned in two files must agree` hook fails the build when they don't. To
take the pre-commit versions:

```bash
python scripts/check_tool_pins.py --fix
```

## Tests

```bash
pytest -m "not integration"
```

This is what CI runs. Every change should come with a test, and a fix should come with
a test that **fails without the fix**. Stash the source change and check that the test
goes red.

Integration tests log in to a real account and change real fans. They are skipped
unless you opt in:

```bash
cp tests/template.env tests/.env    # USERNAME, PASSWORD, FAN_ID
RUN_INTEGRATION=1 pytest -m integration -v -s
```

### Rules that must not regress

- **Credentials never reach logs.** Every log line that writes request or response
  data must go through `redact()` in `pysmartcocoon/redact.py`. Tests check captured
  log output, not just return values.
- **Never close a session you did not create.** Home Assistant passes in a shared
  session.
- **Fan control methods return `bool`.** Don't discard the result anywhere in the
  chain, or a rejected command looks like it worked.
- **Never connect to the MQTT broker with a fan's `mqtt_username`/`mqtt_password`.**
  They belong to the fan, and using them knocks the real fan offline.

## Pull requests

1. Branch from `main`.
2. Add tests, and update the README or `CHANGELOG.md` (under a new heading) if users
   would notice the change.
3. Run `pre-commit run --all-files` and `pytest -m "not integration"`.
4. Open the pull request. `main` is protected, and branches must be up to date
   before merging.

## Releasing

Maintainers only. Publishing is automated through PyPI Trusted Publishing; there is
no API token.

1. Add the release to `CHANGELOG.md`.
2. Run `bumpver update --patch` (or `--minor`). This updates `pyproject.toml` and
   `pysmartcocoon/__init__.py`, then commits, tags and pushes.
3. The `release.yml` workflow builds, checks and publishes the tag. It refuses to
   publish if the tag and `pyproject.toml` disagree.

A release reaches Home Assistant users only after
[ha-smartcocoon](https://github.com/davecpearce/ha-smartcocoon) updates its pin in
`manifest.json` and `requirements.txt` and makes its own release.

## Reporting bugs

Open an [issue](https://github.com/davecpearce/pysmartcocoon/issues). Include the
library version, what you expected, what happened, and debug logs (see the
[Debug Guide](DEBUG_GUIDE.md)). If you use Home Assistant, report it on
[ha-smartcocoon](https://github.com/davecpearce/ha-smartcocoon/issues) instead.

## License

Contributions are licensed under the [MIT License](../LICENSE.md).
