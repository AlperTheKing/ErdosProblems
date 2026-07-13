#!/usr/bin/env python3
"""Exact natural-modulus Bose-Chowla carry and construction audit.

All acceptance checks use integer or finite-field arithmetic.  The finite-field
constructor is imported from P12; every lift, carry condition, and reflected
sum census is recomputed here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ALGEBRA = ROOT / "problems/864/compute/p12/algebraic_scan.py"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p63/natural_bose_holes.json"


def load_algebra():
    spec = importlib.util.spec_from_file_location("p63_algebra", ALGEBRA)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P12 finite-field constructor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def unordered_sum_counts(values: tuple[int, ...]) -> Counter[int]:
    return Counter(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def positive_difference_counts(values: tuple[int, ...]) -> Counter[int]:
    return Counter(
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )


def reflected_census(z: tuple[int, ...], modulus: int, b: int) -> dict[str, object]:
    """Verify the exact lift -> same-parity -> reflected construction chain."""
    p = len(z)
    width = z[-1]
    gamma = modulus - width - 1
    gap = 2 * gamma + b

    sums = unordered_sum_counts(z)
    differences = positive_difference_counts(z)
    if set(differences).intersection(s + gap for s in sums):
        raise AssertionError("signed-ruler supports intersect")

    shifted = tuple(gamma + x for x in z)
    ordered_hole_count = sum(
        1
        for x in shifted
        for y in shifted
        for t in shifted
        for w in shifted
        if x + y + t - w == -b
    )
    if ordered_hole_count != 0:
        raise AssertionError("literal -b in 3B-B")

    same_parity = tuple(2 * x + b for x in shifted)
    threefold = {x + y + t for x in same_parity for y in same_parity for t in same_parity}
    if set(same_parity).intersection(threefold):
        raise AssertionError("same-parity set meets its threefold sumset")

    left = tuple(width - x for x in z)
    span = gap + 2 * width
    if span != 2 * modulus - 2 + b:
        raise AssertionError("natural-modulus span identity failed")
    reflected = tuple(sorted(set(left).union(span - x for x in left)))
    if len(reflected) != 2 * p:
        raise AssertionError("reflected blocks overlap")
    repeated = sorted(
        (total, count)
        for total, count in unordered_sum_counts(reflected).items()
        if count >= 2
    )
    if repeated != [(span, p)]:
        raise AssertionError(("reflected admissibility failed", repeated))
    return {
        "same_parity": list(same_parity),
        "reflected": list(reflected),
        "span": span,
        "translated_N": span + 1,
        "repeated_sums_before_translation": repeated,
    }


def audit_lift(z: tuple[int, ...], modulus: int, b: int) -> dict[str, object]:
    if not z or z[0] != 0:
        raise AssertionError("lift is not endpoint normalized")
    p = len(z)
    width = z[-1]
    gamma = modulus - width - 1
    gap = 2 * gamma + b
    sums = unordered_sum_counts(z)
    differences = positive_difference_counts(z)
    if len(sums) != p * (p + 1) // 2 or max(sums.values()) != 1:
        raise AssertionError("integer Sidon failure")
    if len(differences) != p * (p - 1) // 2 or max(differences.values(), default=0) != 1:
        raise AssertionError("positive-difference failure")

    literal = sorted(set(differences).intersection(s + gap for s in sums))
    ordered_sums = Counter(x + y for x in z for y in z)
    ordered_differences = Counter(t - w for t in z for w in z)
    ordered_positive_differences = Counter(
        {
            difference: multiplicity
            for difference, multiplicity in ordered_differences.items()
            if difference > 0
        }
    )
    direct_hole_count = sum(
        multiplicity * ordered_positive_differences[s + gap]
        for s, multiplicity in ordered_sums.items()
    )
    if (not literal) != (direct_hole_count == 0):
        raise AssertionError("support and ordered 3B-B checks disagree")

    carry_counts = Counter()
    for total, sum_multiplicity in ordered_sums.items():
        for carry in (0, 1, 2):
            difference = carry * modulus - (2 * gamma + b) - total
            carry_counts[carry] += sum_multiplicity * ordered_differences[difference]
    modular_solution_count = sum(carry_counts.values())
    if carry_counts[0] != direct_hole_count:
        raise AssertionError("carry-zero count disagrees with direct hole count")
    if abs(modular_solution_count - p * p) > 2 * p:
        raise AssertionError("Bose modular solution count outside parametrization bound")

    modular_intersection = set(differences).intersection(
        (s + gap) % modulus for s in sums
    )
    wrapped = sorted(
        set(differences).intersection(s + gap - modulus for s in sums)
    )
    if not literal and len(wrapped) != len(modular_intersection):
        raise AssertionError("hole has a non-wrapped modular intersection")

    shifted = tuple(gamma + x for x in z)
    record: dict[str, object] = {
        "b": b,
        "width": width,
        "gamma": gamma,
        "gap": gap,
        "cut_gap": gamma + 1,
        "position_sum": sum(shifted),
        "position_mean_over_modulus": [sum(shifted), p * modulus],
        "literal_hit_count": len(literal),
        "literal_hits": literal[:16],
        "modular_intersection_count": len(modular_intersection),
        "wrapped_intersection_count": len(wrapped),
        "ordered_hole_count": direct_hole_count,
        "ordered_carry_counts": dict(sorted(carry_counts.items())),
        "modular_solution_count": modular_solution_count,
        "valid": not literal,
    }
    if not literal:
        record["construction"] = reflected_census(z, modulus, b)
    return record


def audit_parameter(algebra, q: int) -> dict[str, object]:
    modulus, residues, metadata = algebra.bose_chowla(q)
    if modulus != q * q - 1 or len(residues) != q:
        raise AssertionError("Bose-Chowla parameter mismatch")
    seen: set[tuple[int, ...]] = set()
    by_b: dict[int, list[dict[str, object]]] = {1: [], 2: []}
    minima = {1: None, 2: None}
    valid_examples: list[dict[str, object]] = []
    for unit in algebra.unit_multipliers(modulus, None):
        transformed = tuple((unit * x) % modulus for x in residues)
        for lift, base, cut_gap in algebra.cyclic_lifts(transformed, modulus):
            if lift in seen:
                continue
            seen.add(lift)
            for b in (1, 2):
                rec = audit_lift(lift, modulus, b)
                rec.update({"unit": unit, "base": base, "points": list(lift)})
                hits = int(rec["literal_hit_count"])
                if minima[b] is None or hits < int(minima[b]["literal_hit_count"]):
                    minima[b] = rec
                if bool(rec["valid"]):
                    by_b[b].append(rec)
                    valid_examples.append(rec)
    all_valid = by_b[1] + by_b[2]
    return {
        "q": q,
        "modulus": modulus,
        "metadata": metadata,
        "distinct_lifts": len(seen),
        "valid_b1": len(by_b[1]),
        "valid_b2": len(by_b[2]),
        "minimum_hits_b1": minima[1],
        "minimum_hits_b2": minima[2],
        "minimum_valid_mean": None
        if not all_valid
        else min(
            (rec["position_mean_over_modulus"], rec["unit"], rec["base"])
            for rec in all_valid
        ),
        "maximum_valid_mean": None
        if not all_valid
        else max(
            (rec["position_mean_over_modulus"], rec["unit"], rec["base"])
            for rec in all_valid
        ),
        "valid_examples": valid_examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    algebra = load_algebra()
    rows = []
    for q in args.parameters:
        row = audit_parameter(algebra, q)
        rows.append(row)
        print(
            json.dumps(
                {
                    "q": q,
                    "distinct_lifts": row["distinct_lifts"],
                    "valid_b1": row["valid_b1"],
                    "valid_b2": row["valid_b2"],
                    "min_hits_b1": row["minimum_hits_b1"]["literal_hit_count"],
                    "min_hits_b2": row["minimum_hits_b2"]["literal_hit_count"],
                    "minimum_valid_mean": row["minimum_valid_mean"],
                },
                sort_keys=True,
            )
        )
    result = {
        "arithmetic": "exact integers and finite fields",
        "parameters": args.parameters,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
