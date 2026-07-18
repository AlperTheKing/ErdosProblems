#!/usr/bin/env python3
"""WOWII 144 wave2: stress Lemma E (e <= M(K)) on the two hardest structural
classes: (1) random subdivided multigraphs (many overlapping shortest cycles,
non-forest outside structure), (2) webbed annuli: C_g + two tails + a cross
edge at the exact girth threshold (i + j + delta + 1 >= g), + random legs.

Checks, for every connected cyclic graph with n - girth <= 16:
  girth >= 4 :  min over shortest cycles K of M(K) >= e   (forall-K form)
  girth == 3 :  max over shortest cycles K of M(K) >= e   (exists-K form)

Run:  python stress_lemma_e.py      (seed 20260719, ~5400 distinct graphs)
Result 2026-07-18: 0 violations, 46 tight (M = e) cases at girth >= 4.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "wowii_141" / "oracle"))
sys.path.insert(0, str(ROOT.parent / "oracle"))

from invariants import (all_pairs_dist, ecc_of_set, eccentricities, girth,
                        graph_connected, nx_to_bitadj)
from bridge_tests import shortest_cycles
from route_b_tests import graph6
from lemma_e_tests import M_of_cycle

SEED = 20260719


def subdivided_multigraph(rng):
    k = rng.randrange(2, 6)
    edges = [(i, i + 1) for i in range(k - 1)]
    for _ in range(rng.randrange(2, 5)):
        edges.append((rng.randrange(k), rng.randrange(k)))
    G = nx.Graph()
    G.add_nodes_from(range(k))
    lbl = 0
    for (a, b) in edges:
        L = rng.randrange(1, 7)
        if a == b and L < 3:
            L = 3
        prev = a
        for _ in range(L - 1):
            v = f"s{lbl}"; lbl += 1
            G.add_edge(prev, v); prev = v
        if prev == a and b == a:
            continue
        if G.has_edge(prev, b):
            v = f"s{lbl}"; lbl += 1
            G.add_edge(prev, v); prev = v
        G.add_edge(prev, b)
    for _ in range(rng.randrange(0, 4)):
        base = rng.choice(list(G.nodes()))
        for _ in range(rng.randrange(1, 5)):
            v = f"s{lbl}"; lbl += 1
            G.add_edge(base, v); base = v
    return G


def webbed_annulus(rng):
    g = rng.randrange(8, 20)
    G = nx.cycle_graph(g)
    pos2 = rng.randrange(2, g - 1)
    delta = min(pos2, g - pos2)
    h1 = rng.randrange(2, 8); h2 = rng.randrange(2, 8)
    t1 = [0]; t2 = [pos2]
    for i in range(h1):
        G.add_edge(t1[-1], f"a{i}"); t1.append(f"a{i}")
    for i in range(h2):
        G.add_edge(t2[-1], f"b{i}"); t2.append(f"b{i}")
    added = False
    for i in range(h1, 0, -1):
        for j in range(h2, 0, -1):
            if i + j + delta + 1 >= g and not added:
                G.add_edge(t1[i], t2[j]); added = True
    for jj in range(rng.randrange(0, 4)):
        prev = rng.randrange(g)
        for i in range(rng.randrange(1, 4)):
            G.add_edge(prev, f"L{jj}_{i}"); prev = f"L{jj}_{i}"
    return G


def main() -> None:
    rng = random.Random(SEED)
    bad = []; seen = set(); checked = 0; tight = 0
    gens = [subdivided_multigraph] * 4000 + [webbed_annulus] * 4000
    for genf in gens:
        G = genf(rng)
        if not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 3:
            continue
        g = girth(n, adj)
        if g == 0 or n - g > 16:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc_v = eccentricities(n, dist)
        radius = min(ecc_v)
        cm = 0
        for v in range(n):
            if ecc_v[v] == radius:
                cm |= 1 << v
        e = ecc_of_set(n, dist, cm)
        if e == 0:
            continue
        checked += 1
        vals = [M_of_cycle(n, adj, sorted(K)) for K in shortest_cycles(G, g)]
        if g >= 4:
            if min(vals) < e:
                bad.append(("FORALL", g6, n, g, e, min(vals)))
            if max(vals) == e:
                tight += 1
        elif max(vals) < e:
            bad.append(("EXISTS-g3", g6, n, g, e, max(vals)))
    print("checked:", checked, "tight:", tight, "violations:", len(bad))
    for b in bad[:20]:
        print("  ", b)


if __name__ == "__main__":
    main()
