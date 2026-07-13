#!/usr/bin/env python3
"""Exact neighborhood audit for reflected holes Z intersect (G+3Z)=empty."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "problems/864/compute/p20/results/samples.jsonl"
P45 = ROOT / "problems/864/compute/p45/audit_signed_carry_identity.py"
P46 = ROOT / "problems/864/compute/p46/carry_statistics.py"
OUTPUT = ROOT / "problems/864/compute/p68/hole_neighborhoods.json"


def load_p45():
    spec = importlib.util.spec_from_file_location("p45_for_p68", P45)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P45 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_p46():
    spec = importlib.util.spec_from_file_location("p46_for_p68", P46)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P46 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def support_bits(values: list[int]) -> int:
    out = 0
    for value in values:
        out |= 1 << value
    return out


def reverse_low_bits(bits: int, length: int) -> int:
    if length <= 0:
        return 0
    return int(f"{bits & ((1 << length) - 1):0{length}b}"[::-1], 2)


def difference_from_triples(z: list[int]) -> int:
    points = support_bits(z)
    pair_sums = 0
    for value in z:
        pair_sums |= points << value
    triple_sums = 0
    for value in z:
        triple_sums |= pair_sums << value
    shifts = 0
    for value in z:
        shifts |= reverse_low_bits(triple_sums, value + 1)
    return shifts


def neighborhood(shifts: int, gap: int, width: int) -> dict[str, int | None]:
    lower_bits = shifts & ((1 << gap) - 1)
    previous = lower_bits.bit_length() - 1 if lower_bits else None
    upper_bits = shifts >> (gap + 1)
    next_offset = (upper_bits & -upper_bits).bit_length() - 1 if upper_bits else None
    following = None if next_offset is None else gap + 1 + next_offset
    left_radius = gap if previous is None else gap - previous - 1
    right_radius = width - gap if following is None else following - gap - 1
    return {
        "previous_represented_shift": previous,
        "next_represented_shift": following,
        "left_hole_radius": left_radius,
        "right_hole_radius": right_radius,
        "contiguous_hole_length": left_radius + 1 + right_radius,
    }


def audit_row(row: dict, p45) -> dict[str, object] | None:
    params = p45.reflected_parameters(row)
    if params is None:
        return None
    values, h, b = params
    gamma = min(values)
    z = [value - gamma for value in values]
    p = len(z)
    width = z[-1]
    gap = 2 * gamma + b
    baseline = (3 * p * p - p + 2) // 2
    delta = baseline - h
    shifts = difference_from_triples(z)
    if (shifts >> gap) & 1:
        raise AssertionError("the certified literal hole is represented")
    if p <= 12:
        brute = {
            z4 - z1 - z2 - z3
            for z4 in z
            for z1 in z
            for z2 in z
            for z3 in z
            if z4 >= z1 + z2 + z3
        }
        if shifts != support_bits(sorted(brute)):
            raise AssertionError("bitset support disagrees with brute force")

    local = neighborhood(shifts, gap, width)
    return {
        "sample_id": row["sample_id"],
        "kind": row["kind"],
        "p": p,
        "h": h,
        "b": b,
        "gamma": gamma,
        "G": gap,
        "W": width,
        "delta": delta,
        **local,
        "shift_support_size": shifts.bit_count(),
    }


def exhaustive_small(max_width: int, p46) -> dict[str, object]:
    holes = 0
    hard_holes = 0
    failures = []
    widest = None
    rulers = 0
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            rulers += 1
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            z = sorted(width - value for value in ruler)
            shifts = difference_from_triples(z)
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    center = 2 * width + 2 * gamma + b
                    if center in forbidden:
                        continue
                    holes += 1
                    gap = 2 * gamma + b
                    if (shifts >> gap) & 1:
                        raise AssertionError("P46 hole and Z-3Z support disagree")
                    if gap > width:
                        continue
                    hard_holes += 1
                    local = neighborhood(shifts, gap, width)
                    rec = {
                        "p": p,
                        "width": width,
                        "ruler": list(ruler),
                        "b": b,
                        "gamma": gamma,
                        "G": gap,
                        **local,
                    }
                    if widest is None or int(rec["contiguous_hole_length"]) > int(widest["contiguous_hole_length"]):
                        widest = rec
                    if int(rec["contiguous_hole_length"]) >= 3:
                        failures.append(rec)
    return {
        "max_width": max_width,
        "sidon_rulers": rulers,
        "positive_delta_holes": holes,
        "nontrivial_holes_G_le_W": hard_holes,
        "three_consecutive_hole_failures": len(failures),
        "first_failure": None if not failures else failures[0],
        "widest_hole": widest,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=0)
    args = parser.parse_args()
    p45 = load_p45()
    rows = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        rec = audit_row(json.loads(line), p45)
        if rec is not None and int(rec["delta"]) > 0 and int(rec["G"]) <= int(rec["W"]):
            rows.append(rec)
    if not rows:
        raise AssertionError("no hard reflected profiles")
    widest = max(rows, key=lambda r: (int(r["contiguous_hole_length"]), int(r["p"])))
    normalized = max(
        rows,
        key=lambda r: (
            int(r["contiguous_hole_length"]) ** 2 * 1_000_000
            // int(r["p"]) ** 4
        ),
    )
    result = {
        "arithmetic": "exact integer bitsets",
        "hard_profiles": len(rows),
        "widest_hole": widest,
        "largest_hole_length_over_p2": normalized,
        "rows": rows,
    }
    if args.max_width:
        result["exhaustive"] = exhaustive_small(args.max_width, load_p46())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({k: result[k] for k in result if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
