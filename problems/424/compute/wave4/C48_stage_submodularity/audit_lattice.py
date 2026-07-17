#!/usr/bin/env python3
"""Exact red-team gates for C48 stage monotonicity and lattice claims."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_of(n: int) -> list[tuple[int, int]]:
    out = []
    for a in range(2, math.isqrt(n + 1) + 1):
        if (n + 1) % a:
            continue
        b = (n + 1) // a
        if a < b and allowed(a) and allowed(b):
            out.append((a, b))
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def model(limit: int) -> tuple[list[list[tuple[int, int]]], list[bool], list[int | None]]:
    pairs = [pairs_of(n) if n >= 2 else [] for n in range(limit + 1)]
    member = [False] * (limit + 1)
    rank: list[int | None] = [None] * (limit + 1)
    member[2] = member[3] = True
    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = True
        elif not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x]) for a, b in pairs[n]
            )
    return pairs, member, rank


def first_rank_failures(limit: int, pairs, member, rank) -> dict:
    hard = [(n, rank[n]) for n in range(2, limit + 1)
            if hard_shape(n, pairs[n]) and not member[n]]
    targets = [(2 * q - 1, rank[q])
               for q in range(2, (limit + 1) // 2 + 1)
               if allowed(q) and not member[q] and member[2 * q - 1]]
    max_rank = max([0] + [r for _, r in hard] + [r for _, r in targets])
    cutoffs = sorted({n for n, _ in hard} | {n for n, _ in targets})
    old = {x: 0 for x in cutoffs}
    first_nondecreasing = None
    first_rd = None
    maxima = []
    for d in range(max_rank + 1):
        row_max = (-10**9, 0)
        for x in cutoffs:
            value = sum(n <= x and r <= d for n, r in hard) - sum(
                n <= x and r <= d for n, r in targets
            )
            if value > row_max[0]:
                row_max = (value, x)
            if d > 0 and value > old[x] and first_nondecreasing is None:
                first_nondecreasing = {
                    "X": x, "d": d, "B_previous": old[x], "B_current": value
                }
            if d >= 3 and value > 0 and value > old[x] and first_rd is None:
                first_rd = {
                    "X": x, "d": d, "B_previous": old[x], "B_current": value
                }
            old[x] = value
        maxima.append({"d": d, "maximum": row_max[0], "first_X": row_max[1]})
    return {
        "B_d_nonincreasing_failure": first_nondecreasing,
        "positive_rank_descent_d_ge_3_failure": first_rd,
        "rank_maxima": maxima,
    }


def unsupported(limit: int, pairs, deleted: frozenset[int]) -> frozenset[int]:
    return frozenset(
        n for n in range(4, limit + 1) if allowed(n)
        and not any(a not in deleted and b not in deleted for a, b in pairs[n])
    )


def weight(D: frozenset[int], X: int, hard: set[int], parents: set[int]) -> int:
    return sum(n <= X and n in hard for n in D) - sum(
        2 * q - 1 <= X and q in parents for q in D
    )


def lattice_failures(limit: int, pairs, member, rank) -> dict:
    hard = {n for n in range(2, limit + 1)
            if hard_shape(n, pairs[n]) and not member[n]}
    parents = {q for q in range(2, (limit + 1) // 2 + 1)
               if allowed(q) and not member[q] and member[2 * q - 1]}
    events = sorted(hard | {2 * q - 1 for q in parents})
    values = [n for n in range(4, limit + 1) if allowed(n)]
    empty = unsupported(limit, pairs, frozenset())
    singles = {n: unsupported(limit, pairs, frozenset({n})) for n in values}
    sub = sup = None
    for i, a in enumerate(values):
        for b in values[i + 1:]:
            both = unsupported(limit, pairs, frozenset({a, b}))
            for X in events:
                lhs = weight(singles[a], X, hard, parents) + weight(
                    singles[b], X, hard, parents
                )
                rhs = weight(both, X, hard, parents) + weight(empty, X, hard, parents)
                if lhs < rhs and sub is None:
                    sub = {"X": X, "D1": [a], "D2": [b], "lhs": lhs, "rhs": rhs}
                if lhs > rhs and sup is None:
                    sup = {"X": X, "D1": [a], "D2": [b], "lhs": lhs, "rhs": rhs}
                if sub and sup:
                    return {"submodularity_failure": sub, "supermodularity_failure": sup}
    return {"submodularity_failure": sub, "supermodularity_failure": sup}


def local_death_submodularity(limit: int, pairs) -> dict | None:
    for n in range(4, limit + 1):
        if len(pairs[n]) < 2:
            continue
        (a, _), (c, _) = pairs[n][:2]
        if a in (2, 3) or c in (2, 3):
            continue
        return {
            "n": n,
            "pairs": pairs[n],
            "D1": [a],
            "D2": [c],
            "values": {"u_D1": 0, "u_D2": 0, "u_union": 1, "u_intersection": 0},
        }
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--lattice-limit", type=int, default=300)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pairs, member, rank = model(args.limit)
    small_pairs, small_member, small_rank = model(args.lattice_limit)
    result = {
        "schema_version": 1,
        "limit": args.limit,
        "rank_tests": first_rank_failures(args.limit, pairs, member, rank),
        "local_death_indicator_submodularity_failure": local_death_submodularity(
            args.limit, pairs
        ),
        "signed_one_step_lattice_tests": lattice_failures(
            args.lattice_limit, small_pairs, small_member, small_rank
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
