#!/usr/bin/env python3
"""proverC test #2: candidate N5 assembly (canonical tails + V-merges + z).

Canonical structure w.r.t. a shortest cycle K:
  dK(v) = d(v,K); parent(v) = min-index neighbour one layer down
  (for dK=1: bottom; att(v) = N_K(v)); tail(w) = parent chain of w
  (always an induced path, only its bottom touches K).
Objects:
  TAIL(w)  verts = chain(w), atts = N_K(bottom)
  V(x,y)   for each edge xy off K with root(x) != root(y):
           verts = chain(x) U chain(y) if G[verts] is a tree,
           atts = N_K(bot_x) U N_K(bot_y)
Assembly (this is exactly what the intended proof can build):
  choose z in K, then a set of objects, pairwise vertex-disjoint and
  pairwise non-adjacent, each with |atts - {z}| = 1; mass = total verts.
  N5(K) = max mass.  Claim: exists shortest cycle K with N5(K) >= e.
Exact integer arithmetic; exact branch&bound (capped, cap flagged).
Girth >= 4 only (g=3 handled separately later).
"""
from __future__ import annotations

import json
import random
import sys
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
    all_pairs_dist, ecc_of_set, eccentricities, girth,
    graph_connected, nx_to_bitadj,
)
from sweep_families import build_family_graphs, random_graphs  # noqa: E402
from bridge_tests import adversarial_graphs, shortest_cycles  # noqa: E402
from route_b_tests import (  # noqa: E402
    cycle_random_legs, cycle_random_trees, chorded_cycle, gen_theta,
    forced_girth_random, trap_family, graph6,
)

SEED = 20260718
OUT = ROOT / "test_n5_results.json"
NODE_CAP = 400000


def bits(m):
    while m:
        b = m & -m
        m ^= b
        yield b.bit_length() - 1


def n5_of_cycle(n, adj, kverts, dist):
    k_mask = 0
    for v in kverts:
        k_mask |= 1 << v
    full = (1 << n) - 1
    dK = [min(dist[v][k] for k in kverts) for v in range(n)]
    out_mask = full & ~k_mask
    parent = [-1] * n
    root = [-1] * n
    for v in sorted(bits(out_mask), key=lambda v: dK[v]):
        if dK[v] == 1:
            root[v] = min(bits(adj[v] & k_mask))
        else:
            p = min(u for u in bits(adj[v] & out_mask) if dK[u] == dK[v] - 1)
            parent[v] = p
            root[v] = root[p]

    def chain_mask(w):
        m = 0
        while w != -1 and not (k_mask >> w & 1):
            m |= 1 << w
            if dK[w] == 1:
                break
            w = parent[w]
        return m

    def att_mask(vm):
        a = 0
        for v in bits(vm):
            a |= adj[v] & k_mask
        return a

    objs = {}
    for w in bits(out_mask):
        vm = chain_mask(w)
        objs[vm] = att_mask(vm)
    # V objects
    edges = []
    for v in bits(out_mask):
        for u in bits(adj[v] & out_mask):
            if u < v:
                edges.append((u, v))
    for (u, v) in edges:
        if root[u] == root[v]:
            continue
        vm = chain_mask(u) | chain_mask(v)
        sz = vm.bit_count()
        ecnt = sum((adj[x] & vm).bit_count() for x in bits(vm)) // 2
        if ecnt != sz - 1:
            continue  # not a tree (shared vertex impossible: roots differ)
        objs[vm] = att_mask(vm)

    items = [(vm.bit_count(), vm, am) for vm, am in objs.items()]
    items.sort(key=lambda t: -t[0])
    # closed neighbourhoods for non-adjacency
    nbh = []
    for (_, vm, _) in items:
        c = vm
        for v in bits(vm):
            c |= adj[v]
        nbh.append(c)

    best_all = 0
    capped = False
    for z in kverts:
        zbit = 1 << z
        usable = [i for i, (_, vm, am) in enumerate(items)
                  if (am & ~zbit).bit_count() == 1
                  and bin(am & ~zbit).count("1") >= 0]
        # exact check |atts - z| == 1 means exactly one K-vertex outside z
        # but multiplicity of edges: need exactly one EDGE into K-z.
        # count edges: for each object, edges into K-z:
        ok_items = []
        for i in usable:
            vm = items[i][1]
            ecount = 0
            for v in bits(vm):
                ecount += (adj[v] & k_mask & ~zbit).bit_count()
            if ecount == 1:
                ok_items.append(i)
        order = sorted(ok_items, key=lambda i: -items[i][0])
        sizes = [items[i][0] for i in order]
        suffix = [0] * (len(order) + 1)
        for i in range(len(order) - 1, -1, -1):
            suffix[i] = suffix[i + 1] + sizes[i]
        best = 0
        nodes = 0

        def rec(idx, used_nbh, used_vm, mass):
            nonlocal best, nodes, capped
            if nodes > NODE_CAP:
                capped = True
                return
            nodes += 1
            if mass > best:
                best = mass
            if idx >= len(order) or mass + suffix[idx] <= best:
                return
            i = order[idx]
            _, vm, _ = items[i]
            # include if compatible: disjoint and non-adjacent
            if not (vm & used_nbh):
                rec(idx + 1, used_nbh | nbh[i], used_vm | vm,
                    mass + items[i][0])
            rec(idx + 1, used_nbh, used_vm, mass)

        rec(0, 0, 0, 0)
        if best > best_all:
            best_all = best
    return best_all, capped


