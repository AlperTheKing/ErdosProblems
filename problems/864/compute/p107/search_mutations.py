#!/usr/bin/env python3
"""Exact RM97/P101 mutation search around the P105 and P94/P98 seeds."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import json
from pathlib import Path
from typing import Iterable, Sequence

from core import audit, unordered_sum_map


ROOT = Path(__file__).resolve().parents[4]
P105_JSON = ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json"
P94_JSON = ROOT / "problems/864/compute/p94/c84_archived_audit.json"


def load_seeds() -> dict[str, tuple[tuple[int, ...], int, int]]:
    p105 = json.loads(P105_JSON.read_text(encoding="ascii"))
    source = p105["subset_search"]["source_subset"]
    p94 = json.loads(P94_JSON.read_text(encoding="ascii"))["translation"]["max_ratio_row"]
    p94_values = tuple(int(value) for value in p94["B"])
    p98_values = tuple(value for value in p94_values if value != 4740)
    return {
        "P105_source": (
            tuple(int(value) for value in source["B"]),
            int(source["h"]),
            1,
        ),
        "P94": (p94_values, int(p94["h"]), int(p94["b"])),
        "P98_delete_4740": (p98_values, int(p94["h"]), int(p94["b"])),
    }


def fresh_summary() -> dict[str, object]:
    return {
        "attempted": 0,
        "sidon": 0,
        "positive_defect": 0,
        "literal_hole": 0,
        "full_gate": 0,
        "P101_failures": 0,
        "RM97_failures": 0,
        "max_P101_excess": None,
        "max_P101_row": None,
        "max_RM97_unmatched": None,
        "max_RM97_row": None,
    }


def compact(row: dict[str, object]) -> dict[str, object]:
    return {
        field: row[field]
        for field in (
            "B", "sha256", "p", "h", "b", "delta", "literal_hole",
            "C_S", "T_F", "V_b", "P101_excess", "RM97_demands",
            "RM97_slots", "RM97_matched", "RM97_unmatched",
        )
    }


def record(summary: dict[str, object], row: dict[str, object]) -> None:
    summary["full_gate"] = int(summary["full_gate"]) + 1
    p101 = int(row["P101_excess"])
    rm97 = int(row["RM97_unmatched"])
    if p101 > 0:
        summary["P101_failures"] = int(summary["P101_failures"]) + 1
    if rm97 > 0:
        summary["RM97_failures"] = int(summary["RM97_failures"]) + 1
    if summary["max_P101_excess"] is None or p101 > int(summary["max_P101_excess"]):
        summary["max_P101_excess"] = p101
        summary["max_P101_row"] = compact(row)
    if summary["max_RM97_unmatched"] is None or rm97 > int(summary["max_RM97_unmatched"]):
        summary["max_RM97_unmatched"] = rm97
        summary["max_RM97_row"] = compact(row)


def evaluate(
    summary: dict[str, object], values: Sequence[int], h: int, b: int,
    sidon_known: bool = False,
) -> None:
    summary["attempted"] = int(summary["attempted"]) + 1
    try:
        row = audit(values, h, b)
    except AssertionError as error:
        if sidon_known:
            raise
        if error.args and isinstance(error.args[0], tuple) and error.args[0][0] in {
            "repeated sum", "repeated difference",
        }:
            return
        raise
    summary["sidon"] = int(summary["sidon"]) + 1
    if int(row["delta"]) <= 0:
        return
    summary["positive_defect"] = int(summary["positive_defect"]) + 1
    if not bool(row["literal_hole"]):
        return
    summary["literal_hole"] = int(summary["literal_hole"]) + 1
    record(summary, row)


def merge(items: Iterable[dict[str, object]]) -> dict[str, object]:
    out = fresh_summary()
    for item in items:
        for field in (
            "attempted", "sidon", "positive_defect", "literal_hole",
            "full_gate", "P101_failures", "RM97_failures",
        ):
            out[field] = int(out[field]) + int(item[field])
        for value_field, row_field in (
            ("max_P101_excess", "max_P101_row"),
            ("max_RM97_unmatched", "max_RM97_row"),
        ):
            value = item[value_field]
            if value is not None and (
                out[value_field] is None or int(value) > int(out[value_field])
            ):
                out[value_field] = value
                out[row_field] = item[row_field]
    return out


def insertion_is_sidon(values: Sequence[int], sums: set[int], value: int) -> bool:
    new_sums = [value + old for old in values]
    new_sums.append(2 * value)
    return len(new_sums) == len(set(new_sums)) and sums.isdisjoint(new_sums)


def translation_lane(values: tuple[int, ...], h: int) -> dict[str, object]:
    summary = fresh_summary()
    p = len(values)
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = baseline - h - 1
    for gamma in range(max_gamma + 1):
        translated = tuple(value + gamma for value in values)
        translated_h = h + gamma
        for b in (1, 2):
            evaluate(summary, translated, translated_h, b, sidon_known=True)
    summary["gamma_range"] = [0, max_gamma]
    return summary


def deletion_lane(
    values: tuple[int, ...], h: int, b_values: Sequence[int], maximum: int,
) -> dict[str, object]:
    summary = fresh_summary()
    for count in range(1, maximum + 1):
        for deleted in combinations(range(len(values) - 1), count):
            deleted_set = set(deleted)
            candidate = tuple(
                value for index, value in enumerate(values) if index not in deleted_set
            )
            for b in b_values:
                evaluate(summary, candidate, h, b, sidon_known=True)
    summary["maximum_deleted"] = maximum
    return summary


def direct_insertion_lane(
    values: tuple[int, ...], h: int, b_values: Sequence[int],
) -> dict[str, object]:
    summary = fresh_summary()
    occupied = set(values)
    sums = set(unordered_sum_map(values))
    for value in range(h - 1):
        for b in b_values:
            summary["attempted"] = int(summary["attempted"]) + 1
        if value in occupied or not insertion_is_sidon(values, sums, value):
            continue
        candidate = tuple(sorted(values + (value,)))
        for b in b_values:
            # The attempted count was already included above.
            summary["attempted"] = int(summary["attempted"]) - 1
            evaluate(summary, candidate, h, b, sidon_known=True)
    return summary


def replacement_job(
    job: tuple[tuple[int, ...], int, tuple[int, ...], int]
) -> dict[str, object]:
    values, h, b_values, deleted = job
    summary = fresh_summary()
    remainder = values[:deleted] + values[deleted + 1:]
    occupied = set(remainder)
    sums = set(unordered_sum_map(remainder))
    for value in range(h - 1):
        for _b in b_values:
            summary["attempted"] = int(summary["attempted"]) + 1
        if value in occupied or value == values[deleted]:
            continue
        if not insertion_is_sidon(remainder, sums, value):
            continue
        candidate = tuple(sorted(remainder + (value,)))
        for b in b_values:
            summary["attempted"] = int(summary["attempted"]) - 1
            evaluate(summary, candidate, h, b, sidon_known=True)
    return summary


def replacement_lane(
    values: tuple[int, ...], h: int, b_values: Sequence[int], workers: int,
) -> dict[str, object]:
    jobs = [
        (values, h, tuple(b_values), deleted)
        for deleted in range(len(values) - 1)
    ]
    if workers == 1:
        return merge(replacement_job(job) for job in jobs)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return merge(pool.map(replacement_job, jobs, chunksize=1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    seeds = load_seeds()
    p105, p105_h, _ = seeds["P105_source"]
    p94, p94_h, p94_b = seeds["P94"]
    p98, p98_h, p98_b = seeds["P98_delete_4740"]
    payload = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; at most 16 process workers",
        "workers": args.workers,
        "seeds": {
            name: compact(audit(values, h, b))
            for name, (values, h, b) in seeds.items()
        },
        "P105_source_positive_defect_translations": translation_lane(p105, p105_h),
        "P105_source_one_two_deletions": deletion_lane(p105, p105_h, (1, 2), 2),
        "P105_source_direct_insertions": direct_insertion_lane(p105, p105_h, (1, 2)),
        "P105_source_one_delete_one_insert": replacement_lane(
            p105, p105_h, (1, 2), args.workers
        ),
        "P94_one_two_deletions": deletion_lane(p94, p94_h, (p94_b,), 2),
        "P94_direct_insertions": direct_insertion_lane(p94, p94_h, (p94_b,)),
        "P94_one_delete_one_insert": replacement_lane(
            p94, p94_h, (p94_b,), args.workers
        ),
        "P98_direct_insertions": direct_insertion_lane(p98, p98_h, (p98_b,)),
        "P98_one_delete_one_insert": replacement_lane(
            p98, p98_h, (p98_b,), args.workers
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        key: {
            field: value[field]
            for field in (
                "attempted", "sidon", "positive_defect", "literal_hole",
                "full_gate", "P101_failures", "RM97_failures",
                "max_P101_excess", "max_RM97_unmatched",
            )
        }
        for key, value in payload.items()
        if isinstance(value, dict) and "attempted" in value
    }, indent=2))


if __name__ == "__main__":
    main()

