#!/usr/bin/env python3
"""Exact rank/event audit for critical-parent forest formulations."""

from __future__ import annotations

import argparse
import json
from array import array
from pathlib import Path


INF = 65535
SPLITLESS, ODD, EASY3, HARD = range(1, 5)


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
        old_size = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old_size):
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


class ExactData:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.member = bytearray(limit + 1)
        self.rank = array("H", [INF]) * (limit + 1)
        self.kind = bytearray(limit + 1)
        self.fixed_parent = array("I", [0]) * (limit + 1)
        self.target_parent = array("I", [0]) * (limit + 1)
        self.critical: list[list[int]] = [[] for _ in range(limit + 1)]
        self.lower_blockers: list[list[int]] = [[] for _ in range(limit + 1)]
        self.hard_count = 0
        self.target_count = 0
        self.hole_count = 0
        self.max_rank = 0


def build_exact(limit: int) -> ExactData:
    data = ExactData(limit)
    spf = spf_sieve(limit + 1)
    data.member[2] = data.member[3] = 1

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(data.member[a] and data.member[b] for a, b in pairs):
            data.member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not data.member[q]:
                    data.target_parent[n] = q
                    data.target_count += 1
            continue

        data.hole_count += 1
        if not pairs:
            data.rank[n] = 0
            data.kind[n] = SPLITLESS
        else:
            pair_scores = []
            for a, b in pairs:
                missing = [x for x in (a, b) if not data.member[x]]
                assert missing
                pair_scores.append(min(data.rank[x] for x in missing))
            data.rank[n] = 1 + max(pair_scores)
            if n % 2:
                p = (n + 1) // 2
                assert not data.member[p] and data.rank[p] < data.rank[n]
                data.kind[n] = ODD
                data.fixed_parent[n] = p
            elif hard_shape(n, pairs):
                data.kind[n] = HARD
                data.hard_count += 1
                critical_rank = data.rank[n] - 1
                data.critical[n] = sorted({
                    x
                    for (a, b), score in zip(pairs, pair_scores)
                    if score == critical_rank
                    for x in (a, b)
                    if not data.member[x] and data.rank[x] == critical_rank
                })
                data.lower_blockers[n] = sorted({
                    x
                    for a, b in pairs
                    for x in (a, b)
                    if not data.member[x] and data.rank[x] < data.rank[n]
                })
                assert data.critical[n]
            else:
                p = (n + 1) // 3
                assert allowed(p) and p != 3
                assert not data.member[p] and data.rank[p] < data.rank[n]
                data.kind[n] = EASY3
                data.fixed_parent[n] = p
        data.max_rank = max(data.max_rank, data.rank[n])
    return data


def parent_edges(data: ExactData, n: int, model: str) -> list[int]:
    fixed = data.fixed_parent[n]
    if fixed:
        return [fixed]
    if data.kind[n] != HARD:
        return []
    if model == "canonical_min":
        return [data.critical[n][0]]
    if model == "canonical_max":
        return [data.critical[n][-1]]
    if model == "all_critical":
        return data.critical[n]
    if model == "all_lower_blockers":
        return data.lower_blockers[n]
    raise ValueError(model)


