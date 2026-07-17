#!/usr/bin/env python3
"""Exact global weighted-potential audit for the least grounded set G.

The candidates deliberately pool target mass across canonical T2/T3
components.  All comparisons are integer comparisons after clearing one
global denominator.
"""

from __future__ import annotations

import argparse
import json
import math
from array import array
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Callable


INF = 65535


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
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
    return sorted(result)


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


def build_ground(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    splitless = bytearray(limit + 1)
    member[2] = member[3] = 1
    hard: list[dict] = []
    targets: list[dict] = []
    r3_exits: list[dict] = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs):
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    targets.append({"child": n, "parent": q, "rank": rank[q]})
            if n % 2 == 0 and (n + 1) % 3 == 0:
                q = (n + 1) // 3
                if q % 2 and allowed(q) and not member[q]:
                    r3_exits.append({"child": n, "parent": q, "rank": rank[q]})
            continue

        if not pairs:
            rank[n] = 0
            splitless[n] = 1
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in pairs
            )
        if hard_shape(n, pairs):
            hard.append({"source": n, "rank": rank[n], "pairs": pairs})

    root_cache: dict[int, int] = {}

    def structural_root(n: int) -> int:
        path = []
        while n not in root_cache:
            path.append(n)
            parent = structural_parent(n)
            if parent is None:
                root_cache[n] = n
                break
            if member[parent] or rank[parent] >= rank[n]:
                raise AssertionError(("bad canonical edge", n, parent))
            n = parent
        root = root_cache[n]
        for value in path:
            root_cache[value] = root
        return root

    ordinals: Counter[int] = Counter()
    for target in targets:
        root = structural_root(target["parent"])
        ordinals[root] += 1
        target["root"] = root
        target["ordinal"] = ordinals[root]

    return {
        "member": member,
        "rank": rank,
        "splitless": splitless,
        "hard": hard,
        "targets": targets,
        "r3_exits": r3_exits,
        "maximum_rank": max(
            [0] + [row["rank"] for row in hard] + [row["rank"] for row in targets]
        ),
        "maximum_ordinal": max([0] + [row["ordinal"] for row in targets]),
    }


def event_witness(data: dict, x: int, coefficient: list[int]) -> dict:
    hard_rows = [
        {"source": row["source"], "rank": row["rank"]}
        for row in data["hard"]
        if row["source"] <= x
    ]
    target_rows = [
        {
            "child": row["child"],
            "parent": row["parent"],
            "rank": row["rank"],
            "root": row["root"],
            "ordinal": row["ordinal"],
        }
        for row in data["targets"]
        if row["child"] <= x
    ]
    return {
        "exact_layer_polynomial_H_minus_Q": coefficient,
        "hard_events": hard_rows if len(hard_rows) <= 100 else hard_rows[:100],
        "target_events": target_rows if len(target_rows) <= 100 else target_rows[:100],
        "event_lists_truncated": len(hard_rows) > 100 or len(target_rows) > 100,
    }


def sweep(
    data: dict,
    name: str,
    denominator: int,
    hard_weight: Callable[[dict], int],
    target_weight: Callable[[dict], int],
) -> dict:
    events = [
        (row["source"], 1, row) for row in data["hard"]
    ] + [
        (row["child"], -1, row) for row in data["targets"]
    ]
    events.sort(key=lambda item: item[0])
    deficit = 0
    maximum = 0
    maximum_event = None
    first_positive = None
    last_positive = None
    hard_exact = [0] * (data["maximum_rank"] + 1)
    target_exact = [0] * (data["maximum_rank"] + 1)

    for coordinate, sign, row in events:
        if sign > 0:
            deficit += hard_weight(row)
            hard_exact[row["rank"]] += 1
        else:
            deficit -= target_weight(row)
            target_exact[row["rank"]] += 1
        if deficit > maximum:
            maximum = deficit
            maximum_event = {
                "X": coordinate,
                "kind": "hard" if sign > 0 else "target",
                "event_rank": row["rank"],
                "deficit_numerator": deficit,
                "deficit": str(Fraction(deficit, denominator)),
            }
        if deficit > 0 and first_positive is None:
            coefficient = [
                hard_exact[d] - target_exact[d]
                for d in range(data["maximum_rank"] + 1)
            ]
            first_positive = {
                "X": coordinate,
                "kind": "hard" if sign > 0 else "target",
                "event_rank": row["rank"],
                "deficit_numerator": deficit,
                "deficit": str(Fraction(deficit, denominator)),
                **event_witness(data, coordinate, coefficient),
            }
        if deficit > 0:
            last_positive = {
                "X": coordinate,
                "kind": "hard" if sign > 0 else "target",
                "event_rank": row["rank"],
                "deficit_numerator": deficit,
                "deficit": str(Fraction(deficit, denominator)),
            }
    return {
        "name": name,
        "cleared_denominator": denominator,
        "first_positive": first_positive,
        "last_positive": last_positive,
        "maximum_positive": maximum_event,
        "terminal_deficit_numerator": deficit,
        "terminal_deficit": str(Fraction(deficit, denominator)),
    }


def rank_weight(rank: int, numerator: int, denominator: int, top_rank: int) -> int:
    return numerator**rank * denominator ** (top_rank - rank)


def audit_rank_abel(data: dict, numerator: int, denominator: int) -> dict:
    top_rank = data["maximum_rank"]
    scale = denominator**top_rank
    return sweep(
        data,
        f"rank_abel_t={numerator}/{denominator}",
        scale,
        lambda row: rank_weight(row["rank"], numerator, denominator, top_rank),
        lambda row: rank_weight(row["rank"], numerator, denominator, top_rank),
    )


