#!/usr/bin/env python3
"""WOWII 144, wave2, route B (eccentricity geometry).  Falsifier-first tests for
the candidate proof decomposition of

    C144:  tree(G) >= girth(G) - 1 + e,   e := ecc(G, center)  (FC defs).

Candidate lemmas (s := girth // 2 = floor(g/2), cyclic connected G only):

  P1  (single tail, construction):   tree >= g - 1 + max_K max_x d(x, K)
      over shortest cycles K.
  P2  (reroute, construction):       tree >= diam + ceil(g/2) - 1.
  L3  (metric key lemma):            e <= max( max_K max_x d(x,K), diam - s ).
      Variants scored:
        L3_exists : with D = max over shortest cycles K of max_x d(x,K)
        L3_forall : min over K   (i.e. claim holds for EVERY shortest cycle)
        L3_ecc_ex : e <= max(D, (max over e-realizers x* of ecc(x*)) - s)
        L3_ecc_all: e <= max(D, (min over e-realizers x* of ecc(x*)) - s)
      (P1) + (P2) + (L3_exists)  ==>  C144 for cyclic graphs; acyclic trivial.

Corpora: atlas 2..7, wowii_141 families+random (n<=14), wowii_144 adversarial
(n<=40, metric-only when n > TREE_CAP), plus new adversarial families aimed at
L3: random cycle+legs, cycle+random trees, forced-girth random graphs,
generalized thetas, chorded cycles (cycle + attached outer path), and the
"center trap" sweep (deep tail + flanking legs).

Exact integer arithmetic throughout (wowii_141 oracle machinery).
Output: route_b_results.json (+ stdout summary).
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

OUT = ROOT / "route_b_results.json"
SEED = 20260718
TREE_CAP = 16          # exhaustive induced-tree search only for n <= TREE_CAP
MAX_RECORDS = 40


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode("ascii").strip()


# ------------------------------------------------------------ new adversarial

def _tail(G: nx.Graph, at, length: int, tag: str):
    prev = at
    for i in range(length):
        G.add_edge(prev, f"{tag}{i}")
        prev = f"{tag}{i}"
    return prev


def cycle_random_legs(rng: random.Random) -> tuple[str, nx.Graph]:
    g = rng.randrange(6, 25)
    k = rng.randrange(1, 7)
    spec = []
    G = nx.cycle_graph(g)
    for j in range(k):
        pos = rng.randrange(g)
        L = rng.randrange(1, 9)
        spec.append((pos, L))
        _tail(G, pos, L, f"L{j}_")
    return f"randLegs(g={g},spec={tuple(spec)})", G


def cycle_random_trees(rng: random.Random) -> tuple[str, nx.Graph]:
    g = rng.randrange(6, 21)
    G = nx.cycle_graph(g)
    k = rng.randrange(1, 5)
    label = 0
    for j in range(k):
        pos = rng.randrange(g)
        size = rng.randrange(1, 9)
        nodes = [pos]
        for _ in range(size):
            parent = rng.choice(nodes)
            child = f"t{label}"
            label += 1
            G.add_edge(parent, child)
            nodes.append(child)
    return f"randTrees(g={g},n={G.number_of_nodes()})", G


def forced_girth_random(rng: random.Random, gmin: int) -> tuple[str, nx.Graph] | None:
    n = rng.randrange(9, 17)
    p = rng.choice([0.10, 0.15, 0.22, 0.3])
    G = nx.gnp_random_graph(n, p, seed=rng.randrange(2 ** 31))
    if not nx.is_connected(G):
        return None
    # kill short cycles by deleting one edge of each, keep connected
    for _ in range(200):
        try:
            cyc = nx.find_cycle(G)
        except nx.NetworkXNoCycle:
            return None                       # acyclic - useless here
        nn, adj = nx_to_bitadj(nx.convert_node_labels_to_integers(G))
        gg = girth(nn, adj)
        if gg == 0 or gg >= gmin:
            break
        # find an actual shortest cycle and delete one of its edges
        found = None
        for c in nx.simple_cycles(G, length_bound=gg):
            if len(c) == gg:
                found = c
                break
        if found is None:
            break
        deleted = False
        for i in range(len(found)):
            u, v = found[i], found[(i + 1) % len(found)]
            G.remove_edge(u, v)
            if nx.is_connected(G):
                deleted = True
                break
            G.add_edge(u, v)
        if not deleted:
            break
    nn, adj = nx_to_bitadj(nx.convert_node_labels_to_integers(G))
    gg = girth(nn, adj)
    if gg < gmin:
        return None
    return f"forcedGirth(n={n},p={p},g={gg})", G


def gen_theta(rng: random.Random) -> tuple[str, nx.Graph]:
    k = rng.randrange(3, 6)
    lens = sorted(rng.randrange(2, 9) for _ in range(k))
    if lens.count(lens[0]) == 0:
        pass
    G = nx.Graph()
    for j, L in enumerate(lens):
        prev = "u"
        for i in range(L - 1):
            G.add_edge(prev, f"p{j}_{i}")
            prev = f"p{j}_{i}"
        G.add_edge(prev, "v")
    return f"genTheta{tuple(lens)}", G


def chorded_cycle(rng: random.Random) -> tuple[str, nx.Graph]:
    """C_g plus an outer path (ear) between two cycle vertices, plus legs."""
    g = rng.randrange(6, 21)
    G = nx.cycle_graph(g)
    a = rng.randrange(g)
    b = (a + rng.randrange(2, g - 1)) % g
    earlen = rng.randrange(2, 10)
    prev = a
    for i in range(earlen - 1):
        G.add_edge(prev, f"e{i}")
        prev = f"e{i}"
    G.add_edge(prev, b)
    k = rng.randrange(0, 3)
    for j in range(k):
        _tail(G, rng.randrange(g), rng.randrange(1, 6), f"L{j}_")
    return f"ear(g={g},a={a},b={b},len={earlen})", G


def trap_family() -> list[tuple[str, nx.Graph]]:
    """C_g + deep tail a@0 (the would-be x*) + flanking legs near the antipode:
    engineered attempts to move the center far from x* without depth."""
    out = []
    for g in (8, 10, 12, 14, 16, 18, 20):
        h = g // 2
        for a in (1, 2, 3):
            for flank in (1, 2, 3):
                for L in (2, 3, 4):
                    G = nx.cycle_graph(g)
                    _tail(G, 0, a, "x")
                    _tail(G, h, L, "c0_")
                    _tail(G, (h - flank) % g, L, "c1_")
                    _tail(G, (h + flank) % g, L, "c2_")
                    out.append((f"trap(g={g},a={a},f={flank},L={L})", G))
                # cascade version: legs all around the far half
                G = nx.cycle_graph(g)
                _tail(G, 0, a, "x")
                for jj, pos in enumerate(range(h - h // 2, h + h // 2 + 1)):
                    _tail(G, pos % g, 3, f"c{jj}_")
                out.append((f"trapCascade(g={g},a={a},f={flank})", G))
    return out


# ------------------------------------------------------------ evaluation

def evaluate(name: str, G: nx.Graph, sections: dict, records: dict) -> None:
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    n, adj = nx_to_bitadj(G)
    if n < 2 or not graph_connected(n, adj):
        return
    g = girth(n, adj)
    if g == 0:
        return                                    # acyclic: C144 trivial
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
    s = g // 2

    # per-shortest-cycle far distances
    d_per_cycle = []
    for K in shortest_cycles(G, g):
        k_mask = 0
        for v in K:
            k_mask |= 1 << v
        d_per_cycle.append(max(dist_to_set(dist, x, k_mask) for x in range(n)))
    dmax = max(d_per_cycle)
    dmin = min(d_per_cycle)

    # e-realizers x*
    realizers = [v for v in range(n)
                 if dist_to_set(dist, v, center_mask) == e] if e > 0 else []
    ecc_real_max = max((ecc_v[v] for v in realizers), default=0)
    ecc_real_min = min((ecc_v[v] for v in realizers), default=0)

    slacks = {
        "L3_exists": max(dmax, diam - s) - e,
        "L3_forall": max(dmin, diam - s) - e,
        "L3_ecc_ex": max(dmax, ecc_real_max - s) - e,
        "L3_ecc_all": max(dmax, ecc_real_min - s) - e,
    }

    tree_sz = None
    if n <= TREE_CAP:
        tree_sz, _ = largest_induced_tree(n, adj)
        slacks["P1"] = tree_sz - (g - 1 + dmax)
        slacks["P2"] = tree_sz - (diam + (g + 1) // 2 - 1)
        slacks["C144"] = tree_sz - (g - 1 + e)

    for key, sl in slacks.items():
        sec = sections[key]
        sec["count"] += 1
        sec["hist"][sl] += 1
        if sec["min"] is None or sl < sec["min"]:
            sec["min"] = sl
            sec["min_wit"] = f"{name} [{g6}] n={n} g={g} diam={diam} r={radius} e={e} D={dmax}"
        if sl < 0 and len(sec["viol"]) < MAX_RECORDS:
            sec["viol"].append({
                "family": name, "graph6": g6, "n": n, "girth": g,
                "diam": diam, "radius": radius, "e": e,
                "dmax": dmax, "dmin": dmin, "tree": tree_sz,
                "ecc_realizer_max": ecc_real_max,
                "ecc_realizer_min": ecc_real_min, "slack": sl,
            })
        if sl == 0 and len(sec["tight"]) < MAX_RECORDS:
            sec["tight"].append(f"{name} [{g6}] n={n} g={g} diam={diam} e={e} D={dmax}")


def new_sec():
    return {"count": 0, "hist": Counter(), "min": None, "min_wit": None,
            "viol": [], "tight": []}


def main() -> None:
    rng = random.Random(SEED)
    keys = ["L3_exists", "L3_forall", "L3_ecc_ex", "L3_ecc_all",
            "P1", "P2", "C144"]
    sections = {k: new_sec() for k in keys}
    records = {"seen": set()}

    corpora: list[tuple[str, nx.Graph]] = []

    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 2 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for i in range(3000):
        corpora.append(cycle_random_legs(rng))
    for i in range(1500):
        corpora.append(cycle_random_trees(rng))
    for i in range(1200):
        corpora.append(chorded_cycle(rng))
    for i in range(800):
        corpora.append(gen_theta(rng))
    got = 0
    tries = 0
    while got < 1200 and tries < 20000:
        tries += 1
        r = forced_girth_random(rng, gmin=5)
        if r is not None:
            corpora.append(r)
            got += 1

    for name, G in corpora:
        evaluate(name, G, sections, records)

    result = {"test": "WOWII144_routeB_P1_P2_L3", "seed": SEED,
              "graphs_evaluated": len(records["seen"])}
    for k in keys:
        sec = sections[k]
        result[k] = {
            "count": sec["count"],
            "hist": {str(a): b for a, b in sorted(sec["hist"].items())},
            "min_slack": sec["min"], "min_witness": sec["min_wit"],
            "violations": sec["viol"], "violation_count": len(sec["viol"]),
            "tight_examples": sec["tight"],
        }
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    print("sha256:", hashlib.sha256(encoded).hexdigest().upper())
    for k in keys:
        sec = sections[k]
        print(f"{k:10s} count={sec['count']:6d} min={sec['min']} "
              f"viol={len(sec['viol'])} wit={sec['min_wit']}")


if __name__ == "__main__":
    main()
