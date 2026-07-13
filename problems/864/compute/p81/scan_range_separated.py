#!/usr/bin/env python3
"""Scan Singer cuts at the automatic range-separated literal-hole shift."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from scan_singer_cuts import cyclic_lifts, find_krr, outer_graph, unit_multipliers


ROOT = Path(__file__).resolve().parents[4]


def verify_witness(
    normalized: tuple[int, ...], h: int, b: int, left: list[int], right: list[int]
) -> dict:
    gamma = h - normalized[-1] - 1
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
    pairs = {
        values[j] - values[i]: (values[i], values[j])
        for i in range(p)
        for j in range(i + 1, p)
    }
    shifted_left = [gamma + value for value in left]
    shifted_right = [gamma + value for value in right]
    edges = []
    for outer_low in shifted_left:
        for outer_high in shifted_right:
            inner = pairs[h - (outer_high - outer_low)]
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--unit-limit", type=int, default=128)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.source.read_text(encoding="utf-8").splitlines()[0])
    modulus = int(record["modulus"])
    residues = tuple(int(value) for value in record["residues"])
    units = unit_multipliers(modulus, args.unit_limit)
    p = len(residues)
    baseline = (3 * p * p - p + 2) // 2
    started = time.perf_counter()
    seen = set()
    cuts = 0
    positive_defect_cuts = 0
    k55_cuts = 0
    max_edges = 0
    witness = None
    for multiplier in units:
        transformed = tuple((multiplier * value) % modulus for value in residues)
        for lift, cut_base, cut_gap in cyclic_lifts(transformed, modulus):
            if lift in seen:
                continue
            seen.add(lift)
            cuts += 1
            width = lift[-1]
            gamma = width // 2 + 1
            h = width + gamma + 1
            if h >= baseline:
                continue
            positive_defect_cuts += 1
            differences = {}
            for i, low in enumerate(lift):
                for high in lift[i + 1 :]:
                    difference = high - low
                    if difference in differences:
                        raise AssertionError("non-Sidon Singer lift")
                    differences[difference] = (low, high)
            adjacency, labels = outer_graph(lift, h, differences)
            max_edges = max(max_edges, len(labels))
            if find_krr(adjacency, 5) is not None:
                k55_cuts += 1
            found = find_krr(adjacency, 6)
            if found is not None:
                left, right = found
                witness = {
                    "affine_multiplier": multiplier,
                    "cut_base": cut_base,
                    "cut_gap": cut_gap,
                    **verify_witness(lift, h, 1, left, right),
                }
                break
        if witness is not None:
            break
    output = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "domain": "Singer cyclic cuts at gamma=floor(width/2)+1",
        "source": args.source.resolve().relative_to(ROOT.resolve()).as_posix(),
        "p": p,
        "unit_classes_scanned": len(units),
        "distinct_cuts_scanned": cuts,
        "positive_defect_cuts": positive_defect_cuts,
        "K5_5_cuts": k55_cuts,
        "max_outer_edges": max_edges,
        "K6_6_found": witness is not None,
        "witness": witness,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
