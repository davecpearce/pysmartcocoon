"""Shared helpers for the diagnostic scripts in this directory.

These scripts are run by hand against a live account when an issue needs
real payloads rather than guesses. Keeping the credential loading and the
sys.path bootstrap in one place stops the two copies drifting apart.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The repo root has to reach sys.path before pysmartcocoon is imported, so
# these run from a plain checkout without `pip install -e .` first.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_credentials() -> tuple[str, str]:
    """Return (username, password) from the environment or a .env file.

    Never read from argv: these end up in shell history, and the whole
    point of these scripts is that their output is safe to share.
    """
    username = os.environ.get("SC_USERNAME")
    password = os.environ.get("SC_PASSWORD")

    if not (username and password):
        for candidate in (REPO_ROOT / ".env", REPO_ROOT / "tests" / ".env"):
            if not candidate.is_file():
                continue
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, raw = line.partition("=")
                value = raw.strip().strip("'\"")
                key = key.strip().upper()
                if key in ("SC_USERNAME", "USERNAME") and not username:
                    username = value
                elif key in ("SC_PASSWORD", "PASSWORD") and not password:
                    password = value

    if not (username and password):
        sys.exit(
            "No credentials found.\n"
            "Set SC_USERNAME and SC_PASSWORD in the environment, or put "
            "them in a .env file at the repo root."
        )

    return username, password
