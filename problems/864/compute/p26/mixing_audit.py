"""Exact audit of the P26 Singer complement-mixing formulation."""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import mean
from typing import Sequence


def positive_differences(values: Sequence[int]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def unordered_sums(values: Sequence[int]) -> set[int]:
    return {
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    }


def mixing_counts(values: Sequence[int], modulus: int, d: int) -> dict[str, int]:
    delta = positive_differences(values)
    ordered = 0
    diagonal = 0
    low_unordered = 0
    for i, alpha in enumerate(values):
        for beta in values[i:]:
            if alpha + beta >= d:
                break
            low_unordered += 1
            if d - alpha - beta not in delta:
                if alpha == beta:
                    diagonal += 1
                ordered += 1 if alpha == beta else 2
    return {
        "low_unordered_pairs": low_unordered,
        "missing_unordered": (ordered + diagonal) // 2,
        "missing_ordered": ordered,
        "missing_diagonal": diagonal,
    }


def tetrahedral_count(values: Sequence[int], modulus: int, d: int) -> int:
    value_set = set(values)
    total = 0
    for alpha in values:
        for beta in values:
            remaining = d - alpha - beta
            if remaining <= 0:
                continue
            for delta in values:
                if delta >= remaining:
                    break
                gamma = modulus - d + alpha + beta + delta
                if gamma in value_set:
                    total += 1
    return total


def zero_mode(p: int, modulus: int, d: int) -> Fraction:
    density = Fraction(p, modulus)
    ordered = density**4 * math.comb(d + 2, 3)
    diagonal_domain = ((d + 1) * (d + 1)) // 4
    diagonal = density**3 * diagonal_domain
    return (ordered + diagonal) / 2


def audit_hole(record: dict[str, object]) -> dict[str, object]:
    best = record["best_candidate"]
    if not isinstance(best, dict):
        raise AssertionError("missing candidate")
    modulus = int(record["modulus"])
    b = [int(x) for x in best["points"]]
    length = b[-1]
    center = int(best["candidate_center"])
    c = sorted(length - x for x in b)
    d = modulus + 2 * length - center
    if not 0 < d < modulus:
        raise AssertionError("candidate is outside the complement branch")
    delta = positive_differences(c)
    if len(delta) != (modulus - 1) // 2:
        raise AssertionError("positive differences are not a Singer selector")

    counts = mixing_counts(c, modulus, d)
    tetrahedron = tetrahedral_count(c, modulus, d)
    if tetrahedron != counts["missing_ordered"]:
        raise AssertionError("tetrahedral identity failed")

    sums = unordered_sums(b)
    literal_hole = center not in {s + h for s in sums for h in delta}
    containment = all(
        d - alpha - beta in delta
        for i, alpha in enumerate(c)
        for beta in c[i:]
        if alpha + beta < d
    )
    if literal_hole != containment or not literal_hole:
        raise AssertionError("complement containment disagrees with literal hole")

    p = len(c)
    quadratic = Fraction(d * d, 8 * modulus)
    corrected = zero_mode(p, modulus, d)
    return {
        "parameter": int(record["parameter"]),
        "p": p,
        "modulus": modulus,
        "multiplier": int(best["affine_multiplier"]),
        "cut_base": int(best["cut_base"]),
        "span": length,
        "center": center,
        "d": d,
        "d_over_modulus": str(Fraction(d, modulus)),
        **counts,
        "tetrahedral_count": tetrahedron,
        "quadratic_proposed_main": str(quadratic),
        "quadratic_proposed_main_decimal": float(quadratic),
        "tetrahedral_zero_mode": str(corrected),
        "tetrahedral_zero_mode_decimal": float(corrected),
        "literal_hole_iff_containment": True,
    }


def scan_cuts(record: dict[str, object]) -> list[dict[str, object]]:
    best = record["best_candidate"]
    if not isinstance(best, dict):
        raise AssertionError("missing candidate")
    modulus = int(record["modulus"])
    points = [int(x) for x in best["points"]]
    witness_base = int(best["cut_base"])
    source = sorted((x + witness_base) % modulus for x in points)
    fractions = ((1, 4), (1, 3), (1, 2), (2, 3))
    rows: list[dict[str, object]] = []
    for numerator, denominator in fractions:
        d = numerator * modulus // denominator
        observed: list[int] = []
        for base in source:
            b = sorted((x - base) % modulus for x in source)
            length = b[-1]
            c = sorted(length - x for x in b)
            observed.append(mixing_counts(c, modulus, d)["missing_unordered"])
        p = len(source)
        quadratic = Fraction(d * d, 8 * modulus)
        corrected = zero_mode(p, modulus, d)
        rows.append(
            {
                "d": d,
                "d_over_modulus": str(Fraction(d, modulus)),
                "cuts": len(observed),
                "minimum": min(observed),
                "maximum": max(observed),
                "mean": mean(observed),
                "zero_cuts": sum(value == 0 for value in observed),
                "quadratic_proposed_main": float(quadratic),
                "tetrahedral_zero_mode": float(corrected),
            }
        )
    return rows


def read_record(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="ascii").splitlines()
    if len(lines) != 1:
        raise AssertionError(f"expected one JSON record in {path}")
    return json.loads(lines[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "inputs",
        type=Path,
        nargs="*",
        default=[
            Path("problems/864/compute/p12/parallel_q167_u512.json"),
            Path("problems/864/compute/p12/singer_sample_q167.jsonl"),
        ],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = [read_record(path) for path in args.inputs]
    output = {
        "hole_audits": [audit_hole(record) for record in records],
        "all_cut_scan_first_record": scan_cuts(records[0]),
    }
    rendered = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="ascii")
    print(rendered, end="")


if __name__ == "__main__":
    main()
