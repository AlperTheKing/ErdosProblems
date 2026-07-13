#!/usr/bin/env python3
"""Exact one-mark repair search for the 30-of-36 P75 outer rectangle."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "problems/864/compute/p81/p75_rectangle_repair.json"
P75_B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
    519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
]
H = 988


def difference_pairs(values: tuple[int, ...]) -> dict[int, tuple[int, int]] | None:
    pairs: dict[int, tuple[int, int]] = {}
    for i, low in enumerate(values):
        for high in values[i + 1 :]:
            difference = high - low
            if difference in pairs:
                return None
            pairs[difference] = (low, high)
    return pairs


def rectangle(
    values: tuple[int, ...], pairs: dict[int, tuple[int, int]]
) -> tuple[int, list[dict[str, object]], list[dict[str, object]]]:
    left = values[:6]
    right = values[-6:]
    edges = []
    missing = []
    for outer_low in left:
        for outer_high in right:
            target = H - (outer_high - outer_low)
            inner = pairs.get(target)
            if inner is None:
                missing.append(
                    {
                        "outer_edge": [outer_low, outer_high],
                        "target_inner_difference": target,
                        "reason": "difference absent",
                    }
                )
                continue
            inner_low, inner_high = inner
            if not (outer_low <= inner_low < inner_high <= outer_high):
                missing.append(
                    {
                        "outer_edge": [outer_low, outer_high],
                        "target_inner_difference": target,
                        "represented_pair": [inner_low, inner_high],
                        "reason": "representative not nested",
                    }
                )
                continue
            edges.append(
                {
                    "outer_edge": [outer_low, outer_high],
                    "inner_edge": [inner_low, inner_high],
                    "low_sum": outer_low + inner_low,
                    "high_sum": inner_high + outer_high,
                }
            )
    return len(edges), edges, missing


def exact_verify(values: tuple[int, ...], edges: list[dict[str, object]]) -> dict:
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
    assert values[-1] == H - 1
    assert len(sums) == p * (p + 1) // 2 and max(sums.values()) == 1
    assert len(differences) == p * (p - 1) // 2 and max(differences.values()) == 1
    assert set(differences).isdisjoint({total + 1 for total in sums})
    assert (3 * p * p - p + 2) // 2 - H == 14
    assert len(edges) == 36
    for edge in edges:
        assert edge["low_sum"] + H == edge["high_sum"]
    return {
        "p": p,
        "h": H,
        "b": 1,
        "delta": 14,
        "sum_count": len(sums),
        "difference_count": len(differences),
        "left": list(values[:6]),
        "right": list(values[-6:]),
        "edges": edges,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    current = tuple(P75_B)
    started = time.perf_counter()
    path = []
    total_neighbors = 0
    for step in range(args.steps + 1):
        pairs = difference_pairs(current)
        if pairs is None:
            raise AssertionError("current state is not Sidon")
        score, edges, missing = rectangle(current, pairs)
        path.append(
            {
                "step": step,
                "B": list(current),
                "rectangle_edges": score,
                "missing": missing,
            }
        )
        if score == 36 or step == args.steps:
            break

        occupied = set(current)
        candidates: dict[tuple[int, ...], int] = {}
        for removed in current[:-1]:
            remainder = occupied - {removed}
            for inserted in range(1, H - 1, 2):
                if inserted in remainder:
                    continue
                neighbor = tuple(sorted((*remainder, inserted)))
                if neighbor[-1] != H - 1:
                    continue
                neighbor_pairs = difference_pairs(neighbor)
                if neighbor_pairs is None:
                    continue
                neighbor_score, _, _ = rectangle(neighbor, neighbor_pairs)
                candidates[neighbor] = neighbor_score
        total_neighbors += len(candidates)
        if not candidates:
            break
        best_score = max(candidates.values())
        if best_score <= score:
            path[-1]["local_maximum"] = True
            path[-1]["best_neighbor_score"] = best_score
            break
        current = min(state for state, value in candidates.items() if value == best_score)

    final_pairs = difference_pairs(current)
    if final_pairs is None:
        raise AssertionError("final state is not Sidon")
    final_score, final_edges, final_missing = rectangle(current, final_pairs)
    witness = exact_verify(current, final_edges) if final_score == 36 else None
    output = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "domain": "best-improvement one-mark replacements, odd marks in [1,987], endpoint 987",
        "initial_score": path[0]["rectangle_edges"],
        "final_score": final_score,
        "final_missing": final_missing,
        "distinct_valid_neighbors_examined": total_neighbors,
        "path": path,
        "K6_6_found": witness is not None,
        "witness": witness,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "initial_score": output["initial_score"],
                "final_score": final_score,
                "valid_neighbors": total_neighbors,
                "steps": len(path) - 1,
                "K6_6_found": witness is not None,
                "elapsed_seconds": output["elapsed_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
