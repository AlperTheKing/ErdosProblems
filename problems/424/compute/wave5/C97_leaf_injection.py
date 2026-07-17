#!/usr/bin/env python3
"""Exact Hall audit for the C97 healed derivation-leaf map.

This is a root-labelled map audit, not an event-amortization census.  For a
hole n, its complete missing-factor leaf support is the union of the
structural splitless leaves reached through every currently missing factor
in every admissible factorization.  A hard root h may target a leaf e only
after the literal seed-2 chain of e has reached the least generated closure.
"""

from __future__ import annotations

import argparse
import json
from array import array
from functools import lru_cache
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
OTHER_HOLE = 4


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    p = 2
    while p * p <= limit:
        if spf[p] == p:
            for multiple in range(p * p, limit + 1, p):
                if spf[multiple] == multiple:
                    spf[multiple] = p
        p += 1
    return spf


def divisors(value: int, spf: array) -> list[int]:
    factors: list[tuple[int, int]] = []
    while value > 1:
        p = int(spf[value])
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        factors.append((p, exponent))
    result = [1]
    for p, exponent in factors:
        old = list(result)
        power = 1
        for _ in range(exponent):
            power *= p
            result.extend(d * power for d in old)
    return result


def admissible_pairs(n: int, spf: array) -> tuple[tuple[int, int], ...]:
    product = n + 1
    result = []
    for left in divisors(product, spf):
        if left < 2:
            continue
        right = product // left
        if left >= right:
            continue
        if allowed(left) and allowed(right):
            result.append((left, right))
    return tuple(sorted(result))


def hard_shape(n: int, pairs: tuple[tuple[int, int], ...]) -> bool:
    if n % 2 or not pairs:
        return False
    product = n + 1
    if product % 3:
        return True
    cofactor = product // 3
    return not allowed(cofactor) or cofactor == 3


def root_of_odd(value: int) -> int:
    shifted = value - 1
    return (shifted >> ((shifted & -shifted).bit_length() - 1)) + 1


def literal_chain(root: int, limit: int) -> list[int]:
    result = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def maximum_matching(
    sources: list[int], adjacency: dict[int, tuple[int, ...]]
) -> tuple[int, dict[int, int]]:
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

    matched = sum(augment(source, set()) for source in sources)
    return matched, target_to_source


