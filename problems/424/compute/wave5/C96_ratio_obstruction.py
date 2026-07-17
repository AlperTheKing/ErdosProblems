#!/usr/bin/env python3
"""Exact C96 audit for the common-bank scale comparisons.

This program independently reconstructs the least closure, classifies every
even structural root, and checks the two no-error quarter-scale inequalities.
It also emits finite witnesses showing why structural class membership and the
canonical prime-square shadow do not by themselves control the *healed* bank.
All acceptance decisions use integer arithmetic.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter
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


def factorization(value: int, spf: array) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    while value > 1:
        p = int(spf[value])
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        result.append((p, exponent))
    return result


def divisors_from_factors(factors: list[tuple[int, int]]) -> list[int]:
    divisors = [1]
    for p, exponent in factors:
        old = list(divisors)
        power = 1
        for _ in range(exponent):
            power *= p
            divisors.extend(d * power for d in old)
    return divisors


def admissible_pairs(product: int, spf: array) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for left in divisors_from_factors(factorization(product, spf)):
        if left < 2:
            continue
        right = product // left
        if left >= right:
            continue
        if allowed(left) and allowed(right):
            pairs.append((left, right))
    pairs.sort()
    return pairs


def splitless_class(product: int, spf: array) -> str | None:
    """The arithmetic class from the C74 classification, including N=3."""
    factors = factorization(product, spf)
    if product % 3 != 0:
        minus = [(p, e) for p, e in factors if p % 3 == 2]
        if not minus:
            return "plus_semigroup"
        if len(factors) == 1 and minus == [(factors[0][0], 2)]:
            return "minus_prime_square"
        return None

    v3 = next((e for p, e in factors if p == 3), 0)
    if product == 9:
        return "square_3"
    if v3 == 1 and all(p == 3 or p % 3 == 1 for p, _ in factors):
        return "three_times_plus_semigroup"
    return None


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 != 0 or not pairs:
        return False
    product = n + 1
    if product % 3 != 0:
        return True
    cofactor = product // 3
    return not allowed(cofactor) or cofactor == 3


def root_of_odd(value: int) -> int:
    odd_part = value - 1
    while odd_part % 2 == 0:
        odd_part //= 2
    return odd_part + 1


def literal_chain(root: int, limit: int) -> list[int]:
    result: list[int] = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def audit(limit: int) -> dict:
    require(limit >= 1_000_000, "limit must be at least 1000000")
    spf = smallest_prime_factors(limit + 1)
    state = bytearray(limit + 1)
    active_history = array("I", [0]) * (limit + 1)

    active_hard = 0
    healed_splitless = 0
    splitless_classes: Counter[str] = Counter()
    healed_classes: Counter[str] = Counter()
    hard_shape_count = 0
    first_death: dict[int, int] = {}

    scale_upper_failures = 0
    scale_lower_failures = 0
    first_scale_upper_failure = None
    first_scale_lower_failure = None
    min_upper_margin: tuple[int, int] | None = None
    min_lower_margin: tuple[int, int] | None = None
    min_ratio: tuple[int, int, int] | None = None

    for n in range(2, limit + 1):
        current = OTHER
        pairs: list[tuple[int, int]] = []
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n + 1, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif hard_shape(n, pairs):
                current = HARD
            else:
                current = OTHER_HOLE
        state[n] = current

        if allowed(n) and n % 2 == 0 and n >= 4:
            structural = splitless_class(n + 1, spf)
            require((not pairs) == (structural is not None), f"splitless classification mismatch at {n}")
            if current == SPLITLESS:
                require(structural is not None, f"missing splitless class at {n}")
                splitless_classes[structural] += 1
            if hard_shape(n, pairs):
                hard_shape_count += 1
                require(current in (GENERATED, HARD), f"hard shape classified incorrectly at {n}")

        if current == HARD:
            require(n % 2 == 0, f"odd hard root {n}")
            active_hard += 1

        if n % 2 == 1 and n > 3 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of_odd(n)
                require(root % 2 == 0, f"odd seed-2 root from {n}")
                if state[root] == HARD:
                    require(active_hard > 0, f"hard death underflow at {n}")
                    active_hard -= 1
                    first_death[root] = n
                elif state[root] == SPLITLESS:
                    healed_splitless += 1
                    first_death[root] = n
                    structural = splitless_class(root + 1, spf)
                    require(structural is not None, f"dead splitless root lacks class at {root}")
                    healed_classes[structural] += 1

        active_history[n] = active_hard
        quarter = int(active_history[n // 4])
        upper_margin = healed_splitless + quarter + 1 - active_hard
        lower_margin = 2 * healed_splitless - 7 * quarter
        if min_upper_margin is None or upper_margin < min_upper_margin[0]:
            min_upper_margin = (upper_margin, n)
        if min_lower_margin is None or lower_margin < min_lower_margin[0]:
            min_lower_margin = (lower_margin, n)
        if upper_margin < 0:
            scale_upper_failures += 1
            if first_scale_upper_failure is None:
                first_scale_upper_failure = n
        if lower_margin < 0:
            scale_lower_failures += 1
            if first_scale_lower_failure is None:
                first_scale_lower_failure = n
        if active_hard:
            if min_ratio is None or healed_splitless * min_ratio[1] < min_ratio[0] * active_hard:
                min_ratio = (healed_splitless, active_hard, n)

    require(first_death.get(24) == 5889, "prime-square witness death changed")
    require(state[54] == HARD, "54 is not reconstructed as hard")
    require(state[24] == SPLITLESS, "24 is not reconstructed as splitless")
    require(all(state[v] != GENERATED for v in literal_chain(24, 4 * 54)), "24 heals by 4*54")
    deep_chain = literal_chain(2340, limit)
    require(all(state[v] != GENERATED for v in deep_chain), "2340 chain unexpectedly heals")
    require(splitless_class(7, spf) == "plus_semigroup", "class check for root 6 failed")
    require(splitless_class(2341, spf) == "plus_semigroup", "class check for root 2340 failed")
    require(first_death.get(6) == 41, "root 6 death changed")
    require(2340 not in first_death, "root 2340 unexpectedly has a death")
    require(splitless_class(21, spf) == "three_times_plus_semigroup", "class check for root 20 failed")
    require(splitless_class(16149, spf) == "three_times_plus_semigroup", "class check for root 16148 failed")
    require(first_death.get(20) == 77, "root 20 death changed")
    require(16148 not in first_death, "root 16148 unexpectedly has a death")
    require(min_ratio is not None, "no positive hard-root ratio observed")

    return {
        "schema": "C96-ratio-obstruction-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "counts": {
            "A_H": active_hard,
            "D": healed_splitless,
            "hard_shapes_generated_or_holes": hard_shape_count,
            "splitless_roots": sum(splitless_classes.values()),
        },
        "structural_classes": dict(sorted(splitless_classes.items())),
        "healed_classes": dict(sorted(healed_classes.items())),
        "quarter_scale_gates": {
            "A_H_X_le_D_X_plus_A_H_floor_X_over_4_plus_1": {
                "failure_count": scale_upper_failures,
                "first_failure": first_scale_upper_failure,
                "minimum_margin": min_upper_margin[0],
                "minimum_margin_X": min_upper_margin[1],
            },
            "two_D_X_ge_seven_A_H_floor_X_over_4": {
                "failure_count": scale_lower_failures,
                "first_failure": first_scale_lower_failure,
                "minimum_margin": min_lower_margin[0],
                "minimum_margin_X": min_lower_margin[1],
            },
        },
        "minimum_D_over_A_H": {
            "D": min_ratio[0],
            "A_H": min_ratio[1],
            "X": min_ratio[2],
        },
        "exact_obstructions": {
            "prime_square_shadow": {
                "hard_root": 54,
                "least_minus_prime": 5,
                "shadow_root": 24,
                "four_times_hard_cutoff": 216,
                "visible_shadow_chain": literal_chain(24, 216),
                "first_generated_chain_member": first_death[24],
            },
            "same_plus_semigroup_class": {
                "healed_root": 6,
                "healed_at": first_death[6],
                "persistent_root": 2340,
                "persistent_chain_through_limit": deep_chain,
            },
            "same_three_times_plus_semigroup_class": {
                "healed_root": 20,
                "healed_at": first_death[20],
                "persistent_root": 16148,
                "persistent_chain_through_limit": literal_chain(16148, limit),
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.limit)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
