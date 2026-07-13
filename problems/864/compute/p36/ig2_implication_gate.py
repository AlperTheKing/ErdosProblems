#!/usr/bin/env python3
"""Exact gates for the proposed interval-gap lemma IG2.

IG(c) denotes

    2*N*Z <= 3*H^2*G + c*N*(k-1)*H,

where G=N+H-1-M.  The script:

1. exhausts endpoint-normalized sets and records exact falsifiers to
   IG(0), IG(1), and IG(2) in three nested structural classes;
2. checks IG(c) on every normalized P20 sample at H=ceil(N^(2/3));
3. gates the purely numerical implication from IG2 plus the sharp weighted
   capacity bound for differences of multiplicity at most two to C20.

Every comparison is by integer arithmetic or ``Fraction``.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable

from interval_gate_search import classify, endpoint_sets, profile


def ig_margin(row: dict[str, Any], coefficient: int) -> int:
    n = int(row["N"])
    h = int(row["H"])
    return (
        2 * n * int(row["Z"])
        - 3 * h * h * int(row["G"])
        - coefficient * n * (int(row["k"]) - 1) * h
    )


def with_ig_data(row: dict[str, Any]) -> dict[str, Any]:
    result = row.copy()
    for coefficient in range(3):
        result[f"ig{coefficient}_margin"] = ig_margin(row, coefficient)
    return result


def audit_exhaustive(max_n: int) -> dict[str, Any]:
    classes = ("difference_two", "coherent", "admissible")
    counts = {name: 0 for name in classes}
    failures = {
        str(coefficient): {name: 0 for name in classes}
        for coefficient in range(3)
    }
    first_failure: dict[str, dict[str, Any]] = {
        str(coefficient): {name: None for name in classes}
        for coefficient in range(3)
    }

    for n in range(2, max_n + 1):
        for a in endpoint_sets(n):
            structure = classify(a)
            row: dict[str, Any] | None = None
            for name in classes:
                if not getattr(structure, name):
                    continue
                counts[name] += 1
                if row is None:
                    row = with_ig_data(profile(a, n))
                    row["duplicate_centers"] = list(structure.duplicate_centers)
                    row["repeated_sums"] = list(structure.repeated_sums)
                for coefficient in range(3):
                    key = str(coefficient)
                    if int(row[f"ig{coefficient}_margin"]) > 0:
                        failures[key][name] += 1
                        if first_failure[key][name] is None:
                            first_failure[key][name] = row.copy()

    return {
        "max_N": max_n,
        "class_counts": counts,
        "failure_counts": failures,
        "first_failure": first_failure,
    }


def normalized_sample_profile(sample: dict[str, Any]) -> dict[str, Any] | None:
    values = tuple(int(value) for value in sample["A"])
    if not values:
        raise AssertionError("empty P20 sample")
    if len(values) == 1:
        return None
    shifted = tuple(value - values[0] for value in values)
    span_n = shifted[-1] + 1
    if int(sample["N"]) != span_n:
        raise AssertionError(f"P20 sample is not endpoint-normalized: {sample['sample_id']}")
    return with_ig_data(profile(shifted, span_n))


def audit_p20_samples(path: Path) -> dict[str, Any]:
    failures = {str(coefficient): 0 for coefficient in range(3)}
    first_failure: dict[str, dict[str, Any] | None] = {
        str(coefficient): None for coefficient in range(3)
    }
    largest_margin: dict[str, dict[str, Any] | None] = {
        str(coefficient): None for coefficient in range(3)
    }
    checked = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        sample = json.loads(line)
        row = normalized_sample_profile(sample)
        if row is None:
            continue
        checked += 1
        row["sample_id"] = sample["sample_id"]
        row["kind"] = sample["kind"]
        for coefficient in range(3):
            key = str(coefficient)
            margin = int(row[f"ig{coefficient}_margin"])
            if largest_margin[key] is None or margin > int(
                largest_margin[key][f"ig{coefficient}_margin"]
            ):
                largest_margin[key] = row.copy()
            if margin > 0:
                failures[key] += 1
                if first_failure[key] is None:
                    first_failure[key] = row.copy()
    return {
        "checked_samples": checked,
        "failure_counts": failures,
        "first_failure": first_failure,
        "largest_margin": largest_margin,
    }


def max_k_difference_two(n: int) -> int:
    # binom(k,2) <= 2(N-1).
    return (1 + isqrt(1 + 16 * (n - 1))) // 2


def max_weighted_pairs(h: int, total_pairs: int) -> int:
    """Sharp label-capacity upper bound for W.

    Each d in [1,H-1] supplies two slots of weight H-d.  Filling the slots
    in nonincreasing order maximizes W; pairs at distance at least H have
    zero weight.
    """

    used = min(total_pairs, 2 * (h - 1))
    doubled = used // 2
    remainder = used % 2
    return (
        2 * doubled * h
        - doubled * (doubled + 1)
        + remainder * (h - doubled - 1)
    )


def c20_rhs6(n: int, h: int, k: int) -> int:
    return 8 * n * h * h + 9 * h * h * h + 9 * n * (k - 1) * h


def continuous_candidates(
    n: int, h: int, k: int, s_cap: int
) -> Iterable[Fraction]:
    """All breakpoints/maximizers of the IG2/cap product relaxation."""

    lower = Fraction(0)
    upper = Fraction(n - k)
    if upper < lower:
        return ()

    # S_IG2(G)=(A+B*G)/N; M=N+H-1-G.
    a = n * h * h + 2 * n * (k - 1) * h
    b = 3 * h * h
    support_origin = n + h - 1
    vertex = Fraction(b * support_origin - a, 2 * b)
    crossover = Fraction(n * s_cap - a, b)
    raw = (lower, upper, vertex, crossover)
    return tuple(value for value in raw if lower <= value <= upper)


def relaxed_product_numerator(
    n: int, h: int, k: int, g: Fraction, s_cap: int
) -> tuple[Fraction, str]:
    """Return 6*M*S for the continuous upper relaxation."""

    support = Fraction(n + h - 1) - g
    s_ig2 = Fraction(
        n * h * h + 3 * h * h * g + 2 * n * (k - 1) * h,
        n,
    )
    if s_ig2 <= s_cap:
        return 6 * support * s_ig2, "IG2"
    return 6 * support * s_cap, "capacity"


def audit_implication(max_n: int) -> dict[str, Any]:
    checked_parameters = 0
    failures = 0
    first_failure: dict[str, Any] | None = None
    worst_margin: Fraction | None = None
    worst_record: dict[str, Any] | None = None

    for n in range(2, max_n + 1):
        h = profile((0, n - 1), n)["H"]
        if not isinstance(h, int):
            raise AssertionError("H is not integral")
        for k in range(2, max_k_difference_two(n) + 1):
            if k > n:
                break
            checked_parameters += 1
            total_pairs = k * (k - 1) // 2
            w_cap = max_weighted_pairs(h, total_pairs)
            s_cap = h + 2 * w_cap
            rhs = c20_rhs6(n, h, k)
            for g in continuous_candidates(n, h, k, s_cap):
                lhs, active = relaxed_product_numerator(n, h, k, g, s_cap)
                margin = lhs - rhs
                record = {
                    "N": n,
                    "H": h,
                    "k": k,
                    "G": f"{g.numerator}/{g.denominator}",
                    "active_bound": active,
                    "S_capacity": s_cap,
                    "margin_numerator": margin.numerator,
                    "margin_denominator": margin.denominator,
                }
                if worst_margin is None or margin > worst_margin:
                    worst_margin = margin
                    worst_record = record
                if margin > 0:
                    failures += 1
                    if first_failure is None:
                        first_failure = record

    return {
        "max_N": max_n,
        "checked_N_k_parameters": checked_parameters,
        "failure_count": failures,
        "first_failure": first_failure,
        "worst_margin": worst_record,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-max-n", type=int, default=20)
    parser.add_argument("--implication-max-n", type=int, default=10000)
    parser.add_argument(
        "--p20-samples",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/ig2_gate.json"),
    )
    args = parser.parse_args()

    result = {
        "arithmetic": "integer/rational",
        "IG_definition": "2*N*Z <= 3*H^2*G + c*N*(k-1)*H",
        "exhaustive": audit_exhaustive(args.exhaustive_max_n),
        "p20_samples": audit_p20_samples(args.p20_samples),
        "implication_relaxation": audit_implication(args.implication_max_n),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
