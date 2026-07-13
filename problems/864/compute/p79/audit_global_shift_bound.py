#!/usr/bin/env python3
"""Exact all-shifts audit of |(B+B) intersect (B+B+h)| <= 2|B|-1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterator, Sequence

from audit_outer_codegrees import load_p20_rulers


ROOT = Path(__file__).resolve().parents[4]
P53_WIDTH45 = ROOT / "problems/864/compute/p53/exhaustive_width45_all_translations.json"
P53_DENSE = ROOT / "problems/864/compute/p53/dense_optimal_rulers_scan.json"
P53_SUBSETS = ROOT / "problems/864/compute/p53/counterexample_subset_minimization.json"
P75 = ROOT / "problems/864/fanout/wave5/P75_hard_positive_defect_folds.md"
P20_SAMPLES = ROOT / "problems/864/compute/p20/results/samples.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sidon_rulers(width: int) -> Iterator[tuple[int, ...]]:
    """Generate every integer Sidon subset containing 0 and width."""

    chosen = [0]
    used_differences: set[int] = set()

    def additions(value: int) -> tuple[int, ...] | None:
        new = tuple(value - old for old in chosen)
        if len(new) != len(set(new)) or any(value in used_differences for value in new):
            return None
        return new

    def recurse(next_value: int) -> Iterator[tuple[int, ...]]:
        endpoint = additions(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(next_value, width):
            new = additions(value)
            if new is None:
                continue
            chosen.append(value)
            used_differences.update(new)
            yield from recurse(value + 1)
            used_differences.difference_update(new)
            chosen.pop()

    yield from recurse(1)


def sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    sums: dict[int, tuple[int, int]] = {}
    for index, left in enumerate(values):
        for right in values[index:]:
            total = left + right
            if total in sums:
                raise AssertionError(("not Sidon including diagonals", sums[total], (left, right)))
            sums[total] = (left, right)
    expected = len(values) * (len(values) + 1) // 2
    if len(sums) != expected:
        raise AssertionError((len(sums), expected))
    return sums


def audit_witness(values: Sequence[int], h: int) -> dict[str, object]:
    sums = sum_map(values)
    intersections = []
    for low in sorted(sums):
        high = low + h
        if high in sums:
            intersections.append({
                "low_sum": low,
                "low_pair": list(sums[low]),
                "high_sum": high,
                "high_pair": list(sums[high]),
            })
    p = len(values)
    return {
        "B": list(values),
        "p": p,
        "width": values[-1] - values[0],
        "h": h,
        "unordered_sum_count": len(sums),
        "expected_unordered_sum_count": p * (p + 1) // 2,
        "C_S": len(intersections),
        "two_p_minus_one": 2 * p - 1,
        "excess": len(intersections) - (2 * p - 1),
        "intersections": intersections,
    }


def scan(max_width: int) -> dict[str, object]:
    rulers = shifts = failures = endpoint_shifts = endpoint_failures = 0
    smallest: tuple[object, ...] | None = None
    largest: tuple[object, ...] | None = None
    smallest_endpoint: tuple[object, ...] | None = None
    by_width = []
    for width in range(1, max_width + 1):
        width_rulers = width_shifts = width_failures = 0
        for values in sidon_rulers(width):
            rulers += 1
            width_rulers += 1
            p = len(values)
            sums = sum_map(values)
            for h in range(1, 2 * width + 1):
                shifts += 1
                width_shifts += 1
                c_s = sum(low + h in sums for low in sums)
                excess = c_s - (2 * p - 1)
                row = (p, width, h, values, c_s, excess)
                if largest is None or (excess, c_s, -p, -width, -h) > (
                    largest[5], largest[4], -largest[0], -largest[1], -largest[2]
                ):
                    largest = row
                if excess > 0:
                    failures += 1
                    width_failures += 1
                    if smallest is None or row < smallest:
                        smallest = row
                if h > width:
                    endpoint_shifts += 1
                    if excess > 0:
                        endpoint_failures += 1
                        if smallest_endpoint is None or row < smallest_endpoint:
                            smallest_endpoint = row
        by_width.append({
            "width": width,
            "rulers": width_rulers,
            "shifts": width_shifts,
            "failures": width_failures,
        })
    if smallest is None or largest is None:
        raise AssertionError("expected the all-shifts candidate to fail")
    return {
        "max_width": max_width,
        "normalized_rulers": rulers,
        "all_positive_relevant_shifts": shifts,
        "failure_count": failures,
        "smallest_failure": audit_witness(smallest[3], int(smallest[2])),
        "largest_excess": audit_witness(largest[3], int(largest[2])),
        "endpoint_regime": {
            "definition": "h>diam(B); shifts above 2*diam(B) have C_S=0",
            "tested_shifts": endpoint_shifts,
            "failure_count": endpoint_failures,
            "smallest_failure": None if smallest_endpoint is None else audit_witness(
                smallest_endpoint[3], int(smallest_endpoint[2])
            ),
        },
        "by_width": by_width,
    }


def scan_p20_endpoint_shifts() -> dict[str, object]:
    rulers = load_p20_rulers()
    if len(rulers) != 133:
        raise AssertionError(("P20 ruler count", len(rulers)))
    shifts = failures = 0
    smallest: tuple[object, ...] | None = None
    largest: tuple[object, ...] | None = None
    for item in rulers:
        normalized = tuple(int(value) for value in item["Z"])
        width = normalized[-1]
        p = len(normalized)
        sums = sum_map(normalized)
        sum_bits = sum(1 << total for total in sums)
        source_id = min(str(value) for value in item["source_ids"])
        for translation in range(width):
            h = width + translation + 1
            c_s = (sum_bits & (sum_bits >> h)).bit_count()
            values = tuple(translation + value for value in normalized)
            excess = c_s - (2 * p - 1)
            row = (p, h, values, source_id, c_s, excess)
            shifts += 1
            if largest is None or (excess, c_s, -p, -h) > (
                largest[5], largest[4], -largest[0], -largest[1]
            ):
                largest = row
            if excess > 0:
                failures += 1
                if smallest is None or row < smallest:
                    smallest = row
    if shifts != 590650 or smallest is None or largest is None:
        raise AssertionError(("P20 endpoint scan", shifts, smallest))
    smallest_record = audit_witness(smallest[2], int(smallest[1]))
    smallest_record["source_id"] = smallest[3]
    largest_record = audit_witness(largest[2], int(largest[1]))
    largest_record["source_id"] = largest[3]
    return {
        "domain": "all endpoint shifts diam(B)<h<=2*diam(B) of 133 P20 rulers",
        "source_rulers": len(rulers),
        "tested_shifts": shifts,
        "failure_count": failures,
        "smallest_failure": smallest_record,
        "largest_excess": largest_record,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-width", type=int, default=20)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parent / "global_shift_bound_audit.json",
    )
    args = parser.parse_args()
    if args.max_width < 1:
        raise SystemExit("--max-width must be positive")

    exact_scan = scan(args.max_width)
    p20_endpoint = scan_p20_endpoint_shifts()
    p53_width45 = json.loads(P53_WIDTH45.read_text(encoding="ascii"))
    if p53_width45["smallest_failure"] is not None:
        raise AssertionError("P53 width-45 C_S<=2p-3 gate changed")
    if int(p53_width45["normalized_rulers"]) != 745733:
        raise AssertionError("P53 ruler count changed")
    if int(p53_width45["translations"]) != 30326669:
        raise AssertionError("P53 translation count changed")

    dense = json.loads(P53_DENSE.read_text(encoding="ascii"))
    dense_max_excess = max(
        int(row["best_C_S"]) - (2 * int(row["p"]) - 1)
        for row in dense["reports"]
    )
    subsets = json.loads(P53_SUBSETS.read_text(encoding="ascii"))
    subset_max_excess = max(
        int(row["maximum_C_S"]) - (2 * int(row["subset_size"]) - 1)
        for row in subsets["per_size"]
        if row.get("status") == "OPTIMAL"
    )

    payload = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "candidate": "|(B+B) intersect (B+B+h)| <= 2|B|-1",
        "verdict": "false for arbitrary h and false in the endpoint regime h>diam(B)",
        "all_shifts_exhaustive": exact_scan,
        "p20_endpoint_shift_scan": p20_endpoint,
        "endpoint_regime_existing_exact_gates": {
            "P53_width45": {
                "domain": p53_width45["domain"],
                "normalized_rulers": p53_width45["normalized_rulers"],
                "translations": p53_width45["translations"],
                "stronger_bound_tested": "C_S<=2p-3",
                "failures": 0,
            },
            "P53_dense_orders_20_through_28": {
                "rows": len(dense["reports"]),
                "maximum_C_S_minus_(2p-1)": dense_max_excess,
            },
            "P53_exact_induced_subsets": {
                "optimal_sizes": sum(
                    row.get("status") == "OPTIMAL" for row in subsets["per_size"]
                ),
                "maximum_C_S_minus_(2p-1)": subset_max_excess,
            },
            "P53_p25_equality": {"p": 25, "C_S": 49, "two_p_minus_one": 49},
            "P75_p26_equality": {"p": 26, "C_S": 51, "two_p_minus_one": 51},
        },
        "input_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (P53_WIDTH45, P53_DENSE, P53_SUBSETS, P75, P20_SAMPLES)
        },
        "cp_sat_needed_after_exact_falsifier": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "all_shifts": {
            "rulers": exact_scan["normalized_rulers"],
            "shifts": exact_scan["all_positive_relevant_shifts"],
            "failures": exact_scan["failure_count"],
            "smallest_failure": exact_scan["smallest_failure"],
        },
        "endpoint_regime": exact_scan["endpoint_regime"],
        "P53_width45_endpoint_failures": 0,
        "P20_endpoint_failures": p20_endpoint["failure_count"],
        "P20_smallest_endpoint_failure": p20_endpoint["smallest_failure"],
    }, indent=2))


if __name__ == "__main__":
    main()
