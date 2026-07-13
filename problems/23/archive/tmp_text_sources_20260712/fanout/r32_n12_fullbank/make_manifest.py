"""Write SHA-256 pins for every owned deliverable except cache files."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "MANIFEST.sha256"


def main() -> int:
    paths = sorted(
        path
        for path in HERE.iterdir()
        if path.is_file() and path.name != MANIFEST.name
    )
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in paths
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"files={len(lines)} manifest={hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

