#!/usr/bin/env python3
"""Exact independent gate for the WALL_ATTACK_R5 359-vertex crossing candidate.

The script verifies every graph/cut/geodesic/support claim using integers.  It
also checks active-root separation for the operational door + vertex-slack
bank.  Finally it constructs an exact door-only relaxed-cover primal: the nine
singleton core cuts, each with weight 1/2, cover every bad row exactly once,
saturate every support edge, and put load 1/2 on each restriction-exit edge.
"""

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations


L = [0, 1, 2]
C = 3
R = [4, 5, 6]
U, V = 7, 8
N = 359

relations = [
    (L[0], C),
    (L[1], C),
    (L[2], C),
    (R[0], C),
    (R[1], C),
    (R[2], C),
    (U, V),
]


def internal(rel, copy, t):
    assert 0 <= rel < 7 and 0 <= copy < 10 and 1 <= t <= 5
    return 9 + 5 * (10 * rel + copy) + (t - 1)


def edge(a, b):
    return (a, b) if a < b else (b, a)


support = {edge(x, U) for x in L} | {edge(U, C), edge(C, V)} | {
    edge(V, y) for y in R
}
bad_intended = {edge(x, y) for x in L for y in R}
lock_edges = set()
lock_paths = []
for rel, (a, b) in enumerate(relations):
    for copy in range(10):
        path = [a] + [internal(rel, copy, t) for t in range(1, 6)] + [b]
        lock_paths.append(tuple(path))
        lock_edges |= {edge(path[i], path[i + 1]) for i in range(6)}

edges = support | bad_intended | lock_edges
assert len(edges) == 437

side = [None] * N
for x in L + [C] + R:
    side[x] = 0
for x in [U, V]:
    side[x] = 1
for rel, (a, _b) in enumerate(relations):
    for copy in range(10):
        for t in range(1, 6):
            side[internal(rel, copy, t)] = side[a] ^ (t & 1)
assert all(s in (0, 1) for s in side)

adj = [set() for _ in range(N)]
for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)

triangles = []
for a, b in edges:
    for z in adj[a] & adj[b]:
        triangles.append(tuple(sorted((a, b, z))))
triangles = sorted(set(triangles))
assert not triangles

bad = {e for e in edges if side[e[0]] == side[e[1]]}
assert bad == bad_intended

# Exact global max-cut reduction.  For fixed core sides, each lock path can be
# optimized independently: an even path costs 0 iff its endpoints agree and 1
# otherwise.  Enumerating the 2^8 core assignments with L0 fixed proves the
# unique core optimum and therefore the unique full optimum.
core_vertices = list(range(9))
core_edges = support | bad_intended
core_optima = []
best_bad = None
for mask in range(1 << 8):
    core_side = {0: 0}
    for x in range(1, 9):
        core_side[x] = (mask >> (x - 1)) & 1
    core_bad = sum(core_side[a] == core_side[b] for a, b in core_edges)
    lock_bad_lb = 10 * sum(core_side[a] != core_side[b] for a, b in relations)
    total_bad_lb = core_bad + lock_bad_lb
    if best_bad is None or total_bad_lb < best_bad:
        best_bad = total_bad_lb
        core_optima = [core_side]
    elif total_bad_lb == best_bad:
        core_optima.append(core_side)
assert best_bad == 9
assert len(core_optima) == 1
assert all(core_optima[0][x] == side[x] for x in core_vertices)

blue_edges = edges - bad
blue_adj = [set() for _ in range(N)]
for a, b in blue_edges:
    blue_adj[a].add(b)
    blue_adj[b].add(a)


def bfs_dist_count(start):
    dist = [-1] * N
    count = [0] * N
    dist[start] = 0
    count[start] = 1
    q = deque([start])
    while q:
        x = q.popleft()
        for y in blue_adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                count[y] = count[x]
                q.append(y)
            elif dist[y] == dist[x] + 1:
                count[y] += count[x]
    return dist, count


all_dist = {}
row_support = {}
for x in L:
    dist, count = bfs_dist_count(x)
    all_dist[x] = dist
    for y in R:
        assert dist[y] == 4
        assert count[y] == 1
        row_support[edge(x, y)] = {edge(x, U), edge(U, C), edge(C, V), edge(V, y)}

# Blue connectivity.
assert all(d >= 0 for d in bfs_dist_count(0)[0])

support_union = set().union(*row_support.values())
assert support_union == support
assert len(support_union) == 8

support_multiplicity = Counter(e for s in row_support.values() for e in s)
assert min(support_multiplicity.values()) >= 3

# Every proper atom subset satisfies bare support Hall; only the full nine-row
# set has 9 atoms on 8 support edges.
atoms = sorted(row_support)
violating_subsets = []
for mask in range(1, 1 << len(atoms)):
    chosen = [atoms[i] for i in range(len(atoms)) if (mask >> i) & 1]
    used = set().union(*(row_support[a] for a in chosen))
    if len(chosen) > len(used):
        violating_subsets.append((tuple(chosen), len(used)))
assert len(violating_subsets) == 1
assert len(violating_subsets[0][0]) == 9 and violating_subsets[0][1] == 8

# Exact loads from the nine unique ell=5 rows.
load = [0] * N
for x in L:
    for y in R:
        for z in (x, U, C, V, y):
            load[z] += 5
assert [load[x] for x in L] == [15, 15, 15]
assert [load[y] for y in R] == [15, 15, 15]
assert [load[z] for z in (U, C, V)] == [45, 45, 45]