def audit_first_two(data: dict, second_numerator: int, denominator: int) -> dict:
    return sweep(
        data,
        f"first_two_component_exits_alpha={second_numerator}/{denominator}",
        denominator,
        lambda _row: denominator,
        lambda row: denominator if row["ordinal"] == 1 else (
            second_numerator if row["ordinal"] == 2 else 0
        ),
    )


def audit_geometric_components(data: dict) -> dict:
    top = max(0, data["maximum_ordinal"] - 1)
    scale = 1 << top
    return sweep(
        data,
        "canonical_component_exit_weight=2^(1-ordinal)",
        scale,
        lambda _row: scale,
        lambda row: 1 << (top - (row["ordinal"] - 1)),
    )


def audit_combined(data: dict, numerator: int, denominator: int) -> dict:
    top_rank = data["maximum_rank"]
    top_ordinal = max(0, data["maximum_ordinal"] - 1)
    ordinal_scale = 1 << top_ordinal
    rank_scale = denominator**top_rank
    scale = ordinal_scale * rank_scale

    def base(row: dict) -> int:
        return rank_weight(row["rank"], numerator, denominator, top_rank)

    return sweep(
        data,
        f"combined_rank_{numerator}/{denominator}_and_geometric_component",
        scale,
        lambda row: ordinal_scale * base(row),
        lambda row: (1 << (top_ordinal - (row["ordinal"] - 1))) * base(row),
    )


def transport_r3(data: dict, limit: int) -> dict:
    """Follow the injective 3/2 transport rooted at canonical T3 exits."""
    member = data["member"]
    terminals = {}
    active = {}
    visited_owner: dict[int, int] = {}
    collision = None

    for row in data["r3_exits"]:
        start = row["child"]
        x = start
        path = [x]
        terminal = None
        while True:
            previous_owner = visited_owner.get(x)
            if previous_owner is not None and previous_owner != start:
                collision = collision or {
                    "first_start": previous_owner,
                    "second_start": start,
                    "state": x,
                }
                break
            visited_owner[x] = start
            if x % 2:
                following = 3 * x - 1
                if following > limit:
                    active[start] = {"state": x, "next": following, "path": path}
                    break
                if not member[following]:
                    raise AssertionError(("T3 closure failure", x, following))
                x = following
                path.append(x)
                continue

            parent = 3 * x // 2
            child = 3 * x - 1
            if parent <= limit and member[parent]:
                x = parent
                path.append(x)
                continue
            if child <= limit and not member[child]:
                raise AssertionError(("T3 closure failure", x, child))
            if parent <= limit and not member[parent] and child <= limit:
                terminal = {"child": child, "parent": parent, "path": path}
                terminals[start] = terminal
                break
            active[start] = {
                "state": x,
                "next": parent,
                "prospective_terminal_child": child,
                "path": path,
            }
            break

    terminal_children = [row["child"] for row in terminals.values()]
    return {
        "definition": (
            "odd generated x maps to 3x-1; even generated x maps to 3x/2 "
            "when that value is generated, otherwise 3x-1 is a Q terminal"
        ),
        "r3_roots": len(data["r3_exits"]),
        "terminated_within_limit": len(terminals),
        "active_at_limit": len(active),
        "root_partition_identity": (
            len(data["r3_exits"]) == len(terminals) + len(active)
        ),
        "state_collision": collision,
        "terminal_children_distinct": len(terminal_children) == len(set(terminal_children)),
        "first_terminals": [
            {"start": start, **row} for start, row in list(terminals.items())[:20]
        ],
        "first_active": [
            {"start": start, **row} for start, row in list(active.items())[:20]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = build_ground(args.limit)
    candidates = [
        audit_rank_abel(data, p, q)
        for p, q in (
            (1, 2), (2, 3), (3, 4), (9, 10), (99, 100), (999, 1000)
        )
    ]
    candidates.extend(
        audit_first_two(data, p, q)
        for p, q in ((0, 1), (1, 2), (3, 4), (1, 1))
    )
    candidates.append(audit_geometric_components(data))
    candidates.extend(
        audit_combined(data, p, q)
        for p, q in ((1, 2), (9, 10), (19, 20), (99, 100), (999, 1000))
    )

    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "algorithm": "SPF divisors plus increasing least-grounded recursion",
        "hard": len(data["hard"]),
        "targets": len(data["targets"]),
        "r3_exits": len(data["r3_exits"]),
        "splitless": sum(data["splitless"]),
        "maximum_rank": data["maximum_rank"],
        "maximum_target_ordinal_in_component": data["maximum_ordinal"],
        "rank_histogram_hard": dict(sorted(Counter(
            row["rank"] for row in data["hard"]
        ).items())),
        "rank_histogram_target": dict(sorted(Counter(
            row["rank"] for row in data["targets"]
        ).items())),
        "candidate_audits": candidates,
        "r3_global_transport": transport_r3(data, args.limit),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": args.limit,
        "hard": payload["hard"],
        "targets": payload["targets"],
        "first_failures": {
            row["name"]: None if row["first_positive"] is None else {
                "X": row["first_positive"]["X"],
                "deficit": row["first_positive"]["deficit"],
            }
            for row in candidates
        },
        "r3_transport": {
            key: payload["r3_global_transport"][key]
            for key in (
                "r3_roots", "terminated_within_limit", "active_at_limit",
                "root_partition_identity", "state_collision",
                "terminal_children_distinct",
            )
        },
    }, indent=2))


if __name__ == "__main__":
    main()
