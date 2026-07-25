#!/usr/bin/env python3
"""
Erdos #30 SKTC v2 multiscale probe.

This probe extends the first small-k run by:
  - exact all-optimal-ruler enumeration through a bounded k range;
  - centered interval, residue, Bohr-cell, and tensor observables;
  - greedy/random Sidon controls and random non-Sidon negative controls.

Claim ceiling:
  - finite hypothesis screening and obstruction search only;
  - not evidence for the asymptotic Erdos #30 conjecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True)
class SearchReceipt:
    k: int
    diameter: int
    canonical_optimal_ruler_count: int
    search_nodes: int
    seconds: float
    optimality_verified_by_exhausting_smaller_diameters: bool


@dataclass(frozen=True)
class ObservableRecord:
    family: str
    k: int
    diameter: int
    marks: list[int]
    is_golomb: bool
    collision_certificate_accepts: bool
    pair_count: int
    pair_load: float
    slack_after_pigeonhole: int
    compression_delta_k2_minus_diameter: int
    max_collision_multiplicity: int
    repeated_difference_count: int
    centered_dyadic_interval_discrepancy: dict[str, Any]
    centered_prime_power_residue_discrepancy: dict[str, Any]
    centered_bohr_cell_discrepancy: dict[str, Any]
    centered_difference_histogram_l2: float
    incidence_tensor_spectral_norm: float
    centered_incidence_tensor_spectral_norm: float
    centered_incidence_tensor_spectral_norm_over_sqrt_pairs: float


def canonical_ruler(marks: list[int]) -> tuple[int, ...]:
    diameter = marks[-1]
    reversed_marks = tuple(diameter - x for x in reversed(marks))
    return min(tuple(marks), reversed_marks)


def difference_counts(marks: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for i, a in enumerate(marks):
        for b in marks[:i]:
            d = a - b
            counts[d] = counts.get(d, 0) + 1
    return counts


def is_golomb(marks: Iterable[int]) -> bool:
    counts = difference_counts(list(marks))
    return all(count == 1 for count in counts.values())


def enumerate_fixed_diameter(
    k: int,
    diameter: int,
    *,
    stop_after_first: bool = False,
) -> tuple[list[list[int]], int]:
    rulers: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    nodes = 0
    marks = [0]
    used_diffs: set[int] = set()

    def rec(start: int, remaining_interior: int) -> None:
        nonlocal nodes
        nodes += 1
        if stop_after_first and rulers:
            return
        if remaining_interior == 0:
            new_diffs: list[int] = []
            for a in marks:
                d = diameter - a
                if d <= 0 or d in used_diffs or d in new_diffs:
                    return
                new_diffs.append(d)
            key = canonical_ruler(marks + [diameter])
            if key not in seen:
                seen.add(key)
                rulers.append(list(key))
            return

        max_x = diameter - remaining_interior
        for x in range(start, max_x + 1):
            if stop_after_first and rulers:
                return
            new_diffs = []
            ok = True
            for a in marks:
                d = x - a
                if d <= 0 or d in used_diffs or d in new_diffs:
                    ok = False
                    break
                new_diffs.append(d)
            if not ok:
                continue

            marks.append(x)
            used_diffs.update(new_diffs)
            rec(x + 1, remaining_interior - 1)
            for d in new_diffs:
                used_diffs.remove(d)
            marks.pop()

    rec(1, k - 2)
    return rulers, nodes


def all_optimal_rulers(k: int) -> tuple[list[list[int]], SearchReceipt]:
    if k < 2:
        raise ValueError("k must be at least 2")
    lower = k * (k - 1) // 2
    started = time.perf_counter()
    search_nodes = 0

    for diameter in range(lower, max(2 * k * k, lower + 1)):
        first, nodes = enumerate_fixed_diameter(k, diameter, stop_after_first=True)
        search_nodes += nodes
        if not first:
            continue
        all_rulers, nodes = enumerate_fixed_diameter(k, diameter, stop_after_first=False)
        search_nodes += nodes
        elapsed = time.perf_counter() - started
        receipt = SearchReceipt(
            k=k,
            diameter=diameter,
            canonical_optimal_ruler_count=len(all_rulers),
            search_nodes=search_nodes,
            seconds=elapsed,
            optimality_verified_by_exhausting_smaller_diameters=True,
        )
        return all_rulers, receipt

    raise RuntimeError(f"no ruler found for k={k}")


def greedy_sidonic_ruler(k: int) -> list[int]:
    marks = [0]
    x = 1
    while len(marks) < k:
        candidate = marks + [x]
        if is_golomb(candidate):
            marks.append(x)
        x += 1
    return marks


def random_sidon_controls(
    k: int,
    max_diameter: int,
    sample_count: int,
    rng: random.Random,
    attempts: int,
) -> list[list[int]]:
    controls: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    for _ in range(attempts):
        marks = [0]
        used_diffs: set[int] = set()
        candidates = list(range(1, max_diameter + 1))
        rng.shuffle(candidates)
        for x in candidates:
            new_diffs = []
            ok = True
            for a in marks:
                d = abs(x - a)
                if d == 0 or d in used_diffs or d in new_diffs:
                    ok = False
                    break
                new_diffs.append(d)
            if ok:
                marks.append(x)
                marks.sort()
                used_diffs = set(difference_counts(marks))
            if len(marks) == k:
                key = canonical_ruler(marks)
                if key not in seen:
                    seen.add(key)
                    controls.append(list(key))
                break
        if len(controls) >= sample_count:
            break
    return controls


def random_non_sidon_controls(
    k: int,
    diameter: int,
    sample_count: int,
    rng: random.Random,
    attempts: int,
) -> list[list[int]]:
    controls: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    if diameter + 1 < k:
        return controls
    for _ in range(attempts):
        interior = rng.sample(range(1, diameter), k - 2) if k > 2 else []
        marks = [0, *sorted(interior), diameter]
        if is_golomb(marks):
            continue
        key = canonical_ruler(marks)
        if key in seen:
            continue
        seen.add(key)
        controls.append(list(key))
        if len(controls) >= sample_count:
            break
    return controls


def dyadic_lengths(universe: int) -> list[int]:
    lengths = []
    value = 1
    while value <= universe:
        lengths.append(value)
        value *= 2
    if lengths[-1] != universe:
        lengths.append(universe)
    return lengths


def centered_dyadic_interval_discrepancy(marks: list[int], diameter: int) -> dict[str, Any]:
    k = len(marks)
    universe = diameter + 1
    density = k / universe
    mark_set = set(marks)
    best: dict[str, Any] = {
        "value": 0.0,
        "start": 0,
        "length": 0,
        "count": 0,
        "expected": 0.0,
    }
    for length in dyadic_lengths(universe):
        for start in range(0, universe - length + 1):
            count = sum(1 for x in range(start, start + length) if x in mark_set)
            expected = density * length
            value = abs(count - expected) / k
            if value > best["value"]:
                best = {
                    "value": value,
                    "start": start,
                    "length": length,
                    "count": count,
                    "expected": expected,
                }
    return best


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    r = int(math.sqrt(n))
    for p in range(3, r + 1, 2):
        if n % p == 0:
            return False
    return True


def prime_powers_up_to(n: int) -> list[int]:
    values: set[int] = set()
    for p in range(2, n + 1):
        if not is_prime(p):
            continue
        value = p
        while value <= n:
            values.add(value)
            value *= p
    return sorted(values)


def centered_prime_power_residue_discrepancy(marks: list[int], diameter: int, max_q: int) -> dict[str, Any]:
    k = len(marks)
    universe = diameter + 1
    q_values = prime_powers_up_to(max(2, min(max_q, universe)))
    best: dict[str, Any] = {
        "value": 0.0,
        "q": 0,
        "residue": 0,
        "count": 0,
        "expected": 0.0,
    }
    for q in q_values:
        counts = [0] * q
        for a in marks:
            counts[a % q] += 1
        expected = k / q
        for residue, count in enumerate(counts):
            value = abs(count - expected) / k
            if value > best["value"]:
                best = {
                    "value": value,
                    "q": q,
                    "residue": residue,
                    "count": count,
                    "expected": expected,
                }
    return best


def circular_distance_to_zero(x: int, q: int) -> int:
    x %= q
    return min(x, q - x)


def centered_bohr_cell_discrepancy(marks: list[int], diameter: int, max_q: int) -> dict[str, Any]:
    k = len(marks)
    universe = diameter + 1
    q_values = prime_powers_up_to(max(2, min(max_q, universe)))
    best: dict[str, Any] = {
        "value": 0.0,
        "q": 0,
        "frequency": 0,
        "radius": 0,
        "cell_size": 0,
        "count": 0,
        "expected": 0.0,
    }
    for q in q_values:
        radii = sorted({0, max(1, q // 8), max(1, q // 4)})
        for frequency in range(1, q):
            if math.gcd(frequency, q) != 1:
                continue
            phases = [(frequency * a) % q for a in marks]
            for radius in radii:
                cell_size = sum(1 for residue in range(q) if circular_distance_to_zero(residue, q) <= radius)
                count = sum(1 for phase in phases if circular_distance_to_zero(phase, q) <= radius)
                expected = k * cell_size / q
                value = abs(count - expected) / k
                if value > best["value"]:
                    best = {
                        "value": value,
                        "q": q,
                        "frequency": frequency,
                        "radius": radius,
                        "cell_size": cell_size,
                        "count": count,
                        "expected": expected,
                    }
    return best


def tensor_spectral_metrics(marks: list[int], diameter: int) -> tuple[float, float, float]:
    universe = diameter + 1
    mark_set = set(marks)
    density = len(marks) / universe
    raw = np.zeros((universe, max(1, diameter)), dtype=float)
    centered = np.zeros((universe, max(1, diameter)), dtype=float)
    for d in range(1, diameter + 1):
        col = d - 1
        for x in range(0, universe - d):
            value = 1.0 if x in mark_set and x + d in mark_set else 0.0
            raw[x, col] = value
            centered[x, col] = value - density * density
    raw_norm = float(np.linalg.svd(raw, compute_uv=False)[0]) if raw.size else 0.0
    centered_norm = float(np.linalg.svd(centered, compute_uv=False)[0]) if centered.size else 0.0
    pair_count = len(marks) * (len(marks) - 1) // 2
    normalized = centered_norm / max(1.0, math.sqrt(pair_count))
    return raw_norm, centered_norm, normalized


def centered_difference_histogram_l2(marks: list[int], diameter: int) -> float:
    if diameter <= 0:
        return 0.0
    counts = difference_counts(marks)
    pair_count = len(marks) * (len(marks) - 1) // 2
    expected = pair_count / diameter
    squared = 0.0
    for d in range(1, diameter + 1):
        squared += (counts.get(d, 0) - expected) ** 2
    return math.sqrt(squared / diameter) / max(1.0, math.sqrt(pair_count))


def observable_record(family: str, marks: list[int], max_q: int) -> ObservableRecord:
    marks = sorted(marks)
    diameter = marks[-1]
    k = len(marks)
    pair_count = k * (k - 1) // 2
    counts = difference_counts(marks)
    max_collision = max(counts.values(), default=0)
    repeated = sum(max(0, count - 1) for count in counts.values())
    raw_norm, centered_norm, normalized_norm = tensor_spectral_metrics(marks, diameter)
    return ObservableRecord(
        family=family,
        k=k,
        diameter=diameter,
        marks=marks,
        is_golomb=max_collision <= 1,
        collision_certificate_accepts=max_collision <= 1,
        pair_count=pair_count,
        pair_load=pair_count / diameter if diameter else 0.0,
        slack_after_pigeonhole=diameter - pair_count,
        compression_delta_k2_minus_diameter=k * k - diameter,
        max_collision_multiplicity=max_collision,
        repeated_difference_count=repeated,
        centered_dyadic_interval_discrepancy=centered_dyadic_interval_discrepancy(marks, diameter),
        centered_prime_power_residue_discrepancy=centered_prime_power_residue_discrepancy(marks, diameter, max_q),
        centered_bohr_cell_discrepancy=centered_bohr_cell_discrepancy(marks, diameter, max_q),
        centered_difference_histogram_l2=centered_difference_histogram_l2(marks, diameter),
        incidence_tensor_spectral_norm=raw_norm,
        centered_incidence_tensor_spectral_norm=centered_norm,
        centered_incidence_tensor_spectral_norm_over_sqrt_pairs=normalized_norm,
    )


def aggregate(records: list[ObservableRecord]) -> dict[str, Any]:
    if not records:
        return {}
    fields = [
        "centered_difference_histogram_l2",
        "centered_incidence_tensor_spectral_norm_over_sqrt_pairs",
        "pair_load",
        "compression_delta_k2_minus_diameter",
    ]
    out: dict[str, Any] = {"count": len(records)}
    for field in fields:
        values = [float(getattr(record, field)) for record in records]
        out[field] = {
            "min": min(values),
            "mean": sum(values) / len(values),
            "max": max(values),
        }
    nested_fields = [
        ("centered_dyadic_interval_discrepancy", "dyadic_interval"),
        ("centered_prime_power_residue_discrepancy", "prime_power_residue"),
        ("centered_bohr_cell_discrepancy", "bohr_cell"),
    ]
    for attr, name in nested_fields:
        values = [float(getattr(record, attr)["value"]) for record in records]
        out[name] = {
            "min": min(values),
            "mean": sum(values) / len(values),
            "max": max(values),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=10)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260502)
    parser.add_argument("--control-samples", type=int, default=3)
    parser.add_argument("--control-attempts", type=int, default=2000)
    parser.add_argument("--max-q", type=int, default=64)
    args = parser.parse_args()

    if args.max_k > 10:
        raise SystemExit("Local exact all-optimal enumeration is capped at max_k <= 10 for this probe.")

    rng = random.Random(args.seed)
    receipts: list[SearchReceipt] = []
    records: list[ObservableRecord] = []

    for k in range(2, args.max_k + 1):
        optimal_rulers, receipt = all_optimal_rulers(k)
        receipts.append(receipt)
        for marks in optimal_rulers:
            records.append(observable_record("exact_canonical_optimal", marks, args.max_q))

        greedy = greedy_sidonic_ruler(k)
        records.append(observable_record("greedy_sidon_control", greedy, args.max_q))

        sidon_controls = random_sidon_controls(
            k,
            max_diameter=max(receipt.diameter * 2, greedy[-1]),
            sample_count=args.control_samples,
            rng=rng,
            attempts=args.control_attempts,
        )
        for marks in sidon_controls:
            records.append(observable_record("random_sidon_control", marks, args.max_q))

        non_sidon_controls = random_non_sidon_controls(
            k,
            diameter=receipt.diameter,
            sample_count=args.control_samples,
            rng=rng,
            attempts=args.control_attempts,
        )
        for marks in non_sidon_controls:
            records.append(observable_record("random_non_sidon_negative_control", marks, args.max_q))

    by_family: dict[str, list[ObservableRecord]] = {}
    by_k_family: dict[str, list[ObservableRecord]] = {}
    for record in records:
        by_family.setdefault(record.family, []).append(record)
        by_k_family.setdefault(f"k={record.k}:{record.family}", []).append(record)

    payload = {
        "probe": "erdos30_sktc_multiscale_v2",
        "claim_ceiling": "finite hypothesis screening and obstruction search only; not asymptotic theorem evidence",
        "seed": args.seed,
        "max_k": args.max_k,
        "max_q": args.max_q,
        "control_samples": args.control_samples,
        "search_receipts": [asdict(receipt) for receipt in receipts],
        "aggregate_by_family": {family: aggregate(items) for family, items in sorted(by_family.items())},
        "aggregate_by_k_family": {key: aggregate(items) for key, items in sorted(by_k_family.items())},
        "records": [asdict(record) for record in records],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.out.write_text(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    args.out.with_suffix(args.out.suffix + ".sha256").write_text(f"{sha}  {args.out}\n")
    print(f"Wrote {args.out}")
    print(f"sha256 {sha}")


if __name__ == "__main__":
    main()
