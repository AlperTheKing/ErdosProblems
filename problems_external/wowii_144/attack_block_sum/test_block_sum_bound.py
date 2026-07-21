#!/usr/bin/env python3
"""Exact falsification test for the registered W144-BLOCK 1-sum bound."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import networkx as nx


def girth(G: nx.Graph) -> int | None:
    best = None
    for root in G:
        dist = {root: 0}
        parent = {root: None}
        q = [root]
        for x in q:
            for y in G[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    parent[y] = x
                    q.append(y)
                elif parent[x] != y:
                    z = dist[x] + dist[y] + 1
                    best = z if best is None else min(best, z)
    return best


def eta(G: nx.Graph) -> tuple[int, int, list[int]]:
    D = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {x: max(D[x].values()) for x in G}
    r = min(ecc.values())
    C = [x for x in G if ecc[x] == r]
    e = max(min(D[x][c] for c in C) for x in G)
    return e, r, C


def induced_tree_capacities(G: nx.Graph, root: int) -> tuple[int, int]:
    V = list(G)
    tau = 1
    rho = 1
    for k in range(2, len(V) + 1):
        for S in itertools.combinations(V, k):
            H = G.subgraph(S)
            if nx.is_tree(H):
                tau = k
                if root in S:
                    rho = k
    return tau, rho


def canonical_partition(components: list[set[int]]):
    # Put the first component on side 1 to quotient side exchange.
    m = len(components)
    for mask in range(1 << (m - 1)):
        I = {0}
        for j in range(1, m):
            if mask & (1 << (j - 1)):
                I.add(j)
        if len(I) == m:
            continue
        A = set().union(*(components[j] for j in I))
        B = set().union(*(components[j] for j in range(m) if j not in I))
        yield A, B


def inspect_graph(G: nx.Graph):
    g = girth(G)
    if g is None or g < 5 or not nx.is_connected(G):
        return None, 0
    e, r, C = eta(G)
    target = g - 1 + e
    checked = 0
    for v in nx.articulation_points(G):
        comps = [set(Q) for Q in nx.connected_components(nx.subgraph_view(G, filter_node=lambda x, v=v: x != v))]
        for A, B in canonical_partition(comps):
            checked += 1
            G1 = G.subgraph(A | {v}).copy()
            G2 = G.subgraph(B | {v}).copy()
            tau1, rho1 = induced_tree_capacities(G1, v)
            tau2, rho2 = induced_tree_capacities(G2, v)
            bound = max(tau1, tau2, rho1 + rho2 - 1)
            local = []
            for H, tau in [(G1, tau1), (G2, tau2)]:
                gh = girth(H)
                if gh is None:
                    local.append({"cyclic": False, "order": len(H), "tau": tau})
                else:
                    eh, rh, Ch = eta(H)
                    local.append({"cyclic": True, "order": len(H), "girth": gh, "eta": eh,
                                  "radius": rh, "center": sorted(Ch), "tau": tau,
                                  "w144": tau >= gh - 1 + eh})
            if bound < target and all((not x["cyclic"]) or x["w144"] for x in local):
                tauG, rhoG = induced_tree_capacities(G, v)
                record = {
                    "graph6": nx.to_graph6_bytes(G, header=False).decode().strip(),
                    "order": len(G), "edges": sorted([sorted(x) for x in G.edges()]),
                    "cut_vertex": v, "side1_vertices": sorted(A | {v}),
                    "side2_vertices": sorted(B | {v}), "girth": g, "eta": e,
                    "radius": r, "center": sorted(C), "target": target,
                    "tau1": tau1, "rho1": rho1, "tau2": tau2, "rho2": rho2,
                    "registered_bound": bound, "actual_tau": tauG, "local": local,
                }
                return record, checked
    return None, checked


def main():
    tested_graphs = tested_decompositions = 0
    for G0 in nx.graph_atlas_g():
        if len(G0) < 3 or not nx.is_connected(G0):
            continue
        G = nx.convert_node_labels_to_integers(G0)
        g = girth(G)
        if g is None or g < 5 or not list(nx.articulation_points(G)):
            continue
        tested_graphs += 1
        record, count = inspect_graph(G)
        tested_decompositions += count
        if record:
            out = {"status": "COUNTEREXAMPLE", "tested_graphs_before": tested_graphs,
                   "tested_decompositions_before": tested_decompositions, "record": record}
            Path(__file__).with_name("block_sum_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
            print(json.dumps(out, indent=2))
            return
    out = {"status": "NO_COUNTEREXAMPLE", "tested_graphs": tested_graphs,
           "tested_decompositions": tested_decompositions, "max_order": 7}
    Path(__file__).with_name("block_sum_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
