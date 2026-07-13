#!/usr/bin/env python3
"""Audit every one-mark insertion into the full lifted P88 parent."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106s = load("p106_parent_scan", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")
p106m = load("p106_parent_candidates", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    parent = data["full_P88_q2_lift"]
    base, h = tuple(parent["B"]), int(parent["h"])
    candidates = list(p106m.individually_admissible_insertions(base))
    preserving = []
    best = None
    for value in candidates:
        values = tuple(sorted(base + (value,)))
        row = p106s.audit(values, h, 1)
        retained = {"insertion": value, **row}
        key = (row["intervals"] - row["matched"], row["intervals"] - row["slots"], row["T_F"])
        if best is None or key > best[0]:
            best = (key, retained)
        if row["RM97_failure"]:
            preserving.append(retained)
    result = {
        "base_p": len(base), "h": h,
        "individually_admissible_insertions": len(candidates),
        "RM97_failure_preserving_insertions": len(preserving),
        "best_row": best[1] if best else None,
        "preserving_rows": preserving,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "preserving_rows"}, indent=2))


if __name__ == "__main__":
    main()
