#!/usr/bin/env python3
"""Deterministic targeted falsifier for the W144 full-cycle metric lemma."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
W144 = HERE.parent
sys.path[:0] = [str(W144 / "proverC"), str(HERE)]
from test_gpt_n2 import all_pairs_dist, bits, components_outside, eccentricities, girth, graph6, nx_to_bitadj
from verify_ordinary_triameter_n14 import atts, jmetric

OUT = HERE / "fullcycle_triameter_targeted.json"


def add_if_girth_safe(G, u, v, g):
    if u == v or G.has_edge(u, v):
        return False
    G.add_edge(u, v)
    n, adj = nx_to_bitadj(nx.convert_node_labels_to_integers(G))
    ok = girth(n, adj) >= g
    if not ok:
        G.remove_edge(u, v)
    return ok


def make_graph(rng):
    g = rng.randrange(7, 15)
    G = nx.cycle_graph(g)
    q = rng.randrange(1, 17)
    T = nx.from_prufer_sequence([rng.randrange(q) for _ in range(max(0, q - 2))]) if q >= 2 else nx.empty_graph(1)
    off = len(G)
    G.add_edges_from((off + u, off + v) for u, v in T.edges())
    hv = list(range(off, off + q))
    made = 0
    for _ in range(rng.randrange(1, min(7, q + 2))):
        choices = [(u, a) for u in hv for a in range(g)]
        rng.shuffle(choices)
        for u, a in choices:
            if add_if_girth_safe(G, u, a, g):
                made += 1
                break
    if made == 0:
        return None, None
    for _ in range(rng.randrange(0, 5)):
        u, v = rng.sample(hv, 2) if len(hv) >= 2 else (hv[0], hv[0])
        add_if_girth_safe(G, u, v, g)
    # Other components alter the ambient radius and are part of the exact test.
    for _ in range(rng.randrange(0, 5)):
        prev = rng.randrange(g)
        for _ in range(rng.randrange(1, 7)):
            v = len(G)
            G.add_edge(prev, v)
            prev = v
    G = nx.convert_node_labels_to_integers(G)
    n, adj = nx_to_bitadj(G)
    if girth(n, adj) != g:
        return None, None
    return G, list(range(g))


def evaluate(G, K):
    n, adj = nx_to_bitadj(G)
    g = len(K)
    dist = all_pairs_dist(n, adj)
    r = min(eccentricities(n, dist))
    lam = 2 * r + 1 - g
    km = sum(1 << v for v in K)
    best = None
    for H in components_outside(adj, ((1 << n) - 1) & ~km):
        A = atts(adj, K, H)
        for z in K:
            if not (set(A) - {z}):
                continue
            E = [s for s in K if max(dist[s][y] for y in bits(H)) >= r + 1]
            P, pair = jmetric(adj, K, H, z)
            slack = P - len(E) - lam
            rec = dict(
                graph6=graph6(G), n=n, g=g, r=r, lambda_=lam, K=K,
                H=list(bits(H)), attachments=A, z=z, E_full=E,
                rooted_triameter=P, maximizing_pair=pair, slack=slack,
            )
            if best is None or slack < best[0]:
                best = slack, rec
    return best


def main():
    rng = random.Random(144_20260718)
    result = dict(seed=144_20260718, generated=0, legal_graphs=0, records=0, min_slack=10**9, min_record=None, failure=None)
    for i in range(100_000):
        G, K = make_graph(rng)
        result["generated"] += 1
        if G is None:
            continue
        out = evaluate(G, K)
        if out is None:
            continue
        result["legal_graphs"] += 1
        slack, rec = out
        result["records"] += 1
        if slack < result["min_slack"]:
            result["min_slack"] = slack
            result["min_record"] = rec
            print("BEST", i, slack, rec, flush=True)
        if slack < 0:
            result["failure"] = rec
            break
        if i and i % 10_000 == 0:
            print(i, result["legal_graphs"], result["min_slack"], flush=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result)


if __name__ == "__main__":
    main()
