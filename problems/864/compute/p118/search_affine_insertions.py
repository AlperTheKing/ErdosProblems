#!/usr/bin/env python3
"""Exact P113 Hall search over affine-lift one-mark insertions.

The affine map B -> qB+(q-1), h -> qh preserves every existing fold and
loose triangle while opening integer positions for a new mark.  We inspect
every insertion position that can create a new fold, retain it only when the
augmented endpoint set is Sidon, and score the full P113 resource graph.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import importlib.util
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[4]
CORE_PATH = ROOT / "problems/864/compute/p118/search_p113_falsifier.py"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p118/affine_insertion_search.json"


def load_core():
    spec = importlib.util.spec_from_file_location("p118_core", CORE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_seeds() -> list[dict[str, object]]:
    p103_path = ROOT / "problems/864/compute/p103/audit_relation_matroid.py"
    spec = importlib.util.spec_from_file_location("p103_for_p118", p103_path)
    p103 = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(p103)
    seeds = [{"name": "P88_gamma7", "B": [x + 7 for x in p103.P88], "h": 3293}]
    p106 = json.loads((ROOT / "problems/864/compute/p106/positive_rm97_falsifier_certificate.json").read_text())
    seeds.append({"name": "P106_positive_RM97", "B": p106["B"], "h": p106["h"]})
    p110 = json.loads((ROOT / "problems/864/compute/p110/dimension_falsifiers.json").read_text())
    for key in ("smallest_failure", "strongest_failure"):
        seeds.append({"name": f"P110_{key}", "B": p110[key]["B"], "h": p110[key]["h"]})
    return seeds


def insertion_positions(values: Sequence[int], h: int) -> list[int]:
    sums = {left + right for i, left in enumerate(values) for right in values[i:]}
    positions = {
        candidate
        for mark in values
        for total in sums
        for candidate in (total - h - mark, total + h - mark)
        if 0 <= candidate < h - 1
    }
    return sorted(positions - set(values))


def insertion_is_sidon(values: Sequence[int], differences: set[int], candidate: int) -> bool:
    new_differences = [abs(candidate - mark) for mark in values]
    return (
        len(new_differences) == len(set(new_differences))
        and differences.isdisjoint(new_differences)
    )


def hard_score(row: dict[str, object]) -> tuple[int, ...]:
    return (
        int(row["hall_deficiency"]),
        int(row["difference_deficiency"]),
        int(row["support_deficiency"]),
        int(row["peel_core_excess"]),
        int(row["peel_core_left"]),
        -int(row["resource_slack"]),
        int(row["T_F"]),
    )


def retain(rows: list[dict[str, object]], row: dict[str, object], keep: int) -> None:
    rows.append(row)
    rows.sort(key=hard_score, reverse=True)
    del rows[keep:]


def worker(task: dict[str, object]) -> dict[str, object]:
    core = load_core()
    base = tuple(int(x) for x in task["B"])
    h0 = int(task["h"])
    q = int(task["q"])
    values = tuple(q * x + q - 1 for x in base)
    h = q * h0
    differences = core.positive_differences(values)
    old_folds = core.canonical_folds(values, h)
    old_triangles = len(core.loose_triangles(old_folds))
    positions = insertion_positions(values, h)
    start, stop = int(task["start"]), int(task["stop"])
    tested = valid = changed = failures = 0
    best: list[dict[str, object]] = []
    keep = int(task["keep"])
    for candidate in positions[start:stop]:
        tested += 1
        if not insertion_is_sidon(values, differences, candidate):
            continue
        valid += 1
        augmented = tuple(sorted(values + (candidate,)))
        folds = core.canonical_folds(augmented, h)
        triangles = core.loose_triangles(folds)
        if len(triangles) == old_triangles:
            continue
        changed += 1
        row = core.audit(
            augmented,
            h,
            f"{task['name']} q={q} insert={candidate}",
        )
        failures += int(row["hall_deficiency"] > 0)
        retain(best, row, keep)
    return {
        "name": task["name"],
        "q": q,
        "start": start,
        "stop": stop,
        "candidate_positions": len(positions),
        "tested": tested,
        "valid_sidon": valid,
        "triangle_changed": changed,
        "failures": failures,
        "best": best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--keep", type=int, default=24)
    parser.add_argument("--chunk", type=int, default=512)
    parser.add_argument("--include-q3-p88", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    workers = max(1, min(args.workers, 64))
    seeds = load_seeds()
    tasks = []
    for seed in seeds:
        qs = [2]
        if args.include_q3_p88 and seed["name"] == "P88_gamma7":
            qs.append(3)
        for q in qs:
            values = tuple(q * int(x) + q - 1 for x in seed["B"])
            positions = insertion_positions(values, q * int(seed["h"]))
            for start in range(0, len(positions), args.chunk):
                tasks.append({
                    **seed,
                    "q": q,
                    "start": start,
                    "stop": min(len(positions), start + args.chunk),
                    "keep": args.keep,
                })
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker, task) for task in tasks]
        for future in as_completed(futures):
            results.append(future.result())
    best: list[dict[str, object]] = []
    for result in results:
        for row in result["best"]:
            retain(best, row, args.keep)
    payload = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "domain": "all fold-changing one-mark insertions into selected affine endpoint-Sidon lifts",
        "workers": workers,
        "task_count": len(tasks),
        "tested": sum(int(row["tested"]) for row in results),
        "valid_sidon": sum(int(row["valid_sidon"]) for row in results),
        "triangle_changed": sum(int(row["triangle_changed"]) for row in results),
        "failures": sum(int(row["failures"]) for row in results),
        "best": best,
        "tasks": sorted(results, key=lambda row: (str(row["name"]), int(row["q"]), int(row["start"]))),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(args.output)
    print(json.dumps({key: payload[key] for key in ("tested", "valid_sidon", "triangle_changed", "failures")}, indent=2))
    print(json.dumps(best[:1], indent=2))


if __name__ == "__main__":
    main()
