#!/usr/bin/env python3
"""Targeted exact falsifier for the reserved rooted-capacity candidate N2."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
PROVER = HERE.parent / "proverC"
sys.path.insert(0, str(PROVER))

from test_gpt_n2 import (  # noqa: E402
    all_pairs_dist,
    bits,
    components_outside,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    graph6,
    mz_values,
    nx_to_bitadj,
    shortest_cycles,
)


def evaluate(G: nx.Graph):
    """Return None off-regime, otherwise (best_slack, exact witness data)."""
    if not nx.is_connected(G):
        return None
    G = nx.convert_node_labels_to_integers(G)
    n, adj = nx_to_bitadj(G)
    g = girth(n, adj)
    if g < 5 or n - g > 18:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r, D = min(ecc), max(ecc)
    cmask = sum(1 << v for v in range(n) if ecc[v] == r)
    e = ecc_of_set(n, dist, cmask)
    if e == 0 or e <= D - g // 2:
        return None
    realizers = [v for v in range(n) if dist_to_set(dist, v, cmask) == e]
    best = None
    best_data = None
    for K in shortest_cycles(G, g):
        kverts = sorted(K)
        kmask = sum(1 << v for v in kverts)
        comps = components_outside(adj, ((1 << n) - 1) & ~kmask)
        mz = mz_values(n, adj, kverts)
        for x in realizers:
            h = dist_to_set(dist, x, kmask)
            if h >= e:
                return (0, ("tail", K, x, h, e))
            for m in (a for a in kverts if dist[x][a] == h):
                W = [a for a in kverts if dist[a][m] <= e - h - 1]
                covsum = sum(
                    sum(max(dist[sig][y] for y in bits(H)) >= r + 1 for sig in W)
                    for H in comps
                )
                for z in kverts:
                    if z == m:
                        continue
                    slack = 2 * (mz[z] - h) - covsum - max(0, 2 * (e - h) - g)
                    if best is None or slack > best:
                        best = slack
                        best_data = (K, x, h, m, z, tuple(W), covsum, mz[z], mz)
    return best, (n, g, r, D, e, best_data)


def rooted_leg_cycle(g: int, lengths: list[int], chords: list[tuple[int, int]] = []):
    """Cycle with pendant legs, optionally joined by edges between leg tips."""
    G = nx.cycle_graph(g)
    tips = []
    nxt = g
    for root, length in enumerate(lengths):
        prev = root
        for _ in range(length):
            G.add_edge(prev, nxt)
            prev = nxt
            nxt += 1
        tips.append(prev)
    for a, b in chords:
        G.add_edge(tips[a], tips[b])
    return G


def mutate(G: nx.Graph, rng: random.Random) -> nx.Graph:
    H = G.copy()
    n = len(H)
    if rng.random() < 0.55 and n < 24:
        v = n
        H.add_edge(v, rng.randrange(n))
        if rng.random() < 0.45:
            H.add_edge(v, rng.randrange(n))
    else:
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if not H.has_edge(u, v)]
        if pairs:
            H.add_edge(*rng.choice(pairs))
    return H


def main():
    rng = random.Random(20260718)
    seeds = []
    for g in range(5, 13):
        for _ in range(200):
            lengths = [rng.randrange(0, 5) for _ in range(g)]
            if sum(lengths) <= 18:
                seeds.append(rooted_leg_cycle(g, lengths))
    population = seeds
    seen = set()
    best_seen = None
    checked = residual = 0
    for generation in range(7):
        scored = []
        for G in population:
            key = graph6(nx.convert_node_labels_to_integers(G))
            if key in seen:
                continue
            seen.add(key)
            checked += 1
            out = evaluate(G)
            if out is None:
                continue
            residual += 1
            slack, data = out
            scored.append((slack, key, G, data))
            if best_seen is None or slack < best_seen[0]:
                best_seen = (slack, key, data)
                print("BEST", best_seen, flush=True)
            if slack < 0:
                print("COUNTEREXAMPLE", key, data, flush=True)
                return
        scored.sort(key=lambda t: t[0])
        parents = [t[2] for t in scored[:80]]
        if not parents:
            parents = rng.sample(seeds, min(80, len(seeds)))
        population = [mutate(rng.choice(parents), rng) for _ in range(1200)]
        print({"generation": generation, "checked": checked,
               "residual": residual, "best": best_seen}, flush=True)
    print({"checked": checked, "residual": residual, "best": best_seen})


if __name__ == "__main__":
    main()

