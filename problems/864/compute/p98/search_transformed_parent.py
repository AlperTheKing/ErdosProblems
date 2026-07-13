#!/usr/bin/env python3
"""Exact transformed-subset and local-neighborhood falsifier for C84 components."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from component_core import audit, canonical_folds, component_data, correction_V, normalized, score
from cpsat_unrestricted_scan import recovery_data


ROOT = Path(__file__).resolve().parents[4]
SOURCE = (0, 6, 22, 24, 56, 95, 137, 146, 172, 173, 201, 258, 273, 306, 311, 365, 369)


def masks(values: Sequence[int]) -> tuple[int, int]:
    sum_mask = 0
    difference_mask = 0
    for i, left in enumerate(values):
        for right in values[i:]:
            sum_mask |= 1 << (left + right)
        for right in values[i + 1:]:
            difference_mask |= 1 << (right - left)
    return sum_mask, difference_mask


def is_sidon(values: Sequence[int]) -> bool:
    seen = set()
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in seen:
                return False
            seen.add(total)
    return True


def component_key(row: dict[str, object]) -> tuple[int, int, int, int, int]:
    return (
        int(row["maximum_component_excess"]),
        int(row["maximum_component_triangles"]),
        -int(row["maximum_component_folds"]),
        int(row["T_F"]),
        -int(row["C_S"]),
    )


def scan_base(values: Sequence[int], counters: dict[str, int], records: dict[str, object]) -> None:
    p = len(values)
    if p < 3:
        return
    width = values[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    if max_gamma < 0:
        return
    sum_mask, difference_mask = masks(values)
    counters["normalized_bases"] += 1
    for gamma in range(max_gamma + 1):
        h = width + gamma + 1
        if (sum_mask & (sum_mask >> h)).bit_count() == 0:
            continue
        counters["folded_translations"] += 1
        for b in (1, 2):
            counters["full_gate_candidates"] += 1
            if ((sum_mask << (2 * gamma + b)) & difference_mask) != 0:
                continue
            counters["literal_holes"] += 1
            B = tuple(value + gamma for value in values)
            row = audit(B, h, b)
            if int(row["T_F"]) > 0:
                counters["nonzero_triangle_rows"] += 1
            excess = int(row["maximum_component_excess"])
            if excess > 0:
                counters["failures"] += 1
                records.setdefault("failure", row)
            if (
                int(row["maximum_component_triangles"]) > 0
                and excess == 0
            ):
                counters["tight_rows"] += 1
                old = records.get("largest_tight")
                if old is None or (
                    int(row["maximum_component_triangles"]), int(row["T_F"])
                ) > (
                    int(old["maximum_component_triangles"]), int(old["T_F"])
                ):
                    records["largest_tight"] = row
            old = records.get("best")
            if old is None or component_key(row) > component_key(old):
                records["best"] = row


def scan_pure(values: Sequence[int], counters: dict[str, int], records: dict[str, object]) -> None:
    row = score(values, values[-1] + 1)
    counters["systems"] += 1
    if int(row["C_S"]) > 0:
        counters["with_folds"] += 1
    if int(row["T_F"]) > 0:
        counters["with_triangles"] += 1
    excess = int(row["maximum_component_excess"])
    if excess == 0 and int(row["maximum_component_triangles"]) > 0:
        counters["tight_component_rows"] += 1
        old = records.get("largest_tight")
        if old is None or (
            int(row["maximum_component_triangles"]), int(row["T_F"])
        ) > (
            int(old["maximum_component_triangles"]), int(old["T_F"])
        ):
            records["largest_tight"] = row
    if excess > 0:
        counters["component_failures"] += 1
        recovery = recovery_data(tuple(values), row)
        if int(recovery["full_recovery_count"]) > 0:
            counters["recoverable_component_failures"] += 1
        retained = {**row, "recovery": recovery}
        old = records.get("smallest_component_failure")
        if old is None or (int(row["p"]), int(row["h"]), row["B"]) < (
            int(old["p"]), int(old["h"]), old["B"]
        ):
            records["smallest_component_failure"] = retained
    if int(row["T_F"]) > int(row["C_S"]):
        counters["global_failures"] += 1
        retained = {**row, "recovery": recovery_data(tuple(values), row)}
        old = records.get("smallest_global_failure")
        if old is None or (int(row["p"]), int(row["h"]), row["B"]) < (
            int(old["p"]), int(old["h"]), old["B"]
        ):
            records["smallest_global_failure"] = retained
    for phase in (1, 2):
        counters["corrected_tests"] += 1
        correction = correction_V(values, values[-1] + 1, phase)
        margin = int(row["T_F"]) - int(row["C_S"]) - correction
        if margin > 0:
            counters["corrected_failures"] += 1
            retained = {**row, "b": phase, "V_b": correction, "corrected_excess": margin}
            old = records.get("smallest_corrected_failure")
            if old is None or (int(row["p"]), int(row["h"]), phase, row["B"]) < (
                int(old["p"]), int(old["h"]), int(old["b"]), old["B"]
            ):
                records["smallest_corrected_failure"] = retained
        old_margin = records.get("maximum_corrected_excess")
        if old_margin is None or margin > int(old_margin):
            records["maximum_corrected_excess"] = margin
            records["maximum_corrected_excess_row"] = {
                **row, "b": phase, "V_b": correction, "corrected_excess": margin,
            }


def subset_bases(parent: Sequence[int]) -> Iterable[tuple[int, ...]]:
    seen: set[tuple[int, ...]] = set()
    size = len(parent)
    for mask in range(1, 1 << size):
        if mask.bit_count() < 3:
            continue
        raw = tuple(parent[index] for index in range(size) if mask & (1 << index))
        for oriented in (normalized(raw), normalized(raw[-1] - value for value in raw)):
            if oriented not in seen:
                seen.add(oriented)
                yield oriented


def local_neighbors(parent: Sequence[int]) -> Iterable[tuple[int, ...]]:
    """All endpoint-preserving one-delete/one-insert Sidon neighbors."""
    width = parent[-1]
    seen: set[tuple[int, ...]] = set()
    for deleted in range(1, len(parent) - 1):
        remainder = parent[:deleted] + parent[deleted + 1:]
        occupied = set(remainder)
        for inserted in range(1, width):
            if inserted in occupied:
                continue
            candidate = tuple(sorted(remainder + (inserted,)))
            if candidate == tuple(parent) or candidate in seen or not is_sidon(candidate):
                continue
            seen.add(candidate)
            yield candidate


def new_counters() -> dict[str, int]:
    return {
        "normalized_bases": 0,
        "folded_translations": 0,
        "full_gate_candidates": 0,
        "literal_holes": 0,
        "nonzero_triangle_rows": 0,
        "tight_rows": 0,
        "failures": 0,
    }


def new_pure_counters() -> dict[str, int]:
    return {
        "systems": 0,
        "with_folds": 0,
        "with_triangles": 0,
        "tight_component_rows": 0,
        "component_failures": 0,
        "global_failures": 0,
        "recoverable_component_failures": 0,
        "corrected_tests": 0,
        "corrected_failures": 0,
    }


def raw_parent_certificate() -> dict[str, object]:
    h = SOURCE[-1] + 1
    folds = canonical_folds(SOURCE, h)
    triangles, components = component_data(folds, SOURCE)
    maximum = components[0]
    if (maximum.folds, maximum.triangles, maximum.excess) != (7, 8, 1):
        raise AssertionError(maximum)
    return {
        "B": list(SOURCE), "p": len(SOURCE), "h": h,
        "C_S": len(folds), "T_F": len(triangles),
        "maximum_component_folds": maximum.folds,
        "maximum_component_triangles": maximum.triangles,
        "maximum_component_excess": maximum.excess,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    subset_counts, subset_records = new_counters(), {}
    subset_pure_counts, subset_pure_records = new_pure_counters(), {}
    subset_base_count = 0
    for base in subset_bases(SOURCE):
        subset_base_count += 1
        scan_pure(base, subset_pure_counts, subset_pure_records)
        scan_base(base, subset_counts, subset_records)

    local_counts, local_records = new_counters(), {}
    local_pure_counts, local_pure_records = new_pure_counters(), {}
    local_base_count = 0
    local_sidon_count = 0
    local_seen: set[tuple[int, ...]] = set()
    for orientation in (SOURCE, tuple(SOURCE[-1] - value for value in reversed(SOURCE))):
        for base in local_neighbors(orientation):
            if base in local_seen:
                continue
            local_seen.add(base)
            local_sidon_count += 1
            local_base_count += 1
            scan_pure(base, local_pure_counts, local_pure_records)
            scan_base(base, local_counts, local_records)

    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "raw_parent": raw_parent_certificate(),
        "subset_translation_domain": {
            "definition": "all subsets of the 17-mark parent with at least 3 marks, both normalized orientations, all positive-defect folded translations, b=1,2",
            "distinct_oriented_subsets": subset_base_count,
            **subset_counts,
            **subset_records,
        },
        "subset_pure_domain": {
            "definition": "all distinct normalized orientations of all parent subsets with at least 3 marks; endpoint Sidon only",
            "distinct_oriented_subsets": subset_base_count,
            **subset_pure_counts,
            **subset_pure_records,
        },
        "local_transformation_domain": {
            "definition": "all endpoint-preserving one-delete/one-insert Sidon neighbors of both parent orientations, all positive-defect folded translations, b=1,2",
            "distinct_sidon_neighbors": local_sidon_count,
            **local_counts,
            **local_records,
        },
        "local_pure_domain": {
            "definition": "all endpoint-preserving one-delete/one-insert Sidon neighbors of both parent orientations; endpoint Sidon only",
            "distinct_sidon_neighbors": local_sidon_count,
            **local_pure_counts,
            **local_pure_records,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
