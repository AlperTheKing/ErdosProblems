#!/usr/bin/env python3
"""Exhaust one/two-mark extensions of the p=65 near-positive RM witness."""

from __future__ import annotations

import argparse
import hashlib
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


p106s = load("p106_near_search", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")
p106m = load("p106_near_mutation", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    seed_data = json.loads((ROOT / "problems/864/compute/p106/extension_8.json").read_text())
    seed = tuple(seed_data["RM97_witness"]["B"])
    h, b = int(seed_data["RM97_witness"]["h"]), 1
    insertions = list(p106m.individually_admissible_insertions(seed))
    preserving = []
    one_rows = 0
    best_one = None
    for value in insertions:
        values = tuple(sorted(seed + (value,)))
        row = p106s.audit(values, h, b)
        one_rows += 1
        retained = {"insertion": value, **row}
        key = (row["intervals"] - row["matched"], row["intervals"] - row["slots"], row["T_F"])
        if best_one is None or key > best_one[0]:
            best_one = (key, retained)
        if row["RM97_failure"]:
            preserving.append(value)

    pair_tests = 0
    witness = None
    for i, left in enumerate(preserving):
        for right in preserving[i + 1:]:
            values = tuple(sorted(seed + (left, right)))
            if not p106m.is_sidon(values):
                continue
            pair_tests += 1
            row = p106s.audit(values, h, b)
            if not row["RM97_failure"]:
                continue
            p = len(values)
            witness = {
                "B": values, "insertions": [left, right],
                "p": p, "h": h, "b": b,
                "delta": (3 * p * p - p + 2) // 2 - h,
                "sha256": hashlib.sha256(",".join(map(str, values)).encode("ascii")).hexdigest(),
                **row,
            }
            break
        if witness is not None:
            break
    result = {
        "seed_p": len(seed), "h": h,
        "individually_admissible_insertions": len(insertions),
        "one_mark_rows_audited": one_rows,
        "one_mark_failure_preserving": len(preserving),
        "compatible_failure_preserving_pairs_audited": pair_tests,
        "best_one_mark_row": best_one[1] if best_one else None,
        "positive_defect_RM97_witness": witness,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = dict(result)
    if witness is not None:
        summary["positive_defect_RM97_witness"] = {
            key: value for key, value in witness.items() if key != "B"
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
