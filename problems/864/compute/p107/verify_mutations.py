#!/usr/bin/env python3
"""Replay every extremal row retained by the P107 mutation search."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="ascii"))
    checked = 0
    for lane in payload.values():
        if not isinstance(lane, dict):
            continue
        for key in ("max_P101_row", "max_RM97_row"):
            stored = lane.get(key)
            if stored is None:
                continue
            fresh = audit(stored["B"], int(stored["h"]), int(stored["b"]))
            for field in (
                "sha256", "p", "h", "b", "delta", "literal_hole", "C_S",
                "T_F", "V_b", "P101_excess", "RM97_demands", "RM97_slots",
                "RM97_matched", "RM97_unmatched",
            ):
                if fresh[field] != stored[field]:
                    raise AssertionError((key, field, fresh[field], stored[field]))
            checked += 1
    print({"status": "PASS", "retained_rows_checked": checked})


if __name__ == "__main__":
    main()

