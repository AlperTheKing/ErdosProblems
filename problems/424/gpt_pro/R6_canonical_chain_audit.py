#!/usr/bin/env python3
"""Independent exact replay of the CX-R6 canonical-chain identity."""

from __future__ import annotations

import json
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_for(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def build(limit: int) -> tuple[bytearray, list[int], list[list[tuple[int, int]]]]:
    member = bytearray(limit + 1)
    rank = [-1] * (limit + 1)
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    member[2] = member[3] = 1
    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs[n] = pairs_for(n)
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = 1
            continue
        if not pairs[n]:
            rank[n] = 0
            continue
        blockers = []
        for a, b in pairs[n]:
            missing = [rank[x] for x in (a, b) if not member[x]]
            assert missing and min(missing) >= 0
            blockers.append(min(missing))
        rank[n] = 1 + max(blockers)
    return member, rank, pairs


def seed3_easy(n: int) -> bool:
    if n % 2 or (n + 1) % 3:
        return False
    parent = (n + 1) // 3
    return parent != 3 and allowed(parent)


def hard(n: int, pairs: list[list[tuple[int, int]]]) -> bool:
    return n % 2 == 0 and bool(pairs[n]) and not seed3_easy(n)


def audit(limit: int = 2000) -> dict:
    member, rank, pairs = build(limit + 1)
    max_rank = max(rank)
    checks = 0
    maximum_gap = -10**9
    maximum_event = None

    for x in range(4, limit + 1):
        y = (x + 1) // 2
        for d in range(max_rank + 1):
            w = {
                n
                for n in range(2, x + 1)
                if allowed(n) and not member[n] and rank[n] <= d
            }

            # Canonical-parent closure.
            for n in w:
                if n % 2:
                    parent = (n + 1) // 2
                    if n != 3:
                        assert parent in w
                        assert rank[n] >= rank[parent] + 1
                elif seed3_easy(n):
                    parent = (n + 1) // 3
                    assert parent in w
                    assert rank[n] >= rank[parent] + 1

            h = sum(hard(n, pairs) for n in w)
            e = sum(not pairs[n] for n in w)
            j = sum(seed3_easy(n) for n in w)

            q = r = c = 0
            terminals = []
            for n in w:
                child = 2 * n - 1
                if child in w:
                    continue
                terminals.append(n)
                if n > y:
                    c += 1
                elif member[child]:
                    q += 1
                else:
                    assert child <= x and allowed(child)
                    assert rank[child] > d
                    r += 1

            assert h + e + j == len(terminals)
            assert len(terminals) == q + r + c
            assert h + e + j == q + r + c
            assert h - q == r + c - e - j

            gap = h - q
            if gap > maximum_gap:
                maximum_gap = gap
                maximum_event = {
                    "X": x,
                    "d": d,
                    "H": h,
                    "Q": q,
                    "R": r,
                    "C": c,
                    "E": e,
                    "J": j,
                }
            checks += 1

    result = {
        "limit": limit,
        "max_rank": max_rank,
        "checked_X_d_pairs": checks,
        "maximum_H_minus_Q": maximum_gap,
        "maximum_event": maximum_event,
        "identity_verified": True,
    }
    out = Path(__file__).with_name("R6_canonical_chain_audit_2000.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))

