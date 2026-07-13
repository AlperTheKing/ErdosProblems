#!/usr/bin/env python3
"""Exact finite-state search for a periodic strong-induction core in Erdos 424.

For fixed multipliers D contained in A and a modulus M divisible by every d in
D, a residue r is supported by d when r == -1 (mod d) and every possible
residue of (n+1)/d (mod M), for n == r (mod M), is retained. A nonempty fixed
point, together with a finite base interval, certifies a periodic subset of A.
"""

from __future__ import annotations

import argparse
import json
import math
from array import array
from pathlib import Path


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", [0]) * (limit + 1)
    for prime in range(2, math.isqrt(limit) + 1):
        if spf[prime]:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            if not spf[multiple]:
                spf[multiple] = prime
    return spf


def divisors_from_spf(value: int, spf: array) -> list[int]:
    remaining = value
    divisors = [1]
    while remaining > 1:
        prime = spf[remaining] or remaining
        old = tuple(divisors)
        power = 1
        while remaining % prime == 0:
            remaining //= prime
            power *= prime
            divisors.extend(divisor * power for divisor in old)
    divisors.sort()
    return divisors


def generate_a(limit: int) -> bytearray:
    """Generate exact membership through limit by ascending factor recursion."""
    member = bytearray(limit + 1)
    for seed in (2, 3):
        if seed <= limit:
            member[seed] = 1
    spf = smallest_prime_factors(limit + 1)
    for n in range(4, limit + 1):
        product = n + 1
        for divisor in divisors_from_spf(product, spf):
            if divisor * divisor >= product:
                break
            if member[divisor] and member[product // divisor]:
                member[n] = 1
                break
    return member


def a_divisors(modulus: int, member: bytearray) -> tuple[int, ...]:
    spf = smallest_prime_factors(modulus)
    return tuple(
        divisor
        for divisor in divisors_from_spf(modulus, spf)
        if divisor >= 2 and member[divisor]
    )


def quotient_residues(
    modulus: int, residue: int, multiplier: int
) -> tuple[int, ...]:
    """All quotient residues as n ranges over residue modulo modulus."""
    assert modulus % multiplier == 0
    assert (residue + 1) % multiplier == 0
    base = (residue + 1) // multiplier
    step = modulus // multiplier
    return tuple(
        (base + digit * step) % modulus for digit in range(multiplier)
    )


def base_mask(
    modulus: int,
    member: bytearray,
    start: int,
    stop: int,
) -> bytearray:
    """Retain residues whose representatives in [start, stop] all lie in A."""
    allowed = bytearray(b"\x01") * modulus
    for n in range(start, stop + 1):
        if not member[n]:
            allowed[n % modulus] = 0
    return allowed


def greatest_core(
    modulus: int,
    multipliers: tuple[int, ...],
    initial: bytearray | None = None,
) -> tuple[bytearray, list[int], int]:
    """Return greatest exact quotient-state core, choices, and pass count."""
    if not multipliers:
        return bytearray(modulus), [-1] * modulus, 0
    for multiplier in multipliers:
        if modulus % multiplier:
            raise ValueError(f"{multiplier} does not divide modulus {modulus}")

    candidates: list[list[tuple[int, tuple[int, ...]]]] = [
        [] for _ in range(modulus)
    ]
    for multiplier in multipliers:
        for residue in range(multiplier - 1, modulus, multiplier):
            candidates[residue].append(
                (
                    multiplier,
                    quotient_residues(modulus, residue, multiplier),
                )
            )

    active = (
        bytearray(initial)
        if initial is not None
        else bytearray(b"\x01") * modulus
    )
    passes = 0
    while True:
        passes += 1
        changed = False
        new = bytearray(active)
        for residue, is_active in enumerate(active):
            if not is_active:
                continue
            if not any(
                all(active[q] for q in quotients)
                for _, quotients in candidates[residue]
            ):
                new[residue] = 0
                changed = True
        active = new
        if not changed:
            break

    choices = [-1] * modulus
    for residue, is_active in enumerate(active):
        if not is_active:
            continue
        choices[residue] = min(
            multiplier
            for multiplier, quotients in candidates[residue]
            if all(active[q] for q in quotients)
        )
    return active, choices, passes


def verify_core(
    modulus: int,
    multipliers: tuple[int, ...],
    active: bytearray,
    choices: list[int],
) -> None:
    multiplier_set = set(multipliers)
    for residue, is_active in enumerate(active):
        if not is_active:
            assert choices[residue] == -1
            continue
        multiplier = choices[residue]
        assert multiplier in multiplier_set
        assert modulus % multiplier == 0
        assert (residue + 1) % multiplier == 0
        assert all(
            active[q]
            for q in quotient_residues(modulus, residue, multiplier)
        )


def write_certificate(
    path: Path,
    modulus: int,
    multipliers: tuple[int, ...],
    active: bytearray,
    choices: list[int],
    base_start: int | None,
    base_stop: int | None,
) -> None:
    residues = [r for r, bit in enumerate(active) if bit]
    payload = {
        "modulus": modulus,
        "multipliers": list(multipliers),
        "residues": residues,
        "choices": {str(r): choices[r] for r in residues},
        "base_start": base_start,
        "base_stop": base_stop,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moduli", nargs="+", type=int, required=True)
    parser.add_argument(
        "--multipliers",
        nargs="*",
        type=int,
        help="fixed verified multipliers; default is all A-divisors of M",
    )
    parser.add_argument(
        "--base-start",
        type=int,
        help="impose exact base interval [L, max(D)*L]",
    )
    parser.add_argument("--certificate", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    maximum = max(args.moduli)
    if args.multipliers:
        maximum = max(maximum, max(args.multipliers))

    provisional = generate_a(maximum)
    jobs: list[tuple[int, tuple[int, ...], int | None, int | None]] = []
    required_limit = maximum
    for modulus in args.moduli:
        multipliers = (
            tuple(sorted(set(args.multipliers)))
            if args.multipliers
            else a_divisors(modulus, provisional)
        )
        for multiplier in multipliers:
            if modulus % multiplier:
                raise ValueError(
                    f"multiplier {multiplier} does not divide modulus {modulus}"
                )
            if not provisional[multiplier]:
                raise ValueError(f"multiplier {multiplier} is not in A")
        base_start = args.base_start
        base_stop = max(multipliers) * base_start if multipliers and base_start else None
        if base_stop:
            required_limit = max(required_limit, base_stop)
        jobs.append((modulus, multipliers, base_start, base_stop))

    member = (
        provisional
        if required_limit == maximum
        else generate_a(required_limit)
    )
    nonempty = []
    for modulus, multipliers, start, stop in jobs:
        initial = (
            base_mask(modulus, member, start, stop)
            if start and stop
            else None
        )
        active, choices, passes = greatest_core(
            modulus, multipliers, initial
        )
        verify_core(modulus, multipliers, active, choices)
        residues = [r for r, bit in enumerate(active) if bit]
        print(
            f"M={modulus} D={list(multipliers)} base={start}:{stop} "
            f"passes={passes} core={len(residues)}/{modulus}"
        )
        if residues:
            nonempty.append(
                (modulus, multipliers, active, choices, start, stop)
            )

    if args.certificate:
        if len(nonempty) != 1:
            raise ValueError(
                "certificate output requires exactly one nonempty core"
            )
        write_certificate(args.certificate, *nonempty[0])


if __name__ == "__main__":
    main()
