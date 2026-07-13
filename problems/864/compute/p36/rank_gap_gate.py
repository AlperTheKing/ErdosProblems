#!/usr/bin/env python3
"""Exact rank-gap upper bound for the centered interval energy.

Let x_i=min(H,a_{i+1}-a_i), n=k-1, and L=sum_i x_i=M-H.
For rank r, the clipped r-step distances have total T_r and contribute

    W_r = (n-r+1)H - T_r.

The untruncated r-step sums use gap x_j with an explicit coverage
coefficient.  Given only sum(x_j)=L and 1<=x_j<=H, their smallest possible
total is obtained by putting excess gap mass on the smallest coefficients.
Given that total, the smallest possible clipped total is obtained by
concentrating distance mass into as few rank-r sums as possible.  Both are
finite greedy optimizations, proved by exchanges, and are implemented below
with integer arithmetic.

This produces a rigorous geometry-aware upper bound for W.  The separate
difference-label capacity bound uses nu(d)<=2.  The audit checks identities,
the rank bound, and whether the minimum of the two bounds implies C20.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ig2_implication_gate import max_weighted_pairs
from interval_gate_search import classify, endpoint_sets, profile
from p20_ambient_ig_gate import ambient_profile


def rank_coefficients(n: int, r: int) -> list[int]:
    if not 1 <= r <= n:
        raise ValueError("rank outside 1..n")
    block_count = n - r + 1
    result = []
    for gap_index in range(1, n + 1):
        first_start = max(1, gap_index - r + 1)
        last_start = min(gap_index, block_count)
        result.append(last_start - first_start + 1)
    if sum(result) != block_count * r:
        raise AssertionError("rank coefficient sum failed")
    return result


def minimum_untruncated_rank_sum(n: int, h: int, length: int, r: int) -> int:
    """Minimum sum of all rank-r block sums for clipped gaps."""

    if not n <= length <= n * h:
        raise ValueError("infeasible clipped-gap length")
    coefficients = sorted(rank_coefficients(n, r))
    excess = length - n
    result = (n - r + 1) * r
    for coefficient in coefficients:
        addition = min(excess, h - 1)
        result += coefficient * addition
        excess -= addition
        if excess == 0:
            break
    if excess:
        raise AssertionError("gap-mass allocation did not terminate")
    return result


def minimum_truncated_total(
    block_count: int, h: int, r: int, untruncated_total: int
) -> int:
    """Minimum sum min(H,d_i) from a lower bound on sum d_i.

    This is used only for r<H.  Each d_i lies in [r,rH].  Starting from r,
    one variable can absorb r(H-1) extra units while its clipped value rises
    by only H-r; concentrating the extra mass is therefore optimal.
    """

    if not 1 <= r < h:
        raise ValueError("truncated optimization requires 1 <= r < H")
    baseline = block_count * r
    maximum = block_count * r * h
    if not baseline <= untruncated_total <= maximum:
        raise ValueError("rank total outside its box constraints")
    extra = untruncated_total - baseline
    absorption = r * (h - 1)
    saturated, remainder = divmod(extra, absorption)
    if saturated > block_count:
        raise AssertionError("too many saturated rank blocks")
    return (
        baseline
        + saturated * (h - r)
        + min(remainder, h - r)
    )


def rank_gap_w_bound(n: int, h: int, length: int) -> int:
    if n == 0:
        return 0
    total = 0
    for r in range(1, min(n, h - 1) + 1):
        block_count = n - r + 1
        untruncated = minimum_untruncated_rank_sum(n, h, length, r)
        truncated = minimum_truncated_total(block_count, h, r, untruncated)
        total += block_count * h - truncated
    return total


def actual_rank_data(a: list[int], h: int) -> tuple[int, list[int]]:
    clipped_gaps = [min(h, right - left) for left, right in zip(a, a[1:])]
    length = sum(clipped_gaps)
    total_w = 0
    row_totals = []
    for r in range(1, min(len(clipped_gaps), h - 1) + 1):
        distances = [
            sum(clipped_gaps[start : start + r])
            for start in range(len(clipped_gaps) - r + 1)
        ]
        truncated = sum(min(h, value) for value in distances)
        row_totals.append(truncated)
        total_w += len(distances) * h - truncated
    return total_w, row_totals


def bound_record(row: dict[str, Any]) -> dict[str, Any]:
    n = int(row["k"]) - 1
    h = int(row["H"])
    length = int(row["M"]) - h
    rank_bound = rank_gap_w_bound(n, h, length)
    pair_capacity = max_weighted_pairs(h, int(row["k"]) * n // 2)
    combined = min(rank_bound, pair_capacity)
    s_bound = h + 2 * combined
    c20_bound_margin = (
        6 * int(row["M"]) * s_bound
        - 8 * int(row["N"]) * h * h
        - 9 * h * h * h
        - 9 * int(row["N"]) * n * h
    )
    result = row.copy()
    result.update(
        {
            "clipped_gap_length": length,
            "rank_gap_W_bound": rank_bound,
            "label_capacity_W_bound": pair_capacity,
            "combined_W_bound": combined,
            "actual_W": int(row["W"]),
            "bound_slack": combined - int(row["W"]),
            "c20_bound_margin": c20_bound_margin,
        }
    )
    return result


def audit_p20(path: Path) -> dict[str, Any]:
    rank_failures = 0
    implication_failures = 0
    first_rank_failure = None
    first_implication_failure = None
    worst_implication = None
    checked = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        sample = json.loads(line)
        row = ambient_profile(sample)
        actual_w, _ = actual_rank_data(row["A"], int(row["H"]))
        if actual_w != int(row["W"]):
            raise AssertionError(f"rank identity failed: {sample['sample_id']}")
        result = bound_record(row)
        result["sample_id"] = sample["sample_id"]
        checked += 1
        if int(result["bound_slack"]) < 0:
            rank_failures += 1
            if first_rank_failure is None:
                first_rank_failure = result
        if int(result["c20_bound_margin"]) > 0:
            implication_failures += 1
            if first_implication_failure is None:
                first_implication_failure = result
        if worst_implication is None or int(result["c20_bound_margin"]) > int(
            worst_implication["c20_bound_margin"]
        ):
            worst_implication = result
    return {
        "checked": checked,
        "rank_bound_failure_count": rank_failures,
        "first_rank_bound_failure": first_rank_failure,
        "C20_implication_failure_count": implication_failures,
        "first_C20_implication_failure": first_implication_failure,
        "worst_C20_bound_margin": worst_implication,
    }


def audit_exhaustive(max_n: int) -> dict[str, Any]:
    checked = 0
    rank_failures = 0
    implication_failures = 0
    first_implication_failure = None
    for ambient_n in range(2, max_n + 1):
        for a in endpoint_sets(ambient_n):
            if not classify(a).difference_two:
                continue
            row = profile(a, ambient_n)
            actual_w, _ = actual_rank_data(list(a), int(row["H"]))
            if actual_w != int(row["W"]):
                raise AssertionError("exhaustive rank identity failed")
            result = bound_record(row)
            checked += 1
            if int(result["bound_slack"]) < 0:
                rank_failures += 1
            if int(result["c20_bound_margin"]) > 0:
                implication_failures += 1
                if first_implication_failure is None:
                    first_implication_failure = result
    return {
        "max_N": max_n,
        "checked_difference_two_sets": checked,
        "rank_bound_failure_count": rank_failures,
        "C20_implication_failure_count": implication_failures,
        "first_C20_implication_failure": first_implication_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-max-n", type=int, default=20)
    parser.add_argument(
        "--p20-samples",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/rank_gap_gate.json"),
    )
    args = parser.parse_args()
    result = {
        "arithmetic": "integer",
        "exhaustive": audit_exhaustive(args.exhaustive_max_n),
        "p20_samples": audit_p20(args.p20_samples),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