class BalanceDSU:
    def __init__(self, size: int) -> None:
        self.parent = array("i", [-1]) * size
        self.anchor = array("I", [0]) * size
        self.hard = array("i", [0]) * size
        self.exits = array("i", [0]) * size
        self.positive_sum = 0
        self.positive_count = 0
        self.components = 0

    def add(self, x: int) -> None:
        assert self.parent[x] == -1
        self.parent[x] = x
        self.anchor[x] = x
        self.components += 1

    def find(self, x: int) -> int:
        p = self.parent[x]
        assert p >= 0
        while p != self.parent[p]:
            p = self.parent[p]
        while x != p:
            nxt = self.parent[x]
            self.parent[x] = p
            x = nxt
        return p

    def _remove_positive(self, root: int) -> None:
        balance = self.hard[root] - self.exits[root]
        if balance > 0:
            self.positive_sum -= balance
            self.positive_count -= 1

    def _add_positive(self, root: int) -> None:
        balance = self.hard[root] - self.exits[root]
        if balance > 0:
            self.positive_sum += balance
            self.positive_count += 1

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        self._remove_positive(ra)
        self._remove_positive(rb)
        if self.anchor[ra] > self.anchor[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.anchor[ra] = min(self.anchor[ra], self.anchor[rb])
        self.hard[ra] += self.hard[rb]
        self.exits[ra] += self.exits[rb]
        self.components -= 1
        self._add_positive(ra)

    def add_hard(self, x: int) -> None:
        root = self.find(x)
        self._remove_positive(root)
        self.hard[root] += 1
        self._add_positive(root)

    def add_exit(self, x: int) -> None:
        root = self.find(x)
        self._remove_positive(root)
        self.exits[root] += 1
        self._add_positive(root)

    def positive_rows(self) -> list[dict]:
        rows = []
        for x, p in enumerate(self.parent):
            if p != x:
                continue
            balance = self.hard[x] - self.exits[x]
            if balance > 0:
                rows.append({
                    "anchor": self.anchor[x],
                    "hard": self.hard[x],
                    "exits": self.exits[x],
                    "deficit": balance,
                })
        return sorted(rows, key=lambda row: (-row["deficit"], row["anchor"]))


def audit_model_rank(data: ExactData, model: str, depth: int) -> dict:
    dsu = BalanceDSU(data.limit + 1)
    global_balance = 0
    max_global = 0
    max_positive_sum = 0
    max_positive_count = 0
    first_failure = None

    for n in range(2, data.limit + 1):
        if not data.member[n] and data.rank[n] <= depth:
            dsu.add(n)
            for p in parent_edges(data, n, model):
                assert p < n and data.rank[p] < data.rank[n]
                dsu.union(n, p)
            if data.kind[n] == HARD:
                dsu.add_hard(n)
                global_balance += 1

        q = data.target_parent[n]
        if q and data.rank[q] <= depth:
            dsu.add_exit(q)
            global_balance -= 1

        max_global = max(max_global, global_balance)
        max_positive_sum = max(max_positive_sum, dsu.positive_sum)
        max_positive_count = max(max_positive_count, dsu.positive_count)
        if dsu.positive_sum > 1 and first_failure is None:
            first_failure = {
                "X": n,
                "d": depth,
                "global_excess": global_balance,
                "positive_sum": dsu.positive_sum,
                "positive_count": dsu.positive_count,
                "components": dsu.components,
                "positive_components": dsu.positive_rows()[:20],
            }

    return {
        "d": depth,
        "maximum_global_excess": max_global,
        "maximum_positive_component_sum": max_positive_sum,
        "maximum_positive_component_count": max_positive_count,
        "first_component_failure": first_failure,
    }


def witness_snapshot(
    data: ExactData, model: str, cutoff: int, depth: int
) -> list[dict]:
    dsu = BalanceDSU(data.limit + 1)
    for n in range(2, cutoff + 1):
        if not data.member[n] and data.rank[n] <= depth:
            dsu.add(n)
            for p in parent_edges(data, n, model):
                dsu.union(n, p)
            if data.kind[n] == HARD:
                dsu.add_hard(n)
        q = data.target_parent[n]
        if q and data.rank[q] <= depth:
            dsu.add_exit(q)

    rows: dict[int, dict] = {}

    def row_for(x: int) -> dict:
        root = dsu.find(x)
        if root not in rows:
            rows[root] = {
                "anchor": dsu.anchor[root],
                "hard_events": [],
                "target_events": [],
                "hole_members": [],
            }
        return rows[root]

    for n in range(2, cutoff + 1):
        if not data.member[n] and data.rank[n] <= depth:
            row_for(n)["hole_members"].append({"n": n, "rank": data.rank[n]})
            if data.kind[n] == HARD:
                row_for(n)["hard_events"].append({
                    "n": n,
                    "rank": data.rank[n],
                    "parent_edges": parent_edges(data, n, model),
                    "critical": data.critical[n],
                })
        q = data.target_parent[n]
        if q and data.rank[q] <= depth:
            row_for(q)["target_events"].append({
                "child": n,
                "parent": q,
                "rank": data.rank[q],
            })

    event_rows = []
    for row in rows.values():
        if not row["hard_events"] and not row["target_events"]:
            continue
        row["hard_count"] = len(row["hard_events"])
        row["exit_count"] = len(row["target_events"])
        row["deficit"] = row["hard_count"] - row["exit_count"]
        event_rows.append(row)
    return sorted(event_rows, key=lambda row: row["anchor"])


def audit_model(data: ExactData, model: str) -> dict:
    by_rank = [
        audit_model_rank(data, model, depth)
        for depth in range(data.max_rank + 1)
    ]
    failures = [
        row["first_component_failure"]
        for row in by_rank
        if row["first_component_failure"] is not None
    ]
    first_failure = (
        min(failures, key=lambda row: (row["X"], row["d"]))
        if failures else None
    )
    if first_failure is not None:
        first_failure["snapshot"] = witness_snapshot(
            data, model, first_failure["X"], first_failure["d"]
        )
    return {
        "model": model,
        "claim": "sum_C max(H_C_le_d(X)-Q_C_le_d(X),0) <= 1",
        "first_failure": first_failure,
        "maximum_global_excess": max(
            row["maximum_global_excess"] for row in by_rank
        ),
        "maximum_positive_component_sum": max(
            row["maximum_positive_component_sum"] for row in by_rank
        ),
        "maximum_positive_component_count": max(
            row["maximum_positive_component_count"] for row in by_rank
        ),
        "by_rank": by_rank,
    }


def audit_siblings(data: ExactData) -> dict:
    first_failure = None
    first_nonunit = None
    histogram = {"healed": 0, "unit_hole": 0, "larger_jump_hole": 0}

    for h in range(2, data.limit + 1):
        if data.kind[h] != HARD:
            continue
        rows = []
        for p in data.critical[h]:
            child = 2 * p - 1
            assert child < h
            if data.member[child]:
                histogram["healed"] += 1
                rows.append({
                    "parent": p,
                    "parent_rank": data.rank[p],
                    "seed2_child": child,
                    "status": "healed",
                })
            else:
                jump = data.rank[child] - data.rank[p]
                key = "unit_hole" if jump == 1 else "larger_jump_hole"
                histogram[key] += 1
                if jump != 1 and first_nonunit is None:
                    first_nonunit = {
                        "hard": h,
                        "hard_rank": data.rank[h],
                        "parent": p,
                        "parent_rank": data.rank[p],
                        "seed2_child": child,
                        "child_rank": data.rank[child],
                        "jump": jump,
                    }
                rows.append({
                    "parent": p,
                    "parent_rank": data.rank[p],
                    "seed2_child": child,
                    "status": "hole",
                    "child_rank": data.rank[child],
                })
        if first_failure is None and not any(
            row["status"] == "healed"
            or row.get("child_rank") == data.rank[h]
            for row in rows
        ):
            first_failure = {
                "hard": h,
                "hard_rank": data.rank[h],
                "critical_choices": rows,
            }

    return {
        "claim": (
            "each hard h has critical p with T2(p) healed or "
            "rho(T2(p))=rho(h)"
        ),
        "first_failure": first_failure,
        "first_nonunit_critical_jump": first_nonunit,
        "choice_histogram": histogram,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = build_exact(args.limit)
    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "exact_census": {
            "holes": data.hole_count,
            "hard": data.hard_count,
            "targets": data.target_count,
            "maximum_rank": data.max_rank,
        },
        "critical_seed2_sibling": audit_siblings(data),
        "component_models": [
            audit_model(data, model)
            for model in (
                "canonical_min",
                "canonical_max",
                "all_critical",
                "all_lower_blockers",
            )
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": payload["limit"],
        "exact_census": payload["exact_census"],
        "critical_seed2_sibling": payload["critical_seed2_sibling"],
        "component_models": [
            {
                key: row[key]
                for key in (
                    "model",
                    "first_failure",
                    "maximum_global_excess",
                    "maximum_positive_component_sum",
                    "maximum_positive_component_count",
                )
            }
            for row in payload["component_models"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