# Forced crossing V0 -> W by atom L1-R0.
v0 = frozenset({L[0], U, C, V, R[0]})
w = frozenset(set(v0) | {L[1]})
cross_atom_support_vertices = frozenset({L[1], U, C, V, R[0]})
assert cross_atom_support_vertices & v0
assert not cross_atom_support_vertices <= v0
assert w == v0 | cross_atom_support_vertices
assert edge(L[1], U) in row_support[edge(L[1], R[0])]

# Restriction-exit ports: one endpoint in the 9-core restriction and one lock
# internal endpoint.  Door and inside-vertex slack are exact active sinks.
core = frozenset(range(9))
ports = []
for a, b in lock_edges:
    if (a in core) ^ (b in core):
        inside, outside = (a, b) if a in core else (b, a)
        ports.append((edge(a, b), inside, outside))
assert len(ports) == 140


def door_sink(port):
    return ("door", port[0])


def vertex_sink(port):
    return ("vertexSlack", port[1])


def sink_cap(sink):
    kind, key = sink
    if kind == "door":
        return Fraction(25)
    if kind == "vertexSlack":
        return Fraction(max(0, N - load[key]))
    raise AssertionError(sink)


def active_neighbors(port):
    return frozenset(s for s in (door_sink(port), vertex_sink(port)) if sink_cap(s) > 0)


l0_ports = [p for p in ports if p[1] == L[0]]
l1_ports = [p for p in ports if p[1] == L[1]]
assert len(l0_ports) == len(l1_ports) == 10
assert all(active_neighbors(p) for p in ports)
assert all(active_neighbors(p0).isdisjoint(active_neighbors(p1)) for p0 in l0_ports for p1 in l1_ports)

# Root components under the partial active bank are indexed by the inside core
# vertex, since only that vertex-slack sink is shared among its ten doors.
root_of_port = {p: p[1] for p in ports}
assert {root_of_port[p] for p in l0_ports} == {L[0]}
assert {root_of_port[p] for p in l1_ports} == {L[1]}
assert L[0] != L[1]

# Exact door-only full-bank primal.  Use every singleton core cut with weight
# 1/2.  A bad K3,3 edge is separated by its two endpoint singletons, every
# support edge by its two endpoint singletons, and each lock exit edge by its
# unique core-endpoint singleton.
singleton_weight = {x: Fraction(1, 2) for x in core}


def singleton_boundary(x):
    return {e for e in blue_edges if x in e}


def singleton_separated_rows(x):
    return {a for a in bad_intended if x in a}


for x in core:
    assert len(singleton_separated_rows(x)) <= len(singleton_boundary(x))

row_coverage = {
    a: sum((singleton_weight[x] for x in core if a in singleton_separated_rows(x)), Fraction(0))
    for a in bad_intended
}
assert set(row_coverage.values()) == {Fraction(1)}

support_congestion = {
    e: sum((singleton_weight[x] for x in core if e in singleton_boundary(x)), Fraction(0))
    for e in support
}
assert set(support_congestion.values()) == {Fraction(1)}

port_by_edge = {p[0]: p for p in ports}
assert len(port_by_edge) == len(ports)
external_load = {
    e: sum((singleton_weight[x] for x in core if e in singleton_boundary(x)), Fraction(0))
    for e in port_by_edge
}
assert set(external_load.values()) == {Fraction(1, 2)}

# Deterministically assign each external edge to its edge-labelled door sink.
# Distinct graph edges have distinct door sinks, so every sink receives 1/2
# against capacity 25; C5Base, prune, and vertex slack are unnecessary.
door_margin = {e: Fraction(25) - external_load[e] for e in external_load}
assert set(door_margin.values()) == {Fraction(49, 2)}
scaled_door_margin = {e: Fraction(25) - 25 * external_load[e] for e in external_load}
assert set(scaled_door_margin.values()) == {Fraction(25, 2)}

vertex_sink_load = {
    x: sum((external_load[e] for e, p in port_by_edge.items() if p[1] == x), Fraction(0))
    for x in core
}
vertex_slack_cap = {x: Fraction(N - load[x]) for x in core}
assert max(vertex_sink_load.values()) == 30
assert min(vertex_slack_cap.values()) == 314
vertex_slack_margin = {x: vertex_slack_cap[x] - vertex_sink_load[x] for x in core}
assert min(vertex_slack_margin.values()) == 284

result = {
    "n": N,
    "edges": len(edges),
    "triangle_free": True,
    "displayed_bad": len(bad),
    "global_min_bad": best_bad,
    "core_optima_mod_complement": len(core_optima),
    "blue_connected": True,
    "ell5_rows": len(row_support),
    "unique_geodesic_rows": len(row_support),
    "support_edges": len(support_union),
    "only_bare_sse_violation_size": len(violating_subsets[0][0]),
    "forced_crossing": {"from": sorted(v0), "to": sorted(w), "new_vertex": L[1]},
    "restriction_exit_ports": len(ports),
    "l0_l1_partial_active_sink_disjoint": True,
    "partial_root_crossing": [L[0], L[1]],
    "singleton_primal_cuts": len(singleton_weight),
    "singleton_primal_weight": str(Fraction(1, 2)),
    "row_coverage": str(min(row_coverage.values())),
    "support_congestion": str(max(support_congestion.values())),
    "max_external_load": str(max(external_load.values())),
    "min_door_margin": str(min(door_margin.values())),
    "min_25scaled_door_margin": str(min(scaled_door_margin.values())),
    "door_only_fullbank_primal": True,
    "max_vertex_sink_load": str(max(vertex_sink_load.values())),
    "min_vertex_slack_cap": str(min(vertex_slack_cap.values())),
    "min_vertex_slack_margin": str(min(vertex_slack_margin.values())),
    "vertex_slack_only_fullbank_primal": True,
    "actual_graph_to_bank_constructor_missing": True,
}
print(result)
