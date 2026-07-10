"""Exact reconstruction of GPT-Pro's 28/27 active ell=5 circuit."""

from __future__ import annotations

import json
from collections import Counter, deque
from fractions import Fraction


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        assert u != v and v not in adj[u]
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs_counts(adj: list[set[int]], source: int) -> tuple[list[int], list[int]]:
    dist = [-1] * len(adj)
    count = [0] * len(adj)
    dist[source] = 0
    count[source] = 1
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                count[v] = count[u]
                queue.append(v)
            elif dist[v] == dist[u] + 1:
                count[v] += count[u]
    return dist, count


def full_support(
        blue: set[tuple[int, int]], adj: list[set[int]],
        atom: tuple[int, int]) -> tuple[int, int, set[tuple[int, int]], set[int]]:
    a, b = atom
    da, wa = bfs_counts(adj, a)
    db, wb = bfs_counts(adj, b)
    distance = da[b]
    support = {
        e for e in blue
        if da[e[0]] + 1 + db[e[1]] == distance
        or da[e[1]] + 1 + db[e[0]] == distance
    }
    vertices = {
        v for v in range(len(adj))
        if da[v] >= 0 and db[v] >= 0 and da[v] + db[v] == distance
    }
    assert wa[b] == wb[a]
    return distance, wa[b], support, vertices


def has_matching_after_delete(
        masks: list[int], deleted: int, edge_count: int) -> bool:
    owner = [-1] * edge_count

    def augment(atom: int, seen: list[bool]) -> bool:
        mask = masks[atom]
        while mask:
            bit = mask & -mask
            support_index = bit.bit_length() - 1
            mask ^= bit
            if seen[support_index]:
                continue
            seen[support_index] = True
            if owner[support_index] < 0 or augment(owner[support_index], seen):
                owner[support_index] = atom
                return True
        return False

    return all(
        atom == deleted or augment(atom, [False] * edge_count)
        for atom in range(len(masks))
    )


def verify_triangle_free(n: int, graph_edges: set[tuple[int, int]]) -> None:
    adj = adjacency(n, graph_edges)
    assert all(not (adj[u] & adj[v]) for u, v in graph_edges)


def local_gadget_maxcut() -> int:
    # One bad chord plus a six-edge path on seven vertices.
    local_edges = {edge(0, 6)} | {edge(i, i + 1) for i in range(6)}
    return max(
        sum(((mask >> u) & 1) != ((mask >> v) & 1)
            for u, v in local_edges)
        for mask in range(1 << 7)
    )


def main() -> None:
    w = 26
    support = {edge(i, (i + 1) % 26) for i in range(26)} | {edge(w, 0)}
    cyclic_atoms = {edge(i, (i + 4) % 26) for i in range(26)}
    atoms = cyclic_atoms | {edge(w, 3), edge(w, 23)}
    active_vertices = [(9 * k) % 26 for k in range(13)]
    active_edges = {
        edge(active_vertices[i], active_vertices[i + 1])
        for i in range(len(active_vertices) - 1)
    }
    blue_core = support | active_edges

    assert len(support) == 27
    assert len(atoms) == 28
    assert len(active_edges) == 12
    assert len(blue_core) == 39
    assert active_vertices[0] == 0 and active_vertices[-1] == 4
    assert not (active_edges & support)
    verify_triangle_free(27, blue_core | atoms)

    core_adj = adjacency(27, blue_core)
    support_order = sorted(support)
    support_index = {e: i for i, e in enumerate(support_order)}
    masks = []
    vertex_union = set()
    for atom in sorted(atoms):
        distance, path_count, atom_support, vertices = full_support(
            blue_core, core_adj, atom)
        assert distance == 4 and path_count == 1
        assert atom_support <= support
        vertex_union.update(vertices)
        mask = sum(1 << support_index[e] for e in atom_support)
        assert mask.bit_count() == 4
        masks.append(mask)
    assert vertex_union == set(range(27))
    assert set().union(*(
        {support_order[i] for i in range(len(support_order)) if (mask >> i) & 1}
        for mask in masks
    )) == support
    assert all(
        has_matching_after_delete(masks, deleted, len(support))
        for deleted in range(len(atoms))
    )

    # Add one private length-six blue path for every atom.
    side = [i % 2 for i in range(26)] + [1]
    blue = set(blue_core)
    private_paths = []
    next_vertex = 27
    for a, b in sorted(atoms):
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        for step, vertex in enumerate(internal, 1):
            assert vertex == len(side)
            side.append(side[a] ^ (step % 2))
        path = [a] + internal + [b]
        assert side[b] == side[a]
        for u, v in zip(path, path[1:]):
            assert side[u] != side[v]
            blue.add(edge(u, v))
        private_paths.append(path)

    n = next_vertex
    graph_edges = blue | atoms
    assert n == 167
    assert len(blue) == 207
    assert len(graph_edges) == 235
    assert blue.isdisjoint(atoms)
    verify_triangle_free(n, graph_edges)
    assert all(side[u] != side[v] for u, v in blue)
    assert all(side[u] == side[v] for u, v in atoms)
    assert local_gadget_maxcut() == 6
    displayed_cut = len(blue)
    maxcut_upper_bound = len(blue_core) + 6 * len(atoms)
    assert displayed_cut == maxcut_upper_bound == 207

    full_adj = adjacency(n, blue)
    loads = [Fraction(0) for _ in range(n)]
    ell_hist = Counter()
    for atom in sorted(atoms):
        distance, path_count, atom_support, vertices = full_support(
            blue, full_adj, atom)
        assert distance == 4 and path_count == 1
        assert atom_support <= support
        ell_hist[distance + 1] += 1
        for v in vertices:
            loads[v] += distance + 1
    assert ell_hist == Counter({5: 28})
    assert max(loads) == 35

    bad_count = len(graph_edges) - displayed_cut
    gamma_lower_bound = 25 * bad_count
    displayed_gamma = sum(ell * ell * count for ell, count in ell_hist.items())
    assert bad_count == 28
    assert displayed_gamma == gamma_lower_bound == 700

    print(json.dumps({
        "core": {
            "vertices": 27,
            "atoms": len(atoms),
            "supportEdges": len(support),
            "activePathEdges": len(active_edges),
            "exactMinimalCircuit": True,
        },
        "lock": {
            "N": n,
            "edges": len(graph_edges),
            "blueEdges": len(blue),
            "badEdges": bad_count,
            "maxCut": displayed_cut,
            "gamma": displayed_gamma,
            "triangleFree": True,
        },
        "loads": {"max": str(max(loads)), "minSlack": str(n - max(loads))},
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
