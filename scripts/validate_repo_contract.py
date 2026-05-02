#!/usr/bin/env python3
"""Validate the minimal repository contract for cloud-360.

This intentionally avoids README.md because the current README is known to be
incorrect and must not be treated as the source of truth for this contract.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    ".gitignore",
    "docs/adr/0001-repo-scope.md",
    "scripts/validate_repo_contract.py",
    ".github/workflows/ci.yml",
)
FORBIDDEN_NEW_PATH_PARTS = {
    "prod",
    "production",
    "secrets",
}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def git_diff_name_only(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def validate_required_files() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        return fail("Missing required contract files: " + ", ".join(missing))
    return 0


def validate_readme_not_modified() -> int:
    changed_files = set(git_diff_name_only("--cached")) | set(git_diff_name_only())
    if "README.md" in changed_files:
        return fail("README.md must not be modified by the minimal repo contract")
    return 0


def validate_no_production_config_added() -> int:
    changed_files = set(git_diff_name_only("--cached")) | set(git_diff_name_only())
    violations: list[str] = []

    for path in changed_files:
        parts = {part.lower() for part in Path(path).parts}
        if parts & FORBIDDEN_NEW_PATH_PARTS:
            violations.append(path)

    if violations:
        return fail(
            "Production/secret-scoped paths are out of scope for this contract: "
            + ", ".join(sorted(violations))
        )
    return 0


def main() -> int:
    checks = (
        validate_required_files,
        validate_readme_not_modified,
        validate_no_production_config_added,
    )
    for check in checks:
        result = check()
        if result != 0:
            return result

    print("Repository contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
