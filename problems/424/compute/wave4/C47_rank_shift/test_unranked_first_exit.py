#!/usr/bin/env python3
"""Test whether one canonical-component exit pays each hard root.

The canonical hole forest uses the seed-2 parent for odd holes and the
seed-3 parent for seed-3-easy even holes. Splitless and hard holes are
roots. For every component, only its first generated seed-2 child is kept.
This checker tests H(X) <= Q_first(X) + 1 at every coordinate.
"""

from __future__ import annotations

import argparse
import json
from array import array
from pathlib import Path

from test_rank_shift import INF, allowed, hard_shape, pairs_for, spf_sieve


def audit(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    root = array("I", [0]) * (limit + 1)
    exit_count = bytearray(limit + 1)
    member[2] = member[3] = 1

    hard_count = 0
    selected_exit_count = 0
    maximum_excess = -10**18
    maximum_record = None
    first_strict_failure = None
    first_additive_one_failure = None

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        generated = any(member[a] and member[b] for a, b in pairs)

        if generated:
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    component = root[q]
                    if component == 0 or rank[q] == INF:
                        raise AssertionError(("bad target parent", n, q))
                    if exit_count[component] == 0:
                        selected_exit_count += 1
                    if exit_count[component] < 255:
                        exit_count[component] += 1
        else:
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

            hard = hard_shape(n, pairs)
            if n % 2:
                q = (n + 1) // 2
                if member[q] or root[q] == 0 or rank[q] >= rank[n]:
                    raise AssertionError(("bad seed-2 forest edge", n, q))
                root[n] = root[q]
            elif not hard and pairs:
                q = (n + 1) // 3
                if member[q] or root[q] == 0 or rank[q] >= rank[n]:
                    raise AssertionError(("bad seed-3 forest edge", n, q))
                root[n] = root[q]
            else:
                root[n] = n

            if hard:
                hard_count += 1

        excess = hard_count - selected_exit_count
        record = {
            "X": n,
            "H": hard_count,
            "Q_first": selected_exit_count,
            "excess": excess,
        }
        if excess > maximum_excess:
            maximum_excess = excess
            maximum_record = record
        if first_strict_failure is None and excess > 0:
            first_strict_failure = record
        if first_additive_one_failure is None and excess > 1:
            first_additive_one_failure = record

    return {
        "schema_version": 1,
        "limit": limit,
        "statement": "H(X) <= first_seed2_exit_components(X) + 1",
        "hard_total": hard_count,
        "selected_exit_total": selected_exit_count,
        "maximum_excess": maximum_excess,
        "maximum_record": maximum_record,
        "first_strict_failure": first_strict_failure,
        "first_additive_one_failure": first_additive_one_failure,
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
