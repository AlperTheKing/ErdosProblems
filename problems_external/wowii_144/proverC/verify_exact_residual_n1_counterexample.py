#!/usr/bin/env python3
"""Standalone exact verifier for the W144 Candidate N1 counterexample.

This uses only the Python standard library.  It reconstructs the graph from
three explicit paths, enumerates every simple cycle, recomputes the full
distance matrix, and exactly enumerates the top outside-subset layers needed
to determine every M_z(K).
"""

from __future__ import annotations

import itertools
import json
from collections import deque
from pathlib import Path


N = 36
K = tuple(range(14))
EXPECTED_G6 = (
    "chCGGC@?G?_@?@_?_?O?O??C??G??G??C??@???G???__?@????????_??_G???O"
    "????C????G????G????C????@?????G?????_???O@"
)
OUT = Path(__file__).with_name(
    "exact_residual_n1_counterexample_certificate.json"
)


def path_edges(path: list[int]) -> list[tuple[int, int]]:
    return list(zip(path, path[1:]))


# C_14, one leaf at 12, a 10-edge (10,5)-ear, and a 13-edge
# (17,22)-ear whose endpoints are internal vertices of the first ear.
EDGES = (
    path_edges(list(range(14)) + [0])
    + [(12, 14)]
    + path_edges([10, 15, 16, 17, 18, 19, 20, 21, 22, 23, 5])
    + path_edges([17, 26, 25, 24, 35, 34, 33, 32, 31, 30, 29, 28, 27, 22])
)
EDGES = sorted({tuple(sorted(e)) for e in EDGES})


def adjacency() -> list[set[int]]:
    adj = [set() for _ in range(N)]
    for u, v in EDGES:
        assert u != v
        adj[u].add(v)
        adj[v].add(u)
    return adj


ADJ = adjacency()


