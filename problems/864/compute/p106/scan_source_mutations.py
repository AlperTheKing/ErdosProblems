#!/usr/bin/env python3
"""Exact direct RM97 scan of one-mark P105 source mutations."""

from __future__ import annotations

import argparse
import heapq
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


p106 = load("p106_mutations", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")


def is_sidon(values):
    seen = set()
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in seen:
                return False
            seen.add(total)
    return True


def greedy_match(intervals, slots):
    intervals = sorted((row["left"], row["right"]) for row in intervals)
    points = sorted(row["value"] for row in slots)
    heap = []
    index = matched = 0
    for point in points:
        while index < len(intervals) and intervals[index][0] <= point:
            heapq.heappush(heap, intervals[index][1]); index += 1
        if heap and heap[0] < point:
            return matched
        if heap:
            heapq.heappop(heap); matched += 1
    return matched


def audit(values, h, b):
    folds, triangles, intervals, slots, _differences = p106.residual_system(values, h, b)
    matched = greedy_match(intervals, slots)
    return {
        "C_S": len(folds), "T_F": len(triangles),
        "V_b": len(slots) - 2 * len(folds),
        "intervals": len(intervals), "slots": len(slots),
        "matched": matched, "failure": matched != len(intervals),
    }


def individually_admissible_insertions(base):
    occupied = set(base)
    sums = {left + right for i, left in enumerate(base) for right in base[i:]}
    for value in range(1, base[-1]):
        if value in occupied:
            continue
        new_sums = [value + mark for mark in base] + [2 * value]
        if len(set(new_sums)) == len(new_sums) and set(new_sums).isdisjoint(sums):
            yield value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    source = data["subset_search"]["source_subset"]
    base, h = tuple(source["B"]), int(source["h"])
    candidates = []
    for deleted in range(1, len(base) - 1):
        values = base[:deleted] + base[deleted + 1:]
        candidates.append((f"delete {base[deleted]}", values))
    insertions = list(individually_admissible_insertions(base))
    for inserted in insertions:
        candidates.append((f"insert {inserted}", tuple(sorted(base + (inserted,)))))

    rows = failures = 0
    first = None
    best = None
    for transform, values in candidates:
        assert is_sidon(values)
        p = len(values)
        delta = (3 * p * p - p + 2) // 2 - h
        if delta <= 0:
            continue
        for b in (1, 2):
            rows += 1
            row = audit(values, h, b)
            retained = {"transform": transform, "p": p, "h": h, "b": b, "delta": delta, **row}
            if row["failure"]:
                failures += 1
                first = first or {"B": values, **retained}
            key = (row["intervals"] - row["slots"], row["intervals"] - row["matched"], row["T_F"])
            if best is None or key > best[0]:
                best = (key, retained)
    result = {
        "source_p": len(base), "source_h": h,
        "direct_deletions": len(base) - 2,
        "individually_admissible_insertions": insertions,
        "positive_defect_phase_rows": rows,
        "RM97_failures": failures,
        "first_failure": first,
        "closest_row": best[1] if best else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
