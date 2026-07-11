"""Adversarial two-local-minimum gate on balanced C5 blow-ups.

The N=10 rectangle atom is C5[2].  For C5[t], choosing one shortest row
for each bad A0-A4 edge is a three-coordinate array/Latin-trade problem.
This gate searches structured and random row tuples, descends to a one-local
minimum of the exact R20 obligation score, and then asks whether a failed
collision matching has any strict two-row descent.

All graph, score, matching, and cut checks are exact integers.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_r19_global_base_census import edge, evaluate_rows  # noqa: E402
from _codex_r20_two_row_exchange_gate import obligation_score  # noqa: E402


def balanced_c5(t: int):
    layers = [tuple(range(i * t, (i + 1) * t)) for i in range(5)]
    blue = {
        edge(u, v)
        for i in range(4)
        for u in layers[i]
        for v in layers[i + 1]
    }
    bad = {edge(u, v) for u in layers[0] for v in layers[4]}
    adj = {v: set() for v in range(5 * t)}
    for u, v in blue | bad:
        adj[u].add(v)
        adj[v].add(u)
    bad_edges = tuple(sorted(bad))
    families = tuple(
        tuple(
            (u, a, b, c, v)
            for a in layers[1]
            for b in layers[2]
            for c in layers[3]
        )
        for u, v in bad_edges
    )
    cyc = {bad_edge: list(families[i]) for i, bad_edge in enumerate(bad_edges)}
    info = {
        "Bset": blue,
        "Mset": bad,
        "M": list(bad_edges),
        "adj": adj,
        "cyc": cyc,
        "ell": {bad_edge: 5 for bad_edge in bad_edges},
    }
    return layers, info, families


def verify_graph(t: int, layers, info, families):
    n = 5 * t
    edges = info["Bset"] | info["Mset"]
    for a, b, c in combinations(range(n), 3):
        assert not ({edge(a, b), edge(a, c), edge(b, c)} <= edges)
    min_bad = len(info["Mset"])
    for mask in range(1 << (n - 1)):
        same = 0
        for u, v in edges:
            cu = 0 if u == n - 1 else (mask >> u) & 1
            cv = 0 if v == n - 1 else (mask >> v) & 1
            same += cu == cv
        min_bad = min(min_bad, same)
    assert min_bad == t * t
    for i, (u, v) in enumerate(info["M"]):
        assert len(families[i]) == t**3
        for row in families[i]:
            assert row[0] == u and row[-1] == v and len(set(row)) == 5
            assert all(edge(x, y) in info["Bset"] for x, y in zip(row, row[1:]))
        assert not (set(info["adj"][u]) & set(info["adj"][v]))
    return {"triangleFree": True, "minimumBadEdges": min_bad,
            "familySize": t**3, "badEdges": t * t}


def rows_of(families, choice):
    return tuple(families[i][choice[i]] for i in range(len(choice)))


def score_of(n, info, families, choice, cache):
    value = cache.get(choice)
    if value is None:
        value = obligation_score(n, info, rows_of(families, choice))
        cache[choice] = value
    return value


def one_neighbors(choice, family_size):
    for i in range(len(choice)):
        for replacement in range(family_size):
            if replacement == choice[i]:
                continue
            yield i, replacement, choice[:i] + (replacement,) + choice[i + 1:]


def two_neighbors(choice, family_size):
    for i, j in combinations(range(len(choice)), 2):
        for ri in range(family_size):
            if ri == choice[i]:
                continue
            for rj in range(family_size):
                if rj == choice[j]:
                    continue
                out = list(choice)
                out[i] = ri
                out[j] = rj
                yield i, j, ri, rj, tuple(out)


def descend_one(n, info, families, choice, cache):
    steps = 0
    family_size = len(families[0])
    while True:
        old = score_of(n, info, families, choice, cache)
        best = (old, choice)
        for _, _, candidate in one_neighbors(choice, family_size):
            value = score_of(n, info, families, candidate, cache)
            if (value, candidate) < best:
                best = (value, candidate)
        if best[0] >= old:
            return choice, old, steps
        choice = best[1]
        steps += 1


def structured_choice(t: int, coeffs):
    # bad-edge order is (A0 index, A4 index); row order is A1,A2,A3.
    out = []
    for i in range(t):
        for j in range(t):
            digits = tuple((a * i + b * j + c) % t for a, b, c in coeffs)
            out.append((digits[0] * t + digits[1]) * t + digits[2])
    return tuple(out)


def run_start(args):
    t, seed, structured = args
    n = 5 * t
    _, info, families = balanced_c5(t)
    rng = random.Random(seed)
    if structured:
        coeffs = tuple(
            (rng.randrange(t), rng.randrange(t), rng.randrange(t))
            for _ in range(3)
        )
        choice = structured_choice(t, coeffs)
    else:
        choice = tuple(rng.randrange(t**3) for _ in range(t * t))
    cache = {}
    one_min, score, steps = descend_one(n, info, families, choice, cache)
    rows = rows_of(families, one_min)
    kind, _, detail = evaluate_rows(f"C5[{t}]", n, info, rows, "row-reserved")
    if kind == "pass":
        return {"status": "matchingPass", "steps": steps, "score": score}
    best_two = None
    for i, j, ri, rj, candidate in two_neighbors(one_min, t**3):
        value = score_of(n, info, families, candidate, cache)
        item = (value, candidate, i, j, ri, rj)
        if best_two is None or item < best_two:
            best_two = item
    assert best_two is not None
    if best_two[0] < score:
        return {
            "status": "matchingFailTwoDescent",
            "steps": steps,
            "score": score,
            "bestTwoScore": best_two[0],
        }
    return {
        "status": "falsifier",
        "seed": seed,
        "structured": structured,
        "choice": list(one_min),
        "rows": [list(row) for row in rows],
        "score": score,
        "bestTwoScore": best_two[0],
        "matchingFailure": detail,
        "oneDescentSteps": steps,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=3)
    parser.add_argument("--starts", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.t < 2:
        parser.error("--t must be at least 2")
    if args.starts < 1:
        parser.error("--starts must be positive")
    if not 1 <= args.workers <= 61:
        parser.error("--workers must be between 1 and 61 on Windows")
    return args


def main():
    args = parse_args()
    layers, info, families = balanced_c5(args.t)
    graph_check = verify_graph(args.t, layers, info, families)
    jobs = [
        (args.t, args.seed + i, i % 2 == 0)
        for i in range(args.starts)
    ]
    counts = {}
    examples = {}
    falsifiers = []
    if args.workers == 1:
        results = map(run_start, jobs)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(run_start, jobs, chunksize=1)
    try:
        for result in results:
            status = result["status"]
            counts[status] = counts.get(status, 0) + 1
            examples.setdefault(status, result)
            if status == "falsifier":
                falsifiers.append(result)
    finally:
        if pool is not None:
            pool.shutdown()
    print(json.dumps({
        "parameters": vars(args),
        "graphCheck": graph_check,
        "counts": dict(sorted(counts.items())),
        "examples": examples,
        "falsifiers": falsifiers[:8],
        "verdict": "FALSIFIED" if falsifiers else "NO_FALSIFIER",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