def evaluate(name, G, res, seen):
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    n, adj = nx_to_bitadj(G)
    if n < 4 or n > 32 or not graph_connected(n, adj):
        return
    g = girth(n, adj)
    if g < 3:
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
    best = -1
    any_capped = False
    for K in shortest_cycles(G, g):
        val, capped = n5_of_cycle(n, adj, sorted(K), dist)
        any_capped |= capped
        if val > best:
            best = val
        if best >= e:
            break
    bucket = ("g3" if g == 3 else "g4" if g == 4 else
              "EXT" if g >= 2 * r else "SLACK")
    st = res.setdefault(bucket, {"count": 0, "viol": [], "min_slack": None,
                                 "min_wit": None, "capped": 0})
    st["count"] += 1
    if any_capped:
        st["capped"] += 1
    sl = best - e
    if st["min_slack"] is None or sl < st["min_slack"]:
        st["min_slack"] = sl
        st["min_wit"] = f"{name} [{g6}] n={n} g={g} r={r} e={e} N5={best}"
    if sl < 0 and len(st["viol"]) < 30:
        st["viol"].append({"family": name, "graph6": g6, "n": n, "g": g,
                           "r": r, "e": e, "N5": best})


def hard_named():
    out = []
    for g6 in ("F~AGO", "FhELO", "MA?OQO@@@CocOC?`?"):
        out.append((f"named[{g6}]", nx.from_graph6_bytes(g6.encode())))
    return out


def triangle_adversarial(rng):
    G = nx.cycle_graph(3)
    nxt = 3
    for _ in range(rng.randrange(1, 6)):
        pos = rng.randrange(3)
        size = rng.randrange(1, 9)
        nodes = []
        G.add_edge(pos, nxt)
        nodes.append(nxt)
        nxt += 1
        for _ in range(size - 1):
            p = rng.choice(nodes)
            G.add_edge(p, nxt)
            nodes.append(nxt)
            nxt += 1
        # random extra edges into the triangle (multi-attach)
        for v in nodes:
            if rng.random() < 0.25:
                G.add_edge(v, rng.randrange(3))
    return ("triAdv", G)


def crown_wide(rng):
    g = rng.randrange(4, 15)
    G = nx.cycle_graph(g)
    nxt = 100
    size = rng.randrange(2, 10)
    nodes = [nxt]
    G.add_edge(rng.randrange(g), nxt)
    nxt += 1
    for _ in range(size - 1):
        p = rng.choice(nodes)
        G.add_edge(p, nxt)
        nodes.append(nxt)
        nxt += 1
    for v in nodes:
        if rng.random() < 0.35:
            G.add_edge(v, rng.randrange(g))
    for _ in range(rng.randrange(0, 4)):
        pos = rng.randrange(g)
        ln = rng.randrange(1, 6)
        prev = pos
        for _ in range(ln):
            G.add_edge(prev, nxt)
            prev = nxt
            nxt += 1
    return ("crownWide", G)


def main():
    rng = random.Random(SEED)
    res = {}
    seen = set()
    corpora = []
    corpora += hard_named()
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 4 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    for _ in range(1500):
        corpora.append(triangle_adversarial(rng))
    for _ in range(1200):
        corpora.append(crown_wide(rng))
    for n_ in range(8, 15):
        for p_ in (12, 18, 25, 40):
            for _ in range(60):
                corpora.append((f"gnp{n_}",
                                nx.gnp_random_graph(
                                    n_, p_ / 100,
                                    seed=rng.randrange(1 << 30))))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(900):
        corpora.append(cycle_random_legs(rng))
    for _ in range(700):
        corpora.append(cycle_random_trees(rng))
    for _ in range(600):
        corpora.append(chorded_cycle(rng))
    for _ in range(400):
        corpora.append(gen_theta(rng))
    got, tries = 0, 0
    while got < 800 and tries < 15000:
        tries += 1
        rgr = forced_girth_random(rng, gmin=4)
        if rgr is not None:
            corpora.append(rgr)
            got += 1
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(900):
        corpora.append(cycle_random_legs(rng))
    for _ in range(700):
        corpora.append(cycle_random_trees(rng))
    for _ in range(600):
        corpora.append(chorded_cycle(rng))
    for _ in range(400):
        corpora.append(gen_theta(rng))
    for name, G in corpora:
        evaluate(name, G, res, seen)

    OUT.write_text(json.dumps(res, indent=2, sort_keys=True,
                              default=str) + "\n")
    for b in sorted(res):
        st = res[b]
        print(f"{b}: count={st['count']} viol={len(st['viol'])} "
              f"minSlack={st['min_slack']} capped={st['capped']}")
        print("   wit:", st["min_wit"])
        for v in st["viol"][:8]:
            print("   CE:", v)


if __name__ == "__main__":
    main()
