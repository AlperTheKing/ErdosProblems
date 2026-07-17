#!/usr/bin/env python3
"""Scan natural missing-factor matching graphs at every small cutoff."""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from pathlib import Path


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(product: int) -> list[tuple[int, int]]:
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def build_closure(limit: int) -> tuple[
    set[int],
    list[int],
    dict[int, list[int]],
    dict[int, list[int]],
]:
    generated = {2, 3}
    reducible = []
    direct_missing: dict[int, list[int]] = {}
    transitive_shadow: dict[int, list[int]] = {}
    for n in range(4, limit + 1):
        pairs = admissible_pairs(n + 1)
        if any(left in generated and right in generated for left, right in pairs):
            generated.add(n)
            continue
        if not allowed(n) or not pairs:
            continue

        missing = sorted(
            {
                endpoint
                for left, right in pairs
                for endpoint in (left, right)
                if endpoint not in generated
            }
        )
        if not missing:
            raise AssertionError(f"reducible hole {n} has no missing endpoint")
        shadow = set(missing)
        for endpoint in missing:
            shadow.update(transitive_shadow.get(endpoint, ()))
        reducible.append(n)
        direct_missing[n] = missing
        transitive_shadow[n] = sorted(shadow)
    return generated, reducible, direct_missing, transitive_shadow


def maximum_matching(
    left_values: list[int],
    adjacency: dict[int, list[tuple[str, int]]],
) -> tuple[dict[int, tuple[str, int]], dict[tuple[str, int], int]]:
    pair_left: dict[int, tuple[str, int]] = {}
    pair_right: dict[tuple[str, int], int] = {}

    def augment(left: int, seen: set[tuple[str, int]]) -> bool:
        for right in adjacency[left]:
            if right in seen:
                continue
            seen.add(right)
            mate = pair_right.get(right)
            if mate is None or augment(mate, seen):
                pair_left[left] = right
                pair_right[right] = left
                return True
        return False

    for left in left_values:
        augment(left, set())
    return pair_left, pair_right


def hall_witness(
    left_values: list[int],
    adjacency: dict[int, list[tuple[str, int]]],
    pair_left: dict[int, tuple[str, int]],
    pair_right: dict[tuple[str, int], int],
) -> dict[str, object]:
    reachable_left = {left for left in left_values if left not in pair_left}
    reachable_right: set[tuple[str, int]] = set()
    queue = deque(sorted(reachable_left))
    while queue:
        left = queue.popleft()
        for right in adjacency[left]:
            if pair_left.get(left) == right or right in reachable_right:
                continue
            reachable_right.add(right)
            mate = pair_right.get(right)
            if mate is not None and mate not in reachable_left:
                reachable_left.add(mate)
                queue.append(mate)

    neighbor_union = {
        right for left in reachable_left for right in adjacency[left]
    }
    if neighbor_union != reachable_right:
        raise AssertionError("alternating witness is not its full neighborhood")
    deficit = len(reachable_left) - len(reachable_right)
    if deficit <= 0:
        raise AssertionError("alternating witness has no Hall deficit")
    return {
        "left_count": len(reachable_left),
        "neighbor_count": len(reachable_right),
        "deficit": deficit,
        "left_values": sorted(reachable_left),
        "neighbor_values": [
            {"copy": copy, "hole": hole}
            for copy, hole in sorted(reachable_right)
        ],
    }


def graph_at(
    cutoff: int,
    reducible: list[int],
    candidates: dict[int, list[int]],
    copies: int,
) -> tuple[list[int], dict[int, list[tuple[str, int]]]]:
    half = (cutoff + 1) // 2
    third = (cutoff + 1) // 3
    left_values = [value for value in reducible if value <= cutoff]
    adjacency: dict[int, list[tuple[str, int]]] = {}
    for left in left_values:
        neighbors = [
            ("half", hole)
            for hole in candidates[left]
            if hole <= half
        ]
        if copies == 2:
            neighbors.extend(
                ("third", hole)
                for hole in candidates[left]
                if hole <= third
            )
        adjacency[left] = sorted(set(neighbors))
    return left_values, adjacency


def scan_variant(
    name: str,
    limit: int,
    reducible: list[int],
    candidates: dict[int, list[int]],
    copies: int,
) -> dict[str, object]:
    for cutoff in range(4, limit + 1):
        left_values, adjacency = graph_at(
            cutoff, reducible, candidates, copies
        )
        pair_left, pair_right = maximum_matching(left_values, adjacency)
        if len(pair_left) == len(left_values):
            continue
        return {
            "name": name,
            "cutoffs_verified_before_failure": cutoff - 4,
            "first_failure_cutoff": cutoff,
            "left_count": len(left_values),
            "matching_size": len(pair_left),
            "total_deficit": len(left_values) - len(pair_left),
            "hall_witness": hall_witness(
                left_values, adjacency, pair_left, pair_right
            ),
        }
    return {
        "name": name,
        "cutoffs_verified_before_failure": limit - 3,
        "first_failure_cutoff": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 600:
        raise SystemExit("--limit must be at least 600")

    generated, reducible, direct, shadow = build_closure(args.limit)
    least = {value: [neighbors[0]] for value, neighbors in direct.items()}
    variants = [
        scan_variant(
            "direct missing endpoints, one half-scale copy",
            args.limit,
            reducible,
            direct,
            1,
        ),
        scan_variant(
            "least missing endpoint, half-plus-third copies",
            args.limit,
            reducible,
            least,
            2,
        ),
        scan_variant(
            "all direct missing endpoints, half-plus-third copies",
            args.limit,
            reducible,
            direct,
            2,
        ),
        scan_variant(
            "transitive missing-endpoint shadow, half-plus-third copies",
            args.limit,
            reducible,
            shadow,
            2,
        ),
    ]
    result = {
        "schema_version": 1,
        "limit": args.limit,
        "method": (
            "trial-division least closure; exact augmenting-path maximum "
            "matching and alternating-path Hall witness at every cutoff"
        ),
        "generated_count": len(generated),
        "reducible_count": len(reducible),
        "variants": variants,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    for row in variants:
        print(
            f"{row['name']}: first_failure={row['first_failure_cutoff']}"
        )


if __name__ == "__main__":
    main()
