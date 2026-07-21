#!/usr/bin/env python3
"""proverC diagnostic: run the intended PROOF ALGORITHM for g>=5 and
classify every phenomenon (case split, witness cover, tail conflicts).

Algorithm per (G,K):
  Case I:  H >= e  -> success (tail of any deepest vertex).
  Case II: window W around m=root(x*) (or x* itself if on K), radius
           delta-1, delta=e-h.  Every sigma in W has witnesses
           Omega_sigma = {w : d(sigma,w) >= r+1} (all off K).
           Per root a: T(a) = max depth of a witness with root a
           (over witnesses chosen for all sigma; here: all far vertices).
           Greedy minimal cover R' by arcs Arc(a,T(a)).
           Ledger check: h + sum T(a) >= e (no-wrap) / sum >= r+1 (wrap).
           Conflict graph on tails {tau(w(a)): a in R'} + tau(x*):
           edges = adjacency between tail vertex sets.
           Classify components; attempt assembly by the proof rules:
             - singleton -> tail (1-attach, g>=5)
             - pair with single cross edge -> union, needs z in {a,b}
             - pair multi-cross -> minimal-V (tau(x) U tau(x'))
             - bigger comps -> record (chain)
           at most ONE 2-attachment object allowed (it fixes z).
  Report per graph: which cases, whether assembly >= e, all anomalies.
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
OUT = ROOT / "alg_diag_results.json"


def bits(m):
    while m:
        b = m & -m
        m ^= b
        yield b.bit_length() - 1


def diag_cycle(n, adj, kverts, dist, e, r, cmask):
    """Run the proof algorithm on one shortest cycle. Returns dict."""
    g = len(kverts)
    k_mask = 0
    for v in kverts:
        k_mask |= 1 << v
    full = (1 << n) - 1
    out_mask = full & ~k_mask
    dK = [min(dist[v][k] for k in kverts) for v in range(n)]
    kpos = {k: i for i, k in enumerate(kverts)}

    def dkk(u, v):  # cycle distance between two K vertices
        d0 = abs(kpos[u] - kpos[v]) % g
        return min(d0, g - d0)

    H = max((dK[v] for v in bits(out_mask)), default=0)
    info = {"g": g, "H": H}
    if H >= e:
        info["case"] = "I"
        info["ok"] = True
        return info

    parent = [-1] * n
    root = [-1] * n
    for v in sorted(bits(out_mask), key=lambda v: dK[v]):
        if dK[v] == 1:
            root[v] = min(bits(adj[v] & k_mask))
        else:
            parent[v] = min(u for u in bits(adj[v] & out_mask)
                            if dK[u] == dK[v] - 1)
            root[v] = root[parent[v]]

    def chain(w):
        m = 0
        while True:
            m |= 1 << w
            if dK[w] == 1:
                return m
            w = parent[w]

    # pick x*: try every realizer, prefer one that succeeds; here just
    # analyse the FIRST realizer (min index) -- proof must fix a rule.
    realizers = [v for v in range(n)
                 if min(dist[v][c] for c in bits(cmask)) == e]
    results = []
    for xs in realizers:
        h = dK[xs] if not (k_mask >> xs & 1) else 0
        m_anchor = xs if h == 0 else root[xs]
        delta = e - h
        wrap = 2 * delta - 1 > g
        W = [k for k in kverts if dkk(k, m_anchor) <= delta - 1]
        # witnesses
        Troot = {}
        wit_of = {}
        cover_fail = False
        for sig in W:
            far = [w for w in bits(out_mask) if dist[sig][w] >= r + 1]
            if not far:
                cover_fail = True
                break
            for w in far:
                a = root[w]
                if dK[w] > Troot.get(a, 0):
                    Troot[a] = dK[w]
                    wit_of[a] = w
        if cover_fail:
            results.append({"xs": xs, "fail": "no-witness"})
            continue
        # arcs; greedy minimal cover (drop redundant roots)
        roots = sorted(Troot, key=lambda a: -Troot[a])

        def arc(a):
            return {s for s in W if dkk(s, a) >= r + 1 - Troot[a]}

        chosen = []
        covered = set()
        for a in roots:
            if not arc(a) - covered:
                continue
            chosen.append(a)
            covered |= arc(a)
        if covered != set(W):
            results.append({"xs": xs, "fail": "arc-cover-bug"})
            continue
        # remove redundant (inclusion-minimal)
        changed = True
        while changed:
            changed = False
            for a in list(chosen):
                rest = set()
                for b in chosen:
                    if b != a:
                        rest |= arc(b)
                if set(W) <= rest:
                    chosen.remove(a)
                    changed = True
                    break
        massT = sum(Troot[a] for a in chosen)
        ledger_ok = (massT >= r + 1) if wrap else (h + massT >= e)
        # tails + conflicts
        objs = {a: chain(wit_of[a]) for a in chosen}
        if h >= 1:
            objs["X"] = chain(xs)
        keys = list(objs)
        confl = {k: set() for k in keys}
        for i, ki in enumerate(keys):
            for kj in keys[i + 1:]:
                vm, um = objs[ki], objs[kj]
                nb = 0
                for v in bits(vm):
                    nb |= adj[v]
                if um & nb or um & vm:
                    confl[ki].add(kj)
                    confl[kj].add(ki)
        # component classification
        seen_k = set()
        comp_types = Counter()
        pair2att = 0
        for k in keys:
            if k in seen_k:
                continue
            comp = {k}
            st = [k]
            while st:
                c = st.pop()
                for d2 in confl[c]:
                    if d2 not in comp:
                        comp.add(d2)
                        st.append(d2)
            seen_k |= comp
            if len(comp) == 1:
                comp_types["single"] += 1
            elif len(comp) == 2:
                a, b = sorted(comp)
                vm, um = objs[a], objs[b]
                ce = 0
                for v in bits(vm):
                    ce += (adj[v] & um).bit_count()
                if vm & um:
                    comp_types["overlap"] += 1
                elif ce == 1:
                    comp_types["pair1"] += 1
                    pair2att += 1
                else:
                    comp_types["pairmulti"] += 1
                    pair2att += 1
            else:
                comp_types["chain%d" % len(comp)] += 1
        rec = {"xs": xs, "wrap": wrap, "s": len(chosen),
               "ledger_ok": ledger_ok,
               "massT": massT, "h": h, "delta": delta,
               "mroot_used": (m_anchor in chosen),
               "comp": dict(comp_types), "pair2att": pair2att}
        results.append(rec)
    info["case"] = "II"
    info["runs"] = results
    # aggregate anomalies for this K
    info["any_ledger_fail"] = any(not rr.get("ledger_ok", False)
                                  for rr in results if "fail" not in rr)
    info["any_conflict"] = any(
        sum(v for kk, v in rr.get("comp", {}).items() if kk != "single") > 0
        for rr in results if "fail" not in rr)
    info["multi2att"] = any(rr.get("pair2att", 0) > 1 for rr in results)
    info["mroot"] = any(rr.get("mroot_used") for rr in results)
    return info


def main():
    rng = random.Random(SEED)
    seen = set()
    agg = Counter()
    anomalies = []
    corpora = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 5 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(1200):
        corpora.append(cycle_random_legs(rng))
    for _ in range(900):
        corpora.append(cycle_random_trees(rng))
    for _ in range(800):
        corpora.append(chorded_cycle(rng))
    for _ in range(500):
        corpora.append(gen_theta(rng))
    got, tries = 0, 0
    while got < 900 and tries < 15000:
        tries += 1
        rgr = forced_girth_random(rng, gmin=5)
        if rgr is not None:
            corpora.append(rgr)
            got += 1

    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 5 or n > 40 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g < 5:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc_v = eccentricities(n, dist)
        r = min(ecc_v)
        cmask = 0
        for v in range(n):
            if ecc_v[v] == r:
                cmask |= 1 << v
        e = ecc_of_set(n, dist, cmask)
        if e == 0:
            continue
        agg["graphs"] += 1
        regime = "EXT" if g >= 2 * r else "SLACK"
        agg[f"graphs_{regime}"] += 1
        per_k = []
        for K in shortest_cycles(G, g):
            info = diag_cycle(n, adj, sorted(K), dist, e, r, cmask)
            per_k.append(info)
        caseI = any(i["case"] == "I" for i in per_k)
        if caseI:
            agg[f"caseI_{regime}"] += 1
            continue
        agg[f"caseII_{regime}"] += 1
        led_fail = all(i.get("any_ledger_fail") for i in per_k)
        conf = any(i.get("any_conflict") for i in per_k)
        multi = any(i.get("multi2att") for i in per_k)
        mroot = any(i.get("mroot") for i in per_k)
        if led_fail:
            agg[f"LEDGERFAIL_{regime}"] += 1
            anomalies.append(("ledger", name, g6, e, r, per_k[0]))
        if conf:
            agg[f"conflict_{regime}"] += 1
            anomalies.append(("conflict", name, g6, e, r,
                              [i.get("runs") for i in per_k]))
        if multi:
            agg[f"multi2att_{regime}"] += 1
        if mroot:
            agg[f"mrootwitness_{regime}"] += 1
    print(dict(agg))
    OUT.write_text(json.dumps(
        {"agg": dict(agg),
         "anomalies": [str(a)[:2000] for a in anomalies[:60]]},
        indent=2) + "\n")
    print("anomaly count:", len(anomalies))
    for a in anomalies[:12]:
        print("  ", str(a)[:500])


if __name__ == "__main__":
    main()
