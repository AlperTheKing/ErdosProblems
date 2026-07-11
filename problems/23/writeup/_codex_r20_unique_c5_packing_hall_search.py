"""Falsifier-first search for a unique-row global-minimum Hall obstruction.

Each generated graph is the edge-disjoint union of displayed C5 cycles.  The
fixed cut puts four cycle edges in B and the closing edge in M.  Exact checks
then require:

* triangle-freeness and B-connectivity;
* every displayed bad edge has exactly one shortest B-geodesic, namely its
  displayed length-four row;
* all cycle edge sets are pairwise disjoint.

The last item certifies the displayed cut is maximum: every cut leaves at
least one edge monochromatic in each edge-disjoint odd cycle, while the
displayed cut leaves exactly the one listed bad edge per cycle.  Since the row
database is complete and singleton-valued, its sole tuple is automatically a
global obligation-score minimizer.  A matching failure is therefore a
decisive exact falsifier to global-minimum collision Hall (not to Erdos #23).
"""

from __future__ import annotations

import argparse
import json
import os
import random
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from _codex_r19_global_base_census import edge, evaluate_rows
from _h import Bconn, geos


def triangle_free(n, adjacency):
    return not any(
        adjacency[u] & adjacency[v]
        for u in range(n)
        for v in adjacency[u]
        if u < v
    )


def make_adjacency(n, edges):
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def candidate_cycle(rng, left, right):
    endpoint_side = left if rng.randrange(2) == 0 else right
    opposite = right if endpoint_side is left else left
    u, middle, v = rng.sample(endpoint_side, 3)
    y1, y3 = rng.sample(opposite, 2)
    row = (u, y1, middle, y3, v)
    cycle_edges = tuple(edge(row[i], row[i + 1]) for i in range(4)) + (edge(u, v),)
    return row, cycle_edges


def exact_instance(n, side, rows):
    used = sorted({vertex for row in rows for vertex in row})
    rename = {vertex: index for index, vertex in enumerate(used)}
    rows = [tuple(rename[vertex] for vertex in row) for row in rows]
    side = [side[vertex] for vertex in used]
    n = len(used)
    cycles = [
        tuple(edge(row[i], row[(i + 1) % 5]) for i in range(5))
        for row in rows
    ]
    flat = [e for cycle in cycles for e in cycle]
    if len(set(flat)) != len(flat):
        return None, "cycleEdgeOverlap"
    graph_edges = set(flat)
    adjacency = make_adjacency(n, graph_edges)
    if not triangle_free(n, adjacency):
        return None, "triangle"
    Bset = {e for e in graph_edges if side[e[0]] != side[e[1]]}
    Mset = graph_edges - Bset
    if len(Mset) != len(rows):
        return None, "badCount"
    if not Bconn(n, adjacency, side):
        return None, "blueDisconnected"
    if set(edge(row[0], row[4]) for row in rows) != Mset:
        return None, "badSet"
    for row in rows:
        bad = edge(row[0], row[4])
        paths = tuple(tuple(path) for path in geos(adjacency, side, bad[0], bad[1]))
        canonical = tuple(row) if row[0] == bad[0] else tuple(reversed(row))
        if paths != (canonical,):
            return None, "nonuniqueShortestRow"
    info = {"adj": adjacency, "Bset": Bset, "Mset": Mset}
    kind, _, detail = evaluate_rows("unique-c5-packing", n, info, tuple(rows), "row-reserved")
    return {
        "status": kind,
        "n": n,
        "detail": detail,
        "edges": sorted(graph_edges),
        "blue": sorted(Bset),
        "bad": sorted(Mset),
        "rows": [list(row) for row in rows],
        "cyclePackingSize": len(rows),
        "maxCutCertifiedByEdgeDisjointOddCycles": True,
    }, None


def search_seed(payload):
    seed, n, left_size, cycles_target, attempts, greedy_trials = payload
    rng = random.Random(seed)
    left = list(range(left_size))
    right = list(range(left_size, n))
    side = [0] * left_size + [1] * (n - left_size)
    best = 0
    valid = 0
    rejections = Counter()
    for _ in range(attempts):
        rows = []
        used = set()
        used_vertices = set()
        for _step in range(cycles_target):
            accepted = False
            for _ in range(greedy_trials):
                row, cycle_edges = candidate_cycle(rng, left, right)
                if rows and len(set(row) & used_vertices) != 1:
                    continue
                if any(e in used for e in cycle_edges):
                    continue
                tentative = used | set(cycle_edges)
                if not triangle_free(n, make_adjacency(n, tentative)):
                    continue
                rows.append(row)
                used = tentative
                used_vertices.update(row)
                accepted = True
                break
            if not accepted:
                break
        best = max(best, len(rows))
        if len(rows) != cycles_target:
            continue
        instance, rejection = exact_instance(n, side, rows)
        if instance is None:
            rejections[rejection] += 1
            continue
        valid += 1
        if instance["status"] == "fail":
            return {
                "kind": "falsifier",
                "seed": seed,
                "n": n,
                "leftSize": left_size,
                **instance,
            }
    return {
        "kind": "clean",
        "seed": seed,
        "valid": valid,
        "bestCycles": best,
        "rejections": dict(rejections),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--left", type=int, default=8)
    parser.add_argument("--cycles", type=int, default=8)
    parser.add_argument("--seeds", type=int, default=4096)
    parser.add_argument("--attempts", type=int, default=64)
    parser.add_argument("--greedy-trials", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--output", type=Path,
        default=Path("../../../tmp/codex_r20_unique_c5_packing.json"))
    args = parser.parse_args()
    if not (3 <= args.left <= args.n - 3):
        parser.error("both cut sides need at least three vertices")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")

    payloads = [
        (args.seed + i, args.n, args.left, args.cycles, args.attempts, args.greedy_trials)
        for i in range(args.seeds)
    ]
    valid = 0
    best = 0
    falsifier = None
    rejections = Counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(search_seed, payloads, chunksize=1):
            valid += result.get("valid", 0)
            best = max(best, result.get("bestCycles", 0))
            rejections.update(result.get("rejections", {}))
            if result["kind"] == "falsifier":
                falsifier = result
                pool.shutdown(wait=False, cancel_futures=True)
                break
    out = {
        "parameters": vars(args) | {"output": str(args.output)},
        "validUniqueRowInstances": valid,
        "bestCyclesBuilt": best,
        "rejections": dict(sorted(rejections.items())),
        "falsifier": falsifier,
        "verdict": "FALSIFIED" if falsifier else "NO_FALSIFIER",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2), encoding="ascii")
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    return 1 if falsifier else 0


if __name__ == "__main__":
    raise SystemExit(main())
