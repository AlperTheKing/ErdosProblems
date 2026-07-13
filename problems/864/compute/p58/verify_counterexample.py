#!/usr/bin/env python3
"""Standalone exact verifier for the P58 fold-repair counterexample."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


H = 183
B_SHIFT = 1
B = (33, 60, 72, 75, 79, 81, 95, 119, 124, 132, 149, 150, 160, 182)


def digest(values: list[int]) -> str:
    payload = ",".join(map(str, values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def verify() -> dict[str, object]:
    p = len(B)
    assert tuple(sorted(set(B))) == B
    assert all(0 <= value < H for value in B)
    assert max(B) == H - 1

    sum_representations: dict[int, list[tuple[int, int]]] = {}
    for i, left in enumerate(B):
        for right in B[i:]:
            sum_representations.setdefault(left + right, []).append((left, right))
    assert len(sum_representations) == p * (p + 1) // 2
    assert all(len(reps) == 1 for reps in sum_representations.values())

    difference_representations: dict[int, list[tuple[int, int]]] = {}
    for left in B:
        for right in B:
            difference_representations.setdefault(left - right, []).append((left, right))
    assert len(difference_representations) == p * (p - 1) + 1
    assert len(difference_representations[0]) == p
    assert all(
        len(reps) == 1
        for value, reps in difference_representations.items()
        if value != 0
    )

    sums = sorted(sum_representations)
    differences = sorted(difference_representations)
    positive_differences = [value for value in differences if value > 0]
    sum_residues = {value % H for value in sums}
    difference_residues = {value % H for value in differences}
    c_s = len(sums) - len(sum_residues)
    c_d = len(differences) - len(difference_residues)
    assert c_s == 0
    assert c_d == 0
    assert difference_residues == set(range(H))

    shifted_sums = {value + B_SHIFT for value in sums}
    assert shifted_sums.isdisjoint(positive_differences)

    target = -B_SHIFT
    target_count = 0
    three_b_minus_b = set()
    for x, y, z, w in product(B, repeat=4):
        value = x + y + z - w
        three_b_minus_b.add(value)
        target_count += int(value == target)
    assert target_count == 0
    assert target not in three_b_minus_b

    baseline = (3 * p * p - p + 2) // 2
    delta = baseline - H
    collision_total = c_s + c_d
    excess = max(delta - 5 * collision_total, 0)
    lhs = excess * excess
    rhs = 4 * p**3
    assert delta > 0
    assert lhs > rhs

    return {
        "arithmetic": "exact integers",
        "B": list(B),
        "p": p,
        "h": H,
        "b": B_SHIFT,
        "range_and_endpoint": True,
        "integer_sidon_including_diagonals": True,
        "unordered_sum_count": len(sums),
        "diagonal_sum_count": p,
        "difference_support_count": len(differences),
        "zero_difference_ordered_representations": p,
        "nonzero_difference_representations_are_unique": True,
        "ordered_quadruples_checked": p**4,
        "minus_b_ordered_representations": target_count,
        "minus_b_not_in_3B_minus_B": True,
        "sum_support": sums,
        "positive_difference_support": positive_differences,
        "sum_support_sha256": digest(sums),
        "positive_difference_support_sha256": digest(positive_differences),
        "three_B_minus_B_support_count": len(three_b_minus_b),
        "three_B_minus_B_support_sha256": digest(sorted(three_b_minus_b)),
        "sum_residue_count": len(sum_residues),
        "difference_residue_count": len(difference_residues),
        "difference_residues_are_all_mod_h": True,
        "C_S": c_s,
        "C_D": c_d,
        "baseline": baseline,
        "delta": delta,
        "positive_excess": excess,
        "candidate_lhs": lhs,
        "candidate_rhs": rhs,
        "failure_margin": lhs - rhs,
        "excess_squared_over_p_cubed": str(Fraction(lhs, p**3)),
        "candidate_fails": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p58/counterexample_certificate.json"),
    )
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "p": result["p"],
                "h": result["h"],
                "b": result["b"],
                "C_S": result["C_S"],
                "C_D": result["C_D"],
                "delta": result["delta"],
                "candidate_lhs": result["candidate_lhs"],
                "candidate_rhs": result["candidate_rhs"],
                "failure_margin": result["failure_margin"],
                "ordered_quadruples_checked": result["ordered_quadruples_checked"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
