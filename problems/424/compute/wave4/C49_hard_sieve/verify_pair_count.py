#!/usr/bin/env python3
"""Independent exact verifier for the C49 admissible-pair lower bound."""

from __future__ import annotations

import argparse
import json
from array import array
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def factor(n: int, spf: array) -> list[tuple[int, int]]:
    out = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        out.append((p, exponent))
    return out


def divisors(factors: list[tuple[int, int]]) -> list[int]:
    out = [1]
    for p, exponent in factors:
        old = list(out)
        power = 1
        for _ in range(exponent):
            power *= p
            out.extend(x * power for x in old)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    spf = spf_sieve(args.limit)
    tested = 0
    minimum_slack = None
    equality_examples = []
    failures = []
    exponential_failures = []
    exponential_minimum_slack = None

    for n in range(5, args.limit + 1, 2):
        # Successors of hard sources are 1 mod 6 or 3 mod 18.
        if not (n % 6 == 1 or n % 18 == 3):
            continue
        factors = factor(n, spf)
        omega2 = sum(e for p, e in factors if p % 3 == 2)
        singleton_omega2 = sum(
            1 for p, e in factors if p % 3 == 2 and e == 1
        )
        pairs = 0
        for d in divisors(factors):
            e = n // d
            if 2 <= d < e and allowed(d) and allowed(e):
                pairs += 1
        if pairs == 0:
            continue
        tested += 1
        slack = 4 * pairs + 2 - omega2
        if minimum_slack is None or slack < minimum_slack:
            minimum_slack = slack
        if slack == 0 and len(equality_examples) < 25:
            equality_examples.append({
                "successor": n,
                "omega2": omega2,
                "pairs": pairs,
            })
        if singleton_omega2 >= 2:
            exponential_slack = pairs + 1 - 2 ** (singleton_omega2 - 2)
            if (exponential_minimum_slack is None
                    or exponential_slack < exponential_minimum_slack):
                exponential_minimum_slack = exponential_slack
            if exponential_slack < 0:
                exponential_failures.append({
                    "successor": n,
                    "singleton_omega2": singleton_omega2,
                    "pairs": pairs,
                    "slack": exponential_slack,
                })
        if slack < 0:
            failures.append({
                "successor": n,
                "omega2": omega2,
                "pairs": pairs,
                "slack": slack,
            })
            if len(failures) >= 25:
                break

    result = {
        "limit": args.limit,
        "tested_reducible_successors": tested,
        "minimum_slack": minimum_slack,
        "equality_examples": equality_examples,
        "failures": failures,
        "exponential_minimum_slack": exponential_minimum_slack,
        "exponential_failures": exponential_failures,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