def graph6() -> str:
    assert N <= 62
    bits = []
    for j in range(1, N):
        for i in range(j):
            bits.append(1 if j in ADJ[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    body = []
    for i in range(0, len(bits), 6):
        q = 0
        for b in bits[i:i + 6]:
            q = (q << 1) | b
        body.append(chr(q + 63))
    return chr(N + 63) + "".join(body)


def all_pairs_dist() -> list[list[int]]:
    result = []
    for source in range(N):
        row = [-1] * N
        row[source] = 0
        todo = deque([source])
        while todo:
            v = todo.popleft()
            for w in ADJ[v]:
                if row[w] < 0:
                    row[w] = row[v] + 1
                    todo.append(w)
        assert min(row) >= 0
        result.append(row)
    return result


def all_simple_cycles() -> list[frozenset[tuple[int, int]]]:
    """Enumerate undirected simple cycles, canonicalized by their edge sets."""
    found: set[frozenset[tuple[int, int]]] = set()
    for start in range(N):
        path = [start]
        seen = {start}

        def dfs(v: int) -> None:
            for w in ADJ[v]:
                if w == start:
                    if len(path) >= 3:
                        cyc = path_edges(path + [start])
                        found.add(frozenset(tuple(sorted(e)) for e in cyc))
                elif w > start and w not in seen:
                    seen.add(w)
                    path.append(w)
                    dfs(w)
                    path.pop()
                    seen.remove(w)

        dfs(start)
    return sorted(found, key=lambda c: (len(c), sorted(c)))


def components(vertices: set[int]) -> list[set[int]]:
    left = set(vertices)
    result = []
    while left:
        root = min(left)
        comp = {root}
        todo = [root]
        left.remove(root)
        while todo:
            v = todo.pop()
            for w in ADJ[v] & left:
                left.remove(w)
                comp.add(w)
                todo.append(w)
        result.append(comp)
    return result


def induced_edge_count(vertices: set[int]) -> int:
    return sum(len(ADJ[v] & vertices) for v in vertices) // 2


def is_forest(vertices: set[int]) -> bool:
    return induced_edge_count(vertices) == len(vertices) - len(components(vertices))


def admissible(vertices: set[int], z: int) -> bool:
    if not is_forest(vertices):
        return False
    kset = set(K)
    for comp in components(vertices):
        into_k_minus_z = sum(
            1 for v in comp for w in ADJ[v]
            if w in kset and w != z
        )
        if into_k_minus_z != 1:
            return False
    return True


def exact_mz(outside: list[int]):
    unresolved = set(K)
    best: dict[int, int] = {}
    witnesses: dict[int, list[int]] = {}
    tested_by_size: dict[int, int] = {}
    for size in range(len(outside), -1, -1):
        count = 0
        for choice in itertools.combinations(outside, size):
            count += 1
            vertices = set(choice)
            for z in sorted(unresolved):
                if admissible(vertices, z):
                    best[z] = size
                    witnesses[z] = list(choice)
            unresolved -= best.keys()
        tested_by_size[size] = count
        if not unresolved:
            break
    assert not unresolved
    return best, witnesses, tested_by_size


def main() -> None:
    assert len(EDGES) == 38
    assert graph6() == EXPECTED_G6

    cycles = all_simple_cycles()
    cycle_lengths = [len(c) for c in cycles]
    cycle_vertices = [sorted({v for edge in c for v in edge}) for c in cycles]
    assert cycle_lengths == [14, 15, 18, 19, 23, 27]
    shortest = [vs for c, vs in zip(cycles, cycle_vertices) if len(c) == 14]
    assert shortest == [list(K)]

    dist = all_pairs_dist()
    ecc = [max(row) for row in dist]
    radius = min(ecc)
    diameter = max(ecc)
    center = [v for v in range(N) if ecc[v] == radius]
    d_center = [min(dist[v][c] for c in center) for v in range(N)]
    e = max(d_center)
    realizers = [v for v in range(N) if d_center[v] == e]

    assert radius == 9
    assert diameter == 14
    assert center == [17, 18, 19, 20]
    assert e == 8
    assert realizers == [1]

    g = cycle_lengths[0]
    k = g // 2
    h = min(dist[realizers[0]][a] for a in K)
    assert k == 7 and h == 0
    assert diameter < e + k
    assert h < e - k

    outside = sorted(set(range(N)) - set(K))
    mz, forests, tested_by_size = exact_mz(outside)
    expected_mz = {z: (20 if z == 12 else 21) for z in K}
    assert mz == expected_mz
    assert tested_by_size == {22: 1, 21: 22, 20: 231}
    for z in K:
        assert len(forests[z]) == mz[z]
        assert admissible(set(forests[z]), z)

    # Direct, readable maximum witnesses used in the report.
    f_break_22 = set(outside) - {22}
    f_break_35 = set(outside) - {35}
    f_z12 = set(outside) - {14, 22}
    for z in set(K) - {5, 10, 12}:
        assert admissible(f_break_22, z)
    for z in (5, 10):
        assert admissible(f_break_35, z)
    assert admissible(f_z12, 12)

    outside_components = components(set(outside))
    assert [sorted(c) for c in outside_components] == [
        [14], list(range(15, 36))
    ]
    m = realizers[0]
    delta = e - h
    W = [a for a in K if min(abs(a - m), len(K) - abs(a - m)) <= delta - 1]
    assert delta == 8 and W == list(K)
    e_sets = []
    for comp in outside_components:
        e_h = [sig for sig in K if max(dist[sig][y] for y in comp) >= radius + 1]
        e_sets.append(e_h)
    assert e_sets == [[], list(K)]
    covsum = sum(len(set(e_h) & set(W)) for e_h in e_sets)
    assert covsum == 14
    n2 = {
        z: {
            "M_z": mz[z],
            "coverage_sum": covsum,
            "rhs_2_Mz_minus_h": 2 * (mz[z] - h),
            "slack": 2 * (mz[z] - h) - covsum,
        }
        for z in K if z != m
    }
    assert all(row["slack"] >= 0 for row in n2.values())

    certificate = {
        "claim": "W144 Candidate N1 is false",
        "graph": {
            "graph6": EXPECTED_G6,
            "n": N,
            "m": len(EDGES),
            "edges": EDGES,
            "all_simple_cycle_lengths": cycle_lengths,
            "all_simple_cycle_vertex_sets": cycle_vertices,
            "unique_shortest_cycle": list(K),
        },
        "metric": {
            "eccentricities": ecc,
            "radius": radius,
            "diameter": diameter,
            "center": center,
            "distances_to_center": d_center,
            "center_eccentricity_e": e,
            "e_realizers": realizers,
        },
        "N1": {
            "g": g,
            "k_floor_g_over_2": k,
            "D_lt_e_plus_k": diameter < e + k,
            "x": realizers[0],
            "h_dist_x_K": h,
            "required_lower_bound_e_minus_k": e - k,
            "violation": h < e - k,
            "quantifiers": "unique K and unique e-realizer, so both forall-K/exists-x and exists-K/exists-x versions fail",
        },
        "capacity": {
            "outside_vertices": outside,
            "M_z": mz,
            "M_K": max(mz.values()),
            "maximum_forest_witness_by_z": forests,
            "subset_layers_exhausted": tested_by_size,
            "readable_witnesses": {
                "z_not_5_10_12": sorted(f_break_22),
                "z_5_or_10": sorted(f_break_35),
                "z_12": sorted(f_z12),
            },
        },
        "N2_on_this_wide_window_instance": {
            "anchor_m": m,
            "h": h,
            "delta": delta,
            "W": W,
            "E_H_sets": e_sets,
            "coverage_sum": covsum,
            "by_z_excluding_m": n2,
            "result": "N2 holds; this graph falsifies N1, not N2 or C144",
        },
    }
    OUT.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "certificate": str(OUT),
        "graph6": EXPECTED_G6,
        "cycles": cycle_lengths,
        "g": g,
        "k": k,
        "radius": radius,
        "D": diameter,
        "center": center,
        "e": e,
        "realizers": realizers,
        "h": h,
        "M_z": mz,
        "M_K": max(mz.values()),
        "N2_covsum": covsum,
    }, indent=2))


if __name__ == "__main__":
    main()
