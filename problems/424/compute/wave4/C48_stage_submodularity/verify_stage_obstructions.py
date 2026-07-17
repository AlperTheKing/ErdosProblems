#!/usr/bin/env python3
"""Exact verifier for the C48 arithmetic and finite-Horn obstructions."""

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


def is_hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def least_g(limit: int, pairs: list[list[tuple[int, int]]]) -> list[bool]:
    member = [False] * (limit + 1)
    member[2] = member[3] = True
    for n in range(4, limit + 1):
        if allowed(n) and any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = True
    return member


def one_step_events(limit: int) -> tuple[dict, list[list[tuple[int, int]]]]:
    pairs = [pairs_of(n) if n >= 2 else [] for n in range(limit + 1)]
    member = least_g(limit, pairs)
    events: list[tuple[int, int, int, str]] = []
    for n in range(4, limit + 1):
        if is_hard_shape(n, pairs[n]):
            events.append((n, n, 1, "hard"))
    for q in range(4, (limit + 1) // 2 + 1):
        child = 2 * q - 1
        if allowed(q) and member[child]:
            events.append((child, q, -1, "terminal-parent"))
    events.sort()

    # At the empty deletion base, a one-pair unsupported indicator has
    # mixed second difference +1 on its two endpoints.  A two-pair
    # indicator has difference -1 between endpoints in distinct pairs.
    contributions: dict[tuple[int, int], list[tuple[int, int, int, str]]] = defaultdict(list)
    for event, node, coefficient, kind in events:
        local = pairs[node]
        if len(local) == 1:
            a, b = local[0]
            if a not in (2, 3) and b not in (2, 3):
                contributions[(a, b)].append((event, coefficient, node, kind))
        elif len(local) == 2:
            for x in local[0]:
                for y in local[1]:
                    if x in (2, 3) or y in (2, 3):
                        continue
                    key = tuple(sorted((x, y)))
                    contributions[key].append((event, -coefficient, node, kind))

    first_negative = None
    first_positive = None
    for key, rows in contributions.items():
        rows.sort()
        running = 0
        for event, delta, node, kind in rows:
            running += delta
            record = {
                "X": event,
                "D1": [key[0]],
                "D2": [key[1]],
                "mixed_difference": running,
                "last_node": node,
                "last_kind": kind,
            }
            if running < 0 and (
                first_negative is None
                or (event, key) < (first_negative["X"], tuple(first_negative["D1"] + first_negative["D2"]))
            ):
                first_negative = record
            if running > 0 and (
                first_positive is None
                or (event, key) < (first_positive["X"], tuple(first_positive["D1"] + first_positive["D2"]))
            ):
                first_positive = record

    if first_negative is None or first_positive is None:
        raise AssertionError("requested obstruction range was too small")

    # Directly replay the two advertised witnesses.
    def unsupported(node: int, deleted: set[int]) -> int:
        return int(node not in (2, 3) and all(
            a in deleted or b in deleted for a, b in pairs[node]
        ))

    direct = {}
    for label, record in (("sub", first_negative), ("super", first_positive)):
        x, y = record["D1"][0], record["D2"][0]
        X = record["X"]
        values = []
        for deleted in ({x}, {y}, {x, y}, set()):
            total = 0
            for event, node, coefficient, _ in events:
                if event <= X:
                    total += coefficient * unsupported(node, deleted)
            values.append(total)
        mixed = values[0] + values[1] - values[2] - values[3]
        if mixed != record["mixed_difference"]:
            raise AssertionError((label, record, values, mixed))
        direct[label] = {"f_D1": values[0], "f_D2": values[1],
                         "f_union": values[2], "f_empty": values[3],
                         "mixed_difference": mixed}

    return {
        "event_limit": limit,
        "first_submodularity_failure": first_negative,
        "first_supermodularity_failure": first_positive,
        "direct_replay": direct,
        "sub_witness_pairs": pairs[first_negative["last_node"]],
        "checked_all_empty_base_singleton_pairs": True,
    }, pairs


def finite_horn_obstruction() -> dict:
    nodes = ["s2", "s3", "p", "g5", "g9", "q", "tq", "h1", "h2"]
    seeds = {"s2", "s3"}
    clauses = {
        "s2": [], "s3": [], "p": [],
        "g5": [("s2", "s3")],
        "g9": [("s2", "g5")],
        "q": [("s2", "p")],
        "tq": [("s2", "q")],
        "h1": [("g5", "q")],
        "h2": [("g9", "q")],
    }
    current = set(nodes)
    stages = [sorted(current, key=nodes.index)]
    while True:
        following = set(seeds)
        for node in nodes:
            if node in seeds:
                continue
            if any(a in current and b in current for a, b in clauses[node]):
                following.add(node)
        stages.append(sorted(following, key=nodes.index))
        if following == current:
            break
        current = following
    G = current
    rank = {}
    for node in nodes:
        if node in G:
            continue
        rank[node] = next(i for i in range(1, len(stages)) if node not in stages[i]) - 1
    hard = {"h1", "h2"}
    seed2_edges = {"p": "q", "q": "tq"}
    targets = {
        parent for parent, child in seed2_edges.items()
        if parent not in G and child in G
    }
    H2 = sum(rank[n] <= 2 for n in hard)
    Q2 = sum(rank[n] <= 2 for n in targets)
    if (H2, Q2, H2 - Q2) != (2, 0, 2):
        raise AssertionError((rank, G, targets, H2, Q2))
    return {
        "nodes_in_topological_order": nodes,
        "seeds": sorted(seeds),
        "clauses": {k: [list(x) for x in v] for k, v in clauses.items()},
        "descending_stages": stages,
        "fixed_point_G": sorted(G, key=nodes.index),
        "ranks": rank,
        "hard_nodes": sorted(hard),
        "seed2_edges": seed2_edges,
        "terminal_targets": sorted(targets),
        "rank_prefix_d_2": {"H": H2, "Q": Q2, "excess": H2 - Q2},
        "properties": {
            "all_parents_precede_outputs": all(
                nodes.index(a) < nodes.index(n) and nodes.index(b) < nodes.index(n)
                for n, rows in clauses.items() for a, b in rows
            ),
            "hard_ranks_at_least_two": all(rank[n] >= 2 for n in hard),
            "seed2_chain_rank_strict": rank["p"] < rank["q"] < rank["tq"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 804:
        raise ValueError("limit must be at least 804")
    arithmetic, _ = one_step_events(args.limit)
    result = {
        "schema_version": 1,
        "arithmetic_one_step": arithmetic,
        "finite_horn_obstruction": finite_horn_obstruction(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
