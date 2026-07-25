#!/usr/bin/env python3
"""
Finite SKTC-style probe for Erdos #30.

This is deliberately small and exact. It enumerates optimal Golomb rulers
for k <= max_k by increasing diameter, then computes a few spectral,
residue, interval, and difference-channel observables.

Claim ceiling:
  - useful for hypothesis screening and negative controls;
  - not evidence for the asymptotic Erdos #30 conjecture.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import itertools
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RulerMetrics:
    k: int
    diameter: int
    marks: list[int]
    pair_count: int
    pair_load: float
    slack_after_pigeonhole: int
    compression_delta_k2_minus_diameter: int
    max_mark_fourier_mod_diameter_plus_one: float
    max_difference_fourier_mod_diameter_plus_one: float
    max_residue_discrepancy_q_le_32: float
    max_interval_discrepancy: float


def is_golomb(marks: Iterable[int]) -> bool:
    seen: set[int] = set()
    values = list(marks)
    for i, a in enumerate(values):
        for b in values[:i]:
            d = a - b
            if d <= 0 or d in seen:
                return False
            seen.add(d)
    return True


def first_optimal_ruler(k: int) -> tuple[int, list[int]]:
    if k < 2:
        raise ValueError("k must be at least 2")

    lower = k * (k - 1) // 2
    for diameter in itertools.count(lower):
        interior_count = k - 2
        candidates = range(1, diameter)
        for interior in itertools.combinations(candidates, interior_count):
            marks = [0, *interior, diameter]
            if is_golomb(marks):
                return diameter, marks


def max_fourier(values: list[int], modulus: int) -> float:
    if not values or modulus <= 1:
        return 0.0
    denom = len(values)
    best = 0.0
    for r in range(1, modulus):
        z = sum(cmath.exp(2j * math.pi * r * v / modulus) for v in values)
        best = max(best, abs(z) / denom)
    return best


def positive_differences(marks: list[int]) -> list[int]:
    diffs: list[int] = []
    for i, a in enumerate(marks):
        for b in marks[:i]:
            diffs.append(a - b)
    return diffs


def max_residue_discrepancy(marks: list[int], q_max: int = 32) -> float:
    k = len(marks)
    best = 0.0
    for q in range(2, q_max + 1):
        counts = [0] * q
        for a in marks:
            counts[a % q] += 1
        expected = k / q
        best = max(best, max(abs(c - expected) for c in counts) / k)
    return best


def max_interval_discrepancy(marks: list[int], diameter: int) -> float:
    k = len(marks)
    universe = diameter + 1
    if universe <= 1:
        return 0.0
    lengths = sorted({1, 2, max(1, int(math.sqrt(universe))), max(1, universe // 4), max(1, universe // 2)})
    best = 0.0
    mark_set = set(marks)
    for length in lengths:
        if length > universe:
            continue
        expected = k * length / universe
        for start in range(0, universe - length + 1):
            count = sum(1 for x in range(start, start + length) if x in mark_set)
            best = max(best, abs(count - expected) / k)
    return best


def metrics_for(k: int) -> RulerMetrics:
    diameter, marks = first_optimal_ruler(k)
    pair_count = k * (k - 1) // 2
    diffs = positive_differences(marks)
    assert len(diffs) == pair_count
    assert len(set(diffs)) == pair_count
    modulus = diameter + 1
    return RulerMetrics(
        k=k,
        diameter=diameter,
        marks=marks,
        pair_count=pair_count,
        pair_load=pair_count / diameter,
        slack_after_pigeonhole=diameter - pair_count,
        compression_delta_k2_minus_diameter=k * k - diameter,
        max_mark_fourier_mod_diameter_plus_one=max_fourier(marks, modulus),
        max_difference_fourier_mod_diameter_plus_one=max_fourier(diffs, modulus),
        max_residue_discrepancy_q_le_32=max_residue_discrepancy(marks, min(32, modulus)),
        max_interval_discrepancy=max_interval_discrepancy(marks, diameter),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=8, help="exact enumeration limit; 8 is quick on a laptop")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.max_k > 9:
        raise SystemExit("This exact brute-force probe is intentionally capped at max_k <= 9.")

    rows = [metrics_for(k) for k in range(2, args.max_k + 1)]
    payload = {
        "probe": "erdos30_sktc_exact_small_k",
        "claim_ceiling": "hypothesis-screening only; not asymptotic theorem evidence",
        "max_k": args.max_k,
        "rows": [asdict(row) for row in rows],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.out.write_text(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    args.out.with_suffix(args.out.suffix + ".sha256").write_text(f"{sha}  {args.out.name}\n")
    print(f"Wrote {args.out}")
    print(f"sha256 {sha}")


if __name__ == "__main__":
    main()
