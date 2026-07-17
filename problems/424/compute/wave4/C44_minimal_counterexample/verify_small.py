#!/usr/bin/env python3
"""Independent trial-division and literal-stage verifier for C44."""

from __future__ import annotations

import argparse
import json
from math import isqrt
from pathlib import Path


INF = 10**9


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_for(n: int) -> list[tuple[int, int]]:
    pairs = []
    for a in range(2, isqrt(n + 1) + 1):
        if (n + 1) % a:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            pairs.append((a, b))
    return pairs


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def structural_parent(n: int) -> int | None:
    if n > 3 and n % 2:
        return (n + 1) // 2
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q
    return None


def verify(limit: int) -> dict:
    pairs = {n: pairs_for(n) for n in range(2, limit + 1) if allowed(n)}
    member = [False] * (limit + 1)
    rank = [INF] * (limit + 1)
    member[2] = member[3] = True
    hard = []
    targets = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        n_pairs = pairs[n]
        if any(member[a] and member[b] for a, b in n_pairs):
            member[n] = True
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    targets.append((n, q, rank[q]))
            continue
        if not n_pairs:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in n_pairs
            )
        if hard_shape(n, n_pairs):
            hard.append((n, rank[n]))

    current = {n for n in range(2, limit + 1) if allowed(n)}
    death = {}
    stage = 0
    while True:
        following = {2, 3}
        for n in range(4, limit + 1):
            if allowed(n) and any(a in current and b in current for a, b in pairs[n]):
                following.add(n)
        for n in current - following:
            death[n] = stage
        if following == current:
            break
        current = following
        stage += 1

    membership_mismatches = [
        n for n in range(2, limit + 1)
        if allowed(n) and member[n] != (n in current)
    ]
    rank_mismatches = [
        {"n": n, "recursive": rank[n], "stage": death.get(n)}
        for n in range(2, limit + 1)
        if allowed(n) and not member[n] and rank[n] != death.get(n)
    ]

    root_cache = {}

    def root(n: int) -> int:
        path = []
        while n not in root_cache:
            path.append(n)
            parent = structural_parent(n)
            if parent is None:
                root_cache[n] = n
                break
            assert not member[parent] and rank[parent] < rank[n]
            n = parent
        result = root_cache[n]
        for item in path:
            root_cache[item] = result
        return result

    target_records = [
        {"child": child, "parent": parent, "rank": target_rank, "root": root(parent)}
        for child, parent, target_rank in targets
    ]

    def critical_endpoints(source: int) -> list[int]:
        source_rank = rank[source]
        result = set()
        for a, b in pairs[source]:
            missing = [rank[x] for x in (a, b) if not member[x]]
            if min(missing) != source_rank - 1:
                continue
            result.update(
                x for x in (a, b) if not member[x] and rank[x] == source_rank - 1
            )
        return sorted(result)

    exact_assertions = {
        "source_74": {
            "rank": rank[74],
            "critical": critical_endpoints(74),
            "root_8_boundaries_before": [
                row for row in target_records if row["root"] == 8 and row["child"] < 74
            ],
        },
        "adjacent_114": {
            "source_rank": rank[114],
            "hole_113_rank": rank[113],
            "parent_57_rank": rank[57],
        },
        "source_174": {
            "rank": rank[174],
            "critical": critical_endpoints(174),
            "T2_35_member": member[69],
            "T3_35_rank": rank[104],
        },
        "source_492": {
            "rank": rank[492],
            "critical": critical_endpoints(492),
            "target_449": next(row for row in target_records if row["child"] == 449),
        },
        "source_774": {
            "rank": rank[774],
            "critical": critical_endpoints(774),
            "T2_155_rank": rank[309],
            "T3_155_rank": rank[464],
        },
    }

    assert not membership_mismatches
    assert not rank_mismatches
    assert exact_assertions["source_74"] == {
        "rank": 2, "critical": [15], "root_8_boundaries_before": []
    }
    assert exact_assertions["adjacent_114"] == {
        "source_rank": 2, "hole_113_rank": 4, "parent_57_rank": 3
    }
    assert exact_assertions["source_174"] == {
        "rank": 2, "critical": [35], "T2_35_member": True, "T3_35_rank": 3
    }
    assert exact_assertions["source_492"] == {
        "rank": 3,
        "critical": [29],
        "target_449": {"child": 449, "parent": 225, "rank": 5, "root": 8},
    }
    assert exact_assertions["source_774"] == {
        "rank": 2, "critical": [155], "T2_155_rank": 4, "T3_155_rank": 3
    }

    return {
        "schema_version": 1,
        "limit": limit,
        "literal_stage_updates": stage,
        "membership_mismatches": membership_mismatches,
        "rank_mismatches": rank_mismatches,
        "hard_count": len(hard),
        "target_count": len(targets),
        "exact_assertions": exact_assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 1000:
        raise ValueError("limit must be at least 1000")
    result = verify(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
