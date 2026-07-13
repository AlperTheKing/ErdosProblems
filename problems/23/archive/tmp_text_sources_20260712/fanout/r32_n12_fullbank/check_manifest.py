"""Verify every entry in MANIFEST.sha256."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> int:
    lines = (HERE / "MANIFEST.sha256").read_text(encoding="ascii").splitlines()
    for line in lines:
        expected, name = line.split("  ", 1)
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError((name, actual, expected))
    print(f"PASS files={len(lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

