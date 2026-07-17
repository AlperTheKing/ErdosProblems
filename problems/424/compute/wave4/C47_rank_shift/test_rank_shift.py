#!/usr/bin/env python3
"""Exact gate for a rank-shifted hard/target inequality in Problem 424.

Tests, at every coordinate X and rank d,

    H_{<=d}(X) <= Q_{<=d-1}(X) + 1,

where target events occur at the generated child 2q-1 and carry the
obstruction rank of their missing parent q.  All generation and rank
computations use exact divisor enumeration.
"""

from __future__ import annotations

import argparse
import json
from array import array
from pathlib import Path


INF = 65535
MAX_RANK = 64


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


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old_length = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old_length):
                result.append(result[i] * power)
    return result


def pairs_for(n: int, spf: array) -> list[tuple[int, int]]:
    result = []
    for a in divisors(n + 1, spf):
        if a < 2:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return result


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def audit(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1

    hard_events: list[tuple[int, int]] = []
    target_events: list[tuple[int, int]] = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs):
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    if rank[q] == INF:
                        raise AssertionError(("unknown target rank", n, q))
                    target_events.append((n, rank[q]))
            continue

        if not pairs:
            rank[n] = 0
        else:
            blocker_scores = []
            for a, b in pairs:
                missing = [rank[x] for x in (a, b) if not member[x]]
                if not missing or INF in missing:
                    raise AssertionError(("bad blocker", n, a, b, missing))
                blocker_scores.append(min(missing))
            rank[n] = 1 + max(blocker_scores)

        if rank[n] >= MAX_RANK:
            raise AssertionError(("rank overflow", n, rank[n]))
        if hard_shape(n, pairs):
            hard_events.append((n, rank[n]))

    hard_by_x = {x: r for x, r in hard_events}
    target_by_x = {x: r for x, r in target_events}
    hard_exact = [0] * MAX_RANK
    target_exact = [0] * MAX_RANK
    first_failure = None
    first_strict_failure = None
    maximum_excess = -10**18
    maximum_record = None

    for x in sorted(set(hard_by_x) | set(target_by_x)):
        if x in target_by_x:
            target_exact[target_by_x[x]] += 1
        if x in hard_by_x:
            hard_exact[hard_by_x[x]] += 1

        hard_prefix = 0
        target_prefix_previous = 0
        for d in range(MAX_RANK):
            hard_prefix += hard_exact[d]
            if d > 0:
                target_prefix_previous += target_exact[d - 1]
            excess = hard_prefix - target_prefix_previous
            record = {
                "X": x,
                "d": d,
                "H_le_d": hard_prefix,
                "Q_le_d_minus_1": target_prefix_previous,
                "excess": excess,
            }
            if excess > maximum_excess:
                maximum_excess = excess
                maximum_record = record
            if first_strict_failure is None and excess > 0:
                first_strict_failure = record
            if first_failure is None and excess > 1:
                first_failure = record

    return {
        "schema_version": 1,
        "limit": limit,
        "statement": "H_le_d(X) <= Q_le_d_minus_1(X) + 1",
        "hard_total": len(hard_events),
        "target_total": len(target_events),
        "maximum_rank": max([r for _, r in hard_events + target_events], default=0),
        "maximum_excess": maximum_excess,
        "maximum_record": maximum_record,
        "first_strict_failure": first_strict_failure,
        "first_additive_one_failure": first_failure,
        "hard_exact_by_rank": {str(i): v for i, v in enumerate(hard_exact) if v},
        "target_exact_by_rank": {str(i): v for i, v in enumerate(target_exact) if v},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