def audit(limit: int) -> dict:
    require(limit >= 5_633, "limit must be at least 5633")
    spf = smallest_prime_factors(limit + 1)
    state = bytearray(limit + 1)
    pairs_by_value: list[tuple[tuple[int, int], ...]] = [tuple() for _ in range(limit + 1)]
    hard_roots: list[int] = []
    splitless_roots: list[int] = []
    hard_death: dict[int, int] = {}
    splitless_heal: dict[int, int] = {}
    first_generation_pairs: dict[int, tuple[tuple[int, int], ...]] = {}

    for n in range(2, limit + 1):
        current = OTHER
        pairs: tuple[tuple[int, int], ...] = tuple()
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif hard_shape(n, pairs):
                current = HARD
            else:
                current = OTHER_HOLE
        state[n] = current
        pairs_by_value[n] = pairs

        if current == HARD:
            require(n % 2 == 0, f"odd hard root {n}")
            hard_roots.append(n)
        elif current == SPLITLESS:
            require(n % 2 == 0, f"odd splitless root {n}")
            splitless_roots.append(n)

        if n > 3 and n % 2 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of_odd(n)
                if state[root] == HARD:
                    require(root not in hard_death, f"duplicate hard death for {root}")
                    hard_death[root] = n
                elif state[root] == SPLITLESS:
                    require(root not in splitless_heal, f"duplicate splitless heal for {root}")
                    splitless_heal[root] = n
                    first_generation_pairs[root] = tuple(
                        pair
                        for pair in pairs
                        if state[pair[0]] == GENERATED and state[pair[1]] == GENERATED
                    )

    @lru_cache(maxsize=None)
    def leaf_support(value: int) -> tuple[int, ...]:
        require(state[value] != GENERATED, f"leaf support requested for generated {value}")
        if state[value] == SPLITLESS:
            return (value,)
        leaves: set[int] = set()
        for left, right in pairs_by_value[value]:
            if state[left] != GENERATED:
                leaves.update(leaf_support(left))
            if state[right] != GENERATED:
                leaves.update(leaf_support(right))
        require(leaves, f"reducible hole {value} has empty leaf support")
        return tuple(sorted(leaves))

    first_failure = None
    cutoffs_checked = 0
    for cutoff in range(2, limit + 1):
        young = [
            root
            for root in hard_roots
            if cutoff // 4 < root <= cutoff and hard_death.get(root, limit + 1) > cutoff
        ]
        adjacency = {
            root: tuple(
                leaf
                for leaf in leaf_support(root)
                if splitless_heal.get(leaf, limit + 1) <= cutoff
            )
            for root in young
        }
        matching_size, target_to_source = maximum_matching(young, adjacency)
        cutoffs_checked += 1
        if matching_size + 1 < len(young):
            first_failure = {
                "X": cutoff,
                "floor_X_over_4": cutoff // 4,
                "young_persistent_hard_roots": young,
                "healed_splitless_roots": [
                    root for root in splitless_roots if splitless_heal.get(root, limit + 1) <= cutoff
                ],
                "leaf_support": {str(root): list(leaf_support(root)) for root in young},
                "eligible_healed_leaves": {str(root): list(adjacency[root]) for root in young},
                "maximum_matching": sorted(
                    ({"source": source, "target": target} for target, source in target_to_source.items()),
                    key=lambda row: (row["source"], row["target"]),
                ),
                "matching_number": matching_size,
                "singleton_exception_capacity": 1,
                "total_leaf_local_capacity": matching_size + 1,
                "source_count": len(young),
                "deficit_after_exception": len(young) - matching_size - 1,
            }
            break

    require(first_failure is not None, "no healed-leaf Hall obstruction found")
    require(first_failure["X"] == 114, "first obstruction is no longer X=114")
    require(first_failure["young_persistent_hard_roots"] == [54, 74, 114], "source set changed")
    require(first_failure["healed_splitless_roots"] == [6, 18, 20], "D(114) set changed")
    require(first_failure["matching_number"] == 1, "matching number at X=114 changed")

    witness_roots = [54, 74, 114]
    witness_leaves = sorted({leaf for root in witness_roots for leaf in leaf_support(root)})
    leaf_certificates = {}
    for leaf in witness_leaves:
        heal = splitless_heal.get(leaf)
        require(heal is not None, f"witness leaf {leaf} does not heal by limit")
        leaf_certificates[str(leaf)] = {
            "first_generated_chain_member": heal,
            "chain_through_first_generation": literal_chain(leaf, heal),
            "first_generation_pairs": [list(pair) for pair in first_generation_pairs[leaf]],
        }

    active_at_114 = [
        root for root in hard_roots if root <= 114 and hard_death.get(root, limit + 1) > 114
    ]
    active_at_28 = [
        root for root in hard_roots if root <= 28 and hard_death.get(root, limit + 1) > 28
    ]
    healed_at_114 = [
        root for root in splitless_roots if splitless_heal.get(root, limit + 1) <= 114
    ]
    require(active_at_114 == [54, 74, 114], "A_H(114) mismatch")
    require(active_at_28 == [], "A_H(28) mismatch")
    require(healed_at_114 == [6, 18, 20], "D(114) mismatch")

    source_leaf_union = {leaf for root in witness_roots for leaf in leaf_support(root)}
    bank_certificates = {
        str(root): {
            "first_generated_chain_member": splitless_heal[root],
            "chain_through_first_generation": literal_chain(root, splitless_heal[root]),
            "first_generation_pairs": [list(pair) for pair in first_generation_pairs[root]],
            "in_any_source_leaf_support": root in source_leaf_union,
        }
        for root in healed_at_114
    }

    return {
        "schema": "C97-healed-leaf-hall-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "definitions": {
            "source": "hard roots h with floor(X/4)<h<=X whose literal chain is ungenerated through X",
            "target": "structural splitless leaf e in the complete missing-factor support of h whose chain has healed by X",
            "exception": "one unlabelled unit target",
        },
        "audit": {
            "integer_cutoffs_checked_through_first_failure": cutoffs_checked,
            "no_earlier_failure": True,
            "first_failure": first_failure,
        },
        "scalar_gate_at_114": {
            "A_H_114": len(active_at_114),
            "D_114": len(healed_at_114),
            "A_H_floor_114_over_4": len(active_at_28),
            "right_minus_left_with_plus_one": len(healed_at_114) + len(active_at_28) + 1 - len(active_at_114),
        },
        "source_certificates": {
            str(root): {
                "admissible_pairs": [list(pair) for pair in pairs_by_value[root]],
                "complete_missing_factor_leaf_support": list(leaf_support(root)),
            }
            for root in witness_roots
        },
        "healed_bank_certificates_at_114": bank_certificates,
        "leaf_certificates": leaf_certificates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
