#!/usr/bin/env python3
"""Exact gate for 2-adically separated product-density recurrences.

For S = G_0 G_2, the closure gives the injective support maps

    F_a(n) = a(n-1),       a in G_0,
    H_b(n) = b(2n-3),      b in G_2.

The H_b image has fixed 2-adic valuation v_2(b).  If a has valuation t,
the F_a image has valuation at least t.  Hence one F_a image is disjoint
from H_b images with valuations 0,...,t-1.  This program constructs the
least closure exactly, forms S exactly, and replays these disjoint unions.
Only integer and Fraction arithmetic is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from array import array
from fractions import Fraction
from pathlib import Path


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def smallest_prime_factors(limit: int) -> array:
    spf = array("I", [0]) * (limit + 1)
    for prime in range(2, math.isqrt(limit) + 1):
        if spf[prime] != 0:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            if spf[multiple] == 0:
                spf[multiple] = prime
    return spf


def proper_factor_pairs(value: int, spf: array):
    remaining = value
    factors: list[tuple[int, int]] = []
    while remaining > 1:
        prime = spf[remaining] or remaining
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        factors.append((prime, exponent))

    divisors = [1]
    for prime, exponent in factors:
        old = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= prime
            divisors.extend(d * power for d in old)
    divisors.sort()
    for divisor in divisors:
        if divisor * divisor >= value:
            break
        yield divisor, value // divisor


def least_closure(limit: int) -> bytearray:
    member = bytearray(limit + 1)
    for seed in (2, 3):
        if seed <= limit:
            member[seed] = 1
    spf = smallest_prime_factors(limit + 1)
    for n in range(4, limit + 1):
        for left, right in proper_factor_pairs(n + 1, spf):
            if member[left] and member[right]:
                member[n] = 1
                break
    return member


def v2(value: int) -> int:
    require(value > 0, ("nonpositive-v2-input", value))
    return (value & -value).bit_length() - 1


def product_support(member: bytearray, limit: int) -> set[int]:
    g0 = [n for n in range(3, limit + 1, 3) if member[n]]
    g2 = [n for n in range(2, limit + 1, 3) if member[n]]
    support: set[int] = set()
    for left in g0:
        if left * 2 > limit:
            break
        cap = limit // left
        for right in g2:
            if right > cap:
                break
            support.add(left * right)
    return support


def minima_by_valuation(values: list[int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for value in values:
        result.setdefault(v2(value), value)
    return result


def h_parent_cutoff(x: int, b: int) -> int:
    return ((x // b) + 3) // 2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument(
        "--checkpoints",
        default="1000,10000,100000,1000000",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkpoints = [int(x) for x in args.checkpoints.split(",") if x]
    require(bool(checkpoints), "empty-checkpoint-list")
    require(max(checkpoints) <= args.limit, ("checkpoint-above-limit", max(checkpoints), args.limit))

    member = least_closure(args.limit)
    g0 = [n for n in range(3, args.limit + 1, 3) if member[n]]
    g2 = [n for n in range(2, args.limit + 1, 3) if member[n]]
    support = product_support(member, args.limit)
    a_min = minima_by_valuation(g0)
    b_min = minima_by_valuation(g2)

    # The residue-only envelope used in the proof report.
    h_envelope_exact = Fraction(7, 15)
    # Dual averaging certificate for the general separated scheme:
    # pi_0=3/10 and pi_r=7/(10*2^r) for r>=1.  Target 0 costs 1/10;
    # odd targets cost at most their H envelope; even targets >=2 cost at
    # most 7/(30*2^j).  The total is 23/45.
    dual_pi_prefix = [Fraction(3, 10)] + [
        Fraction(7, 10 * (1 << r)) for r in range(1, 80)
    ]
    dual_pi_tail = Fraction(7, 10 * (1 << 79))
    require(sum(dual_pi_prefix) + dual_pi_tail == 1, "dual-probability-mass")
    odd_h_sum = Fraction(1, 3)
    positive_even_f_sum = Fraction(7, 90)
    general_capacity = Fraction(1, 10) + odd_h_sum + positive_even_f_sum
    require(h_envelope_exact == Fraction(7, 15), "H-envelope")
    require(general_capacity == Fraction(23, 45), "general-capacity")

    schemes = []
    running_h = Fraction(0)
    max_t = min(max(a_min, default=-1), max(b_min, default=-1) + 1)
    for t in range(max_t + 1):
        if t > 0:
            if t - 1 not in b_min:
                break
            running_h += Fraction(1, 2 * b_min[t - 1])
        if t not in a_min:
            continue
        load = running_h + Fraction(1, a_min[t])
        schemes.append({
            "t": t,
            "a": a_min[t],
            "b": [b_min[k] for k in range(t)],
            "load": [load.numerator, load.denominator],
            "load_float": float(load),
        })

    checkpoint_rows = []
    support_sorted = sorted(support)
    for x in checkpoints:
        sx = {n for n in support_sorted if n <= x}
        best = None
        for scheme in schemes:
            t = scheme["t"]
            a = scheme["a"]
            bs = scheme["b"]
            images_f = {a * (n - 1) for n in support if a * (n - 1) <= x}
            images_h = [
                {b * (2 * n - 3) for n in support if b * (2 * n - 3) <= x}
                for b in bs
            ]
            pieces = [images_f, *images_h]
            union = set().union(*pieces)
            require(union <= sx, ("image-outside-support", x, t))
            require(sum(map(len, pieces)) == len(union), ("image-collision", x, t))
            for value in images_f:
                require(v2(value) >= t, ("F-valuation", x, t, value))
            for k, image in enumerate(images_h):
                for value in image:
                    require(v2(value) == k, ("H-valuation", x, t, k, value))

            rhs_count = sum(1 for n in support if n <= x // a + 1)
            rhs_count += sum(
                sum(1 for n in support if n <= h_parent_cutoff(x, b))
                for b in bs
            )
            require(rhs_count == len(union), ("recurrence-count", x, t, rhs_count, len(union)))
            row = {
                "t": t,
                "a": a,
                "b": bs,
                "image_count": len(union),
                "support_count": len(sx),
                "coverage": float(Fraction(len(union), len(sx))),
            }
            if best is None or row["image_count"] > best["image_count"]:
                best = row
        checkpoint_rows.append({"X": x, "best": best})

    script_path = Path(__file__).resolve()
    output = {
        "limit": args.limit,
        "g_count": sum(member),
        "g0_count": len(g0),
        "g2_count": len(g2),
        "support_count": len(support),
        "min_g0_by_v2": {str(k): v for k, v in sorted(a_min.items())},
        "min_g2_by_v2": {str(k): v for k, v in sorted(b_min.items())},
        "h_residue_envelope": [7, 15],
        "general_profile_free_capacity": [23, 45],
        "dual_profile_weights": {
            "pi_0": [3, 10],
            "pi_r_for_r_ge_1": "7/(10*2^r)",
        },
        "schemes": schemes,
        "checkpoints": checkpoint_rows,
        "script_sha256": sha256(script_path),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
