"""Independently verify the GPT Pro counterexample to the active W144 surplus lemma."""

from itertools import combinations

import networkx as nx


ADJ = {
    0: [1, 2, 18], 1: [0, 3], 2: [0, 5, 14], 3: [1, 4, 26],
    4: [3, 6, 11, 17, 19, 28], 5: [2, 27], 6: [4, 7, 8, 10],
    7: [6, 9], 8: [6, 21, 30], 9: [7, 12, 25], 10: [6, 24],
    11: [4], 12: [9, 13], 13: [12, 15, 16, 20, 31], 14: [2],
    15: [13, 23], 16: [13, 22], 17: [4], 18: [0, 20], 19: [4],
    20: [13, 18], 21: [8, 22], 22: [16, 21], 23: [15], 24: [10],
    25: [9], 26: [3], 27: [5], 28: [4, 29], 29: [28], 30: [8],
    31: [13],
}
K = [6, 8, 21, 22, 16, 13, 12, 9, 7]


def main() -> None:
    graph = nx.Graph()
    for u, neighbors in ADJ.items():
        for v in neighbors:
            graph.add_edge(u, v)
    assert set(graph) == set(range(32))
    assert all(set(ADJ[u]) == set(graph[u]) for u in graph)

    cycles = nx.minimum_cycle_basis(graph)
    girth = min(map(len, cycles))
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    eccentricity = {u: max(distances[u].values()) for u in graph}
    radius = min(eccentricity.values())
    diameter = max(eccentricity.values())
    center = {u for u, value in eccentricity.items() if value == radius}
    center_distance = {u: min(distances[u][c] for c in center) for u in graph}
    e = max(center_distance.values())
    realizers = {u for u, value in center_distance.items() if value == e}

    kset = set(K)
    assert len(K) == girth
    assert all(graph.has_edge(K[i], K[(i + 1) % len(K)]) for i in range(len(K)))
    assert graph.subgraph(K).number_of_edges() == len(K)
    assert all(distances[u][v] == min((i - j) % len(K), (j - i) % len(K))
               for i, u in enumerate(K) for j, v in enumerate(K))

    x = 25
    h_by_realizer = {u: min(distances[u][v] for v in K) for u in realizers}
    h = h_by_realizer[x]
    anchors = {v for v in K if distances[x][v] == h}
    m = 9
    delta = e - h
    residual = e > diameter - girth // 2
    components = list(nx.connected_components(graph.subgraph(set(graph) - kset)))
    component = next(c for c in components if x in c)
    cycle_graph = graph.subgraph(K)
    cycle_distances = nx.single_source_shortest_path_length(cycle_graph, m)
    window = {v for v in K if cycle_distances[v] <= delta - 1}
    q = sum(max(distances[sigma][y] for y in component) >= radius + 1
            for sigma in window)
    correction = max(0, 2 * delta - girth)

    values = []
    for z in (7, 12):
        apex = 32
        rooted = graph.subgraph(component).copy()
        rooted.add_node(apex)
        for y in component:
            if any(v in kset - {z} for v in graph[y]):
                rooted.add_edge(apex, y)
        max_order = 0
        vertices = sorted(rooted.nodes() - {apex})
        for size in range(len(vertices) + 1):
            for subset in combinations(vertices, size):
                induced = rooted.subgraph((apex,) + subset)
                if nx.is_tree(induced):
                    max_order = max(max_order, induced.number_of_nodes())
        mu = max_order - 1
        values.append((z, mu, q + correction, 2 * (mu - h)))

    result = {
        "girth": girth, "radius": radius, "diameter": diameter,
        "center": sorted(center), "e": e, "realizers": sorted(realizers),
        "h_by_realizer": h_by_realizer, "anchors": sorted(anchors),
        "delta": delta, "residual": residual, "component": sorted(component),
        "window": sorted(window), "q": q, "correction": correction,
        "root_values": values,
    }
    print(result)
    assert (girth, radius, diameter, center, e, realizers) == (9, 6, 9, {0, 1}, 6, {25})
    assert h == 1 and anchors == {9} and delta == 5 and residual
    assert component == {25} and window == kset and q == 0 and correction == 1
    assert all(mu == 1 and lhs == 1 and rhs == 0 for _, mu, lhs, rhs in values)


if __name__ == "__main__":
    main()
