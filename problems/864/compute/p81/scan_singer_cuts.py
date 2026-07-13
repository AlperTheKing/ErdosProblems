#!/usr/bin/env python3
"""Exact K_6,6 scan over cyclic cuts of a stored Singer difference set."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SOURCE = ROOT / "problems/864/compute/p12/singer_sample_q151.jsonl"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p81/singer_q151_cut_scan.json"


def unit_multipliers(modulus: int, limit: int | None) -> list[int]:
    units = [u for u in range(1, modulus) if math.gcd(u, modulus) == 1]
    units = [u for u in units if u <= (-u) % modulus]
    if limit is None or limit >= len(units):
        return units
    if limit < 1:
        return []
    if limit == 1:
        return [units[0]]
    indices = sorted(
        {round(i * (len(units) - 1) / (limit - 1)) for i in range(limit)}
    )
    return [units[i] for i in indices]


def cyclic_lifts(
    residues: Sequence[int], modulus: int
) -> Iterable[tuple[tuple[int, ...], int, int]]:
    values = tuple(sorted(residues))
    for index, base in enumerate(values):
        previous = values[index - 1]
        gap = (base - previous) % modulus
        lift = tuple(sorted((value - base) % modulus for value in values))
        yield lift, base, gap


def sum_and_difference_data(
    values: Sequence[int],
) -> tuple[int, dict[int, tuple[int, int]]]:
    sum_bits = 0
    sums: set[int] = set()
    differences: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in sums:
                raise AssertionError(("repeated sum", total))
            sums.add(total)
            sum_bits |= 1 << total
        for right in values[i + 1 :]:
            difference = right - left
            if difference in differences:
                raise AssertionError(("repeated difference", difference))
            differences[difference] = (left, right)
    return sum_bits, differences


def first_hole_center(
    sum_bits: int,
    differences: Iterable[int],
    low: int,
    high: int,
) -> int | None:
    if low > high:
        return None
    forbidden = 0
    for difference in differences:
        forbidden |= sum_bits << difference
    for center in range(low, high + 1):
        if not ((forbidden >> center) & 1):
            return center
    return None


def outer_graph(
    values: Sequence[int], h: int, differences: dict[int, tuple[int, int]]
) -> tuple[dict[int, set[int]], dict[tuple[int, int], tuple[int, int]]]:
    adjacency: dict[int, set[int]] = {}
    labels: dict[tuple[int, int], tuple[int, int]] = {}
    for i, outer_low in enumerate(values):
        for outer_high in values[i + 1 :]:
            inner_length = h - (outer_high - outer_low)
            inner = differences.get(inner_length)
            if inner is None:
                continue
            inner_low, inner_high = inner
            if not (outer_low <= inner_low < inner_high <= outer_high):
                continue
            if outer_low + inner_low + h != inner_high + outer_high:
                raise AssertionError(("fold equation", outer_low, outer_high, inner, h))
            if not (2 * outer_low < h <= 2 * outer_high):
                raise AssertionError(("outer bipartition", outer_low, outer_high, h))
            adjacency.setdefault(outer_low, set()).add(outer_high)
            labels[(outer_low, outer_high)] = inner
    return adjacency, labels


def find_krr(adjacency: dict[int, set[int]], order: int) -> tuple[list[int], list[int]] | None:
    reverse: dict[int, set[int]] = {}
    for left, neighbors in adjacency.items():
        for right in neighbors:
            reverse.setdefault(right, set()).add(left)

    def search(side: dict[int, set[int]]) -> tuple[list[int], list[int]] | None:
        counts: Counter[tuple[int, ...]] = Counter()
        witnesses: dict[tuple[int, ...], list[int]] = {}
        for vertex, neighbors in sorted(side.items()):
            if len(neighbors) < order:
                continue
            for subset in itertools.combinations(sorted(neighbors), order):
                counts[subset] += 1
                witnesses.setdefault(subset, []).append(vertex)
                if counts[subset] >= order:
                    return list(witnesses[subset][:order]), list(subset)
        return None

    left_choice = sum(math.comb(len(v), order) for v in adjacency.values() if len(v) >= order)
    right_choice = sum(math.comb(len(v), order) for v in reverse.values() if len(v) >= order)
    if right_choice <= left_choice:
        found = search(reverse)
        if found is None:
            return None
        right, left = found
        return left, right
    return search(adjacency)


def witness_record(
    source: Path,
    multiplier: int,
    cut_base: int,
    cut_gap: int,
    normalized: Sequence[int],
    center: int,
    left: Sequence[int],
    right: Sequence[int],
    labels: dict[tuple[int, int], tuple[int, int]],
) -> dict[str, object]:
    p = len(normalized)
    width = normalized[-1]
    b = 1 if center % 2 else 2
    gamma = (center - 2 * width - b) // 2
    h = gamma + width + 1
    values = [gamma + value for value in normalized]
    shifted_left = [gamma + value for value in left]
    shifted_right = [gamma + value for value in right]
    edges = []
    for outer_low in left:
        for outer_high in right:
            inner_low, inner_high = labels[(outer_low, outer_high)]
            edges.append(
                {
                    "outer_edge": [gamma + outer_low, gamma + outer_high],
                    "inner_edge": [gamma + inner_low, gamma + inner_high],
                    "low_sum": 2 * gamma + outer_low + inner_low,
                    "high_sum": 2 * gamma + inner_high + outer_high,
                }
            )
    return {
        "source": source.resolve().relative_to(ROOT.resolve()).as_posix(),
        "affine_multiplier": multiplier,
        "cut_base": cut_base,
        "cut_gap": cut_gap,
        "center": center,
        "p": p,
        "h": h,
        "b": b,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "B": values,
        "left": shifted_left,
        "right": shifted_right,
        "edges": edges,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--unit-limit", type=int, default=32)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source = args.source.resolve()
    record = json.loads(source.read_text(encoding="utf-8").splitlines()[0])
    modulus = int(record["modulus"])
    residues = tuple(int(value) for value in record["residues"])
    units = unit_multipliers(modulus, args.unit_limit)
    selected_unit_classes = len(units)
    if not (1 <= args.shard_count and 0 <= args.shard_index < args.shard_count):
        raise ValueError("invalid shard")
    units = units[args.shard_index :: args.shard_count]
    p = len(residues)
    baseline = (3 * p * p - p + 2) // 2
    maximum_center = 2 * baseline - 3

    started = time.perf_counter()
    seen: set[tuple[int, ...]] = set()
    cuts = 0
    positive_hole_cuts = 0
    k55_cuts = 0
    k55_records = []
    max_edges = 0
    max_degree = 0
    witness = None
    for multiplier in units:
        transformed = tuple((multiplier * value) % modulus for value in residues)
        for lift, cut_base, cut_gap in cyclic_lifts(transformed, modulus):
            if lift in seen:
                continue
            seen.add(lift)
            cuts += 1
            sum_bits, differences = sum_and_difference_data(lift)
            center = first_hole_center(
                sum_bits, differences, 2 * lift[-1] + 1, maximum_center
            )
            if center is None:
                continue
            b = 1 if center % 2 else 2
            gamma = (center - 2 * lift[-1] - b) // 2
            h = gamma + lift[-1] + 1
            if gamma < 0 or baseline - h <= 0:
                raise AssertionError(("positive defect range", center, gamma, h))
            positive_hole_cuts += 1
            adjacency, labels = outer_graph(lift, h, differences)
            max_edges = max(max_edges, len(labels))
            max_degree = max(max_degree, *(map(len, adjacency.values()) or [0]))
            k55 = find_krr(adjacency, 5)
            if k55 is not None:
                k55_cuts += 1
                k55_records.append(
                    {
                        "affine_multiplier": multiplier,
                        "cut_base": cut_base,
                        "cut_gap": cut_gap,
                        "center": center,
                        "normalized": list(lift),
                        "left": k55[0],
                        "right": k55[1],
                    }
                )
            found = find_krr(adjacency, 6)
            if found is not None:
                left, right = found
                witness = witness_record(
                    source,
                    multiplier,
                    cut_base,
                    cut_gap,
                    lift,
                    center,
                    left,
                    right,
                    labels,
                )
                break
        if witness is not None:
            break

    output = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "domain": "all cyclic cuts from the selected deterministic Singer unit classes; first positive-defect literal-hole center per cut",
        "source": source.relative_to(ROOT).as_posix(),
        "modulus": modulus,
        "p": p,
        "unit_limit": args.unit_limit,
        "selected_unit_classes_before_sharding": selected_unit_classes,
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "unit_classes_scanned": len(units),
        "distinct_cuts_scanned": cuts,
        "positive_hole_cuts": positive_hole_cuts,
        "K5_5_cuts": k55_cuts,
        "K5_5_records": k55_records,
        "max_outer_edges": max_edges,
        "max_left_degree": max_degree,
        "K6_6_found": witness is not None,
        "witness": witness,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
