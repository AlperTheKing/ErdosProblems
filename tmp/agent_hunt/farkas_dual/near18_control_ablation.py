#!/usr/bin/env python3
"""AGENT farkas_dual — Script E: control ablation on the 18-vtx near-candidate.
Question: is the positive switch demand CAUSED by the coverage layer (the x4-yj atoms
whose rows cover the owner stars), or is it generic?

Ablation 1: drop the 5 coverage atoms x4yj  -> family 20 atoms; support shrinks to the
            union of the remaining rows; recompute max kappa of THAT family vs THAT support.
Ablation 2: drop the 10 bibj atoms (the triangle carriers) -> 15 atoms (both owner stars
            + coverage); recompute.
Ablation 3: owner stars only (vbj, mbj; 10 atoms).
Exact integer sweeps (2^18 masks vs the ablated edge sets).
"""
from itertools import combinations
from collections import deque

L = ['v', 'm', 'a'] + ['b%d' % j for j in range(5)]
R = ['x%d' % i for i in range(5)] + ['y%d' % j for j in range(5)]
names = L + R
idx = {s: i for i, s in enumerate(names)}
n = 18
blue = set()
for i in range(5):
    blue.add(frozenset((idx['v'], idx['x%d' % i])))
    blue.add(frozenset((idx['m'], idx['x%d' % i])))
for i in range(4):
    blue.add(frozenset((idx['a'], idx['x%d' % i])))
for j in range(5):
    blue.add(frozenset((idx['a'], idx['y%d' % j])))
    blue.add(frozenset((idx['b%d' % j], idx['y%d' % j])))
bluadj = [set() for _ in range(n)]
for e in blue:
    u, w = tuple(e)
    bluadj[u].add(w)
    bluadj[w].add(u)

def rows_support(at):
    s, t = sorted(at)
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t:
                out.append(tuple(path))
            return
        for w2 in bluadj[path[-1]]:
            if w2 not in path:
                if len(path) == 4 and w2 != t:
                    continue
                dfs(path + [w2])
    dfs([s])
    return {frozenset((r[i], r[i + 1])) for r in out for i in range(4)}

full = []
for j in range(5):
    full.append(frozenset((idx['v'], idx['b%d' % j])))
    full.append(frozenset((idx['m'], idx['b%d' % j])))
for i, j in combinations(range(5), 2):
    full.append(frozenset((idx['b%d' % i], idx['b%d' % j])))
cov = [frozenset((idx['x4'], idx['y%d' % j])) for j in range(5)]

def sweep(tag, atoms):
    sup = set()
    for at in atoms:
        sup |= rows_support(at)
    bad_edges = [tuple(sorted(e)) for e in atoms]
    blue_edges = [tuple(sorted(e)) for e in sup]
    maxk = -10**9
    am = None
    for mask in range(1 << n):
        kb = 0
        for u, w in bad_edges:
            kb += ((mask >> u) ^ (mask >> w)) & 1
        ks = 0
        for u, w in blue_edges:
            ks += ((mask >> u) ^ (mask >> w)) & 1
        if kb - ks > maxk:
            maxk, am = kb - ks, mask
    sv = sorted(names[u] for u in range(n) if (am >> u) & 1)
    print("%-34s: atoms %2d, support %2d, max kappa = %2d at S=%s"
          % (tag, len(atoms), len(sup), maxk, sv))

sweep("FULL near-candidate (25 atoms)", full + cov)
sweep("ablate coverage (drop x4yj)", full)
sweep("ablate b-clique (drop bibj)", [a for a in full if len(a & {idx['b%d' % j] for j in range(5)}) < 2] + cov)
sweep("owner stars only (vbj+mbj)", [a for a in full if idx['v'] in a or idx['m'] in a])
print("DONE ablation")
