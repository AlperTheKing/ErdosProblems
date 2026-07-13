#!/usr/bin/env python3
"""Exact rational-gate census for nontrivial reflected cores in Problem 864."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from audit_core_stability import better_density, better_residual_fraction, record_for


ETA_GATES = (
    (0, 1),
    (1, 12),
    (1, 6),
    (1, 4),
    (1, 3),
    (1, 2),
)


def above_gate(record: dict[str, Any], eta_numerator: int, eta_denominator: int) -> bool:
    # k^2/N > 4/3 + a/b iff 3b k^2 > (4b+3a)N.
    return (
        3 * eta_denominator * record["k"] * record["k"]
        > (4 * eta_denominator + 3 * eta_numerator) * record["N"]
    )


def search_n(n: int) -> dict[str, Any]:
    a = [0]
    sum_counts: dict[int, int] = {0: 1}
    repeated_exception_count = 0
    gate_rows: dict[tuple[int, int], dict[str, Any]] = {
        gate: {
            "eta": f"{gate[0]}/{gate[1]}",
            "count": 0,
            "with_residual_count": 0,
            "completion_failure_count": 0,
            "same_span_completion_failure_count": 0,
            "span_transfer_failure_count": 0,
            "largest_residual_fraction": None,
            "strongest_density_with_residual": None,
        }
        for gate in ETA_GATES
    }

    def evaluate_leaf() -> None:
        nonlocal repeated_exception_count
        record = record_for(tuple(a), n)
        if record["exceptional_multiplicity"] < 2:
            return
        repeated_exception_count += 1
        for gate, row in gate_rows.items():
            if not above_gate(record, *gate):
                continue
            row["count"] += 1
            if record["u"] == 0:
                continue
            row["with_residual_count"] += 1
            if record["completion_admissible"] is False:
                row["completion_failure_count"] += 1
                completion = record["reflected_completion"]
                if completion is None:
                    raise AssertionError("repeated fibre has no completion")
                if min(completion) >= 0 and max(completion) < n:
                    row["same_span_completion_failure_count"] += 1
            if not record["span_transfer_holds"]:
                row["span_transfer_failure_count"] += 1
            if better_residual_fraction(record, row["largest_residual_fraction"]):
                row["largest_residual_fraction"] = record
            if better_density(record, row["strongest_density_with_residual"]):
                row["strongest_density_with_residual"] = record

    def try_add(x: int, repeated_labels: int, continuation: Callable[[int], None]) -> None:
        changed: list[tuple[int, int]] = []
        new_repeated = repeated_labels
        valid = True
        for old_point in (*a, x):
            pair_sum = x + old_point
            old_count = sum_counts.get(pair_sum, 0)
            sum_counts[pair_sum] = old_count + 1
            changed.append((pair_sum, old_count))
            if old_count == 1:
                new_repeated += 1
            if new_repeated > 1:
                valid = False
                break
        if valid:
            a.append(x)
            continuation(new_repeated)
            a.pop()
        for pair_sum, old_count in reversed(changed):
            if old_count:
                sum_counts[pair_sum] = old_count
            else:
                del sum_counts[pair_sum]

    def recurse(x: int, repeated_labels: int) -> None:
        if x == n - 1:
            try_add(x, repeated_labels, lambda _: evaluate_leaf())
            return
        recurse(x + 1, repeated_labels)
        try_add(x, repeated_labels, lambda value: recurse(x + 1, value))

    recurse(1, 0)
    return {
        "N": n,
        "total_endpoint_normalized_subsets": 1 << (n - 2),
        "repeated_exception_count": repeated_exception_count,
        "gates": [gate_rows[gate] for gate in ETA_GATES],
    }


def merge_gate(rows: list[dict[str, Any]], gate_index: int) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "eta": rows[0]["gates"][gate_index]["eta"],
        "count": 0,
        "with_residual_count": 0,
        "completion_failure_count": 0,
        "same_span_completion_failure_count": 0,
        "span_transfer_failure_count": 0,
        "largest_residual_fraction": None,
        "strongest_density_with_residual": None,
    }
    for n_row in rows:
        row = n_row["gates"][gate_index]
        for key in (
            "count",
            "with_residual_count",
            "completion_failure_count",
            "same_span_completion_failure_count",
            "span_transfer_failure_count",
        ):
            merged[key] += row[key]
        residual_record = row["largest_residual_fraction"]
        if residual_record is not None and better_residual_fraction(
            residual_record, merged["largest_residual_fraction"]
        ):
            merged["largest_residual_fraction"] = residual_record
        density_record = row["strongest_density_with_residual"]
        if density_record is not None and better_density(
            density_record, merged["strongest_density_with_residual"]
        ):
            merged["strongest_density_with_residual"] = density_record
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p38/repeated_gate_N22.json"),
    )
    args = parser.parse_args()

    rows = [search_n(n) for n in range(args.min_n, args.max_n + 1)]
    summary = {
        "arithmetic": "integer/rational only",
        "domain": (
            f"all A subset [0,N-1] with endpoints included, "
            f"{args.min_n} <= N <= {args.max_n}, exceptional multiplicity >= 2"
        ),
        "total_subset_count": sum(
            row["total_endpoint_normalized_subsets"] for row in rows
        ),
        "repeated_exception_count": sum(
            row["repeated_exception_count"] for row in rows
        ),
        "gates": [merge_gate(rows, index) for index in range(len(ETA_GATES))],
        "by_N": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "by_N"}))


if __name__ == "__main__":
    main()
