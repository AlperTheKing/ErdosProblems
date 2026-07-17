#!/usr/bin/env python3
"""Independent Python verifier for the C105 structural-pair census."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
FNV_OFFSET = 14_695_981_039_346_656_037
FNV_PRIME = 1_099_511_628_211
MASK64 = (1 << 64) - 1


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for prime in range(2, math.isqrt(limit) + 1):
        if spf[prime] != prime:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            if spf[multiple] == multiple:
                spf[multiple] = prime
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        prime = spf[n]
        exponent = 0
        while n % prime == 0:
            n //= prime
            exponent += 1
        factors.append((prime, exponent))
    result = [1]
    for prime, exponent in factors:
        previous = tuple(result)
        power = 1
        for _ in range(exponent):
            power *= prime
            result.extend(value * power for value in previous)
    return result


def factor_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for left in divisors(product, spf):
        if left < 2:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return sorted(result)


def classify(n: int, pairs: list[tuple[int, int]], state: bytearray) -> int:
    if any(state[left] == GENERATED and state[right] == GENERATED
           for left, right in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        product = n + 1
        if product % 3:
            return HARD
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return OTHER


def seed_root(endpoint: int) -> int:
    if endpoint < 3 or endpoint % 2 == 0:
        raise AssertionError(("seed root input", endpoint))
    while endpoint % 2:
        endpoint = (endpoint + 1) // 2
    return endpoint


def fnv_byte(digest: int, value: int) -> int:
    return ((digest ^ value) * FNV_PRIME) & MASK64


def fnv_u64(digest: int, value: int) -> int:
    for shift in range(0, 64, 8):
        digest = fnv_byte(digest, (value >> shift) & 0xFF)
    return digest


def audit(limit: int) -> dict[str, object]:
    if limit < 534:
        raise ValueError("limit must be at least 534")
    spf = smallest_prime_factors(limit + 1)
    state = bytearray(limit + 1)
    classification_digest = FNV_OFFSET
    metric_digest = FNV_OFFSET
    exact: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "count": 0,
            "zero_s_count": 0,
            "first_zero_s_h": None,
            "last_zero_s_h": None,
            "minimum_s": 1 << 60,
            "minimum_s_h": 0,
            "maximum_deficit": -1,
            "maximum_deficit_h": 0,
        }
    )
    hard_count = 0
    zero_s_count = 0
    largest_zero = (0, 0)
    largest_deficit = (-1, 0, 0, 0)
    witnesses: dict[int, dict[str, object]] = {}

    for n in range(2, limit + 1):
        if n in (2, 3):
            current = GENERATED
            pairs: list[tuple[int, int]] = []
        elif allowed(n):
            pairs = factor_pairs(n, spf)
            current = classify(n, pairs, state)
        else:
            pairs = []
            current = OTHER
        state[n] = current
        classification_digest = fnv_byte(classification_digest, current)
        if current != HARD:
            continue

        pair_rows = []
        structural_pairs = 0
        for left, right in pairs:
            roots = []
            structural = False
            for endpoint in (left, right):
                if state[endpoint] == GENERATED:
                    roots.append(None)
                    continue
                root = seed_root(endpoint)
                if state[root] == GENERATED:
                    raise AssertionError((n, endpoint, root))
                roots.append(root)
                structural |= state[root] == SPLITLESS
            structural_pairs += int(structural)
            pair_rows.append({
                "pair": [left, right],
                "missing_roots": roots,
                "structural": structural,
            })

        d = len(pairs)
        s = structural_pairs
        deficit = d - s
        hard_count += 1
        metric_digest = fnv_u64(metric_digest, n)
        metric_digest = fnv_u64(metric_digest, d)
        metric_digest = fnv_u64(metric_digest, s)
        row = exact[d]
        row["count"] += 1
        if s < row["minimum_s"]:
            row["minimum_s"] = s
            row["minimum_s_h"] = n
            witnesses[n] = {"h": n, "d": d, "s": s, "pairs": pair_rows}
        if deficit > row["maximum_deficit"]:
            row["maximum_deficit"] = deficit
            row["maximum_deficit_h"] = n
            witnesses[n] = {"h": n, "d": d, "s": s, "pairs": pair_rows}
        if s == 0:
            zero_s_count += 1
            row["zero_s_count"] += 1
            if row["first_zero_s_h"] is None:
                row["first_zero_s_h"] = n
            row["last_zero_s_h"] = n
            if d > largest_zero[0] or (d == largest_zero[0] and n < largest_zero[1]):
                largest_zero = (d, n)
        if deficit > largest_deficit[0]:
            largest_deficit = (deficit, n, d, s)

    exact_rows = []
    for d in sorted(exact):
        exact_rows.append({"d": d, **exact[d]})
    return {
        "schema": "C105-independent-python-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "summary": {
            "hard_holes": hard_count,
            "maximum_d": max(exact),
            "zero_s_count": zero_s_count,
            "largest_d_with_s_zero": largest_zero[0],
            "largest_d_with_s_zero_h": largest_zero[1],
            "largest_deficit_d_minus_s": largest_deficit[0],
            "largest_deficit_h": largest_deficit[1],
            "largest_deficit_h_d": largest_deficit[2],
            "largest_deficit_h_s": largest_deficit[3],
        },
        "exact_by_d": exact_rows,
        "digests": {
            "algorithm": "FNV-1a-64 little-endian",
            "classification_2_through_limit": f"{classification_digest:016x}",
            "hard_h_d_s": f"{metric_digest:016x}",
        },
        "witnesses": [witnesses[h] for h in sorted(witnesses)],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output")
    parser.add_argument("--claim")
    args = parser.parse_args()
    result = audit(args.limit)
    if args.claim:
        with open(args.claim, encoding="ascii") as handle:
            claim = json.load(handle)
        keys = [
            "d", "count", "zero_s_count", "first_zero_s_h", "last_zero_s_h",
            "minimum_s", "minimum_s_h", "maximum_deficit", "maximum_deficit_h",
        ]
        claim_rows = [{key: row[key] for key in keys} for row in claim["exact_by_d"]]
        verifier_rows = [{key: row[key] for key in keys} for row in result["exact_by_d"]]
        checks = {
            "limit": claim["limit"] == result["limit"],
            "summary": claim["summary"] == result["summary"],
            "exact_by_d": claim_rows == verifier_rows,
            "digests": claim["digests"] == result["digests"],
        }
        if not all(checks.values()):
            raise AssertionError(checks)
        result["claim_check"] = {"status": "PASS", "checks": checks}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
