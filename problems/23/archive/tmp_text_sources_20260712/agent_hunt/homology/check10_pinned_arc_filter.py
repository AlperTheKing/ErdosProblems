#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 10: the PINNED-TRAFFIC ARC FILTER (t-uniform, kernel-cheap).

Primitive: an edge e is PINNED on a circuit iff some chosen atom uses e in
EVERY row of its complete family (= R50's ProfileForced(e), computable from
the row DB alone).  A pinned edge has selected multiplicity >= 1 in EVERY
tuple, hence is NEVER latent, hence can NEVER be filled as an owner's active
edge by any rotor transition.

Filter: a directed swap arc inserting v between x and y is live only if its
active edge (one of vx, vy) is latent at swap time.  If BOTH vx and vy are
pinned, the arc is DEAD for every tuple.  If exactly one is pinned, the arc's
active edge is FORCED to be the other (a strong per-arc certificate input).

This computes, per reconstructed circuit of #298/#264, for every owner-swap
arc: pinned status of the two inserted edges, and the verdict
DEAD / FORCED-ACTIVE(edge) / FREE.  Also reports the pinned edge set and which
rotor-core squares (if any) have >= 1 pinned edge (the check-3/4 blockade in
ProfileForced language).
"""
import sys
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_atoms_v3 import find_circuits_v3
from fixture_264_variants import find as find_variant
from check7_arc_capture_and_bounce_motif import arcs_of

def pinned_edges(fx, circ):
    pin = set()
    for a in circ:
        fam = fx['rows'][a]
        forced = None
        for r in fam:
            es = {frozenset((r[i], r[i+1])) for i in range(4)}
            forced = es if forced is None else (forced & es)
        pin |= forced
    return pin

def analyze(tag):
    fx = build(tag)
    if tag == '298':
        subs = find_circuits_v3(fx, cap=1000)
    else:
        subs, _ = find_variant(fx, (0,), cap=1000)
    subs = [sorted(map(tuple, s)) for s in subs]
    print(f"\n===== {tag}: {len(subs)} circuits =====")
    for si, circ in enumerate(subs):
        chosen = set(map(tuple, circ))
        dM = defaultdict(int)
        for u, w in circ:
            dM[u] += 1; dM[w] += 1
        OWN = {u for u in range(fx['n']) if len(fx['adj'][u]) == 5 and dM[u] == 5}
        pin = pinned_edges(fx, circ)
        A = arcs_of(fx, circ, OWN)
        dead = forced = free = 0
        forced_edges = defaultdict(int)
        for (a, i, j, m, v, x, y, p) in A:
            e_vx = frozenset((v, x))
            e_vy = frozenset((v, y))
            px, py = e_vx in pin, e_vy in pin
            if px and py:
                dead += 1
            elif px or py:
                forced += 1
                fe = e_vy if px else e_vx
                forced_edges[tuple(sorted(fe))] += 1
            else:
                free += 1
        print(f" circuit#{si}: pinned edges {len(pin)}/24 "
              f"{sorted(tuple(sorted(e)) for e in pin)}")
        print(f"   owner-swap arcs {len(A)}: DEAD(both pinned)={dead} "
              f"FORCED-ACTIVE={forced} FREE={free}")
        if forced_edges:
            print(f"   forced active edges (edge: #arcs): "
                  f"{dict(sorted(forced_edges.items()))}")

if __name__ == '__main__':
    for tag in ('298', '264'):
        analyze(tag)
