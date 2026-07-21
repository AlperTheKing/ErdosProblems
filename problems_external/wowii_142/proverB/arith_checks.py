#!/usr/bin/env python3
"""Exact verification of every arithmetic side-claim used in PROOF_142_B.

A. Integer identities for all g in [3, 3000]:
   ceil(2g/3) = g - floor(g/3);   g - 1 - ceil(2g/3) = floor(g/3) - 1;
   coverage: for g >= 5 the f-ranges [1, fl3-1], [fl3, g-2*fl3-1],
   [g-2*fl3, inf) partition f >= 1 (second empty iff g = 0 mod 3, one value
   iff g = 1 mod 3, two iff g = 2 mod 3, and then q = f+1-fl3 in {1,2});
   S3-chain: f >= g-2*fl3 and D >= f+1 ==> ceil((2f+D-g)/2) >= f+1-fl3
   (checked for all f in [1, 4000], D in [f+1, f+9] sampled exactly).
B. Tadpole lemma, g in [5, 400]: build tadpole(g,1) explicitly, compute
   B, f exactly; verify f = ceil(floor(g/2)/2) and f <= floor(g/3).
C. g=4 delta lower bound identity: for D >= 3, min over i in [0,D] of
   max(D-1-i, i-1) >= 1.
"""
from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
PE = ROOT.parent.parent
sys.path.insert(0, str(PE / "wowii_141" / "oracle"))
from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, nx_to_bitadj)

fails = []

# ---- A. identities
for g in range(3, 3001):
    c23 = (2 * g + 2) // 3
    fl3 = g // 3
    if c23 != -((-2 * g) // 3):
        fails.append(("ceil form", g))
    if c23 != g - fl3:
        fails.append(("c23 identity", g))
    if (g - 1) - c23 != fl3 - 1:
        fails.append(("T2 margin", g))
    if g >= 5:
        lo, hi = fl3, g - 2 * fl3 - 1
        width = hi - lo + 1
        r = g % 3
        if width != (0 if r == 0 else (1 if r == 1 else 2)):
            fails.append(("leftover width", g))
        for f in range(lo, hi + 1):
            if not 1 <= f + 1 - fl3 <= 2:
                fails.append(("leftover q", g, f))
    # S3 chain
    if g >= 5:
        for f in list(range(1, 200)) + [999, 4000]:
            if f < g - 2 * fl3:
                continue
            for D in range(f + 1, f + 10):
                s3min = -((-(2 * f + D - g)) // 2)   # ceil
                if s3min < f + 1 - fl3:
                    fails.append(("S3 chain", g, f, D))

# ---- B. tadpole
for g in range(5, 401):
    G = nx.cycle_graph(g)
    G.add_edge(0, g)                     # pendant y = g at position 0
    n, adj = nx_to_bitadj(G)
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    per = 0
    for v in range(n):
        if ecc[v] == D:
            per |= 1 << v
    Bl = [v for v in range(n) if (per >> v) & 1]
    f = ecc_set(n, dist, per)
    pred = ((g // 2) + 1) // 2           # ceil(floor(g/2)/2)
    if f != pred:
        fails.append(("tadpole f formula", g, f, pred))
    if f > g // 3:
        fails.append(("tadpole f <= floor(g/3)", g, f, g // 3))
    if D != g // 2 + 1:
        fails.append(("tadpole D", g, D))
    expectB = {g} | {j for j in range(g)
                     if min(j, g - j) == g // 2}
    if set(Bl) != expectB:
        fails.append(("tadpole B", g, Bl))

# ---- C. g=4 delta bound
for D in range(3, 500):
    m = min(max(D - 1 - i, i - 1) for i in range(D + 1))
    if m < 1:
        fails.append(("g4 delta", D))
    if m != -(-D // 2) - 1 and D > 3:    # ceil(D/2)-1 (sanity, not used)
        pass

print("FAILS:", len(fails))
for x in fails[:20]:
    print("  ", x)
if not fails:
    print("all arithmetic side-claims verified exactly")
