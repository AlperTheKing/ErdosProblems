#!/usr/bin/env python3
"""Exact finite audit for P69's width-compensated carry obstruction."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[4]
P60_PATH = ROOT / "problems/864/compute/p60/audit_curvature_span.py"
OUTPUT = Path(__file__).with_name("audit_results.json")


def load_p60():
    spec = importlib.util.spec_from_file_location("p60_for_p69", P60_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P60 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sums_and_differences(z: tuple[int, ...]) -> tuple[set[int], set[int]]:
    sums = {z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))}
    differences = {
        z[j] - z[i] for i in range(len(z)) for j in range(i + 1, len(z))
    }
    p = len(z)
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) // 2
    return sums, differences


def nonnegative_three_minus_one(z: tuple[int, ...]) -> set[int]:
    return {
        out - a - b - c
        for out in z
        for a in z
        for b in z
        for c in z
        if out >= a + b + c
    }


def hole_run(support: set[int], gap: int) -> tuple[int, int, int]:
    left = gap
    while left - 1 >= 0 and left - 1 not in support:
        left -= 1
    right = gap
    while right + 1 not in support:
        right += 1
        if right > max(support | {gap}) + gap + 2:
            break
    return left, right, right - left + 1


def ordered_modular_quadruples(B: tuple[int, ...], h: int, b: int) -> int:
    support = set(B)
    return sum(
        ((x + y + z + b) % h) in support
        for x in B
        for y in B
        for z in B
    )


def arc_area(z: tuple[int, ...], gap: int) -> int:
    width = z[-1]
    return sum(
        abs(left - right) <= n < gap + left + right
        for n in range(gap, width)
        for left in z
        for right in z
    )


def audit_pair(z_values: Iterable[int], gap: int, source: str) -> dict[str, object]:
    z = tuple(z_values)
    p = len(z)
    width = z[-1]
    sums, differences = sums_and_differences(z)
    assert not differences.intersection(gap + value for value in sums)

    b = 1 if gap % 2 else 2
    gamma = (gap - b) // 2
    h = gamma + width + 1
    B = tuple(gamma + value for value in z)
    d = h - b
    baseline = (3 * p * p - p + 2) // 2
    delta = baseline - h
    length = gap + 2 * width
    defect = 3 * p * p - length
    assert defect == 2 * delta + p - b

    sum_residues = {(x + y) % h for i, x in enumerate(B) for y in B[i:]}
    difference_residues = {(x - y) % h for x in B for y in B}
    cs = p * (p + 1) // 2 - len(sum_residues)
    cd = p * (p - 1) + 1 - len(difference_residues)
    assert cs >= 0 and cd >= 0
    overlap = sum_residues.intersection(
        {(-b + value) % h for value in difference_residues}
    )
    support_lower = max(delta - cs - cd, 0)
    assert len(overlap) >= support_lower

    modular_q = ordered_modular_quadruples(B, h, b)
    assert modular_q >= len(overlap)
    literal_q = sum(
        x + y + zz + b == w for x in B for y in B for zz in B for w in B
    )
    assert literal_q == 0
    tetrahedron_q = sum(
        x + y + zz < d and ((x + y + zz + b) % h) in set(B)
        for x in B
        for y in B
        for zz in B
    )
    assert tetrahedron_q == 0

    tetrahedron_size = d * (d + 1) * (d + 2) // 6
    fourier_forcing = Fraction(modular_q * tetrahedron_size, 4 * h**3)

    bridge_rhs = 2 * modular_q + 2 * (cs + cd) + p - b
    assert defect <= bridge_rhs

    inversion = width - gap
    low_sums = sum(value <= inversion for value in sums)
    high_differences = sum(value >= gap for value in differences)
    overlap_slack = inversion + 1 - low_sums - high_differences
    assert overlap_slack >= 0

    shifts = nonnegative_three_minus_one(z)
    assert gap not in shifts
    left, right, run = hole_run(shifts, gap)
    area = arc_area(z, gap) if gap < width else 0
    positive_defect = max(defect, 0)
    return {
        "source": source,
        "p": p,
        "Z": list(z),
        "G": gap,
        "W": width,
        "h": h,
        "b": b,
        "delta": delta,
        "length": length,
        "compensated_defect": defect,
        "positive_defect": positive_defect,
        "C_S": cs,
        "C_D": cd,
        "modular_support_overlap": len(overlap),
        "modular_quadruples": modular_q,
        "tetrahedron_size": tetrahedron_size,
        "forced_Lambda_times_Lh5": str(fourier_forcing),
        "support_lower_bound": support_lower,
        "bridge_rhs": bridge_rhs,
        "inversion_width": inversion,
        "low_sum_atoms": low_sums,
        "high_difference_atoms": high_differences,
        "overlap_capacity_slack": overlap_slack,
        "arc_area": area,
        "hole_run": [left, right],
        "hole_run_length": run,
        "square_ratio_over_p3": str(Fraction(positive_defect**2, p**3)),
        "square_le_4p3": positive_defect**2 <= 4 * p**3,
        "square_le_25p3": positive_defect**2 <= 25 * p**3,
        "square_over_arc": None if area == 0 else str(Fraction(positive_defect**2, area)),
        "defect_times_width_over_arc": (
            None if area == 0 else str(Fraction(positive_defect * inversion, area))
        ),
    }


def endpoint_sidon_rulers(max_width: int, p60) -> Iterable[tuple[int, ...]]:
    for width in range(1, max_width + 1):
        for interior_size in range(width):
            for middle in combinations(range(1, width), interior_size):
                z = (0, *middle, width)
                if p60.sidon_data(z) is not None:
                    yield z


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    p60 = load_p60()

    records: list[dict[str, object]] = []
    exhaustive_count = 0
    for z in endpoint_sidon_rulers(args.max_width, p60):
        differences, weighted_sums = p60.sidon_data(z)
        for gap in range(1, z[-1]):
            if p60.valid_gap(differences, weighted_sums, gap):
                records.append(audit_pair(z, gap, "exhaustive"))
                exhaustive_count += 1

    for family_index, family in enumerate(p60.STORED_WITNESSES):
        z = tuple(family["Z"])
        differences, weighted_sums = p60.sidon_data(z)
        for gap in range(1, z[-1]):
            if p60.valid_gap(differences, weighted_sums, gap):
                records.append(audit_pair(z, gap, f"stored-{family_index}"))

    for prime in (3, 5, 7, 11, 13, 17, 19, 23):
        base = tuple(2 * prime * i + (i * i) % prime for i in range(prime))
        z = tuple(2 * value for value in base)
        records.append(audit_pair(z, 1, f"doubled-ET-p{prime}"))

    guards = [
        ("P68-long-hole", (0, 24, 26, 29, 30), 7),
        (
            "P58-clean-Singer-hole",
            (0, 27, 39, 42, 46, 48, 62, 86, 91, 99, 116, 117, 127, 149),
            67,
        ),
    ]
    for source, z, gap in guards:
        records.append(audit_pair(z, gap, source))

    positive = [record for record in records if int(record["positive_defect"]) > 0]
    max_square = max(
        positive,
        key=lambda record: Fraction(str(record["square_ratio_over_p3"])),
    )
    max_hole = max(records, key=lambda record: int(record["hole_run_length"]))
    failures_4 = [record for record in records if not bool(record["square_le_4p3"])]
    failures_25 = [record for record in records if not bool(record["square_le_25p3"])]
    result = {
        "arithmetic": "exact integers and rational ratios",
        "max_width": args.max_width,
        "exhaustive_pairs": exhaustive_count,
        "total_records": len(records),
        "positive_defect_records": len(positive),
        "exact_checks": {
            "defect_identity": "E=3p^2-(G+2W)=2delta+p-b",
            "fold_support_lower_bound": "Qmod >= overlap >= max(delta-C_S-C_D,0)",
            "literal_tetrahedron_count": 0,
            "bridge": "E <= 2Qmod+2(C_S+C_D)+p-b",
            "overlap_capacity": "D_[G,W]+S_[0,W-G] <= W-G+1",
        },
        "square_4p3_failures": len(failures_4),
        "first_square_4p3_failure": None if not failures_4 else failures_4[0],
        "square_25p3_failures": len(failures_25),
        "largest_square_ratio": max_square,
        "widest_literal_hole_run": max_hole,
        "guardrails": [record for record in records if record["source"] != "exhaustive" and (str(record["source"]).startswith("P") or str(record["source"]).startswith("doubled"))],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "guardrails"}, indent=2))


if __name__ == "__main__":
    main()
