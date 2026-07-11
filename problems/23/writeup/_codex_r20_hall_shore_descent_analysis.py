"""Test whether a Hall-failing tuple has a score descent escaping its owner shore."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, product

from _codex_r19_global_base_census import (
    dec,
    edge,
    full_matching,
    global_candidates,
    graph6_for_orders,
    hall_witness,
    loads,
    multiplicities,
    owner_demands,
)
from _codex_r20_one_row_atom_analysis import contiguous
from _codex_r20_two_row_atom_analysis import score_detail
from _codex_r20_two_row_exchange_gate import shortest_row_families


def hall_owner_shore(n, info, rows):
    count = multiplicities(n, rows)
    component = set().union(*(set(row) for row in rows)) if rows else set()
    support = {
        edge(u, v) for row in rows for u, v in zip(row, row[1:])
    }
    active = {
        e for e in info["Bset"]
        if e[0] in component and e[1] in component and e not in support
    }
    reserved = {
        source
        for u, v in active
        for source in ((u, v, 0), (v, u, 0))
    }
    demands = owner_demands(count, component, active)
    demands = {
        owner: [d for d in items if d[0] == "collision"]
        for owner, items in demands.items()
    }
    demands = {owner: items for owner, items in demands.items() if items}
    if not demands:
        return None
    candidates = {
        owner: {
            source: kind
            for source, kind in global_candidates(
                owner, n, count, info["adj"], info["Bset"], info["Mset"],
                "row-reserved",
            ).items()
            if source not in reserved
        }
        for owner in demands
    }
    matching, unmatched = full_matching(demands, candidates)
    if not unmatched:
        return None
    left, right = hall_witness(demands, candidates, matching, unmatched)
    owners = frozenset(owner for owner, _ in left)
    return owners, len(left), len(right)


def analyze_graph(g6):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    sizes = tuple(map(len, families))
    choices = list(product(*(range(size) for size in sizes)))
    scores = {}
    rows_by_choice = {}
    shores = {}
    for choice in choices:
        rows = tuple(families[i][choice[i]] for i in range(len(choice)))
        rows_by_choice[choice] = rows
        scores[choice] = score_detail(n, info, rows)
        shore = hall_owner_shore(n, info, rows)
        if shore is not None:
            shores[choice] = shore

    counts = Counter()
    examples = {}
    for choice, (owners, left_size, right_size) in shores.items():
        old_rows = rows_by_choice[choice]
        old_score = scores[choice][0]
        one = []
        for index, size in enumerate(sizes):
            old_row = old_rows[index]
            for replacement in range(size):
                if replacement == choice[index]:
                    continue
                neighbor = choice[:index] + (replacement,) + choice[index + 1:]
                if scores[neighbor][0] >= old_score:
                    continue
                new_row = families[index][replacement]
                changed = tuple(i for i in range(5) if old_row[i] != new_row[i])
                if not contiguous(changed):
                    continue
                old_inside = len(set(old_row) & owners)
                new_inside = len(set(new_row) & owners)
                one.append((new_inside - old_inside, index, replacement, changed))
        if one:
            counts["oneDescent"] += 1
            if any(delta < 0 for delta, *_ in one):
                counts["oneEscapesShore"] += 1
            else:
                counts["oneDoesNotEscapeShore"] += 1
                examples.setdefault("oneDoesNotEscapeShore", {
                    "g6": g6,
                    "choice": choice,
                    "owners": sorted(owners),
                    "hall": [left_size, right_size],
                    "bestShoreDelta": min(delta for delta, *_ in one),
                })
            continue

        counts["noOneDescent"] += 1
        rectangle_escapes = False
        for left, right in combinations(range(len(choice)), 2):
            for li in range(sizes[left]):
                if li == choice[left]:
                    continue
                for ri in range(sizes[right]):
                    if ri == choice[right]:
                        continue
                    neighbor = list(choice)
                    neighbor[left] = li
                    neighbor[right] = ri
                    neighbor = tuple(neighbor)
                    if scores[neighbor][0] >= old_score:
                        continue
                    old_inside = len(set(old_rows[left]) & owners) + len(
                        set(old_rows[right]) & owners
                    )
                    new_inside = len(set(families[left][li]) & owners) + len(
                        set(families[right][ri]) & owners
                    )
                    if new_inside < old_inside:
                        rectangle_escapes = True
        if rectangle_escapes:
            counts["rectangleEscapesShore"] += 1
        else:
            counts["rectangleDoesNotEscapeShore"] += 1
            examples.setdefault("rectangleDoesNotEscapeShore", {
                "g6": g6,
                "choice": choice,
                "owners": sorted(owners),
                "hall": [left_size, right_size],
            })
    if not shores:
        return None
    return counts, examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=5)
    parser.add_argument("--max-order", type=int, default=11)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = parser.parse_args()
    if not (1 <= args.workers <= 61):
        parser.error("--workers must be between 1 and 61 on Windows")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    counts = Counter()
    examples = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, graph6, chunksize=8):
            if result is None:
                continue
            local_counts, local_examples = result
            counts.update(local_counts)
            for key, example in local_examples.items():
                examples.setdefault(key, example)
    print(json.dumps({
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "counts": dict(sorted(counts.items())),
        "examples": examples,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
