#!/usr/bin/env python3
"""Scan every positive-defect hole center on retained q=167 K_5,5 cuts."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "problems/864/compute/p81/singer_q167_cut_scan_with_k55.json"
OUTPUT = ROOT / "problems/864/compute/p81/singer_q167_k55_all_centers.json"


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

    left_work = sum(math.comb(len(v), order) for v in adjacency.values() if len(v) >= order)
    right_work = sum(math.comb(len(v), order) for v in reverse.values() if len(v) >= order)
    if right_work <= left_work:
        found = search(reverse)
        if found is None:
            return None
        right, left = found
        return left, right
    return search(adjacency)


def exact_witness(
    normalized: list[int], h: int, b: int, left: list[int], right: list[int]
) -> dict:
    width = normalized[-1]
    gamma = h - width - 1
    values = [gamma + value for value in normalized]
    p = len(values)
    sums = Counter(
        values[i] + values[j]
        for i in range(p)
        for j in range(i, p)
    )
    differences = Counter(
        values[j] - values[i]
        for i in range(p)
        for j in range(i + 1, p)
    )
    assert len(sums) == p * (p + 1) // 2 and max(sums.values()) == 1
    assert len(differences) == p * (p - 1) // 2 and max(differences.values()) == 1
    assert set(differences).isdisjoint({total + b for total in sums})
    assert values[-1] == h - 1
    delta = (3 * p * p - p + 2) // 2 - h
    assert delta > 0
    difference_pairs = {
        values[j] - values[i]: (values[i], values[j])
        for i in range(p)
        for j in range(i + 1, p)
    }
    shifted_left = [gamma + value for value in left]
    shifted_right = [gamma + value for value in right]
    edges = []
    for outer_low in shifted_left:
        for outer_high in shifted_right:
            inner = difference_pairs[h - (outer_high - outer_low)]
            assert outer_low <= inner[0] < inner[1] <= outer_high
            edges.append(
                {
                    "outer_edge": [outer_low, outer_high],
                    "inner_edge": list(inner),
                    "low_sum": outer_low + inner[0],
                    "high_sum": inner[1] + outer_high,
                }
            )
    assert len(edges) == 36
    assert all(edge["low_sum"] + h == edge["high_sum"] for edge in edges)
    return {
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "B": values,
        "left": shifted_left,
        "right": shifted_right,
        "edges": edges,
    }


def scan_record(record: dict) -> dict:
    original = tuple(int(value) for value in record["normalized"])
    width = original[-1]
    normalized = tuple(sorted(width - value for value in original))
    p = len(normalized)
    baseline = (3 * p * p - p + 2) // 2

    sum_bits = 0
    difference_pairs: dict[int, tuple[int, int]] = {}
    for i, low in enumerate(original):
        for high in original[i:]:
            sum_bits |= 1 << (low + high)
        for high in original[i + 1 :]:
            difference_pairs[high - low] = (low, high)
    forbidden = 0
    for difference in difference_pairs:
        forbidden |= sum_bits << difference

    values = np.asarray(normalized, dtype=np.int64)
    low_list = []
    high_list = []
    length_list = []
    for i, low in enumerate(normalized):
        for high in normalized[i + 1 :]:
            low_list.append(low)
            high_list.append(high)
            length_list.append(high - low)
    outer_low = np.asarray(low_list, dtype=np.int64)
    outer_high = np.asarray(high_list, dtype=np.int64)
    outer_length = np.asarray(length_list, dtype=np.int64)
    inner_low_by_length = np.full(width + 1, -1, dtype=np.int64)
    inner_high_by_length = np.full(width + 1, -1, dtype=np.int64)
    for difference, (low, high) in difference_pairs.items():
        reflected_low = width - high
        reflected_high = width - low
        inner_low_by_length[difference] = reflected_low
        inner_high_by_length[difference] = reflected_high

    hole_shifts = 0
    k55_shifts = 0
    max_edges = 0
    witness = None
    for h in range(width + 1, baseline):
        b = None
        if not ((forbidden >> (2 * h - 1)) & 1):
            b = 1
        elif not ((forbidden >> (2 * h)) & 1):
            b = 2
        if b is None:
            continue
        hole_shifts += 1
        target = h - outer_length
        in_range = (target > 0) & (target <= width)
        safe_target = np.clip(target, 0, width)
        inner_low = inner_low_by_length[safe_target]
        inner_high = inner_high_by_length[safe_target]
        mask = (
            in_range
            & (inner_low >= outer_low)
            & (inner_high <= outer_high)
        )
        edge_lows = outer_low[mask].tolist()
        edge_highs = outer_high[mask].tolist()
        max_edges = max(max_edges, len(edge_lows))
        adjacency: dict[int, set[int]] = {}
        for low, high in zip(edge_lows, edge_highs):
            adjacency.setdefault(low, set()).add(high)
        if find_krr(adjacency, 5) is not None:
            k55_shifts += 1
        found = find_krr(adjacency, 6)
        if found is not None:
            left, right = found
            witness = exact_witness(list(normalized), h, b, left, right)
            break

    return {
        "affine_multiplier": record["affine_multiplier"],
        "cut_base": record["cut_base"],
        "width": width,
        "hole_shifts_scanned": hole_shifts,
        "K5_5_shifts": k55_shifts,
        "max_outer_edges": max_edges,
        "K6_6_found": witness is not None,
        "witness": witness,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    records = data["K5_5_records"]
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(scan_record, records))
    witnesses = [result["witness"] for result in results if result["witness"] is not None]
    output = {
        "schema_version": 1,
        "arithmetic": "exact integer hole bitsets and integer biclique enumeration; NumPy only vectorizes exact integer lookups",
        "source": args.source.resolve().relative_to(ROOT.resolve()).as_posix(),
        "retained_cuts": len(records),
        "workers": args.workers,
        "hole_shifts_scanned": sum(result["hole_shifts_scanned"] for result in results),
        "K5_5_shifts": sum(result["K5_5_shifts"] for result in results),
        "K6_6_found": bool(witnesses),
        "witness": None if not witnesses else witnesses[0],
        "results": results,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
