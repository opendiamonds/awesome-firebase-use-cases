#!/usr/bin/env python3
"""Fail if pure calculator module imports I/O layers (C1 BR-C-1)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "backend" / "cost" / "cost_calculator.py"

FORBIDDEN = re.compile(
    r"^\s*(?:import|from)\s+(?:httpx|requests|sqlalchemy|fastapi)\b",
    re.MULTILINE,
)


def main() -> int:
    if not TARGET.is_file():
        print(f"ERROR: missing {TARGET.relative_to(ROOT)}", file=sys.stderr)
        return 1

    text = TARGET.read_text(encoding="utf-8")
    hits = [m.group(0).strip() for m in FORBIDDEN.finditer(text)]
    if hits:
        print(
            f"ERROR: forbidden imports in {TARGET.relative_to(ROOT)}:",
            file=sys.stderr,
        )
        for line in hits:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"OK: {TARGET.relative_to(ROOT)} has no forbidden I/O imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
