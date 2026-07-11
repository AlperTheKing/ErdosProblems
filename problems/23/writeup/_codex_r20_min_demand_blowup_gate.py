"""Exact blow-up stress for the R20 minimum-demand transfer relation.

The graph is a nonuniform blow-up of C5.  Rotate the five class sizes so the
minimum adjacent product is the displayed bad block A4-A0, verify the cut is
maximum by exact enumeration of the five class-side counts, choose one
explicit modular shortest row per bad edge, and run the exact reserved-hit
sameOwner+rowCompanion matcher.

This is a deterministic falsifier search, not a proof of universal Hall
completeness.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_r19_global_base_census import edge, evaluate_rows  # noqa: E402


def rotate_at_min_product(sizes):
    products = [sizes[i] * sizes[(i + 1) % 5] for i in range(5)]
    first = min(range(5), key=lambda i: (products[i], i))
    return [sizes[(first + 1 + i) % 5] for i in range(5)]


def quotient_cut_value(sizes, ones):
    total = 0
    for i in range(5):
        j = (i + 1) % 5
        total += (
            ones[i] * (sizes[j] - ones[j])
            + (sizes[i] - ones[i]) * ones[j]
        )
    return total


def fixture(sizes):
    sizes = rotate_at_min_product(sizes)
    offsets = [0]
    for size in sizes:
        offsets.append(offsets[-1] + size)

    def vertex(part, index):
        return offsets[part] + index

    n = sum(sizes)
    edges = set()
    for part in range(5):
        nxt = (part + 1) % 5
        for i in range(sizes[part]):
            for j in range(sizes[nxt]):
                edges.add(edge(vertex(part, i), vertex(nxt, j)))

    side = [0] * n
    for part in (1, 3):
        for i in range(sizes[part]):
            side[vertex(part, i)] = 1
    blue = {e for e in edges if side[e[0]] != side[e[1]]}
    bad = edges - blue

    maximum = max(
        quotient_cut_value(sizes, ones)
        for ones in product(*(range(size + 1) for size in sizes))
    )
    assert len(blue) == maximum
    assert len(bad) == sizes[0] * sizes[4]

    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    for u in range(n):
        for v in adjacency[u]:
            assert not (adjacency[u] & adjacency[v])

    rows = []
    for i in range(sizes[0]):
        for j in range(sizes[4]):
            row = (
                vertex(0, i),
                vertex(1, j % sizes[1]),
                vertex(2, (i + j) % sizes[2]),
                vertex(3, i % sizes[3]),
                vertex(4, j),
            )
            assert all(edge(row[k], row[k + 1]) in blue for k in range(4))
            assert edge(row[0], row[4]) in bad
            rows.append(row)

    info = {"Bset": blue, "Mset": bad, "adj": adjacency}
    return n, sizes, info, rows


def compositions(total, rng):
    cuts = sorted(rng.sample(range(1, total), 4))
    return (
        cuts[0],
        cuts[1] - cuts[0],
        cuts[2] - cuts[1],
        cuts[3] - cuts[2],
        total - cuts[3],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-order", type=int, default=500)
    parser.add_argument("--seed", type=int, default=230026)
    args = parser.parse_args()

    special = [
        (4, 3, 4, 3, 4),
        (4, 3, 4, 3, 5),
        (5, 3, 5, 3, 5),
        (6, 3, 5, 3, 5),
    ]
    rng = random.Random(args.seed)
    vectors = list(special)
    for n in range(18, 23):
        vectors.extend(compositions(n, rng) for _ in range(args.per_order))

    failures = []
    relation_totals = {"sameOwner": 0, "rowCompanion": 0}
    max_demands = 0
    max_active = 0
    special_results = []
    for sizes in vectors:
        n, rotated, info, rows = fixture(sizes)
        kind, _, detail = evaluate_rows(
            str(sizes), n, info, rows, "row-reserved"
        )
        max_demands = max(max_demands, detail["demands"])
        max_active = max(max_active, detail.get("activeEdges", 0))
        for relation, count in detail.get("relations", {}).items():
            relation_totals[relation] = relation_totals.get(relation, 0) + count
        if sizes in special:
            special_results.append({
                "sizes": sizes,
                "rotated": rotated,
                "status": kind,
                "demands": detail["demands"],
                "reservedHits": detail.get("reservedHits", 0),
                "relations": detail.get("relations", {}),
            })
        if kind != "pass" and len(failures) < 20:
            failures.append({"sizes": sizes, "rotated": rotated, **detail})

    print(json.dumps({
        "seed": args.seed,
        "perOrder": args.per_order,
        "orders": [18, 22],
        "randomTested": 5 * args.per_order,
        "specialResults": special_results,
        "maxDemands": max_demands,
        "maxActiveEdges": max_active,
        "relationTotals": relation_totals,
        "failureCount": len(failures),
        "failures": failures,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
