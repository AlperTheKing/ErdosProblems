#!/usr/bin/env python3
"""Exact probes for multiplier-based C39 injections.

All membership and obstruction ranks are reconstructed from the grounded
recurrence.  The candidate edges are deliberately stronger than a single
missing-factor map: a hard source may use any generated odd endpoint in any
of its factorizations and any earlier even generated multiplier 2*k.
"""

from __future__ import annotations

import argparse
import json
from array import array
from pathlib import Path


INF = 65535


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for m in range(p * p, limit + 1, p):
            if spf[m] == m:
                spf[m] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old):
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
    return sorted(result)


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def augment(source: int, edges: list[list[int]], owner: list[int],
            seen: list[int], stamp: int) -> bool:
    for target in edges[source]:
        if seen[target] == stamp:
            continue
        seen[target] = stamp
        if owner[target] < 0 or augment(owner[target], edges, owner, seen, stamp):
            owner[target] = source
            return True
    return False


def audit(limit: int, multiplier_cap: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]

    hard: list[tuple[int, int]] = []
    targets: list[tuple[int, int, int]] = []
    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs[n] = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    targets.append((n, q, rank[q]))
            continue
        if not pairs[n]:
            rank[n] = 0
        else:
            blockers = []
            for a, b in pairs[n]:
                missing = [rank[x] for x in (a, b) if not member[x]]
                assert missing and INF not in missing
                blockers.append(min(missing))
            rank[n] = 1 + max(blockers)
        if hard_shape(n, pairs[n]):
            hard.append((n, rank[n]))

    target_index = {child: i for i, (child, _, _) in enumerate(targets)}
    multipliers = [
        k for k in range(2, min(multiplier_cap, limit // 2) + 1)
        if 2 * k <= limit and member[2 * k]
    ]

    universal_tests = []
    for k in multipliers:
        tested = 0
        first_generated = None
        for a in range(3, limit // k + 1, 2):
            if not allowed(a) or not member[a]:
                continue
            q = k * a
            if not allowed(q):
                continue
            tested += 1
            if member[q]:
                first_generated = {"a": a, "q": q}
                break
        universal_tests.append({
            "k": k,
            "twice_k": 2 * k,
            "tested_before_failure": tested,
            "first_generated_product": first_generated,
        })

    edge_rows: list[list[int]] = []
    zero_degree = []
    first_rank_failure = None
    for source, source_rank in hard:
        children = set()
        generated_endpoints = {
            x for a, b in pairs[source] for x in (a, b) if member[x]
        }
        for a in generated_endpoints:
            if a % 2 == 0:
                continue
            for k in multipliers:
                child = 2 * k * a - 1
                if child > source:
                    break
                q = k * a
                if (
                    child in target_index
                    and rank[q] <= source_rank
                    and member[2 * k]
                    and member[a]
                ):
                    children.add(target_index[child])
        row = sorted(children, key=lambda i: targets[i][0])
        edge_rows.append(row)
        if not row:
            zero_degree.append({
                "source": source,
                "rank": source_rank,
                "pairs": pairs[source],
                "generated_endpoints": sorted(generated_endpoints),
            })

    owner = [-1] * len(targets)
    seen = [0] * len(targets)
    matched = 0
    unmatched = []
    for source_index, row in enumerate(edge_rows):
        if augment(source_index, edge_rows, owner, seen, source_index + 1):
            matched += 1
        else:
            source, source_rank = hard[source_index]
            unmatched.append({
                "source": source,
                "rank": source_rank,
                "degree": len(row),
            })

    hard_counts = [0] * 64
    target_counts = [0] * 64
    target_pos = 0
    first_lower_rank_credit_failure = None
    maximum_lower_rank_credit_excess = 0
    for source, source_rank in hard:
        while target_pos < len(targets) and targets[target_pos][0] <= source:
            target_counts[targets[target_pos][2]] += 1
            target_pos += 1
        hard_counts[source_rank] += 1
        h = q = 0
        for d in range(64):
            h += hard_counts[d]
            q += target_counts[d]
            if h > q + 1 and first_rank_failure is None:
                first_rank_failure = {"X": source, "d": d, "H": h, "Q": q}
        for d in range(3, 64):
            h = sum(hard_counts[:d + 1])
            q = sum(target_counts[:d])
            excess = h - q
            maximum_lower_rank_credit_excess = max(
                maximum_lower_rank_credit_excess, excess
            )
            if excess > 0 and first_lower_rank_credit_failure is None:
                first_lower_rank_credit_failure = {
                    "X": source, "d": d, "H_le_d": h, "Q_le_d_minus_1": q,
                    "excess": excess,
                }

    hard_at = {source: source_rank for source, source_rank in hard}
    target_at = {child: target_rank for child, _, target_rank in targets}
    paired_hard = [0] * 64
    paired_target = [0] * 64
    odd_strict_failures = []
    even_unit_defects = []
    pointwise_pair_failures = []
    maximum_odd_excess = 0
    for x in range(2, limit + 1):
        if x in target_at:
            paired_target[target_at[x]] += 1
        if x in hard_at:
            paired_hard[hard_at[x]] += 1
        h = q = 0
        positive = []
        for d in range(64):
            h += paired_hard[d]
            q += paired_target[d]
            if h > q:
                positive.append({"d": d, "H": h, "Q": q, "excess": h - q})
        if x % 2:
            maximum_odd_excess = max(
                [maximum_odd_excess] + [row["excess"] for row in positive]
            )
            if positive:
                odd_strict_failures.append({"X": x, "positive": positive})
        elif positive:
            even_unit_defects.append({
                "X": x,
                "positive": positive,
                "next_target_rank": target_at.get(x + 1),
            })

    target_by_parent = {parent: (child, target_rank) for child, parent, target_rank in targets}
    for source, source_rank in hard:
        s = (source + 2) // 2
        hit = target_by_parent.get(s)
        if hit is None or hit[1] > source_rank:
            pointwise_pair_failures.append({
                "source": source,
                "source_rank": source_rank,
                "half_coordinate": s,
                "target": hit,
            })

    return {
        "schema_version": 1,
        "limit": limit,
        "multiplier_cap": multiplier_cap,
        "hard_count": len(hard),
        "target_count": len(targets),
        "grounded_rank_prefix_first_failure": first_rank_failure,
        "paired_prefix": {
            "maximum_odd_excess": maximum_odd_excess,
            "odd_strict_failure_count": len(odd_strict_failures),
            "odd_strict_failure_prefix": odd_strict_failures[:20],
            "even_unit_defects": even_unit_defects[:20],
            "pointwise_same_half_coordinate_failure_count": len(pointwise_pair_failures),
            "pointwise_same_half_coordinate_failure_prefix": pointwise_pair_failures[:20],
        },
        "lower_rank_credit": {
            "claim": "H_le_d(X) <= Q_le_(d-1)(X) for d>=3",
            "maximum_excess": maximum_lower_rank_credit_excess,
            "first_failure": first_lower_rank_credit_failure,
        },
        "universal_multiplier_tests": universal_tests,
        "multiplier_edge_graph": {
            "multiplier_count": len(multipliers),
            "edge_count": sum(map(len, edge_rows)),
            "zero_degree_count": len(zero_degree),
            "zero_degree_prefix": zero_degree[:20],
            "matched": matched,
            "unmatched": len(hard) - matched,
            "unmatched_prefix": unmatched[:20],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--multiplier-cap", type=int, default=500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(args.limit, args.multiplier_cap)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": payload["limit"],
        "hard_count": payload["hard_count"],
        "target_count": payload["target_count"],
        "rank_failure": payload["grounded_rank_prefix_first_failure"],
        "paired_prefix": payload["paired_prefix"],
        "lower_rank_credit": payload["lower_rank_credit"],
        "edge_graph": payload["multiplier_edge_graph"],
    }, indent=2))


if __name__ == "__main__":
    main()
