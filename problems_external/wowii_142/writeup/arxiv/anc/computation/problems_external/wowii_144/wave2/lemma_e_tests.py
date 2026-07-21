#!/usr/bin/env python3
"""WOWII 144 wave2: test Lemma E   e <= max_K M(K)   (and per-K variants).

M(K) := max |F| over induced forests F of G - V(K) such that for SOME z in K,
every connected component of F sends exactly one edge into K - {z}.
(Then  (K - z) union F  is an induced tree, so  tree >= g - 1 + M(K):
Lemma M, rigorous for every shortest cycle K since shortest cycles are
chordless.)

Lemma E + Lemma M ==> C144 for cyclic graphs (acyclic case trivial).

Variants scored:
  E_exists : e <= max over shortest cycles K of M(K)
  E_forall : e <= min over shortest cycles K of M(K)

Corpora: same generators as route_b_tests (atlas, families+random, adversarial,
traps, random legs/trees/ears/thetas, forced girth) but capped so that
2^(n - g) enumeration is feasible:  n - g <= EXP_CAP.  Exact arithmetic.
Output: lemma_e_results.json
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    graph_connected,
    largest_induced_tree,
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

OUT = ROOT / "lemma_e_results.json"
SEED = 20260718
EXP_CAP = 17          # enumerate subsets of V-K only if n - g <= EXP_CAP
MAX_RECORDS = 60


def components_of_mask(adj, mask: int) -> list[int]:
    comps = []
    rem = mask
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
            new &= mask & ~reached
            reached |= new
            frontier = new
        comps.append(reached)
        rem &= ~reached
    return comps


def edges_in_mask(adj, mask: int) -> int:
    total = 0
    m = mask
    while m:
        b = m & -m
        m ^= b
        total += (adj[b.bit_length() - 1] & mask).bit_count()
    return total // 2


def M_of_cycle(n: int, adj, k_verts: list[int]) -> int:
    """Exact M(K) by enumeration over subsets of V - K."""
    k_mask = 0
    for v in k_verts:
        k_mask |= 1 << v
    outside = [v for v in range(n) if not (k_mask >> v & 1)]
    no = len(outside)
    best = 0
    for sub in range(1, 1 << no):
        sz = sub.bit_count()
        if sz <= best:
            continue
        mask = 0
        t = sub
        while t:
            b = t & -t
            t ^= b
            mask |= 1 << outside[b.bit_length() - 1]
        # forest check
        if edges_in_mask(adj, mask) != sz - len(components_of_mask(adj, mask)):
            continue
        comps = components_of_mask(adj, mask)
        # per-component neighborhood in K: need exactly one edge into K - z
        # count, for each component, its edge multiset into K
        comp_edges = []          # list of dict {k_vertex: multiplicity}
        ok = True
        for cm in comps:
            tallies = {}
            cc = cm
            while cc:
                b = cc & -cc
                cc ^= b
                nbr = adj[b.bit_length() - 1] & k_mask
                while nbr:
                    kb = nbr & -nbr
                    nbr ^= kb
                    kv = kb.bit_length() - 1
                    tallies[kv] = tallies.get(kv, 0) + 1
            if not tallies:
                ok = False       # component with no edge to K at all: can
                break            # never connect => not usable in this form
            comp_edges.append(tallies)
        if not ok:
            continue
        # exists z in K s.t. every component has exactly one edge into K - z
        found_z = False
        for z in k_verts:
            good = True
            for tallies in comp_edges:
                tot = sum(mult for kv, mult in tallies.items() if kv != z)
                if tot != 1:
                    good = False
                    break
            if good:
                found_z = True
                break
        if found_z:
            best = sz
    return best


def evaluate(name, G, sec_ex, sec_all, records) -> None:
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    n, adj = nx_to_bitadj(G)
    if n < 2 or not graph_connected(n, adj):
        return
    g = girth(n, adj)
    if g == 0 or n - g > EXP_CAP:
        return
    g6 = graph6(G)
    if g6 in records["seen"]:
        return
    records["seen"].add(g6)

    dist = all_pairs_dist(n, adj)
    ecc_v = eccentricities(n, dist)
    radius = min(ecc_v)
    diam = max(ecc_v)
    center_mask = 0
    for v in range(n):
        if ecc_v[v] == radius:
            center_mask |= 1 << v
    e = ecc_of_set(n, dist, center_mask)

    m_vals = [M_of_cycle(n, adj, sorted(K)) for K in shortest_cycles(G, g)]
    m_max, m_min = max(m_vals), min(m_vals)

    for sec, mv in ((sec_ex, m_max), (sec_all, m_min)):
        sl = mv - e
        sec["count"] += 1
        sec["hist"][sl] += 1
        if sec["min"] is None or sl < sec["min"]:
            sec["min"] = sl
            sec["min_wit"] = (f"{name} [{g6}] n={n} g={g} diam={diam} "
                              f"r={radius} e={e} M={mv}")
        if sl < 0 and len(sec["viol"]) < MAX_RECORDS:
            tree_sz = largest_induced_tree(n, adj)[0] if n <= 16 else None
            sec["viol"].append({
                "family": name, "graph6": g6, "n": n, "girth": g,
                "diam": diam, "radius": radius, "e": e, "M": mv,
                "tree": tree_sz, "slack": sl,
            })
        if sl == 0 and len(sec["tight"]) < MAX_RECORDS:
            sec["tight"].append(f"{name} [{g6}] n={n} g={g} e={e} M={mv}")


def main() -> None:
    rng = random.Random(SEED)
    sec_ex = {"count": 0, "hist": Counter(), "min": None, "min_wit": None,
              "viol": [], "tight": []}
    sec_all = {"count": 0, "hist": Counter(), "min": None, "min_wit": None,
               "viol": [], "tight": []}
    records = {"seen": set()}

    corpora = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 2 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for i in range(1500):
        corpora.append(cycle_random_legs(rng))
    for i in range(1000):
        corpora.append(cycle_random_trees(rng))
    for i in range(800):
        corpora.append(chorded_cycle(rng))
    for i in range(600):
        corpora.append(gen_theta(rng))
    got, tries = 0, 0
    while got < 800 and tries < 15000:
        tries += 1
        r = forced_girth_random(rng, gmin=5)
        if r is not None:
            corpora.append(r)
            got += 1

    for name, G in corpora:
        evaluate(name, G, sec_ex, sec_all, records)

    result = {"test": "WOWII144_lemmaE", "seed": SEED,
              "graphs_evaluated": len(records["seen"])}
    for tag, sec in (("E_exists", sec_ex), ("E_forall", sec_all)):
        result[tag] = {
            "count": sec["count"],
            "hist": {str(a): b for a, b in sorted(sec["hist"].items())},
            "min_slack": sec["min"], "min_witness": sec["min_wit"],
            "violations": sec["viol"], "violation_count": len(sec["viol"]),
            "tight_examples": sec["tight"][:MAX_RECORDS],
        }
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    print("sha256:", hashlib.sha256(encoded).hexdigest().upper())
    for tag in ("E_exists", "E_forall"):
        r = result[tag]
        print(f"{tag}: count={r['count']} min={r['min_slack']} "
              f"viol={r['violation_count']}")
        print("   wit:", r["min_witness"])


if __name__ == "__main__":
    main()
