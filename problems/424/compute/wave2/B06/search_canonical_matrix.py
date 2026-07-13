#!/usr/bin/env python3
"""Search collision-free residue routings for a supercritical transfer matrix."""

from __future__ import annotations

import argparse
import itertools
import math
from collections import deque

from search_periodic_core import generate_a


def residue_closure(
    modulus: int, multipliers: tuple[int, ...]
) -> bytearray:
    """Exact residue closure of the finite affine subsystem."""
    active = bytearray(modulus)
    queue: deque[int] = deque()
    for seed in multipliers:
        residue = seed % modulus
        if not active[residue]:
            active[residue] = 1
            queue.append(residue)
    while queue:
        residue = queue.popleft()
        for multiplier in multipliers:
            child = (multiplier * residue - 1) % modulus
            if not active[child]:
                active[child] = 1
                queue.append(child)
    return active


def lcm(values: tuple[int, ...]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, value)
    return result


def safe_edges(
    state_modulus: int,
    sieve_modulus: int,
    multipliers: tuple[int, ...],
    priority: tuple[int, ...],
) -> tuple[bytearray, list[list[tuple[int, int]]]]:
    """Build edges (target, denominator) surviving exact priority conflicts."""
    if state_modulus % (sieve_modulus * lcm(multipliers)):
        raise ValueError("state modulus must be divisible by sieve_modulus*lcm(D)")
    allowed_state = residue_closure(state_modulus, multipliers)
    allowed_sieve = residue_closure(sieve_modulus, multipliers)
    earlier: list[int] = []
    edges: list[list[tuple[int, int]]] = [
        [] for _ in range(state_modulus)
    ]
    for multiplier in priority:
        for source, allowed in enumerate(allowed_state):
            if not allowed:
                continue
            safe = True
            for competitor in earlier:
                product = multiplier * source
                if product % competitor:
                    continue
                other_parent = product // competitor
                if allowed_sieve[other_parent % sieve_modulus]:
                    safe = False
                    break
            if safe:
                target = (multiplier * source - 1) % state_modulus
                edges[source].append((target, multiplier))
        earlier.append(multiplier)
    return allowed_state, edges


def spectral_bounds(
    active: bytearray,
    edges: list[list[tuple[int, int]]],
    iterations: int,
) -> tuple[float, float, list[float]]:
    """Power iterate and return final Collatz lower/upper ratios."""
    vector = [1.0 if bit else 0.0 for bit in active]
    lower = 0.0
    upper = math.inf
    for _ in range(iterations):
        image = [0.0] * len(vector)
        for source, outgoing in enumerate(edges):
            value = vector[source]
            if not value:
                continue
            for target, denominator in outgoing:
                image[target] += value / denominator
        ratios = [
            image[state] / vector[state]
            for state, bit in enumerate(active)
            if bit and vector[state] > 0
        ]
        lower = min(ratios)
        upper = max(ratios)
        scale = max(image)
        if scale == 0:
            return 0.0, 0.0, image
        vector = [value / scale for value in image]
    return lower, upper, vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=int, required=True)
    parser.add_argument("--sieve-modulus", type=int, required=True)
    parser.add_argument(
        "--state-factor",
        type=int,
        default=1,
        help="Q = state_factor * sieve_modulus * lcm(D)",
    )
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument(
        "--all-priorities",
        action="store_true",
        help="test every priority order; intended only for small D",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    full = generate_a(args.cutoff)
    multipliers = tuple(n for n, bit in enumerate(full) if bit)
    base = args.sieve_modulus * lcm(multipliers)
    state_modulus = args.state_factor * base
    priorities = (
        itertools.permutations(multipliers)
        if args.all_priorities
        else (multipliers,)
    )

    best = (-1.0, math.inf, (), 0, 0)
    tested = 0
    for priority in priorities:
        active, edges = safe_edges(
            state_modulus,
            args.sieve_modulus,
            multipliers,
            priority,
        )
        lower, upper, _ = spectral_bounds(active, edges, args.iterations)
        edge_count = sum(map(len, edges))
        tested += 1
        if lower > best[0]:
            best = (
                lower,
                upper,
                priority,
                sum(active),
                edge_count,
            )
    lower, upper, priority, active_count, edge_count = best
    print(f"D={list(multipliers)}")
    print(
        f"sieve={args.sieve_modulus} state={state_modulus} "
        f"active={active_count} edges={edge_count} priorities={tested}"
    )
    print(f"best_priority={list(priority)}")
    print(f"collatz_lower={lower:.15f} collatz_upper={upper:.15f}")


if __name__ == "__main__":
    main()
