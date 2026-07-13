#!/usr/bin/env python3
"""Exact full-gate mutation search around P94's 116-on-116 tight row."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

from component_core import audit, canonical_folds, component_data, unordered_sum_map


ROOT = Path(__file__).resolve().parents[4]
P94 = ROOT / "problems/864/compute/p94/c84_archived_audit.json"


def insertion_is_sidon(values: Sequence[int], sums: set[int], value: int) -> bool:
    new_sums = [value + old for old in values]
    new_sums.append(2 * value)
    return len(new_sums) == len(set(new_sums)) and sums.isdisjoint(new_sums)


def fresh_summary() -> dict[str, object]:
    return {
        "attempted": 0,
        "sidon": 0,
        "full_gate": 0,
        "with_triangles": 0,
        "tight_rows": 0,
        "failures": 0,
        "global_failures": 0,
        "maximum_global_excess": None,
        "maximum_global_excess_row": None,
        "best": None,
        "largest_tight": None,
        "first_failure": None,
    }


def row_key(row: dict[str, object]) -> tuple[int, int, int, int, int]:
    return (
        int(row["maximum_component_excess"]),
        int(row["maximum_component_triangles"]),
        -int(row["maximum_component_folds"]),
        int(row["T_F"]),
        -int(row["C_S"]),
    )


def record(summary: dict[str, object], row: dict[str, object]) -> None:
    summary["full_gate"] = int(summary["full_gate"]) + 1
    if int(row["T_F"]) > 0:
        summary["with_triangles"] = int(summary["with_triangles"]) + 1
    excess = int(row["maximum_component_excess"])
    if excess > 0:
        summary["failures"] = int(summary["failures"]) + 1
        if summary["first_failure"] is None:
            summary["first_failure"] = row
    global_excess = int(row["T_F"]) - int(row["C_S"])
    if global_excess > 0:
        summary["global_failures"] = int(summary["global_failures"]) + 1
    old_global = summary["maximum_global_excess"]
    if old_global is None or global_excess > int(old_global):
        summary["maximum_global_excess"] = global_excess
        summary["maximum_global_excess_row"] = row
    if excess == 0 and int(row["maximum_component_triangles"]) > 0:
        summary["tight_rows"] = int(summary["tight_rows"]) + 1
        old = summary["largest_tight"]
        if old is None or (
            int(row["maximum_component_triangles"]), int(row["T_F"])
        ) > (
            int(old["maximum_component_triangles"]), int(old["T_F"])
        ):
            summary["largest_tight"] = row
    old = summary["best"]
    if old is None or row_key(row) > row_key(old):
        summary["best"] = row


def merge(summaries: Iterable[dict[str, object]]) -> dict[str, object]:
    out = fresh_summary()
    for summary in summaries:
        for key in ("attempted", "sidon", "full_gate", "with_triangles", "tight_rows", "failures", "global_failures"):
            out[key] = int(out[key]) + int(summary[key])
        if (
            summary["maximum_global_excess"] is not None
            and (
                out["maximum_global_excess"] is None
                or int(summary["maximum_global_excess"]) > int(out["maximum_global_excess"])
            )
        ):
            out["maximum_global_excess"] = summary["maximum_global_excess"]
            out["maximum_global_excess_row"] = summary["maximum_global_excess_row"]
        for key in ("best", "largest_tight"):
            row = summary[key]
            if row is None:
                continue
            old = out[key]
            if key == "best":
                better = old is None or row_key(row) > row_key(old)
            else:
                better = old is None or (
                    int(row["maximum_component_triangles"]), int(row["T_F"])
                ) > (
                    int(old["maximum_component_triangles"]), int(old["T_F"])
                )
            if better:
                out[key] = row
        if out["first_failure"] is None and summary["first_failure"] is not None:
            out["first_failure"] = summary["first_failure"]
    return out


def load_seed() -> tuple[tuple[int, ...], int, int]:
    payload = json.loads(P94.read_text(encoding="ascii"))
    row = payload["translation"]["max_ratio_row"]
    return tuple(int(value) for value in row["B"]), int(row["h"]), int(row["b"])


def seed_certificate(B: Sequence[int], h: int, b: int) -> tuple[dict[str, object], set[int], list[int]]:
    row = audit(B, h, b)
    folds = canonical_folds(B, h)
    triangles, components = component_data(folds, B)
    tight = [component for component in components if component.triangles == component.folds and component.triangles]
    if len(tight) != 1 or (tight[0].folds, tight[0].triangles) != (116, 116):
        raise AssertionError(tight)
    core_marks = {mark for fold_id in tight[0].fold_ids for mark in folds[fold_id]}
    outside = sorted(set(B) - core_marks)
    if len(core_marks) != 84 or len(outside) != 20:
        raise AssertionError((len(core_marks), outside))
    return row, core_marks, outside


def deletion_lane(B: tuple[int, ...], h: int, b: int, maximum: int) -> dict[str, object]:
    summary = fresh_summary()
    endpoint_index = len(B) - 1
    for count in range(1, maximum + 1):
        for deleted in combinations(range(endpoint_index), count):
            summary["attempted"] = int(summary["attempted"]) + 1
            deleted_set = set(deleted)
            candidate = tuple(value for index, value in enumerate(B) if index not in deleted_set)
            summary["sidon"] = int(summary["sidon"]) + 1
            try:
                row = audit(candidate, h, b)
            except AssertionError as error:
                if error.args and isinstance(error.args[0], tuple) and error.args[0][0] == "positive defect":
                    continue
                raise
            record(summary, row)
    return summary


def outside_deletion_lane(
    B: tuple[int, ...], h: int, b: int, outside: Sequence[int], maximum: int
) -> dict[str, object]:
    summary = fresh_summary()
    for count in range(maximum + 1):
        for deleted in combinations(outside, count):
            summary["attempted"] = int(summary["attempted"]) + 1
            deleted_set = set(deleted)
            candidate = tuple(value for value in B if value not in deleted_set)
            summary["sidon"] = int(summary["sidon"]) + 1
            try:
                row = audit(candidate, h, b)
            except AssertionError as error:
                if error.args and isinstance(error.args[0], tuple) and error.args[0][0] == "positive defect":
                    continue
                raise
            record(summary, row)
    return summary


def insertion_lane(B: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    summary = fresh_summary()
    occupied = set(B)
    sums = set(unordered_sum_map(B))
    for value in range(h - 1):
        if value in occupied:
            continue
        summary["attempted"] = int(summary["attempted"]) + 1
        if not insertion_is_sidon(B, sums, value):
            continue
        summary["sidon"] = int(summary["sidon"]) + 1
        candidate = tuple(sorted(B + (value,)))
        try:
            row = audit(candidate, h, b)
        except AssertionError as error:
            if error.args and error.args[0] == "literal hole":
                continue
            raise
        record(summary, row)
    return summary


def replacement_job(job: tuple[tuple[int, ...], int, int, int]) -> dict[str, object]:
    B, h, b, deleted = job
    summary = fresh_summary()
    remainder = B[:deleted] + B[deleted + 1:]
    occupied = set(remainder)
    sums = set(unordered_sum_map(remainder))
    for value in range(h - 1):
        if value in occupied or value == B[deleted]:
            continue
        summary["attempted"] = int(summary["attempted"]) + 1
        if not insertion_is_sidon(remainder, sums, value):
            continue
        summary["sidon"] = int(summary["sidon"]) + 1
        candidate = tuple(sorted(remainder + (value,)))
        try:
            row = audit(candidate, h, b)
        except AssertionError as error:
            if error.args and error.args[0] == "literal hole":
                continue
            raise
        record(summary, row)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workers = max(1, min(16, args.workers))
    B, h, b = load_seed()
    seed, core_marks, outside = seed_certificate(B, h, b)
    jobs = [(B, h, b, deleted) for deleted in range(len(B) - 1)]
    if workers == 1:
        replacement_rows = [replacement_job(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            replacement_rows = list(pool.map(replacement_job, jobs, chunksize=1))
    payload = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; every retained row passes all four gates",
        "workers": workers,
        "seed": seed,
        "seed_tight_component": {
            "folds": 116,
            "triangles": 116,
            "support_marks": len(core_marks),
            "outside_marks": outside,
        },
        "all_one_and_two_deletions": deletion_lane(B, h, b, 2),
        "all_outside_core_deletions_through_five": outside_deletion_lane(B, h, b, outside, 5),
        "all_direct_interior_insertions": insertion_lane(B, h, b),
        "all_one_delete_one_insert_replacements": merge(replacement_rows),
    }
    payload["total_failures"] = sum(
        int(payload[key]["failures"])
        for key in (
            "all_one_and_two_deletions",
            "all_outside_core_deletions_through_five",
            "all_direct_interior_insertions",
            "all_one_delete_one_insert_replacements",
        )
    )
    payload["total_global_failures"] = sum(
        int(payload[key]["global_failures"])
        for key in (
            "all_one_and_two_deletions",
            "all_outside_core_deletions_through_five",
            "all_direct_interior_insertions",
            "all_one_delete_one_insert_replacements",
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
