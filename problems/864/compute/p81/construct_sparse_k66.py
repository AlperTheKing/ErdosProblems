#!/usr/bin/env python3
"""Construct a sparse exact Sidon outer K_6,6 with a parity literal hole."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "problems/864/compute/p81/sparse_k66_witness.json"


def odd_random(rng: random.Random, low: int, high: int) -> int:
    value = rng.randrange(low | 1, high, 2)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=86481)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    h = 10**15
    endpoint = h - 1
    result = None
    for attempt in range(1, args.attempts + 1):
        while True:
            left = sorted({odd_random(rng, 1, 10**7) for _ in range(6)})
            gaps = sorted({odd_random(rng, 2 * 10**7, 3 * 10**7) for _ in range(6)})
            if len(left) != 6 or len(gaps) != 6:
                continue
            inner_lengths = [a + q for a in left for q in gaps]
            if len(set(inner_lengths)) == 36:
                break
        right = sorted(h - q for q in gaps)
        edge_data = []
        inner_marks = []
        for a in left:
            for v in right:
                q = h - v
                length = a + q
                c = odd_random(rng, h // 4, h // 2 - 4 * 10**7)
                u = c + length
                inner_marks.extend((c, u))
                edge_data.append((a, v, c, u))
        values = sorted(set((*left, *right, *inner_marks, endpoint)))
        if len(values) != 85:
            continue
        differences = Counter(
            values[j] - values[i]
            for i in range(len(values))
            for j in range(i + 1, len(values))
        )
        if len(differences) != 85 * 84 // 2 or max(differences.values()) != 1:
            continue
        sums = Counter(
            values[i] + values[j]
            for i in range(len(values))
            for j in range(i, len(values))
        )
        if len(sums) != 85 * 86 // 2 or max(sums.values()) != 1:
            continue
        if not set(differences).isdisjoint({total + 1 for total in sums}):
            continue
        pair_for_difference = {
            values[j] - values[i]: (values[i], values[j])
            for i in range(len(values))
            for j in range(i + 1, len(values))
        }
        edges = []
        for a in left:
            for v in right:
                inner = pair_for_difference[h - (v - a)]
                if not (a <= inner[0] < inner[1] <= v):
                    raise AssertionError((a, v, inner))
                edges.append(
                    {
                        "outer_edge": [a, v],
                        "inner_edge": list(inner),
                        "low_sum": a + inner[0],
                        "high_sum": inner[1] + v,
                    }
                )
        if len(edges) != 36 or not all(
            edge["low_sum"] + h == edge["high_sum"] for edge in edges
        ):
            raise AssertionError("K6,6 verification")
        delta = (3 * 85 * 85 - 85 + 2) // 2 - h
        result = {
            "attempt": attempt,
            "p": 85,
            "h": h,
            "b": 1,
            "delta": delta,
            "positive_defect": delta > 0,
            "B": values,
            "left": left,
            "right": right,
            "sum_count": len(sums),
            "difference_count": len(differences),
            "literal_hole": True,
            "edges": edges,
        }
        break
    output = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "attempt_limit": args.attempts,
        "seed": args.seed,
        "found": result is not None,
        "witness": result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "found": result is not None,
                "attempt": None if result is None else result["attempt"],
                "delta": None if result is None else result["delta"],
            }
        )
    )


if __name__ == "__main__":
    main()
