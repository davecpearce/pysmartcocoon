#!/usr/bin/env python3
"""Fail when a tool pinned in two places disagrees with itself.

`black`, `isort` and `bandit` are pinned both in `requirements_test.txt`
and as a `rev` in `.pre-commit-config.yaml`. pre-commit is what gates CI,
so when the two drift the formatter judging a pull request is not the one
anyone runs locally.

Each half has its own updater and neither sees the other: dependabot bumps
`requirements_test.txt`, and the monthly `pre-commit autoupdate` workflow
bumps the `rev`s. Both open pull requests that would drift the pair.

Rather than hold a list of known pairs -- which would miss the next tool to
become dual-pinned -- this derives a package name from each hook repo URL
and checks whether `requirements_test.txt` also pins it. Hooks under
`repo: local` (pylint here) carry no `rev` and are not compared.

Run locally with:

    python scripts/check_tool_pins.py          # report, exit 1 on mismatch
    python scripts/check_tool_pins.py --fix    # rewrite requirements_test.txt

`--fix` treats the pre-commit `rev` as the source of truth, which is what
the autoupdate workflow needs after bumping the hooks.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PRE_COMMIT = REPO_ROOT / ".pre-commit-config.yaml"
REQUIREMENTS = REPO_ROOT / "requirements_test.txt"

#: Hook repos whose name differs from the package they install. The common
#: `mirrors-x` / `x-pre-commit` spellings are derived, so this is only for
#: genuine exceptions.
NAME_OVERRIDES: dict[str, str] = {
    "pre-commit-hooks": "",  # a hook bundle, not a pinned package
    "prettier": "",  # npm, never in requirements_test.txt
}

_REQ_PIN = re.compile(r"^([A-Za-z0-9._-]+)==([A-Za-z0-9._-]+)\s*$")


def package_for(repo_url: str) -> str:
    """Return the PyPI package a hook repo installs, or "" if not one."""
    slug = repo_url.rstrip("/").rsplit("/", 1)[-1].lower()
    slug = re.sub(r"^mirrors-", "", slug)
    slug = re.sub(r"-pre-commit$", "", slug)
    return NAME_OVERRIDES.get(slug, slug)


def precommit_pins() -> dict[str, str]:
    """Return {package: version} for every revisioned hook repo."""
    config = yaml.safe_load(PRE_COMMIT.read_text())
    pins: dict[str, str] = {}
    for repo in config.get("repos", []):
        url, rev = repo.get("repo"), repo.get("rev")
        if not url or url == "local" or not rev:
            continue
        package = package_for(str(url))
        if package:
            pins[package] = str(rev).lstrip("vV")
    return pins


def requirement_pins() -> dict[str, str]:
    """Return {package: version} for every `==` pin in requirements_test."""
    pins: dict[str, str] = {}
    for line in REQUIREMENTS.read_text().splitlines():
        match = _REQ_PIN.match(line.strip())
        if match:
            pins[match.group(1).lower()] = match.group(2)
    return pins


def fix(hooks: dict[str, str], mismatched: list[str]) -> None:
    """Rewrite the mismatched requirement pins to the hook revs."""
    lines = []
    for line in REQUIREMENTS.read_text().splitlines():
        match = _REQ_PIN.match(line.strip())
        if match and match.group(1).lower() in mismatched:
            name = match.group(1)
            line = f"{name}=={hooks[name.lower()]}"
        lines.append(line)
    REQUIREMENTS.write_text("\n".join(lines) + "\n")


def main() -> int:
    """Compare the two sources, and explain or apply the fix."""
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n", maxsplit=1)[0]
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="set requirements_test.txt to the pre-commit revs",
    )
    args = parser.parse_args()

    for path in (PRE_COMMIT, REQUIREMENTS):
        if not path.is_file():
            print(f"::error::{path} not found")
            return 1

    hooks = precommit_pins()
    reqs = requirement_pins()
    shared = sorted(set(hooks) & set(reqs))
    if not shared:
        print("No tool is pinned in both files. Nothing to compare.")
        return 0

    mismatched = [p for p in shared if hooks[p] != reqs[p]]
    for package in shared:
        mark = "MISMATCH" if package in mismatched else "ok"
        print(
            f"  {mark:9} {package:<10} "
            f"pre-commit={hooks[package]:<9} requirements={reqs[package]}"
        )

    if not mismatched:
        print(f"\nAll {len(shared)} dual-pinned tool(s) agree.")
        return 0

    if args.fix:
        fix(hooks, mismatched)
        print(
            f"\nSet {', '.join(mismatched)} in requirements_test.txt "
            "to match the pre-commit revs."
        )
        return 0

    print()
    for package in mismatched:
        print(
            f"::error::{package} is pinned at {hooks[package]} in "
            f".pre-commit-config.yaml but {reqs[package]} in "
            "requirements_test.txt."
        )
    print(
        "\n  pre-commit is what gates CI, so while these disagree the tool"
        "\n  enforced on a pull request is not the one you run locally."
        "\n  Set both to the same version in one commit. To take the"
        "\n  pre-commit revs:"
        "\n\n    python scripts/check_tool_pins.py --fix"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
