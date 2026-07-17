#!/usr/bin/env python3
"""Independent recursive verifier for the C98 lower-quarter certificate."""

from __future__ import annotations

import argparse
import json
import math
from functools import cache
from pathlib import Path


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


@cache
def pairs(n: int) -> tuple[tuple[int, int], ...]:
    result = []
    product = n + 1
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return tuple(result)


@cache
def generated(n: int) -> bool:
    if n in (2, 3):
        return True
    if not allowed(n):
        return False
    return any(generated(a) and generated(b) for a, b in pairs(n))


def hard_shape(n: int) -> bool:
    ps = pairs(n)
    if n % 2 or not ps:
        return False
    product = n + 1
    if product % 3:
        return True
    parent = product // 3
    return not allowed(parent) or parent == 3


def hard_root(n: int) -> bool:
    return allowed(n) and hard_shape(n) and not generated(n)


def splitless_root(n: int) -> bool:
    return n >= 4 and n % 2 == 0 and allowed(n) and not pairs(n)


def chain(root: int, limit: int) -> list[int]:
    result = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def first_generated(root: int, limit: int) -> int | None:
    for value in chain(root, limit):
        if generated(value):
            return value
    return None


def active_hard(cutoff: int) -> list[int]:
    return [
        root for root in range(4, cutoff + 1, 2)
        if hard_root(root) and first_generated(root, cutoff) is None
    ]


def healed_splitless(cutoff: int) -> list[int]:
    # A splitless root e>cutoff/2 has no seed-2 child visible by cutoff.
    return [
        root for root in range(4, cutoff // 2 + 1, 2)
        if splitless_root(root) and first_generated(root, cutoff) is not None
    ]


def roots_from_details(rows: list[dict]) -> list[int]:
    return [row["root"] for row in rows]


def verify_witness(claim: dict, y: int, key: str) -> dict:
    witness = claim[key]
    require(witness["Y"] == y and witness["X"] == 4 * y, (key, "cutoff"))
    expected_hard = active_hard(y)
    expected_supply = healed_splitless(4 * y)
    actual_hard = roots_from_details(witness["hard_roots"])
    actual_supply = sorted(
        roots_from_details(witness["downward_supply"])
        + roots_from_details(witness["fresh_upper_supply"])
    )
    require(actual_hard == expected_hard, (key, "hard", actual_hard, expected_hard))
    require(actual_supply == expected_supply,
            (key, "supply", actual_supply, expected_supply))
    for row in witness["downward_supply"] + witness["fresh_upper_supply"]:
        root = row["root"]
        require(first_generated(root, 4 * y) == row["first_generated"],
                (key, "death", root))
        a, b = row["generating_pair"]
        require((a, b) in pairs(row["first_generated"]),
                (key, "pair", root, a, b))
        require(generated(a) and generated(b), (key, "generated-pair", root))
    return {
        "Y": y,
        "A_H_Y": len(expected_hard),
        "D_4Y": len(expected_supply),
    }


def verify_local_counterexample(claim: dict) -> dict:
    local = claim["prime_support_local_counterexample"]
    supplies = healed_splitless(216)
    require(active_hard(54) == [54], "first hard source changed")
    require(pairs(54) == ((5, 11),) and generated(5) and not generated(11),
            "54 descent changed")
    require(pairs(11) == ((2, 6),) and generated(2) and splitless_root(6),
            "11 descent changed")
    require(supplies == [6, 18, 20, 38, 66], ("D216", supplies))
    radical = math.prod(local["prime_support"])
    neighbors = [root for root in supplies if math.gcd(root + 1, radical) > 1]
    require(neighbors == local["support_local_neighbors"] == [6, 20, 38],
            ("neighbors", neighbors))
    require(2 * len(neighbors) == 6 < 7, "support capacity is not deficient")
    require(first_generated(24, 216) is None, "shadow 24 healed by 216")
    require(first_generated(120, 216) is None, "shadow 120 healed by 216")
    return {
        "Y": 54,
        "D_216": supplies,
        "support_neighbors": neighbors,
        "capacity": 2 * len(neighbors),
        "demand": 7,
    }


def verify_hall(claim: dict) -> dict:
    hall = claim["tight_root_labelled_Hall_instance"]
    y = hall["Y"]
    sources = active_hard(y)
    supplies = healed_splitless(4 * y)
    require(sources == hall["active_hard_roots"], "Hall source list mismatch")
    require(supplies == hall["healed_splitless_roots"], "Hall supply list mismatch")

    minimum = None
    for index, source in enumerate(sources, 1):
        available = sum(root <= 2 * source for root in supplies)
        margin = 2 * available - 7 * index
        row = (margin, index, source, available)
        if minimum is None or row[0] < minimum[0]:
            minimum = row
    require(minimum is not None and minimum[0] == 9, ("prefix-minimum", minimum))

    used: set[tuple[int, int]] = set()
    require(len(hall["greedy_assignment"]) == len(sources), "assignment length")
    for source, row in zip(sources, hall["greedy_assignment"], strict=True):
        require(row["hard_root"] == source and len(row["slots"]) == 7,
                ("assignment-row", source))
        for root, copy in row["slots"]:
            slot = (root, copy)
            require(root in supplies and copy in (0, 1), ("invalid-slot", slot))
            require(root <= 2 * source, ("nonlocal-slot", source, slot))
            require(slot not in used, ("reused-slot", slot))
            used.add(slot)
    require(len(used) == 7 * len(sources) == 609, ("used-slots", len(used)))
    all_slots = {(root, copy) for root in supplies for copy in (0, 1)}
    unused = {tuple(slot) for slot in hall["unused_slots"]}
    require(all_slots - used == unused and len(unused) == 9,
            ("unused-slots", len(unused)))
    return {
        "Y": y,
        "sources": len(sources),
        "supplies": len(supplies),
        "used_slots": len(used),
        "unused_slots": len(unused),
        "minimum_prefix_margin": minimum[0],
    }


def verify(claim_path: Path) -> dict:
    claim = json.loads(claim_path.read_text(encoding="ascii"))
    require(claim["schema"] == "C98-lower-quarter-hall-v1", "wrong schema")
    local = verify_local_counterexample(claim)
    downward = verify_witness(claim, 174, "first_downward_only_counterexample")
    hall = verify_hall(claim)
    require(downward == {"Y": 174, "A_H_Y": 5, "D_4Y": 25}, downward)
    require(hall["sources"] == 87 and hall["supplies"] == 309, hall)
    return {
        "schema": "C98-lower-quarter-independent-v1",
        "claim": str(claim_path).replace("\\", "/"),
        "status": "exact_match",
        "local_counterexample": local,
        "downward_counterexample": downward,
        "Hall_instance": hall,
        "recursive_generated_values": generated.cache_info().currsize,
        "trial_division_pair_tables": pairs.cache_info().currsize,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.claim)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
