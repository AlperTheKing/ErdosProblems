#!/usr/bin/env python3
"""Independent exact verifier for the registered ordinary MW counterexample."""
from __future__ import annotations

import json
import networkx as nx

GRAPH6 = "XhCGGC@?G?_@?@??o?G??A?C??G??G??C??@???G?G?_??@_???"
K = tuple(range(15))
X, M, Z = 24, 0, 14


def cycle_distance(a: int, b: int, g: int) -> int:
    d = abs(a - b)
    return min(d, g - d)


def main() -> None:
    G = nx.from_graph6_bytes(GRAPH6.encode("ascii"))
    assert len(G) == 25 and nx.is_connected(G)
    assert nx.girth(G) == 15
    assert all(G.has_edge(K[i], K[(i + 1) % len(K)]) for i in range(len(K)))

    dist = dict(nx.all_pairs_shortest_path_length(G))
    eccentricity = {v: max(dist[v].values()) for v in G}
    radius, diameter = min(eccentricity.values()), max(eccentricity.values())
    center = {v for v in G if eccentricity[v] == radius}
    center_distance = {v: min(dist[v][c] for c in center) for v in G}
    eta = max(center_distance.values())
    realizers = {v for v in G if center_distance[v] == eta}
    assert (radius, diameter, center, eta, realizers) == (7, 9, {6, 9}, 7, {X})

    kset = set(K)
    height = min(dist[X][v] for v in K)
    anchors = {v for v in K if dist[X][v] == height}
    assert (height, anchors) == (1, {M}) and height < eta
    assert diameter <= eta + len(K) // 2 - 1 and eta <= radius

    delta = eta - height
    window = {v for v in K if cycle_distance(M, v, len(K)) <= delta - 1}
    assert delta == 6
    assert window == {0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14}

    outside = set(G) - kset
    components = [set(c) for c in nx.connected_components(G.subgraph(outside))]

    def attachments(component: set[int]) -> set[int]:
        return {v for v in K if any(G.has_edge(v, y) for y in component)}

    def cover(component: set[int]) -> set[int]:
        return {s for s in window if max(dist[s][y] for y in component) >= radius + 1}

    assert G.has_edge(M, Z)
    assert all(not (attachments(c) == {Z} and cover(c)) for c in components)
    H = next(c for c in components if 15 in c)
    assert H == set(range(15, 24)) and X not in H
    assert attachments(H) == {4, 11} and len(attachments(H) - {Z}) == 2
    EH = cover(H)
    assert EH == window

    rho = -1
    J = G.subgraph(H).copy()
    J.add_node(rho)
    for y in H:
        if set(G.neighbors(y)) & (kset - {Z}):
            J.add_edge(rho, y)
    assert set(J.neighbors(rho)) == {16, 22}
    jdist = dict(nx.all_pairs_shortest_path_length(J))
    p = {y: jdist[rho][y] for y in H}
    rooted_triameter = max(p[u] + p[v] + jdist[u][v] for u in H for v in H)
    assert rooted_triameter == 10

    best_rooted_tree = 0
    hlist = sorted(H)
    for mask in range(1 << len(hlist)):
        vertices = {rho} | {hlist[i] for i in range(len(hlist)) if mask & (1 << i)}
        if nx.is_tree(J.subgraph(vertices)):
            best_rooted_tree = max(best_rooted_tree, len(vertices))
    mu = best_rooted_tree - 1
    assert mu == 8

    lambda_ = 2 * radius + 1 - len(K)
    q = len(EH)
    assert (q, lambda_, rooted_triameter) == (11, 0, 10)
    assert q + lambda_ > rooted_triameter
    assert q + lambda_ <= 2 * mu

    print(json.dumps({
        "graph6": GRAPH6,
        "n": len(G), "g": len(K), "r": radius, "D": diameter,
        "center": sorted(center), "eta": eta, "x": X, "h": height,
        "m": M, "delta": delta, "W": sorted(window), "z": Z,
        "H": sorted(H), "attachments": sorted(attachments(H)),
        "q_H": q, "lambda": lambda_, "P_z_H": rooted_triameter,
        "mu_z_H": mu, "MW_slack": rooted_triameter - q - lambda_,
    }, indent=2))


if __name__ == "__main__":
    main()
