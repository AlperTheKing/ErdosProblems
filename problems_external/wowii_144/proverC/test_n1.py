#!/usr/bin/env python3
"""proverC test #1: candidate N1 (one tail per branch, z-feasible) >= e.

N1(K) := max over z in K of  sum over branches B of G-K of
         max{ L(u) : u in B, d(u,K)=1, |N_K(u) \ {z}| = 1 }   (0 if none)
where L(u) = longest layer-increasing path in G-K starting at u
(increasing in d(.,K); such a path is automatically induced and only its
bottom vertex u has neighbours in K).

N1(K) <= M(K) always (union of the chosen tails is a valid F).
Claim to test:  e >= 1, cyclic  ==>  exists shortest cycle K: N1(K) >= e.
Also track the forall-K version and the z-relaxed version, per girth bucket.

Exact integer arithmetic only.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
WAVE2 = ROOT.parent / "wave2"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))
sys.path.insert(0, str(WAVE2))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    graph_connected,
    nx_to_bitadj,
)
from sweep_families import build_family_graphs, random_graphs  # noqa: E402
from bridge_tests import adversarial_graphs, shortest_cycles  # noqa: E402
from route_b_tests import (  # noqa: E402
    cycle_random_legs,
    cycle_random_trees,
    chorded_cycle,
    gen_theta,
    forced_girth_random,
    trap_family,
    graph6,
)
from lemma_e_tests import M_of_cycle  # noqa: E402

SEED = 20260718
OUT = ROOT / "test_n1_results.json"
M_CAP = 15          # exact M only if n - g <= M_CAP


def branches_of(n: int, adj, k_mask: int) -> list[int]:
    comps = []
    rem = ((1 << n) - 1) & ~k_mask
    while rem:
        start = rem & -rem
        reached = start
        frontier = start
        while frontier:
            new = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                new |= adj[b.bit_length() - 1]
            new &= ~k_mask & ~reached & ((1 << n) - 1)
            reached |= new
            frontier = new
        comps.append(reached)
        rem &= ~reached
    return comps


def n1_of_cycle(n: int, adj, kverts: list[int], dist) -> tuple[int, int]:
    """Return (N1(K), N1_relaxed(K))."""
    k_mask = 0
    for v in kverts:
        k_mask |= 1 << v
    dK = [min(dist[v][k] for k in kverts) for v in range(n)]
    outside = [v for v in range(n) if not (k_mask >> v & 1)]
    # longest increasing path from each vertex (in d(.,K)), DP high->low
    L = [0] * n
    for v in sorted(outside, key=lambda v: -dK[v]):
        best = 0
        nbr = adj[v] & ~k_mask
        while nbr:
            b = nbr & -nbr
            nbr ^= b
            u = b.bit_length() - 1
            if dK[u] == dK[v] + 1 and L[u] > best:
                best = L[u]
        L[v] = 1 + best
    branches = branches_of(n, adj, k_mask)
    # bottoms per branch with their K-neighbour sets
    binfo = []
    for bm in branches:
        bots = []
        m = bm
        while m:
            b = m & -m
            m ^= b
            u = b.bit_length() - 1
            if dK[u] == 1:
                nk = adj[u] & k_mask
                bots.append((u, nk, L[u]))
        binfo.append(bots)
    best_n1 = 0
    for z in kverts:
        zbit = 1 << z
        tot = 0
        for bots in binfo:
            m = 0
            for (u, nk, lu) in bots:
                if bin(nk & ~zbit).count("1") == 1 and lu > m:
                    m = lu
            tot += m
        if tot > best_n1:
            best_n1 = tot
    relaxed = sum(max((lu for (_, _, lu) in bots), default=0)
                  for bots in binfo)
    return best_n1, relaxed


def evaluate(name, G, stats, seen):
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    n, adj = nx_to_bitadj(G)
    if n < 3 or n > 34 or not graph_connected(n, adj):
        return
    g = girth(n, adj)
    if g == 0:
        return
    g6 = graph6(G)
    if g6 in seen:
        return
    seen.add(g6)
    dist = all_pairs_dist(n, adj)
    ecc_v = eccentricities(n, dist)
    r = min(ecc_v)
    cm = 0
    for v in range(n):
        if ecc_v[v] == r:
            cm |= 1 << v
    e = ecc_of_set(n, dist, cm)
    if e == 0:
        return
    n1s, rels = [], []
    for K in shortest_cycles(G, g):
        kv = sorted(K)
        a, b = n1_of_cycle(n, adj, kv, dist)
        n1s.append(a)
        rels.append(b)
    bucket = str(g) if g <= 6 else "7+"
    st = stats.setdefault(bucket, {
        "count": 0, "ex_viol": [], "fa_viol": 0, "rel_viol": 0,
        "min_ex_slack": None, "min_ex_wit": None})
    st["count"] += 1
    ex_slack = max(n1s) - e
    if st["min_ex_slack"] is None or ex_slack < st["min_ex_slack"]:
        st["min_ex_slack"] = ex_slack
        st["min_ex_wit"] = f"{name} [{g6}] n={n} g={g} r={r} e={e} N1max={max(n1s)}"
    if ex_slack < 0 and len(st["ex_viol"]) < 40:
        mk = None
        if n - g <= M_CAP:
            Ks = list(shortest_cycles(G, g))
            mk = max(M_of_cycle(n, adj, sorted(K)) for K in Ks)
        st["ex_viol"].append({
            "family": name, "graph6": g6, "n": n, "g": g, "r": r, "e": e,
            "N1_max": max(n1s), "N1_relaxed_max": max(rels), "M_max": mk})
    if min(n1s) < e:
        st["fa_viol"] += 1
    if max(rels) < e:
        st["rel_viol"] += 1


def crowns():
    out = []
    # girth 4..6 crowns: cycle + outer path at distance 1
    for g in (4, 5, 6):
        for span in range(2, g + 1):
            G = nx.cycle_graph(g)
            for i in range(span):
                G.add_edge(f"c{i}", g and i % g)
            for i in range(span - 1):
                G.add_edge(f"c{i}", f"c{i+1}")
            if girth(*nx_to_bitadj(nx.convert_node_labels_to_integers(G))) == g:
                out.append((f"crown{g}_{span}", G))
    # deeper shallow-wide branches on larger cycles
    rng = random.Random(SEED + 7)
    for trial in range(400):
        g = rng.randrange(6, 16)
        G = nx.cycle_graph(g)
        nxt = 1000
        # branch: random tree whose vertices get extra edges to K far apart
        size = rng.randrange(2, 9)
        nodes = [nxt]; nxt += 1
        att0 = rng.randrange(g)
        G.add_edge(att0, nodes[0])
        for _ in range(size - 1):
            p = rng.choice(nodes)
            G.add_edge(p, nxt)
            nodes.append(nxt); nxt += 1
        # optional extra attachments
        for v in nodes:
            if rng.random() < 0.3:
                G.add_edge(v, rng.randrange(g))
        # a few pendant legs elsewhere
        for _ in range(rng.randrange(0, 4)):
            pos = rng.randrange(g)
            ln = rng.randrange(1, 5)
            prev = pos
            for _ in range(ln):
                G.add_edge(prev, nxt)
                prev = nxt; nxt += 1
        n2, adj2 = nx_to_bitadj(nx.convert_node_labels_to_integers(G))
        if graph_connected(n2, adj2) and girth(n2, adj2) == g:
            out.append((f"wide{trial}", G))
    return out


def main() -> None:
    rng = random.Random(SEED)
    stats: dict = {}
    seen: set = set()
    corpora = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 3 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    corpora += crowns()
    for _ in range(1200):
        corpora.append(cycle_random_legs(rng))
    for _ in range(900):
        corpora.append(cycle_random_trees(rng))
    for _ in range(700):
        corpora.append(chorded_cycle(rng))
    for _ in range(500):
        corpora.append(gen_theta(rng))
    got, tries = 0, 0
    while got < 700 and tries < 12000:
        tries += 1
        rgr = forced_girth_random(rng, gmin=5)
        if rgr is not None:
            corpora.append(rgr)
            got += 1

    for name, G in corpora:
        evaluate(name, G, stats, seen)

    res = {"test": "proverC_N1", "seed": SEED, "graphs": len(seen),
           "buckets": {}}
    for b in sorted(stats):
        st = stats[b]
        res["buckets"][b] = {
            "count": st["count"],
            "exists_viol": len(st["ex_viol"]),
            "forall_viol": st["fa_viol"],
            "relaxed_viol": st["rel_viol"],
            "min_exists_slack": st["min_ex_slack"],
            "min_exists_witness": st["min_ex_wit"],
            "exists_viol_records": st["ex_viol"],
        }
    OUT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    for b in sorted(res["buckets"]):
        rb = res["buckets"][b]
        print(f"g={b}: count={rb['count']} exViol={rb['exists_viol']} "
              f"faViol={rb['forall_viol']} relViol={rb['relaxed_viol']} "
              f"minSlack={rb['min_exists_slack']}")
        print("   wit:", rb["min_exists_witness"])
        for vrec in rb["exists_viol_records"][:6]:
            print("   CE:", vrec)


if __name__ == "__main__":
    main()
