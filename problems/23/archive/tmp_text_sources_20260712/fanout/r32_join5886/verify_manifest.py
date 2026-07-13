"""Verify every artifact hash listed in this lane's manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "MANIFEST.sha256"


def main() -> None:
    checked = 0
    for raw_line in MANIFEST.read_text(encoding="ascii").splitlines():
        if not raw_line.strip():
            continue
        expected, name = raw_line.split(maxsplit=1)
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        assert actual == expected.lower(), (name, expected, actual)
        checked += 1
    print(f"PASS local manifest {checked}/{checked}")


if __name__ == "__main__":
    main()
