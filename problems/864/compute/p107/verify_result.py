#!/usr/bin/env python3
"""Standalone replay of every P107 retained candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import audit


def candidates(value):
    if isinstance(value, dict):
        if all(field in value for field in ("B", "h", "b", "C_S", "T_F")):
            yield value
        for child in value.values():
            yield from candidates(child)
    elif isinstance(value, list):
        for child in value:
            yield from candidates(child)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="ascii"))
    checked = 0
    seen = set()
    for stored in candidates(payload):
        identity = (stored.get("sha256"), stored.get("h"), stored.get("b"))
        if identity in seen:
            continue
        seen.add(identity)
        fresh = audit(stored["B"], int(stored["h"]), int(stored["b"]))
        for field in (
            "sha256", "p", "h", "b", "delta", "sum_count",
            "difference_count", "literal_hole", "C_S", "T_F", "V_b",
            "P101_excess", "RM97_demands", "RM97_slots", "RM97_matched",
            "RM97_unmatched", "folds", "triangles",
        ):
            if fresh[field] != stored[field]:
                raise AssertionError((field, fresh[field], stored[field]))
        checked += 1
    print({"status": "PASS", "candidates_checked": checked})


if __name__ == "__main__":
    main()
