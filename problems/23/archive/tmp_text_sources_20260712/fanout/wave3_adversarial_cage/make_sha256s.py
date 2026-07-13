#!/usr/bin/env python3
"""Write stable SHA-256 sums for every owned artifact except the sum file."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "SHA256SUMS.txt"


def main() -> None:
    lines = []
    for path in sorted(HERE.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path == OUTPUT:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"wrote {len(lines)} hashes to {OUTPUT}")


if __name__ == "__main__":
    main()
