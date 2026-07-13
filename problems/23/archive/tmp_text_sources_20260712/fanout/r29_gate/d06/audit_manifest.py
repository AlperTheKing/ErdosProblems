"""Strict independent input gate for the claimed R29 Hamming-one census.

No claimed structural shortcut is accepted.  A future reproducible census must
supply the graph, cut, complete row bank, selected tuple, and score scope.
All numeric score values are parsed as integers or fractions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REQUIRED = ("vertices", "edges", "cut_side", "rows", "selected", "scope")


def canonical_hash(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def exact(value: object) -> Fraction:
    if isinstance(value, bool):
        raise TypeError("booleans are not exact scores")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"non-exact numeric input: {value!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ns = ap.parse_args()
    data = json.loads(ns.manifest.read_text(encoding="utf-8"), parse_float=lambda _: (_ for _ in ()).throw(ValueError("floats forbidden")))
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise SystemExit("INCOMPLETE MANIFEST: missing " + ", ".join(missing))
    # Force exact parsing of every explicitly supplied numeric score parameter.
    for value in data.get("score_parameters", {}).values():
        exact(value)
    print(json.dumps({"status": "input-complete", "canonical_sha256": canonical_hash(data)}, sort_keys=True))


if __name__ == "__main__":
    main()
