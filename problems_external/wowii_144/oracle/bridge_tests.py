#!/usr/bin/env python3
"""Bridge-claim tests for WOWII Conjecture 144 (FC GraphConjecture144.lean:
girth - 1 + ecc(G, center) <= tree(G), center = min-eccentricity vertices,
ecc(G,S) = max_{v not in S} min_{s in S} dist(v,s), 0 if S = univ).

Q1  For every connected CYCLIC graph, does there EXIST a shortest cycle K
    (|K| = girth, necessarily chordless) and a vertex x with
    d(x, V(K)) >= ecc(G, center)?
    Checked as:  max_K max_x d(x, V(K))  >=  ecc(G, center).
    All shortest cycles are enumerated with nx.simple_cycles(length_bound=girth)
    (every yielded cycle then has length exactly girth); cross-validated against
    the edge-deletion girth from invariants.py.

Q2  Is eccent(v) >= radius + d(v, center) for EVERY vertex v of every
    connected graph?  (d(v, center) = min over center vertices; 0 on center.)

Q4  (atlas only)  For diametral geodesics P (shortest u-v paths with
    dist(u,v) = diam) and every x:  tree(G) >= |V(P)| + d(x, V(P))?
    Both quantifier readings are scored:
      forall-P : tree >= (diam+1) + max_P max_x d(x,P)
      exists-P : tree >= (diam+1) + min_P max_x d(x,P)

Test corpora:
  * atlas: all connected graphs on 2..7 vertices (networkx graph atlas)
  * families_random: the wowii_141 structured families + seeded random graphs
    (reused verbatim from ../../wowii_141/oracle/sweep_families.py, n <= 14)
  * adversarial: graphs designed so the center is far from every shortest
    cycle -- spiders with a cycle hung at depth d, two cycles joined by long
    paths through a legged central hub, cycles with asymmetric deep legs,
    cycle + balanced-binary-tree hybrids (n up to ~40)

Everything is exact integer arithmetic (reuses the bitmask BFS machinery from
the wowii_141 oracle).  Output: bridge_results.json.
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
sys.path.insert(0, str(W141))

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

OUT = ROOT / "bridge_results.json"
SEED = 20260718  # same seed as the wowii_141 random sweep (reproducible)
MAX_VIOLATION_RECORDS = 50


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode("ascii").strip()


def base_invariants(G: nx.Graph):
    """G must have nodes 0..n-1 (so bit index == node label)."""
    n, adj = nx_to_bitadj(G)
    assert graph_connected(n, adj)
    dist = all_pairs_dist(n, adj)
    ecc_v = eccentricities(n, dist)
    radius = min(ecc_v)
    diam = max(ecc_v)
    center_mask = 0
    for v in range(n):
        if ecc_v[v] == radius:
            center_mask |= 1 << v
    ecc_center = ecc_of_set(n, dist, center_mask)
    g = girth(n, adj)
    return n, adj, dist, ecc_v, radius, diam, center_mask, ecc_center, g


# ---------------------------------------------------------------- Q1

def shortest_cycles(G: nx.Graph, g: int) -> list[frozenset]:
    """All cycles of length == girth, as vertex sets (girth cycles are
    chordless, so a vertex set determines the cycle)."""
    assert g >= 3
    found = set()
    shortest_seen = None
    for c in nx.simple_cycles(G, length_bound=g):
        if shortest_seen is None or len(c) < shortest_seen:
            shortest_seen = len(c)
        if len(c) == g:
            found.add(frozenset(c))
    # cross-validate the two girth computations
    assert found, f"no cycle of length girth={g} found by simple_cycles"
    assert shortest_seen == g, f"simple_cycles found length {shortest_seen} < girth {g}"
    return sorted(found, key=sorted)


def q1_eval(G: nx.Graph, n: int, dist, g: int, ecc_center: int):
    """Return (best, witness_cycle, witness_x): best = max_K max_x d(x,K)."""
    best = -1
    wit_cycle = None
    wit_x = None
    for K in shortest_cycles(G, g):
        k_mask = 0
        for v in K:
            k_mask |= 1 << v
        for x in range(n):
            d = dist_to_set(dist, x, k_mask)
            if d > best:
                best = d
                wit_cycle = sorted(K)
                wit_x = x
    return best, wit_cycle, wit_x


# ---------------------------------------------------------------- Q2

def q2_eval(n: int, dist, ecc_v, radius: int, center_mask: int):
    """Return (min_slack, witness_v): slack_v = eccent(v) - radius - d(v,C)."""
    worst = None
    wit = None
    for v in range(n):
        s = ecc_v[v] - radius - dist_to_set(dist, v, center_mask)
        if worst is None or s < worst:
            worst = s
            wit = v
    return worst, wit


# ---------------------------------------------------------------- Q4

def q4_eval(G: nx.Graph, n: int, adj, dist, diam: int):
    """Return (tree, maxd_forall, maxd_exists): max/min over diametral
    geodesics P of max_x d(x, V(P))."""
    tree_sz, _ = largest_induced_tree(n, adj)
    maxd_all = []
    for u in range(n):
        for v in range(u + 1, n):
            if dist[u][v] == diam:
                for path in nx.all_shortest_paths(G, u, v):
                    p_mask = 0
                    for w in path:
                        p_mask |= 1 << w
                    mx = max(dist_to_set(dist, x, p_mask) for x in range(n))
                    maxd_all.append(mx)
    assert maxd_all
    return tree_sz, max(maxd_all), min(maxd_all)


# ---------------------------------------------------------------- adversarial

def _path_from(G: nx.Graph, start, length: int, tag: str):
    prev = start
    for i in range(length):
        G.add_edge(prev, f"{tag}{i}")
        prev = f"{tag}{i}"
    return prev


def _attach_cycle(G: nx.Graph, root, g: int, tag: str):
    cyc = [root] + [f"{tag}{i}" for i in range(g - 1)]
    for i in range(g):
        G.add_edge(cyc[i], cyc[(i + 1) % g])


def spider_cycle(legs: tuple[int, ...], g: int, d: int) -> nx.Graph:
    """Spider hub with legs of the given lengths; a C_g attached to the hub
    via a path of d edges (d = 0: hub lies on the cycle)."""
    G = nx.Graph()
    G.add_node("h")
    for j, L in enumerate(legs):
        _path_from(G, "h", L, f"L{j}_")
    root = _path_from(G, "h", d, "p")
    _attach_cycle(G, root, g, "c")
    return G


def two_cycles_tree(g1: int, g2: int, a: int, b: int,
                    legs: tuple[int, ...]) -> nx.Graph:
    """C_g1 --path(a)-- hub --path(b)-- C_g2, extra legs at the hub."""
    G = nx.Graph()
    G.add_node("h")
    r1 = _path_from(G, "h", a, "a")
    _attach_cycle(G, r1, g1, "c")
    r2 = _path_from(G, "h", b, "b")
    _attach_cycle(G, r2, g2, "d")
    for j, L in enumerate(legs):
        _path_from(G, "h", L, f"L{j}_")
    return G


def cycle_multi_legs(g: int, spec: tuple[tuple[int, int], ...]) -> nx.Graph:
    """C_g with a leg (path) of given length at each given cycle position."""
    G = nx.cycle_graph(g)
    for j, (pos, L) in enumerate(spec):
        _path_from(G, pos % g, L, f"L{j}_")
    return G


def cycle_binary_tree(g: int, depth: int, d: int) -> nx.Graph:
    """C_g joined by a path of d edges to the root of a balanced binary tree."""
    G = nx.cycle_graph(g)
    T = nx.relabel_nodes(nx.balanced_tree(2, depth),
                         {v: f"t{v}" for v in nx.balanced_tree(2, depth)})
    G.update(T)
    root = _path_from(G, 0, d, "p")
    if root == 0:
        G.add_edge(0, "t0")
    else:
        G.add_edge(root, "t0")
    return G


def adversarial_graphs() -> list[tuple[str, nx.Graph]]:
    out: list[tuple[str, nx.Graph]] = []
    # A1: balanced spiders with a cycle hung at depth d
    for g in (3, 4, 5, 6, 8):
        for R in (3, 5, 8):
            for m in (2, 3, 5):
                for d in (0, 1, 2, 3, 5, 8):
                    if m * R + d + g <= 40:
                        out.append((f"spiderCycle(g={g},R={R},m={m},d={d})",
                                    spider_cycle((R,) * m, g, d)))
    # A1b: unbalanced spider legs (moves the center into a leg)
    for g in (3, 5):
        for legs in ((8, 7, 2), (10, 4, 4), (6, 6, 6, 1), (9, 1, 1, 1),
                     (12, 3), (7, 7, 7)):
            for d in (0, 2, 4, 7):
                out.append((f"spiderCycleU(g={g},legs={legs},d={d})",
                            spider_cycle(legs, g, d)))
    # A2: two cycles joined by long paths through a legged central hub
    for g1 in (3, 4, 5, 6):
        for g2 in (g1, g1 + 1, g1 + 3):
            for a in (1, 2, 4, 6):
                for b in (a, a + 2, a + 4):
                    for legs in ((), (3,), (a + 1,), (2, 2)):
                        if g1 + g2 + a + b + sum(legs) + 1 <= 40:
                            out.append(
                                (f"twoCycles(g1={g1},g2={g2},a={a},b={b},legs={legs})",
                                 two_cycles_tree(g1, g2, a, b, legs)))
    # A3: cycles with asymmetric deep legs at several positions
    for g in (6, 8, 10, 12):
        for spec in (((0, 1), (g // 2, 6)), ((0, 2), (g // 2, 5)),
                     ((0, 3), (g // 2, 8)), ((0, 6), (g // 2, 6)),
                     ((0, 1), (1, 7)), ((0, 4), (1, 4), (g // 2, 9)),
                     ((0, 10),), ((0, 5), (g // 3, 5), (2 * g // 3, 5))):
            out.append((f"cycleLegs(g={g},spec={spec})",
                        cycle_multi_legs(g, spec)))
    # A4: cycle + balanced binary tree at depth d
    for g in (3, 4, 5, 6):
        for depth in (2, 3, 4):
            for d in (0, 2, 4):
                if g + d + 2 ** (depth + 1) - 1 <= 40:
                    out.append((f"cycleBTree(g={g},depth={depth},d={d})",
                                cycle_binary_tree(g, depth, d)))
    return out


# ---------------------------------------------------------------- sweeps

def new_section():
    return {
        "graphs": 0, "cyclic": 0,
        "q1_slack_hist": Counter(), "q1_min_slack": None, "q1_min_witness": None,
        "q1_violations": [],
        "q2_slack_hist": Counter(), "q2_min_slack": None, "q2_min_witness": None,
        "q2_violations": [],
    }


def run_q1_q2(sec: dict, name: str, G: nx.Graph) -> None:
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    n, adj, dist, ecc_v, radius, diam, center_mask, ecc_center, g = \
        base_invariants(G)
    g6 = graph6(G)
    sec["graphs"] += 1

    # Q2 on every connected graph
    s2, v2 = q2_eval(n, dist, ecc_v, radius, center_mask)
    sec["q2_slack_hist"][s2] += 1
    if sec["q2_min_slack"] is None or s2 < sec["q2_min_slack"]:
        sec["q2_min_slack"] = s2
        sec["q2_min_witness"] = f"{name} [{g6}] v={v2}"
    if s2 < 0 and len(sec["q2_violations"]) < MAX_VIOLATION_RECORDS:
        sec["q2_violations"].append({
            "family": name, "graph6": g6, "n": n,
            "vertex": v2, "eccent_v": ecc_v[v2], "radius": radius,
            "dist_v_center": dist_to_set(dist, v2, center_mask),
            "center": [u for u in range(n) if center_mask >> u & 1],
            "slack": s2,
        })

    # Q1 on cyclic graphs
    if g > 0:
        sec["cyclic"] += 1
        best, wit_cycle, wit_x = q1_eval(G, n, dist, g, ecc_center)
        s1 = best - ecc_center
        sec["q1_slack_hist"][s1] += 1
        if sec["q1_min_slack"] is None or s1 < sec["q1_min_slack"]:
            sec["q1_min_slack"] = s1
            sec["q1_min_witness"] = (f"{name} [{g6}] girth={g} "
                                     f"ecc_center={ecc_center} best_far={best}")
        if s1 < 0 and len(sec["q1_violations"]) < MAX_VIOLATION_RECORDS:
            sec["q1_violations"].append({
                "family": name, "graph6": g6, "n": n, "girth": g,
                "ecc_center": ecc_center, "max_K_max_x_dist": best,
                "best_cycle": wit_cycle, "best_x": wit_x,
                "center": [u for u in range(n) if center_mask >> u & 1],
                "slack": s1,
            })


def finalize(sec: dict) -> dict:
    out = dict(sec)
    out["q1_slack_hist"] = {str(k): v for k, v in
                            sorted(sec["q1_slack_hist"].items())}
    out["q2_slack_hist"] = {str(k): v for k, v in
                            sorted(sec["q2_slack_hist"].items())}
    out["q1_violation_count"] = len(sec["q1_violations"])
    out["q2_violation_count"] = len(sec["q2_violations"])
    return out


def main() -> None:
    result: dict = {"test": "WOWII_144_bridge_claims_Q1_Q2_Q4", "seed": SEED}

    # ---------------- atlas (with Q4)
    atlas_sec = new_section()
    q4 = {"graphs": 0,
          "forall_slack_hist": Counter(), "forall_min": None, "forall_wit": None,
          "exists_slack_hist": Counter(), "exists_min": None, "exists_wit": None,
          "forall_violations": [], "exists_violations": []}
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() < 2 or not nx.is_connected(graph):
            continue
        G = nx.convert_node_labels_to_integers(graph, ordering="default")
        run_q1_q2(atlas_sec, "atlas", G)

        n, adj, dist, ecc_v, radius, diam, center_mask, ecc_center, g = \
            base_invariants(G)
        tree_sz, maxd_forall, maxd_exists = q4_eval(G, n, adj, dist, diam)
        q4["graphs"] += 1
        g6 = graph6(G)
        for tag, maxd in (("forall", maxd_forall), ("exists", maxd_exists)):
            slack = tree_sz - (diam + 1 + maxd)
            q4[f"{tag}_slack_hist"][slack] += 1
            if q4[f"{tag}_min"] is None or slack < q4[f"{tag}_min"]:
                q4[f"{tag}_min"] = slack
                q4[f"{tag}_wit"] = f"[{g6}] tree={tree_sz} diam={diam} maxd={maxd}"
            if slack < 0 and len(q4[f"{tag}_violations"]) < MAX_VIOLATION_RECORDS:
                q4[f"{tag}_violations"].append({
                    "graph6": g6, "n": n, "tree": tree_sz, "diam": diam,
                    "path_order": diam + 1, "max_x_dist": maxd, "slack": slack,
                })
    q4["forall_slack_hist"] = {str(k): v for k, v in
                               sorted(q4["forall_slack_hist"].items())}
    q4["exists_slack_hist"] = {str(k): v for k, v in
                               sorted(q4["exists_slack_hist"].items())}
    q4["forall_violation_count"] = len(q4["forall_violations"])
    q4["exists_violation_count"] = len(q4["exists_violations"])
    result["atlas"] = finalize(atlas_sec)
    result["q4_atlas"] = q4

    # ---------------- wowii_141 families + random (Q1/Q2)
    fam_sec = new_section()
    rng = random.Random(SEED)
    seen: set[str] = set()
    for name, G in build_family_graphs() + random_graphs(rng):
        if G.number_of_nodes() < 2 or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        run_q1_q2(fam_sec, name, G)
    result["families_random"] = finalize(fam_sec)

    # ---------------- adversarial (Q1/Q2)
    adv_sec = new_section()
    seen_adv: set[str] = set()
    for name, G in adversarial_graphs():
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        g6 = graph6(G)
        if g6 in seen_adv:
            continue
        seen_adv.add(g6)
        run_q1_q2(adv_sec, name, G)
    result["adversarial"] = finalize(adv_sec)

    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()

    summary = {
        "output_sha256": digest,
        "atlas": {k: result["atlas"][k] for k in
                  ("graphs", "cyclic", "q1_min_slack", "q1_min_witness",
                   "q1_violation_count", "q2_min_slack", "q2_min_witness",
                   "q2_violation_count", "q1_slack_hist", "q2_slack_hist")},
        "q4_atlas": {k: q4[k] for k in
                     ("graphs", "forall_min", "forall_wit",
                      "forall_violation_count", "exists_min", "exists_wit",
                      "exists_violation_count")},
        "families_random": {k: result["families_random"][k] for k in
                            ("graphs", "cyclic", "q1_min_slack",
                             "q1_min_witness", "q1_violation_count",
                             "q2_min_slack", "q2_min_witness",
                             "q2_violation_count")},
        "adversarial": {k: result["adversarial"][k] for k in
                        ("graphs", "cyclic", "q1_min_slack", "q1_min_witness",
                         "q1_violation_count", "q2_min_slack",
                         "q2_min_witness", "q2_violation_count")},
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
