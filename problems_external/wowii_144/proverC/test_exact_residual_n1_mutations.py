#!/usr/bin/env python3
"""Targeted exact falsifier for the residual-window N1 statement.

The search mutates unicyclic girth-g graphs consisting of a chordless cycle
with pendant paths at its vertices.  These are useful adversaries because the
unconditional N1 statement is known to fail in this family.  Every tested
graph is evaluated from its exact distance matrix.  The unique shortest cycle
is the base cycle, so there is no cycle-enumeration truncation.

Candidate tested (existential K, existential e-realizer x):

    g >= 5 and D < e + floor(g/2)
      ==> max_{x: d(x,C)=e} d(x,K) >= e-floor(g/2).

Run: python test_exact_residual_n1_mutations.py
Output: exact_residual_n1_mutations.json
"""

from __future__ import annotations

import json
import random
from pathlib import Path


SEED = 20260718
TRIALS = 200_000
OUT = Path(__file__).with_name("exact_residual_n1_mutations.json")


def evaluate(g: int, legs: list[int]):
    """Exact invariants of a cycle with one pendant path per cycle vertex."""
    # A vertex is (root, depth), depth 0 being a cycle vertex.  The graph
    # distance is explicit; on the same positive-depth leg it is the depth
    # difference, and otherwise it goes through the two cycle roots.
    verts = [(i, d) for i, length in enumerate(legs)
             for d in range(length + 1)]
    n = len(verts)

    def dc(i: int, j: int) -> int:
        q = abs(i - j)
        return min(q, g - q)

    dist = [[0] * n for _ in range(n)]
    for a, (i, di) in enumerate(verts):
        for b in range(a + 1, n):
            j, dj = verts[b]
            if i == j:
                val = abs(di - dj)
            else:
                val = di + dc(i, j) + dj
            dist[a][b] = dist[b][a] = val

    ecc = [max(row) for row in dist]
    radius = min(ecc)
    diameter = max(ecc)
    centers = [v for v, q in enumerate(ecc) if q == radius]
    d_center = [min(dist[v][c] for c in centers) for v in range(n)]
    e = max(d_center)
    realizers = [v for v, q in enumerate(d_center) if q == e]
    hmax = max(verts[x][1] for x in realizers)
    k = g // 2
    residual = diameter < e + k
    slack = hmax - (e - k)
    return {
        "n": n, "g": g, "k": k, "radius": radius,
        "diameter": diameter, "e": e, "hmax": hmax,
        "slack": slack, "residual": residual,
        "centers": [verts[c] for c in centers],
        "realizers": [verts[x] for x in realizers],
    }


def main() -> None:
    rng = random.Random(SEED)
    checked = 0
    residual = 0
    nontrivial = 0
    min_slack = None
    min_record = None
    violation = None

    # A state is mutated from the preceding state, with periodic restarts.
    g = 5
    legs = [0] * g
    for trial in range(TRIALS):
        if trial % 127 == 0:
            g = rng.randint(5, 20)
            legs = [0] * g
            budget = rng.randint(3, max(3, 40 - g))
            for _ in range(budget):
                legs[rng.randrange(g)] += 1
        else:
            i = rng.randrange(g)
            if legs[i] and rng.random() < 0.45:
                legs[i] -= 1
            elif sum(legs) < 40 - g:
                legs[i] += 1

        rec = evaluate(g, legs)
        checked += 1
        if not rec["residual"]:
            continue
        residual += 1
        if rec["e"] > rec["k"]:
            nontrivial += 1
        if min_slack is None or rec["slack"] < min_slack:
            min_slack = rec["slack"]
            min_record = {"legs": legs.copy(), **rec}
        if rec["slack"] < 0:
            violation = {"trial": trial, "legs": legs.copy(), **rec}
            break

    result = {
        "test": "exact_residual_N1_cycle_pendant_path_mutations",
        "seed": SEED,
        "planned_trials": TRIALS,
        "checked": checked,
        "residual": residual,
        "nontrivial_e_gt_k": nontrivial,
        "minimum_slack": min_slack,
        "minimum_record": min_record,
        "violation": violation,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
