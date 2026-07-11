"""Classify every two-row-only descent in the exact N<=10 R20 gate.

The output records whether the best strict two-row repair is a coordinatewise
rectangle exchange: at every path position the unordered pair of vertices is
preserved, with one or more positions swapped between the two rows.
"""

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
    evaluate_rows,
    graph6_for_orders,
    loads,
    multiplicities,
)
from _codex_r20_two_row_exchange_gate import shortest_row_families


def score_detail(n, info, rows):
    count = multiplicities(n, rows)
    collision = sum(
        max(0, count[x][y] - 1) for x in range(n) for y in range(n)
    )
    vertices = {v for row in rows for v in row}
    support = {
        edge(u, v) for row in rows for u, v in zip(row, row[1:])
    }
    active = {
        e for e in info["Bset"]
        if e[0] in vertices and e[1] in vertices and e not in support
    }
    return 2 * collision + 2 * len(active), collision, len(active)


def two_neighbors(choice, family_sizes):
    for left, right in combinations(range(len(choice)), 2):
        for li in range(family_sizes[left]):
            if li == choice[left]:
                continue
            for ri in range(family_sizes[right]):
                if ri == choice[right]:
                    continue
                out = list(choice)
                out[left] = li
                out[right] = ri
                yield left, right, tuple(out)


def one_has_descent(choice, family_sizes, scores):
    for index, size in enumerate(family_sizes):
        for replacement in range(size):
            if replacement == choice[index]:
                continue
            out = choice[:index] + (replacement,) + choice[index + 1:]
            if scores[out][0] < scores[choice][0]:
                return True
    return False


def exchange_signature(info, families, choice, best):
    left, right, repaired = best
    old_left = families[left][choice[left]]
    old_right = families[right][choice[right]]
    new_left = families[left][repaired[left]]
    new_right = families[right][repaired[right]]
    preserved = all(
        sorted((old_left[i], old_right[i])) ==
        sorted((new_left[i], new_right[i]))
        for i in range(5)
    )
    swapped = tuple(
        i for i in range(5)
        if (old_left[i], old_right[i]) == (new_right[i], new_left[i])
        and old_left[i] != old_right[i]
    )
    changed_positions = tuple(
        i for i in range(5)
        if (old_left[i], old_right[i]) != (new_left[i], new_right[i])
    )
    bad_left = set(info["M"][left])
    bad_right = set(info["M"][right])
    return {
        "columnPairPreserved": preserved,
        "changedPositions": changed_positions,
        "swappedPositions": swapped,
        "badEndpointIntersection": len(bad_left & bad_right),
        "oldRowIntersection": len(set(old_left) & set(old_right)),
        "newRowIntersection": len(set(new_left) & set(new_right)),
    }


def analyze_graph(g6):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    sizes = tuple(map(len, families))
    choices = list(product(*(range(size) for size in sizes)))
    scores = {}
    failures = set()
    rows_by_choice = {}
    for choice in choices:
        rows = tuple(families[i][choice[i]] for i in range(len(choice)))
        rows_by_choice[choice] = rows
        scores[choice] = score_detail(n, info, rows)
        kind, _, _ = evaluate_rows(g6, n, info, rows, "row-reserved")
        if kind == "fail":
            failures.add(choice)

    atoms = []
    for choice in sorted(failures):
        if one_has_descent(choice, sizes, scores):
            continue
        candidates = [
            (scores[repaired][0], left, right, repaired)
            for left, right, repaired in two_neighbors(choice, sizes)
            if scores[repaired][0] < scores[choice][0]
        ]
        if not candidates:
            atoms.append({"missingTwoRowDescent": True})
            continue
        _, left, right, repaired = min(candidates)
        signature = exchange_signature(
            info, families, choice, (left, right, repaired)
        )
        signature.update({
            "oldScore": scores[choice][0],
            "newScore": scores[repaired][0],
            "collisionDelta": scores[repaired][1] - scores[choice][1],
            "activeDelta": scores[repaired][2] - scores[choice][2],
        })
        atoms.append(signature)
    if not atoms:
        return None
    return {"g6": g6, "order": n, "atoms": atoms}


def freeze(value):
    if isinstance(value, dict):
        return tuple(sorted((key, freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=5)
    parser.add_argument("--max-order", type=int, default=10)
    parser.add_argument("--workers", type=int, default=min(48, os.cpu_count() or 1))
    args = parser.parse_args()
    if not (1 <= args.workers <= 64):
        parser.error("--workers must be between 1 and 64")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    counter = Counter()
    witnesses = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, graph6, chunksize=4):
            if result is None:
                continue
            witnesses.append({
                "g6": result["g6"],
                "order": result["order"],
                "atomCount": len(result["atoms"]),
                "representative": result["atoms"][0],
            })
            counter.update(freeze(atom) for atom in result["atoms"])
    payload = {
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "graphsWithTwoRowOnlyAtoms": len(witnesses),
        "totalAtoms": sum(counter.values()),
        "signatureCount": len(counter),
        "allColumnPairPreserved": all(
            dict(signature).get("columnPairPreserved") is True
            for signature in counter
        ),
        "signatures": [
            {"count": count, **dict(signature)}
            for signature, count in counter.most_common()
        ],
        "witnesses": witnesses,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
