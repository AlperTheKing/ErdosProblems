#!/usr/bin/env python3
"""Exact targeted search for high-pair hard sources witnessed by one seed root."""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path


UINT64_MAX = (1 << 64) - 1
MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


@functools.lru_cache(maxsize=None)
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in MR_BASES_64:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def pollard_brent(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    for attempt in range(1, 65):
        rng = random.Random((n << 7) ^ attempt)
        y = rng.randrange(1, n - 1)
        c = rng.randrange(1, n - 1)
        m = 128
        g = r = q = 1
        x = ys = 0
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += m
            r <<= 1
        if g == n:
            while True:
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
                if g > 1:
                    break
        if g != n:
            return g
    raise RuntimeError(("pollard-rho-failed", n))


@functools.lru_cache(maxsize=None)
def factor_tuple(n: int) -> tuple[tuple[int, int], ...]:
    require(1 <= n <= UINT64_MAX, ("factor-range", n))
    factors: list[int] = []

    def split(value: int) -> None:
        if value == 1:
            return
        if is_prime(value):
            factors.append(value)
            return
        divisor = pollard_brent(value)
        split(divisor)
        split(value // divisor)

    split(n)
    factors.sort()
    packed: list[tuple[int, int]] = []
    for p in factors:
        if packed and packed[-1][0] == p:
            packed[-1] = (p, packed[-1][1] + 1)
        else:
            packed.append((p, 1))
    product = 1
    for p, exponent in packed:
        require(is_prime(p), ("composite-factor", n, p))
        product *= p**exponent
    require(product == n, ("factor-product", n, product))
    return tuple(packed)


def divisors_from_factorization(factors: tuple[tuple[int, int], ...]) -> list[int]:
    divisors = [1]
    for p, exponent in factors:
        old = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= p
            divisors.extend(value * power for value in old)
    return sorted(divisors)


def admissible_pairs_from_product(
    product: int, factors: tuple[tuple[int, int], ...] | None = None
) -> tuple[tuple[int, int], ...]:
    if factors is None:
        factors = factor_tuple(product)
    pairs = []
    for left in divisors_from_factorization(factors):
        if left < 2:
            continue
        right = product // left
        if left >= right:
            break
        if allowed(left) and allowed(right):
            pairs.append((left, right))
    return tuple(pairs)


@functools.lru_cache(maxsize=None)
def generated(n: int) -> bool:
    if n in (2, 3):
        return True
    if not allowed(n):
        return False
    for left, right in admissible_pairs_from_product(n + 1):
        if generated(left) and generated(right):
            return True
    return False


def seed_root(endpoint: int) -> int:
    require(endpoint > 1 and endpoint % 2 == 1, ("seed-root-domain", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


@dataclass(frozen=True)
class Candidate:
    h: int
    product: int
    factors: tuple[tuple[int, int], ...]
    pairs: tuple[tuple[int, int], ...]
    hard: bool
    fixed_root_witness: bool


def classify_candidate(
    product: int, factors: tuple[tuple[int, int], ...], root: int
) -> Candidate:
    h = product - 1
    pairs = admissible_pairs_from_product(product, factors)
    easy_seed_three = (
        product % 3 == 0 and product // 3 != 3 and allowed(product // 3)
    )
    hard = (
        h % 2 == 0
        and allowed(h)
        and bool(pairs)
        and not easy_seed_three
        and all(not (generated(left) and generated(right)) for left, right in pairs)
    )
    witness = hard and any(
        not generated(endpoint) and seed_root(endpoint) == root
        for pair in pairs
        for endpoint in pair
    )
    return Candidate(h, product, factors, pairs, hard, witness)


def candidate_json(candidate: Candidate, root: int) -> dict[str, object]:
    pair_rows = []
    for left, right in candidate.pairs:
        endpoints = []
        for endpoint in (left, right):
            is_generated = generated(endpoint)
            endpoints.append(
                {
                    "value": endpoint,
                    "generated": is_generated,
                    "missing_root": None if is_generated else seed_root(endpoint),
                }
            )
        pair_rows.append({"a": left, "b": right, "endpoints": endpoints})
    d = len(candidate.pairs)
    denominator = root - 1
    dyadic_bin = denominator.bit_length() - 1
    failure_d = (1 << dyadic_bin) + 1
    return {
        "h": candidate.h,
        "h_plus_1": candidate.product,
        "factorization": [[p, exponent] for p, exponent in candidate.factors],
        "d": d,
        "hard": candidate.hard,
        "fixed_root": root,
        "fixed_root_witness": candidate.fixed_root_witness,
        "pairs": pair_rows,
        "single_root_bin_test": {
            "dyadic_bin_j": dyadic_bin,
            "minimum_D_for_failure": failure_d,
            "source_qualifies_at_failure_D": d >= failure_d + 1,
            "lhs_D_times_one_root": failure_d,
            "rhs_2_to_j": 1 << dyadic_bin,
            "fails": candidate.fixed_root_witness and d >= failure_d + 1,
        },
    }


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [p for p in range(2, limit + 1) if sieve[p]]


def merge_square_factor(
    base_factors: tuple[tuple[int, int], ...], q: int
) -> tuple[tuple[int, int], ...]:
    merged = dict(base_factors)
    merged[q] = merged.get(q, 0) + 2
    return tuple(sorted(merged.items()))


def merge_pair_factors(
    base_factors: tuple[tuple[int, int], ...], q: int, r: int
) -> tuple[tuple[int, int], ...]:
    merged = dict(base_factors)
    merged[q] = merged.get(q, 0) + 1
    merged[r] = merged.get(r, 0) + 1
    return tuple(sorted(merged.items()))


def validate_known(root: int) -> list[dict[str, object]]:
    known = (
        (535, ((5, 1), (107, 1)), 1),
        (7_634_275, ((5, 2), (11, 1), (17, 1), (23, 1), (71, 1)), 12),
        (
            2_796_867_115,
            ((5, 1), (7, 1), (17, 1), (107, 1), (197, 1), (223, 1)),
            16,
        ),
    )
    rows = []
    for product, expected_factors, expected_d in known:
        require(factor_tuple(product) == expected_factors, ("known-factorization", product))
        candidate = classify_candidate(product, expected_factors, root)
        require(candidate.hard, ("known-not-hard", product - 1))
        require(candidate.fixed_root_witness, ("known-no-root", product - 1, root))
        require(len(candidate.pairs) == expected_d, ("known-d", product - 1, len(candidate.pairs)))
        rows.append(
            {
                "h": product - 1,
                "d": len(candidate.pairs),
                "factorization": [[p, exponent] for p, exponent in expected_factors],
            }
        )
    require(not generated(107) and seed_root(107) == root, "107 chain check")
    require(not generated(213) and seed_root(213) == root, "213 chain check")
    require(not generated(425) and seed_root(425) == root, "425 chain check")
    require(generated(849), "849 must terminate the missing chain")
    return rows


def search_square_lifts(
    base: int,
    root: int,
    prime_limit: int,
    minimum_d: int,
    max_hits: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    base_factors = factor_tuple(base)
    require(classify_candidate(base, base_factors, root).hard, ("base-not-hard", base))
    hits = []
    tested = arithmetic_eligible = high_pair = 0
    for q in primes_through(prime_limit):
        if q in (2, 3) or base % q == 0:
            continue
        product = base * q * q
        if product > UINT64_MAX:
            break
        tested += 1
        if product % 3 != 1:
            continue
        arithmetic_eligible += 1
        factors = merge_square_factor(base_factors, q)
        pairs = admissible_pairs_from_product(product, factors)
        if len(pairs) < minimum_d:
            continue
        high_pair += 1
        candidate = classify_candidate(product, factors, root)
        if candidate.hard and candidate.fixed_root_witness:
            hits.append(candidate_json(candidate, root))
            if len(hits) >= max_hits:
                break
    return hits, {
        "primes_tested": tested,
        "arithmetic_eligible": arithmetic_eligible,
        "high_pair_candidates": high_pair,
    }


def search_pair_lifts(
    base: int,
    root: int,
    prime_limit: int,
    minimum_d: int,
    max_hits: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    base_factors = factor_tuple(base)
    require(classify_candidate(base, base_factors, root).hard, ("base-not-hard", base))
    primes = [
        q for q in primes_through(prime_limit) if q not in (2, 3) and base % q != 0
    ]
    hits = []
    tested = arithmetic_eligible = high_pair = 0
    for index, q in enumerate(primes):
        for r in primes[index + 1 :]:
            product = base * q * r
            if product > UINT64_MAX:
                break
            tested += 1
            if product % 3 != 1:
                continue
            arithmetic_eligible += 1
            factors = merge_pair_factors(base_factors, q, r)
            pairs = admissible_pairs_from_product(product, factors)
            if len(pairs) < minimum_d:
                continue
            high_pair += 1
            candidate = classify_candidate(product, factors, root)
            if candidate.hard and candidate.fixed_root_witness:
                hits.append(candidate_json(candidate, root))
    hits.sort(key=lambda row: int(row["h"]))
    return hits[:max_hits], {
        "prime_pairs_tested": tested,
        "arithmetic_eligible": arithmetic_eligible,
        "high_pair_candidates": high_pair,
        "hard_fixed_root_hits": len(hits),
    }


def search_supports(
    channel: int,
    root: int,
    prime_limit: int,
    extra_count: int,
    minimum_d: int,
    max_hits: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    fixed_by_channel = {
        107: ((107, 1),),
        213: ((3, 1), (71, 1)),
        425: ((5, 2), (17, 1)),
    }
    fixed = fixed_by_channel[channel]
    fixed_primes = {p for p, _ in fixed}
    pool = [
        q
        for q in primes_through(prime_limit)
        if q != 2 and q not in fixed_primes
    ]
    hits = []
    tested = arithmetic_eligible = high_pair = 0
    for extras in itertools.combinations(pool, extra_count):
        factors = tuple(sorted(fixed + tuple((q, 1) for q in extras)))
        product = math.prod(p**exponent for p, exponent in factors)
        if product > UINT64_MAX:
            continue
        tested += 1
        h = product - 1
        if h % 2 != 0 or not allowed(h):
            continue
        arithmetic_eligible += 1
        pairs = admissible_pairs_from_product(product, factors)
        if len(pairs) < minimum_d:
            continue
        high_pair += 1
        candidate = classify_candidate(product, factors, root)
        if candidate.hard and candidate.fixed_root_witness:
            hits.append(candidate_json(candidate, root))
    hits.sort(key=lambda row: int(row["h"]))
    return hits[:max_hits], {
        "supports_tested": tested,
        "arithmetic_eligible": arithmetic_eligible,
        "high_pair_candidates": high_pair,
        "hard_fixed_root_hits": len(hits),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=int, default=2_796_867_115)
    parser.add_argument("--root", type=int, default=54)
    parser.add_argument("--lift", choices=("square", "pair", "support"), default="square")
    parser.add_argument("--channel", choices=(107, 213, 425), type=int, default=107)
    parser.add_argument("--extra-count", type=int, default=7)
    parser.add_argument("--prime-limit", type=int, default=10_000)
    parser.add_argument("--minimum-d", type=int, default=34)
    parser.add_argument("--max-hits", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(2 <= args.root <= UINT64_MAX, ("root", args.root))
    require(5 <= args.prime_limit <= 10_000_000, ("prime-limit", args.prime_limit))
    require(1 <= args.minimum_d <= 1_000_000, ("minimum-d", args.minimum_d))
    require(1 <= args.max_hits <= 1000, ("max-hits", args.max_hits))
    require(1 <= args.extra_count <= 16, ("extra-count", args.extra_count))

    started = time.perf_counter()
    validation = validate_known(args.root)
    if args.lift == "square":
        hits, counts = search_square_lifts(
            args.base, args.root, args.prime_limit, args.minimum_d, args.max_hits
        )
        family = "N=base*q^2 for prime q not dividing 6*base"
    elif args.lift == "pair":
        hits, counts = search_pair_lifts(
            args.base, args.root, args.prime_limit, args.minimum_d, args.max_hits
        )
        family = "N=base*q*r for distinct primes q<r, qr=1 mod 3, gcd(qr,6*base)=1"
    else:
        hits, counts = search_supports(
            args.channel,
            args.root,
            args.prime_limit,
            args.extra_count,
            args.minimum_d,
            args.max_hits,
        )
        family = (
            f"N divisible by fixed missing endpoint {args.channel}, with "
            f"{args.extra_count} additional distinct odd primes"
        )
    elapsed = time.perf_counter() - started
    payload = {
        "schema": "C109-fixed-root-square-lift-search-v1",
        "exactness": {
            "integer_domain": "unsigned 64-bit",
            "primality": "deterministic Miller-Rabin bases valid below 2^64",
            "factorization": "deterministic-seeded Pollard-Brent; prime factors and product rechecked",
            "closure": "memoized full admissible-divisor recursion to seeds 2,3",
            "floating_point_acceptance": False,
        },
        "parameters": {
            "base": args.base,
            "root": args.root,
            "lift": args.lift,
            "channel": args.channel,
            "extra_count": args.extra_count,
            "prime_limit": args.prime_limit,
            "minimum_d": args.minimum_d,
            "max_hits": args.max_hits,
            "family": family,
        },
        "known_validation": validation,
        "counts": counts,
        "hits": hits,
        "cache": {
            "generated": generated.cache_info()._asdict(),
            "factorizations": factor_tuple.cache_info()._asdict(),
            "primality": is_prime.cache_info()._asdict(),
        },
        "timing_seconds": elapsed,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.write_text(encoded, encoding="ascii")
    digest = hashlib.sha256(encoded.encode("ascii")).hexdigest()
    print(
        f"tested={counts.get('primes_tested', counts.get('prime_pairs_tested'))} "
        f"high_pair={counts['high_pair_candidates']} "
        f"hits={len(hits)} sha256={digest} elapsed={elapsed:.3f}s"
    )
    if hits:
        print(f"first_h={hits[0]['h']} d={hits[0]['d']}")
    return 0


if __name__ == "__main__":
    sys.setrecursionlimit(100_000)
    raise SystemExit(main())
