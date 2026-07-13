#!/usr/bin/env python3
"""Exact finite-residue searches for the Erdos 424 affine subsystem.

The searches use integer arithmetic only.  They test the two most direct
globally residue-decodable constructions:

* a one-letter decoder which assigns one of 2, 3, 5 to each output residue;
* natural exact-cover trees whose leaves are affine blocks with bounded
  counts of each letter.

The accompanying note proves that no finite globally residue-decodable block
automaton can be critical at exponent one.  These finite searches are useful
replays of the obstruction, not a proof by bounded exhaustion.
"""

from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from math import prod
from typing import Iterable


LETTERS = (2, 3, 5)
SEEDS = (2, 3, 5)
ROOTS = (9, 14)


def affine_coefficients(word: Iterable[int]) -> tuple[int, int]:
    """Return (a,b) for the block map x |-> a*x-b."""
    a, b = 1, 0
    for k in word:
        if k not in LETTERS:
            raise ValueError(f"invalid letter {k}")
        a, b = k * a, k * b + 1
    return a, b


def modular_preimages(modulus: int, target: int, k: int) -> tuple[int, ...]:
    """Solve k*r-1 == target (mod modulus), with k dividing modulus."""
    if modulus % k:
        raise ValueError("the modulus must be divisible by every letter")
    if (target + 1) % k:
        return ()
    base = ((target + 1) // k) % (modulus // k)
    return tuple(base + j * (modulus // k) for j in range(k))


def selector_options(modulus: int) -> dict[int, tuple[int, ...]]:
    if modulus % 30:
        raise ValueError("selector search requires a multiple of 30")
    return {
        q: tuple(k for k in LETTERS if (q + 1) % k == 0)
        for q in range(modulus)
    }


def critical_core(modulus: int, policy: dict[int, int]) -> tuple[frozenset[int], int]:
    """Return the exact column-stochastic core of a one-letter policy.

    A target q colored k has column sum one only if all k modular preimages
    remain in the core.  Iterative deletion computes the greatest such set.
    """
    current = frozenset(policy)
    rounds = 0
    while True:
        following = frozenset(
            q
            for q in current
            if all(r in current for r in modular_preimages(modulus, q, policy[q]))
        )
        rounds += 1
        if following == current:
            return current, rounds
        current = following


def exhaustive_selector_search(modulus: int = 30) -> dict[str, object]:
    """Exhaust every output-residue last-letter selector."""
    options = selector_options(modulus)
    fixed = {q: ks[0] for q, ks in options.items() if len(ks) == 1}
    variable = [(q, ks) for q, ks in options.items() if len(ks) > 1]
    expected = prod(len(ks) for _, ks in variable)
    policy_count = 0
    maximum_core_size = 0
    extinction_round_histogram: dict[int, int] = {}

    for choices in itertools.product(*(ks for _, ks in variable)):
        policy = fixed | {q: k for (q, _), k in zip(variable, choices)}
        core, rounds = critical_core(modulus, policy)
        policy_count += 1
        maximum_core_size = max(maximum_core_size, len(core))
        extinction_round_histogram[rounds] = extinction_round_histogram.get(rounds, 0) + 1

    assert policy_count == expected
    return {
        "modulus": modulus,
        "colored_residues": sum(bool(ks) for ks in options.values()),
        "variable_residues": len(variable),
        "policy_count": policy_count,
        "maximum_critical_core_size": maximum_core_size,
        "extinction_round_histogram": dict(sorted(extinction_round_histogram.items())),
    }


def _block_leaf_sources(modulus: int, cap: int) -> dict[tuple[int, int, int, int, int], int]:
    """Map (target,e2,e3,e5,carry) to a bit mask of source residues."""
    leaves: dict[tuple[int, int, int, int, int], int] = {}

    def visit(e2: int, e3: int, e5: int, slope: int, offset: int) -> None:
        if e2 + e3 + e5:
            for source in range(modulus):
                value = slope * source - offset
                target = value % modulus
                carry = ((value - target) // modulus) % slope
                key = (target, e2, e3, e5, carry)
                leaves[key] = leaves.get(key, 0) | (1 << source)
        if e2 < cap:
            visit(e2 + 1, e3, e5, 2 * slope, 2 * offset + 1)
        if e3 < cap:
            visit(e2, e3 + 1, e5, 3 * slope, 3 * offset + 1)
        if e5 < cap:
            visit(e2, e3, e5 + 1, 5 * slope, 5 * offset + 1)

    visit(0, 0, 0, 1, 0)
    return leaves


def natural_block_cover_search(modulus: int = 30, cap: int = 3) -> dict[str, object]:
    """Prune natural 2/3/5 exact-cover trees to their greatest fixed point.

    A node (d,t) represents t modulo d.  It may be covered by one affine
    block of slope d, or split into the p children modulo p*d.  Every leaf's
    source residue must belong to the current state set.
    """
    if modulus % 30:
        raise ValueError("block search requires a multiple of 30")
    leaves = _block_leaf_sources(modulus, cap)
    state_mask = (1 << modulus) - 1
    sizes = [modulus]

    while state_mask:
        next_mask = 0
        for target in range(modulus):
            if not (state_mask >> target) & 1:
                continue

            @lru_cache(maxsize=None)
            def cover(e2: int, e3: int, e5: int, carry: int) -> bool:
                slope = (2**e2) * (3**e3) * (5**e5)
                if e2 + e3 + e5:
                    sources = leaves.get((target, e2, e3, e5, carry), 0)
                    if sources & state_mask:
                        return True
                exponents = (e2, e3, e5)
                for index, prime in enumerate(LETTERS):
                    if exponents[index] >= cap:
                        continue
                    child = list(exponents)
                    child[index] += 1
                    if all(
                        cover(child[0], child[1], child[2], carry + j * slope)
                        for j in range(prime)
                    ):
                        return True
                return False

            if cover(0, 0, 0, 0):
                next_mask |= 1 << target

        sizes.append(next_mask.bit_count())
        if next_mask == state_mask:
            break
        state_mask = next_mask

    return {
        "modulus": modulus,
        "maximum_letter_count_per_block": cap,
        "fixed_point_sizes": sizes,
        "critical_state_residues": [r for r in range(modulus) if (state_mask >> r) & 1],
    }


def affine_orbit_counts(limit: int, checkpoints: Iterable[int]) -> dict[int, int]:
    """Count S exactly as the union of the orbits rooted at 9 and 14."""
    reached = bytearray(limit + 1)
    for root in ROOTS:
        if root <= limit:
            reached[root] = 1
    for x in range(1, limit + 1):
        if not reached[x]:
            continue
        for k in LETTERS:
            child = k * x - 1
            if child <= limit:
                reached[child] = 1

    wanted = sorted(set(x for x in checkpoints if 1 <= x <= limit))
    result: dict[int, int] = {}
    total = 0
    wanted_index = 0
    for x in range(1, limit + 1):
        total += reached[x]
        if x in SEEDS:
            total += 1
        while wanted_index < len(wanted) and wanted[wanted_index] == x:
            result[x] = total
            wanted_index += 1
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modulus", type=int, default=30)
    parser.add_argument("--max-block-cap", type=int, default=3)
    parser.add_argument("--orbit-limit", type=int, default=100_000)
    args = parser.parse_args()

    invariant_checks = 0
    for length in range(1, 8):
        for word in itertools.product(LETTERS, repeat=length):
            slope, offset = affine_coefficients(word)
            assert slope >= 2 and 1 <= offset < slope
            invariant_checks += 1

    output = {
        "affine_coefficient_invariant_checks": invariant_checks,
        "selector_search": exhaustive_selector_search(args.modulus),
        "natural_block_cover_searches": [
            natural_block_cover_search(args.modulus, cap)
            for cap in range(1, args.max_block_cap + 1)
        ],
        "orbit_counts": affine_orbit_counts(
            args.orbit_limit,
            (10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000),
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
