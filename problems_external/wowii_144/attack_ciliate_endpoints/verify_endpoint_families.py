"""Exact checks for the two endpoint-ciliate obstruction families.

The script uses NetworkX only for exact unweighted distances.  Every structural
claim about the displayed induced subgraphs is checked directly from the
induced edge sets.
"""

from __future__ import annotations

import networkx as nx


def girth(G: nx.Graph) -> int:
    best = len(G) + 1
    for s in G:
        dist = {s: 0}
        parent = {s: None}
        queue = [s]
        for u in queue:
            for v in G[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    best = min(best, dist[u] + dist[v] + 1)
    return 0 if best == len(G) + 1 else best


def parameters(G: nx.Graph) -> tuple[int, int, int, int, set[int]]:
    d = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {v: max(d[v].values()) for v in G}
    radius = min(ecc.values())
    center = {v for v in G if ecc[v] == radius}
    diameter = max(ecc.values())
    center_ecc = max(min(d[v][c] for c in center) for v in G)
    return girth(G), radius, diameter, center_ecc, center


def is_induced_tree(G: nx.Graph, S: set[int]) -> bool:
    H = G.subgraph(S)
    return len(H) > 0 and nx.is_tree(H)


def leaf_odd_cycle(r: int) -> tuple[nx.Graph, set[int]]:
    G = nx.cycle_graph(2 * r + 1)
    leaf = 2 * r + 1
    G.add_edge(0, leaf)
    # Delete the attachment root: the remaining cycle vertices form P_(2r).
    H = set(range(1, 2 * r + 1))
    return G, H


def two_leg_even_cycle(m: int) -> tuple[nx.Graph, set[int], list[set[int]]]:
    cycle_n = 10 * m
    G = nx.cycle_graph(cycle_n)
    K = set(range(cycle_n))
    components: list[set[int]] = []
    nxt = cycle_n
    for root in (0, 2 * m):
        C: set[int] = set()
        last = root
        for _ in range(2 * m):
            G.add_edge(last, nxt)
            C.add(nxt)
            last = nxt
            nxt += 1
        components.append(C)
    return G, K, components


def verify() -> None:
    l_checks = 0
    for r in range(2, 31):
        G, H = leaf_odd_cycle(r)
        g, rad, diam, e, _ = parameters(G)
        assert (g, rad, diam, e) == (2 * r + 1, r, r + 1, 1)
        assert len(H) == 2 * r and is_induced_tree(G, H)
        outside = set(G) - H
        assert len(outside) == 2
        for mask in range(1, 1 << len(outside)):
            A = {v for i, v in enumerate(sorted(outside)) if mask >> i & 1}
            assert not is_induced_tree(G, H | A)
        target = g - 1 + e
        exchange = set(G) - {r}
        assert len(exchange) == target and is_induced_tree(G, exchange)
        l_checks += 1

    gm_checks = 0
    for m in range(1, 31):
        G, K, components = two_leg_even_cycle(m)
        g, rad, diam, e, _ = parameters(G)
        assert (g, rad, diam, e) == (10 * m, 5 * m, 7 * m, 3 * m)
        assert all(len(C) == 2 * m and is_induced_tree(G, C) for C in components)
        target = g - 1 + e
        assert (len(K) - 1) + max(map(len, components)) < target
        z = 5 * m  # neither attachment root
        full = (K - {z}) | components[0] | components[1]
        assert is_induced_tree(G, full)
        assert len(full) == 14 * m - 1 >= target
        # Lemma-M witness: the two outside components are a forest and each
        # sends exactly one edge into K - {z}.
        F = components[0] | components[1]
        assert nx.is_forest(G.subgraph(F))
        for C in components:
            boundary = [(u, v) for u in C for v in K - {z} if G.has_edge(u, v)]
            assert len(boundary) == 1
        assert len(F) == 4 * m >= e

        # The same graph also contains the other endpoint ciliate P_(2r):
        # break K next to root 0 and extend the resulting path by the first
        # vertex of the pendant path at 0.
        cycle_break = 10 * m - 1
        first_leg_vertex = 10 * m
        path_endpoint = (K - {cycle_break}) | {first_leg_vertex}
        assert len(path_endpoint) == 10 * m == 2 * rad
        path_graph = G.subgraph(path_endpoint)
        assert nx.is_tree(path_graph) and max(dict(path_graph.degree()).values()) <= 2
        outside_components = [
            set(C) for C in nx.connected_components(G.subgraph(set(G) - path_endpoint))
        ]
        assert sorted(map(len, outside_components)) == sorted([1, 2 * m - 1, 2 * m])
        if m >= 2:
            # Even deleting arbitrary endpoint vertices cannot compensate for
            # the cardinality deficit when only one outside component is used.
            assert len(path_endpoint) + max(map(len, outside_components)) < target
        exchanged = set(G) - {cycle_break}
        assert is_induced_tree(G, exchanged) and len(exchanged) >= target
        gm_checks += 1

    print({"L_r_instances": l_checks, "G_m_instances": gm_checks, "failures": 0})


if __name__ == "__main__":
    verify()
