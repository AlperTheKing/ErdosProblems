#!/usr/bin/env python3
"""Independent recursive verifier for the C97 healed-leaf obstruction."""

from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


@lru_cache(maxsize=None)
def pairs(n: int) -> tuple[tuple[int, int], ...]:
    if not allowed(n):
        return tuple()
    product = n + 1
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return tuple(result)


@lru_cache(maxsize=None)
def generated(n: int) -> bool:
    if n in (2, 3):
        return True
    if not allowed(n):
        return False
    return any(generated(left) and generated(right) for left, right in pairs(n))


def splitless(n: int) -> bool:
    return allowed(n) and n not in (2, 3) and not pairs(n)


def hard_root(n: int) -> bool:
    if n % 2 or generated(n) or not pairs(n):
        return False
    product = n + 1
    if product % 3:
        return True
    cofactor = product // 3
    return not allowed(cofactor) or cofactor == 3


def chain(root: int, limit: int) -> list[int]:
    result = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def first_generated(root: int, limit: int) -> int | None:
    return next((value for value in chain(root, limit) if generated(value)), None)


@lru_cache(maxsize=None)
def leaf_support(value: int) -> tuple[int, ...]:
    require(not generated(value), f"generated value {value} has no missing-factor support")
    if splitless(value):
        return (value,)
    leaves: set[int] = set()
    for left, right in pairs(value):
        if not generated(left):
            leaves.update(leaf_support(left))
        if not generated(right):
            leaves.update(leaf_support(right))
    require(leaves, f"reducible hole {value} has no leaf")
    return tuple(sorted(leaves))


def maximum_matching(sources: list[int], adjacency: dict[int, tuple[int, ...]]) -> int:
    target_to_source: dict[int, int] = {}

    def augment(source: int, seen: set[int]) -> bool:
        for target in adjacency[source]:
            if target in seen:
                continue
            seen.add(target)
            owner = target_to_source.get(target)
            if owner is None or augment(owner, seen):
                target_to_source[target] = source
                return True
        return False

    return sum(augment(source, set()) for source in sources)


def persistent_hard_roots(cutoff: int) -> list[int]:
    result = []
    for root in range(2, cutoff + 1, 2):
        if hard_root(root) and first_generated(root, cutoff) is None:
            result.append(root)
    return result


def healed_splitless_roots(cutoff: int) -> list[int]:
    return [
        root
        for root in range(2, cutoff + 1, 2)
        if splitless(root) and first_generated(root, cutoff) is not None
    ]


def leaf_matching_at(cutoff: int) -> tuple[list[int], list[int], dict[int, tuple[int, ...]], int]:
    persistent = persistent_hard_roots(cutoff)
    young = [root for root in persistent if root > cutoff // 4]
    healed = healed_splitless_roots(cutoff)
    healed_set = set(healed)
    adjacency = {
        root: tuple(leaf for leaf in leaf_support(root) if leaf in healed_set)
        for root in young
    }
    return young, healed, adjacency, maximum_matching(young, adjacency)


def verify(claim_path: Path) -> dict:
    claim = json.loads(claim_path.read_text(encoding="ascii"))
    require(claim["schema"] == "C97-healed-leaf-hall-v1", "wrong claim schema")

    expected_pairs = {
        54: ((5, 11),),
        74: ((5, 15),),
        114: ((5, 23),),
    }
    expected_leaves = {54: (6,), 74: (8,), 114: (8, 12)}
    for root in (54, 74, 114):
        require(hard_root(root), f"{root} is not an exact hard root")
        require(pairs(root) == expected_pairs[root], f"factor pairs changed for {root}")
        require(leaf_support(root) == expected_leaves[root], f"leaf support changed for {root}")

    first_heals = {6: 41, 8: 449, 12: 5_633}
    for root, death in first_heals.items():
        require(splitless(root), f"{root} is not splitless")
        require(first_generated(root, death - 1) is None, f"{root} heals before {death}")
        require(first_generated(root, death) == death, f"{root} does not first heal at {death}")

    bank_heals = {6: (41, ((3, 14),)), 18: (69, ((5, 14),)), 20: (77, ((3, 26),))}
    source_leaf_union = {6, 8, 12}
    for root, (death, certificates) in bank_heals.items():
        require(splitless(root), f"bank root {root} is not splitless")
        require(first_generated(root, death - 1) is None, f"bank root {root} heals early")
        require(first_generated(root, death) == death, f"bank root {root} heal mismatch")
        actual = tuple(pair for pair in pairs(death) if generated(pair[0]) and generated(pair[1]))
        require(actual == certificates, f"bank root {root} generation certificate mismatch")

    first_failure = None
    for cutoff in range(2, 115):
        young, healed, adjacency, matching = leaf_matching_at(cutoff)
        if matching + 1 < len(young):
            first_failure = {
                "X": cutoff,
                "young": young,
                "healed": healed,
                "adjacency": {str(root): list(targets) for root, targets in adjacency.items()},
                "matching_number": matching,
            }
            break

    require(first_failure is not None and first_failure["X"] == 114, "X=114 is not first failure")
    require(first_failure["young"] == [54, 74, 114], "young source set mismatch")
    require(first_failure["healed"] == [6, 18, 20], "D(114) target set mismatch")
    require(first_failure["adjacency"] == {"54": [6], "74": [], "114": []}, "adjacency mismatch")
    require(first_failure["matching_number"] == 1, "matching number mismatch")
    require(persistent_hard_roots(28) == [], "A_H(28) is nonempty")

    saved = claim["audit"]["first_failure"]
    require(saved["X"] == first_failure["X"], "saved cutoff mismatch")
    require(saved["young_persistent_hard_roots"] == first_failure["young"], "saved sources mismatch")
    require(saved["healed_splitless_roots"] == first_failure["healed"], "saved healed set mismatch")
    require(saved["eligible_healed_leaves"] == first_failure["adjacency"], "saved adjacency mismatch")
    require(saved["matching_number"] == first_failure["matching_number"], "saved matching mismatch")
    saved_bank = claim["healed_bank_certificates_at_114"]
    for root, (death, certificates) in bank_heals.items():
        row = saved_bank[str(root)]
        require(row["first_generated_chain_member"] == death, f"saved bank death mismatch for {root}")
        require(row["first_generation_pairs"] == [list(pair) for pair in certificates], f"saved bank pair mismatch for {root}")
        require(row["in_any_source_leaf_support"] == (root in source_leaf_union), f"saved incidence mismatch for {root}")

    return {
        "schema": "C97-healed-leaf-hall-verifier-v1",
        "claim": str(claim_path).replace("\\", "/"),
        "status": "exact_match",
        "integer_cutoffs_checked": 113,
        "first_failure_X": 114,
        "young_sources": first_failure["young"],
        "D_114": first_failure["healed"],
        "matching_number": first_failure["matching_number"],
        "deficit_after_singleton": 1,
        "recursive_values_evaluated": generated.cache_info().currsize,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.claim)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
