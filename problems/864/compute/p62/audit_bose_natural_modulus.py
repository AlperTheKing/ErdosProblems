#!/usr/bin/env python3
"""Exact Bose-Chowla carry audit at the natural modulus h=q^2-1."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ALGEBRA = ROOT / "problems/864/compute/p12/algebraic_scan.py"
OUTPUT = ROOT / "problems/864/compute/p62/bose_natural_modulus.json"


def load_algebra():
    spec = importlib.util.spec_from_file_location("p12_algebra", ALGEBRA)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load algebraic_scan.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bitset(values: set[int]) -> int:
    out = 0
    for value in values:
        out |= 1 << value
    return out


def audit_lift(values: tuple[int, ...], h: int) -> dict[str, object]:
    z = tuple(sorted(values))
    if not z or z[0] != 0:
        raise AssertionError("lift is not endpoint normalized")
    p = len(z)
    width = z[-1]
    gamma = h - width - 1
    if gamma < 0:
        raise AssertionError("lift span exceeds natural modulus")

    sums: dict[int, int] = {}
    for i, left in enumerate(z):
        for right in z[i:]:
            total = left + right
            if total in sums:
                raise AssertionError("integer Sidon failure")
            sums[total] = 1 if left == right else 2
    differences = {
        z[j] - z[i] for i in range(p) for j in range(i + 1, p)
    }
    if len(differences) != p * (p - 1) // 2:
        raise AssertionError("positive difference collision")

    sum_bits = bitset(set(sums))
    difference_bits = bitset(differences)
    folded = sum_bits & (sum_bits >> h)
    cs = folded.bit_count()
    cd = 0
    cursor = folded
    while cursor:
        low_bit = cursor & -cursor
        low_sum = low_bit.bit_length() - 1
        cd += sums[low_sum] * sums[low_sum + h]
        cursor ^= low_bit

    valid_b = []
    for b in (1, 2):
        gap = 2 * gamma + b
        if not (difference_bits & (sum_bits << gap)):
            valid_b.append(b)
    return {
        "width": width,
        "gamma": gamma,
        "sum_collisions": cs,
        "difference_collisions": cd,
        "valid_b": valid_b,
        "points": list(z),
    }


def audit_parameter(algebra, q: int) -> dict[str, object]:
    modulus, residues, _ = algebra.bose_chowla(q)
    seen: set[tuple[int, ...]] = set()
    valid = []
    zero_fold_valid = []
    collision_hist: dict[str, int] = {}
    for unit in algebra.unit_multipliers(modulus, None):
        transformed = tuple((unit * x) % modulus for x in residues)
        for lift, base, cut_gap in algebra.cyclic_lifts(transformed, modulus):
            if lift in seen:
                continue
            seen.add(lift)
            row = audit_lift(lift, modulus)
            key = f"{row['sum_collisions']},{row['difference_collisions']}"
            collision_hist[key] = collision_hist.get(key, 0) + 1
            if row["valid_b"]:
                rec = {
                    **row,
                    "unit": unit,
                    "base": base,
                    "cut_gap": cut_gap,
                }
                valid.append(rec)
                if row["sum_collisions"] == 0 and row["difference_collisions"] == 0:
                    zero_fold_valid.append(rec)
    p = len(residues)
    baseline = (3 * p * p - p + 2) // 2
    return {
        "q": q,
        "p": p,
        "modulus": modulus,
        "delta_at_natural_modulus": baseline - modulus,
        "unit_classes": len(algebra.unit_multipliers(modulus, None)),
        "distinct_lifts": len(seen),
        "valid_lifts": len(valid),
        "zero_fold_valid_lifts": len(zero_fold_valid),
        "collision_histogram": collision_hist,
        "first_valid": None if not valid else valid[0],
        "first_zero_fold_valid": None if not zero_fold_valid else zero_fold_valid[0],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    algebra = load_algebra()
    rows = []
    for q in args.parameters:
        row = audit_parameter(algebra, q)
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if not k.startswith("first_")}, sort_keys=True))
    result = {
        "arithmetic": "exact integers and finite fields",
        "parameters": args.parameters,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
