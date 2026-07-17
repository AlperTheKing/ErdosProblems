#!/usr/bin/env python3
"""Find first empty-base lattice failures using only actual-hole directions."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
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


def hard(n: int, rows: list[tuple[int, int]]) -> bool:
    if n % 2 or not rows:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    limit = args.limit
    if limit < 594:
        raise ValueError("limit must be at least 594")

    rows = [pairs_of(n) if n >= 2 else [] for n in range(limit + 1)]
    G = [False] * (limit + 1)
    G[2] = G[3] = True
    for n in range(4, limit + 1):
        if allowed(n) and any(G[a] and G[b] for a, b in rows[n]):
            G[n] = True

    events = []
    for n in range(4, limit + 1):
        if hard(n, rows[n]):
            events.append((n, n, 1, "hard"))
    for q in range(4, (limit + 1) // 2 + 1):
        if allowed(q) and G[2 * q - 1]:
            events.append((2 * q - 1, q, -1, "terminal-parent"))
    events.sort()

    running: dict[tuple[int, int], int] = defaultdict(int)
    first_negative = None
    first_positive = None
    for event, node, coefficient, kind in events:
        local = rows[node]
        changes = []
        if len(local) == 1:
            a, b = local[0]
            changes.append((tuple(sorted((a, b))), coefficient))
        elif len(local) == 2:
            for x in local[0]:
                for y in local[1]:
                    changes.append((tuple(sorted((x, y))), -coefficient))
        for key, change in changes:
            if key[0] in (2, 3) or key[1] in (2, 3):
                continue
            if G[key[0]] or G[key[1]]:
                continue
            running[key] += change
            record = {
                "X": event,
                "D1": [key[0]],
                "D2": [key[1]],
                "mixed_difference": running[key],
                "last_node": node,
                "last_kind": kind,
                "last_node_pairs": [list(pair) for pair in local],
            }
            if running[key] < 0 and first_negative is None:
                first_negative = record
            if running[key] > 0 and first_positive is None:
                first_positive = record

    if first_negative is None or first_positive is None:
        raise AssertionError("no two-sided failure in requested range")

    result = {
        "schema_version": 1,
        "limit": limit,
        "domain": "empty-base singleton directions D1,D2 contained in actual A\\G",
        "first_submodularity_failure": first_negative,
        "first_supermodularity_failure": first_positive,
        "exhaustive_for_all_event_cutoffs_through_limit": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
