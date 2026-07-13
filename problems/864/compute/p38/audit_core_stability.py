#!/usr/bin/env python3
"""Exact finite audit for reflected-core stability in Problem 864.

The search is endpoint-normalized: A is a subset of [0, N-1] containing
both endpoints.  Thus N is the shortest ambient interval size for A.
Every gate and reported comparison uses integer arithmetic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


def fraction_record(numerator: int, denominator: int) -> dict[str, int | str]:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return {
        "numerator": numerator,
        "denominator": denominator,
        "display": f"{numerator}/{denominator}",
    }


def fraction_greater(
    left_numerator: int,
    left_denominator: int,
    right_numerator: int,
    right_denominator: int,
) -> bool:
    return left_numerator * right_denominator > right_numerator * left_denominator


def sum_profile(a: tuple[int, ...]) -> tuple[int | None, dict[int, int]]:
    counts: dict[int, int] = {}
    for right_index, right in enumerate(a):
        for left in a[: right_index + 1]:
            pair_sum = left + right
            counts[pair_sum] = counts.get(pair_sum, 0) + 1
    repeated = [pair_sum for pair_sum, count in counts.items() if count >= 2]
    if len(repeated) > 1:
        raise AssertionError("nonadmissible set reached record builder")
    return (repeated[0] if repeated else None), counts


def is_admissible(a: set[int]) -> bool:
    repeated_labels = 0
    counts: dict[int, int] = {}
    ordered = sorted(a)
    for right_index, right in enumerate(ordered):
        for left in ordered[: right_index + 1]:
            pair_sum = left + right
            old_count = counts.get(pair_sum, 0)
            counts[pair_sum] = old_count + 1
            if old_count == 1:
                repeated_labels += 1
                if repeated_labels > 1:
                    return False
    return True


def record_for(a: tuple[int, ...], n: int) -> dict[str, Any]:
    sigma, counts = sum_profile(a)
    point_set = set(a)
    k = len(a)
    span = n - 1

    if sigma is None:
        core: tuple[int, ...] = ()
        residual = a
        delta = 0
        p = 0
        exceptional_multiplicity = 0
    else:
        core = tuple(x for x in a if sigma - x in point_set)
        residual = tuple(x for x in a if sigma - x not in point_set)
        delta = int(sigma % 2 == 0 and sigma // 2 in point_set)
        if (len(core) - delta) % 2:
            raise AssertionError("core parity failed")
        p = (len(core) - delta) // 2
        exceptional_multiplicity = counts[sigma]
        if exceptional_multiplicity != p + delta:
            raise AssertionError("exceptional fibre/core identity failed")

    c = len(core)
    u = len(residual)
    if c + u != k:
        raise AssertionError("core/residual partition failed")

    if core:
        core_span = core[-1] - core[0]
        residual_inside_core_span = sum(core[0] < x < core[-1] for x in residual)
        residual_left_of_core = sum(x < core[0] for x in residual)
        residual_right_of_core = sum(x > core[-1] for x in residual)
    else:
        core_span = 0
        residual_inside_core_span = 0
        residual_left_of_core = 0
        residual_right_of_core = 0

    # P09 exact difference packing, cleared by 2.
    difference_packing_lhs2 = (
        2 * p * (p + delta) + 2 * c * u + u * (u - 1)
    )
    if difference_packing_lhs2 > 2 * span:
        raise AssertionError("P09 difference packing failed")

    # The transfer inequality needed to infer a sharp core result merely by
    # subtracting the residual's geometric span contribution:
    #   L-L_C >= 3/4 (k^2-c^2).
    # Positive margin means this candidate is false.
    span_transfer_margin4 = 3 * (k * k - c * c) - 4 * (span - core_span)

    # Sharp 2/sqrt(3) finite gate, with N rather than span: 3 k^2 > 4 N.
    sharp_excess = 3 * k * k - 4 * n

    completion: tuple[int, ...] | None = None
    completion_admissible: bool | None = None
    completion_added = 0
    if sigma is not None:
        completion_set = point_set | {sigma - x for x in residual}
        completion = tuple(sorted(completion_set))
        completion_added = len(completion_set) - k
        completion_admissible = is_admissible(completion_set)

    return {
        "A": list(a),
        "N": n,
        "span": span,
        "k": k,
        "sigma": sigma,
        "exceptional_multiplicity": exceptional_multiplicity,
        "p": p,
        "delta": delta,
        "core": list(core),
        "c": c,
        "residual": list(residual),
        "u": u,
        "core_span": core_span,
        "residual_inside_core_span": residual_inside_core_span,
        "residual_left_of_core": residual_left_of_core,
        "residual_right_of_core": residual_right_of_core,
        "density": fraction_record(k * k, n),
        "residual_fraction": fraction_record(u, k),
        "sharp_excess_3k2_minus_4N": sharp_excess,
        "above_sharp_gate": sharp_excess > 0,
        "difference_packing_lhs2": difference_packing_lhs2,
        "difference_packing_slack2": 2 * span - difference_packing_lhs2,
        "span_transfer_margin4": span_transfer_margin4,
        "span_transfer_holds": span_transfer_margin4 <= 0,
        "reflected_completion": list(completion) if completion is not None else None,
        "completion_added": completion_added,
        "completion_admissible": completion_admissible,
    }


def better_density(candidate: dict[str, Any], current: dict[str, Any] | None) -> bool:
    if current is None:
        return True
    return fraction_greater(
        candidate["k"] * candidate["k"],
        candidate["N"],
        current["k"] * current["k"],
        current["N"],
    )


def better_residual_fraction(
    candidate: dict[str, Any], current: dict[str, Any] | None
) -> bool:
    if current is None:
        return True
    left = candidate["u"] * current["k"]
    right = current["u"] * candidate["k"]
    if left != right:
        return left > right
    return better_density(candidate, current)


def search_n(n: int) -> dict[str, Any]:
    if n < 2:
        raise ValueError("N must be at least two")

    a = [0]
    sum_counts: dict[int, int] = {0: 1}
    admissible_count = 0
    repeated_exception_count = 0
    above_sharp_count = 0
    above_sharp_with_residual_count = 0
    span_transfer_failure_count = 0
    completion_failure_count = 0
    best_density_with_residual: dict[str, Any] | None = None
    largest_residual_above_sharp: dict[str, Any] | None = None
    strongest_span_transfer_failure: dict[str, Any] | None = None
    minima_by_p_u_delta: dict[tuple[int, int, int], dict[str, Any]] = {}

    def evaluate_leaf() -> None:
        nonlocal admissible_count, repeated_exception_count, above_sharp_count
        nonlocal above_sharp_with_residual_count, span_transfer_failure_count
        nonlocal completion_failure_count, best_density_with_residual
        nonlocal largest_residual_above_sharp, strongest_span_transfer_failure

        admissible_count += 1
        record = record_for(tuple(a), n)
        if record["sigma"] is not None:
            repeated_exception_count += 1
        if record["u"] > 0 and better_density(record, best_density_with_residual):
            best_density_with_residual = record
        if record["above_sharp_gate"]:
            above_sharp_count += 1
            if record["u"] > 0:
                above_sharp_with_residual_count += 1
                if better_residual_fraction(record, largest_residual_above_sharp):
                    largest_residual_above_sharp = record
        if not record["span_transfer_holds"]:
            span_transfer_failure_count += 1
            if (
                strongest_span_transfer_failure is None
                or record["span_transfer_margin4"]
                > strongest_span_transfer_failure["span_transfer_margin4"]
            ):
                strongest_span_transfer_failure = record
        if record["completion_admissible"] is False:
            completion_failure_count += 1

        key = (record["p"], record["u"], record["delta"])
        current = minima_by_p_u_delta.get(key)
        if current is None or record["span"] < current["span"]:
            minima_by_p_u_delta[key] = record

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
        "admissible_count": admissible_count,
        "repeated_exception_count": repeated_exception_count,
        "above_sharp_count": above_sharp_count,
        "above_sharp_with_residual_count": above_sharp_with_residual_count,
        "span_transfer_failure_count": span_transfer_failure_count,
        "completion_failure_count": completion_failure_count,
        "best_density_with_residual": best_density_with_residual,
        "largest_residual_fraction_above_sharp": largest_residual_above_sharp,
        "strongest_span_transfer_failure": strongest_span_transfer_failure,
        "minima_by_p_u_delta": [
            minima_by_p_u_delta[key] for key in sorted(minima_by_p_u_delta)
        ],
    }


def deletion_descendants(a: tuple[int, ...]) -> dict[str, Any]:
    sigma, _ = sum_profile(a)
    if sigma is None:
        raise ValueError("deletion audit requires a repeated exceptional sum")
    point_set = set(a)
    if any(sigma - x not in point_set for x in a):
        raise ValueError("deletion audit requires a fully reflected set")

    lower = tuple(x for x in a if 2 * x < sigma)
    midpoint = tuple(x for x in a if 2 * x == sigma)
    if not lower:
        raise ValueError("deletion audit requires an off-diagonal pair")

    checked = 0
    failures: list[dict[str, Any]] = []
    by_deleted_count: dict[int, dict[str, Any]] = {}
    for mask in range(1 << len(lower)):
        deleted_lower = tuple(
            lower[index] for index in range(len(lower)) if mask & (1 << index)
        )
        descendant = set(a)
        for x in deleted_lower:
            descendant.remove(sigma - x)
        checked += 1
        if not is_admissible(descendant):
            failures.append(
                {"deleted_lower": list(deleted_lower), "A": sorted(descendant)}
            )
        t = len(deleted_lower)
        row = by_deleted_count.setdefault(
            t,
            {
                "deleted_partner_count": t,
                "descendant_k": len(a) - t,
                "residual_u": t,
                "core_c": len(a) - 2 * t,
                "count": 0,
            },
        )
        row["count"] += 1

    return {
        "source_A": list(a),
        "sigma": sigma,
        "pair_count": len(lower),
        "midpoint_count": len(midpoint),
        "descendants_checked": checked,
        "failure_count": len(failures),
        "failures": failures,
        "by_deleted_count": [by_deleted_count[key] for key in sorted(by_deleted_count)],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p38/exhaustive_N22.json"),
    )
    args = parser.parse_args()

    results = [search_n(n) for n in range(args.min_n, args.max_n + 1)]
    all_best_residual = [
        row["best_density_with_residual"]
        for row in results
        if row["best_density_with_residual"] is not None
    ]
    all_above_sharp_residual = [
        row["largest_residual_fraction_above_sharp"]
        for row in results
        if row["largest_residual_fraction_above_sharp"] is not None
    ]
    strongest_density_with_residual = None
    for record in all_best_residual:
        if better_density(record, strongest_density_with_residual):
            strongest_density_with_residual = record
    largest_residual_above_sharp = None
    for record in all_above_sharp_residual:
        if better_residual_fraction(record, largest_residual_above_sharp):
            largest_residual_above_sharp = record

    # The N=31 P09 witness is a one-sided deletion of the fully reflected
    # ten-point P03 witness.  This independently checks the exact hereditary
    # mechanism without adding that larger N to the exhaustive domain.
    deletion_audit = deletion_descendants(
        (0, 1, 3, 8, 12, 18, 22, 27, 29, 30)
    )

    summary = {
        "arithmetic": "integer/rational only",
        "domain": (
            f"all A subset [0,N-1] with endpoints included, "
            f"{args.min_n} <= N <= {args.max_n}"
        ),
        "total_subset_count": sum(
            row["total_endpoint_normalized_subsets"] for row in results
        ),
        "admissible_count": sum(row["admissible_count"] for row in results),
        "above_sharp_count": sum(row["above_sharp_count"] for row in results),
        "above_sharp_with_residual_count": sum(
            row["above_sharp_with_residual_count"] for row in results
        ),
        "span_transfer_failure_count": sum(
            row["span_transfer_failure_count"] for row in results
        ),
        "completion_failure_count": sum(
            row["completion_failure_count"] for row in results
        ),
        "strongest_density_with_residual": strongest_density_with_residual,
        "largest_residual_fraction_above_sharp": largest_residual_above_sharp,
        "deletion_audit": deletion_audit,
        "by_N": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in summary.items()
                if key not in {"by_N"}
            }
        )
    )


if __name__ == "__main__":
    main()
