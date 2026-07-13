#!/usr/bin/env python3
"""Find RM97-deficient one-mark mutations near the lifted P105 witness."""

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


p106 = load("p106_lifted_windows", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")
p106m = load("p106_lifted_match", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    witness = data["subset_search"]["q2_lifted_witness"]
    base, h = tuple(witness["B"]), int(witness["h"])
    candidates = []
    for deleted in range(1, len(base) - 1):
        candidates.append((f"delete {base[deleted]}", base[:deleted] + base[deleted + 1:]))
    insertions = list(p106m.individually_admissible_insertions(base))
    for inserted in insertions:
        candidates.append((f"insert {inserted}", tuple(sorted(base + (inserted,)))))

    rows = failures = 0
    records = []
    for transform, values in candidates:
        for b in (1, 2):
            rows += 1
            folds, triangles, intervals, slots, _differences = p106.residual_system(values, h, b)
            matched = p106m.greedy_match(intervals, slots)
            if matched == len(intervals):
                continue
            failures += 1
            records.append({
                "transform": transform, "p": len(values), "h": h, "b": b,
                "delta": (3 * len(values) ** 2 - len(values) + 2) // 2 - h,
                "C_S": len(folds), "T_F": len(triangles),
                "V_b": len(slots) - 2 * len(folds),
                "intervals": len(intervals), "slots": len(slots),
                "matched": matched,
            })
    result = {
        "base_p": len(base), "h": h,
        "direct_deletions": len(base) - 2,
        "individually_admissible_insertions": insertions,
        "phase_rows": rows, "RM97_failures": failures,
        "failure_records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "failure_records"}, indent=2))
    print(json.dumps(records[:5], indent=2))


if __name__ == "__main__":
    main()
