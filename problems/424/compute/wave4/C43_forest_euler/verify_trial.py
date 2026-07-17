#!/usr/bin/env python3
"""Independent trial-divisor and descending-stage verifier for C43."""

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


def build(limit: int) -> dict:
    pairs = {n: pairs_for(n) for n in range(2, limit + 1) if allowed(n)}
    member = [False] * (limit + 1)
    rank = [INF] * (limit + 1)
    member[2] = member[3] = True
    hard = []
    targets = []
    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        ps = pairs[n]
        if any(member[a] and member[b] for a, b in ps):
            member[n] = True
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    targets.append((n, q, rank[q]))
            continue
        if not ps:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in ps
            )
        if hard_shape(n, ps):
            hard.append((n, rank[n]))
    return {
        "pairs": pairs,
        "member": member,
        "rank": rank,
        "hard": hard,
        "targets": targets,
    }


def descending_check(data: dict, limit: int) -> dict:
    pairs = data["pairs"]
    current = {n for n in range(2, limit + 1) if allowed(n)}
    death = {}
    stage = 0
    while True:
        nxt = {2, 3}
        for n in range(4, limit + 1):
            if allowed(n) and any(a in current and b in current for a, b in pairs[n]):
                nxt.add(n)
        for n in current - nxt:
            death[n] = stage
        if nxt == current:
            break
        current = nxt
        stage += 1

    membership_mismatches = []
    rank_mismatches = []
    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        if (n in current) != data["member"][n]:
            membership_mismatches.append(n)
        if not data["member"][n] and death[n] != data["rank"][n]:
            rank_mismatches.append({
                "n": n,
                "descending": death[n],
                "recursive": data["rank"][n],
            })
    return {
        "updates": stage,
        "membership_mismatches": membership_mismatches,
        "rank_mismatches": rank_mismatches,
    }


class DSU:
    def __init__(self, limit: int) -> None:
        self.parent = list(range(limit + 1))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return
        if a > b:
            a, b = b, a
        self.parent[b] = a


def lower_parent_edges(data: dict, n: int) -> list[int]:
    member = data["member"]
    rank = data["rank"]
    ps = data["pairs"][n]
    if n % 2:
        return [(n + 1) // 2]
    if not hard_shape(n, ps):
        if ps:
            return [(n + 1) // 3]
        return []
    return sorted({
        x
        for a, b in ps
        for x in (a, b)
        if not member[x] and rank[x] < rank[n]
    })


def component_snapshot(data: dict, cutoff: int, depth: int) -> list[dict]:
    member = data["member"]
    rank = data["rank"]
    dsu = DSU(cutoff)
    holes = [
        n for n in range(2, cutoff + 1)
        if allowed(n) and not member[n] and rank[n] <= depth
    ]
    for n in holes:
        for p in lower_parent_edges(data, n):
            dsu.union(n, p)

    rows = {}
    for n, r in data["hard"]:
        if n > cutoff or r > depth:
            continue
        root = dsu.find(n)
        rows.setdefault(root, {"anchor": root, "hard": [], "targets": []})
        rows[root]["hard"].append(n)
    for child, parent, r in data["targets"]:
        if child > cutoff or r > depth:
            continue
        root = dsu.find(parent)
        rows.setdefault(root, {"anchor": root, "hard": [], "targets": []})
        rows[root]["targets"].append({"child": child, "parent": parent})
    for row in rows.values():
        row["deficit"] = len(row["hard"]) - len(row["targets"])
    return sorted(rows.values(), key=lambda row: row["anchor"])


def first_component_failure(data: dict, stop: int) -> dict | None:
    max_rank = max(r for n, r in data["hard"] if n <= stop)
    for cutoff in range(2, stop + 1):
        for depth in range(max_rank + 1):
            rows = component_snapshot(data, cutoff, depth)
            positive_sum = sum(max(row["deficit"], 0) for row in rows)
            if positive_sum > 1:
                return {
                    "X": cutoff,
                    "d": depth,
                    "positive_sum": positive_sum,
                    "components": rows,
                }
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.limit >= 774

    data = build(args.limit)
    stage = descending_check(data, args.limit)
    failure = first_component_failure(data, 114)
    tight_rows = component_snapshot(data, 362, 2)
    tight = {
        "X": 362,
        "d": 2,
        "global_excess": sum(row["deficit"] for row in tight_rows),
        "positive_sum": sum(max(row["deficit"], 0) for row in tight_rows),
        "negative_sum": sum(min(row["deficit"], 0) for row in tight_rows),
        "positive_count": sum(row["deficit"] > 0 for row in tight_rows),
        "negative_count": sum(row["deficit"] < 0 for row in tight_rows),
        "components": tight_rows,
    }
    sibling = {
        "pairs_774": data["pairs"][774],
        "rank_155": data["rank"][155],
        "member_309": data["member"][309],
        "rank_309": data["rank"][309],
        "rank_774": data["rank"][774],
    }
    assert not stage["membership_mismatches"]
    assert not stage["rank_mismatches"]
    assert failure is not None
    assert (failure["X"], failure["d"], failure["positive_sum"]) == (114, 2, 2)
    assert tight["global_excess"] == 1
    assert sibling == {
        "pairs_774": [(5, 155)],
        "rank_155": 1,
        "member_309": False,
        "rank_309": 4,
        "rank_774": 2,
    }

    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "descending_check": stage,
        "first_all_lower_component_failure": failure,
        "tight_prefix_component_decomposition": tight,
        "critical_sibling_witness": sibling,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
