"""Exact deterministic checker for the 3164-vertex IES counterexample.

The graph consists of:

* a 13-vertex minimal support-deficient ell=5 core;
* 14 parity-lock paths from every core vertex to one anchor, making the
  displayed cut the unique maximum cut on that factor (modulo complement);
* 315 copies of a nine-vertex max-cut gadget, all meeting the first factor
  only at the overloaded core vertex 4.

The maximum-cut certificate is compositional.  With the anchor color fixed,
changing any core vertex loses one edge on each of its 14 lock paths, while
the core can gain at most its 13 displayed bad edges.  Each Q copy has
maximum cut 10 for either fixed color of its shared vertex, checked by
exhausting all 2^8 remaining colorings.  Hence the global maximum cut is
825 + 315 * 10 = 3975 and has 4618 - 3975 = 643 bad edges.

For Gamma minimality, every connected-blue maximum cut has those same 643
bad edges.  A blue path between equal-colored endpoints has even length;
triangle-freeness excludes length two, so every bad row has ell >= 5 and
Gamma >= 25 * 643.  The displayed cut has every bad row at ell=5, attaining
that lower bound.

All graph, path, Hall, load, and hash calculations below are exact.  The
canonical edge-list encoding is one sorted ``u v\n`` ASCII record per edge.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from itertools import product


Edge = tuple[int, int]

CORE_N = 13
ANCHOR = 13
LOCKS_PER_CORE_VERTEX = 14
Q_COPIES = 315
LOAD_VERTEX = 4

CORE_SIDE = (0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1)

CORE_SUPPORT: tuple[Edge, ...] = (
    (0, 8),
    (1, 9),
    (2, 9),
    (3, 10),
    (4, 10),
    (0, 11),
    (3, 11),
    (9, 11),
    (3, 12),
    (5, 12),
    (6, 12),
    (7, 12),
)

CORE_CHORD: Edge = (4, 8)

CORE_BAD: tuple[Edge, ...] = (
    (0, 5),
    (0, 6),
    (0, 7),
    (1, 8),
    (1, 10),
    (1, 12),
    (2, 8),
    (2, 10),
    (2, 12),
    (4, 5),
    (4, 6),
    (4, 7),
    (5, 9),
)

Q_SHARED_VERTEX = 6
Q_SIDE = (1, 1, 1, 0, 0, 0, 0, 1, 1)
Q_EDGES: tuple[Edge, ...] = (
    (0, 5),
    (0, 6),
    (1, 6),
    (2, 6),
    (1, 7),
    (2, 7),
    (3, 7),
    (4, 7),
    (3, 8),
    (4, 8),
    (5, 8),
    (6, 8),
)

EXPECTED_EDGE_SHA256 = (
    "38a790b5b9ccfd7afc55301401cdd2e60a55bd6aba03c9cc38a3db2cac705073"
)
EXPECTED_MIN_SUPPORT_BY_SIZE = (None, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11, 11, 12, 12)


def edge(u: int, v: int) -> Edge:
    assert u != v
    return (u, v) if u < v else (v, u)


def add_new(target: set[Edge], e: Edge) -> None:
    e = edge(*e)
    assert e not in target
    target.add(e)


def build_graph() -> dict[str, object]:
    side = list(CORE_SIDE) + [0]
    all_edges: set[Edge] = set()
    blue_edges: set[Edge] = set()
    bad_edges: set[Edge] = set()

    for e in CORE_SUPPORT + (CORE_CHORD,):
        add_new(all_edges, e)
        add_new(blue_edges, e)
    for e in CORE_BAD:
        add_new(all_edges, e)
        add_new(bad_edges, e)

    next_vertex = ANCHOR + 1
    lock_paths: list[tuple[int, tuple[int, ...]]] = []
    for x in range(CORE_N):
        length = 4 if CORE_SIDE[x] == 0 else 5
        assert (CORE_SIDE[x] ^ side[ANCHOR]) == length % 2
        for _ in range(LOCKS_PER_CORE_VERTEX):
            internal = tuple(range(next_vertex, next_vertex + length - 1))
            next_vertex += length - 1
            for step, v in enumerate(internal, 1):
                assert v == len(side)
                side.append(CORE_SIDE[x] ^ (step % 2))
            path = (x,) + internal + (ANCHOR,)
            assert side[path[-1]] == CORE_SIDE[x] ^ (length % 2)
            for u, v in zip(path, path[1:]):
                e = edge(u, v)
                add_new(all_edges, e)
                add_new(blue_edges, e)
            lock_paths.append((x, path))

    h_n = next_vertex
    h_edge_count = len(all_edges)
    h_blue_count = len(blue_edges)
    h_bad_count = len(bad_edges)

    q_maps: list[tuple[int, ...]] = []
    for _ in range(Q_COPIES):
        mapping = [-1] * 9
        mapping[Q_SHARED_VERTEX] = LOAD_VERTEX
        for local in range(9):
            if local == Q_SHARED_VERTEX:
                continue
            mapping[local] = next_vertex
            assert next_vertex == len(side)
            side.append(Q_SIDE[local])
            next_vertex += 1
        for u, v in Q_EDGES:
            e = edge(mapping[u], mapping[v])
            add_new(all_edges, e)
            if Q_SIDE[u] != Q_SIDE[v]:
                add_new(blue_edges, e)
            else:
                add_new(bad_edges, e)
        q_maps.append(tuple(mapping))

    assert next_vertex == len(side)
    assert all_edges == blue_edges | bad_edges
    assert blue_edges.isdisjoint(bad_edges)

    return {
        "n": next_vertex,
        "side": tuple(side),
        "edges": all_edges,
        "blue": blue_edges,
        "bad": bad_edges,
        "lockPaths": tuple(lock_paths),
        "qMaps": tuple(q_maps),
        "hN": h_n,
        "hEdges": h_edge_count,
        "hBlue": h_blue_count,
        "hBad": h_bad_count,
    }


def adjacency(n: int, edges: set[Edge]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs_counts(adj: list[set[int]], source: int) -> tuple[list[int], list[int]]:
    """Return exact distances and shortest-path counts from ``source``."""
    dist = [-1] * len(adj)
    ways = [0] * len(adj)
    dist[source] = 0
    ways[source] = 1
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                ways[v] = ways[u]
                queue.append(v)
            elif dist[v] == dist[u] + 1:
                ways[v] += ways[u]
    return dist, ways


def path_max_with_fixed_endpoints(length: int, left: int, right: int) -> int:
    """Exhaust the internal colors of one path with fixed endpoint colors."""
    best = -1
    for internal in product((0, 1), repeat=length - 1):
        colors = (left,) + internal + (right,)
        value = sum(colors[i] != colors[i + 1] for i in range(length))
        best = max(best, value)
    return best


def q_maxcut_by_fixed_shared_color() -> dict[int, dict[str, int]]:
    others = [v for v in range(9) if v != Q_SHARED_VERTEX]
    result: dict[int, dict[str, int]] = {}
    for fixed in (0, 1):
        best = -1
        multiplicity = 0
        for mask in range(1 << len(others)):
            colors = [0] * 9
            colors[Q_SHARED_VERTEX] = fixed
            for i, v in enumerate(others):
                colors[v] = (mask >> i) & 1
            value = sum(colors[u] != colors[v] for u, v in Q_EDGES)
            if value > best:
                best = value
                multiplicity = 1
            elif value == best:
                multiplicity += 1
        result[fixed] = {"maxCut": best, "multiplicity": multiplicity}
    return result


def check_lock_maxcut_certificate(lock_paths: tuple[tuple[int, tuple[int, ...]], ...]) -> dict[str, object]:
    parity_table: dict[str, int] = {}
    for length in (4, 5):
        for left in (0, 1):
            for right in (0, 1):
                got = path_max_with_fixed_endpoints(length, left, right)
                expected = length if (left ^ right) == length % 2 else length - 1
                assert got == expected
                parity_table[f"L{length}:{left}{right}"] = got

    path_count = Counter(x for x, _ in lock_paths)
    assert path_count == Counter({x: LOCKS_PER_CORE_VERTEX for x in range(CORE_N)})
    assert all(len(path) - 1 == (4 if CORE_SIDE[x] == 0 else 5) for x, path in lock_paths)

    core_edges = set(CORE_SUPPORT) | {CORE_CHORD} | set(CORE_BAD)
    displayed_core_cut = sum(CORE_SIDE[u] != CORE_SIDE[v] for u, v in core_edges)
    assert displayed_core_cut == 13

    max_observed_core_gain = 0
    max_nonzero_gain_after_locks: int | None = None
    for mask in range(1 << CORE_N):
        colors = [CORE_SIDE[v] ^ ((mask >> v) & 1) for v in range(CORE_N)]
        core_cut = sum(colors[u] != colors[v] for u, v in core_edges)
        core_gain = core_cut - displayed_core_cut
        changed = mask.bit_count()

        # Only the 13 displayed bad core edges can become newly cut.
        assert core_gain <= len(CORE_BAD)
        max_observed_core_gain = max(max_observed_core_gain, core_gain)

        if mask:
            gain_after_lock_bound = core_gain - LOCKS_PER_CORE_VERTEX * changed
            assert gain_after_lock_bound < 0
            if max_nonzero_gain_after_locks is None:
                max_nonzero_gain_after_locks = gain_after_lock_bound
            else:
                max_nonzero_gain_after_locks = max(
                    max_nonzero_gain_after_locks, gain_after_lock_bound
                )

    assert max_nonzero_gain_after_locks is not None
    return {
        "coreBadGainBound": len(CORE_BAD),
        "locksPerChangedCoreVertex": LOCKS_PER_CORE_VERTEX,
        "maxObservedCoreGain": max_observed_core_gain,
        "maxNonzeroGainAfterLockBound": max_nonzero_gain_after_locks,
        "parityTable": parity_table,
    }


def canonical_edge_payload(edges: set[Edge]) -> bytes:
    return "".join(f"{u} {v}\n" for u, v in sorted(edges)).encode("ascii")


def main() -> None:
    graph = build_graph()
    n = graph["n"]
    side = graph["side"]
    edges = graph["edges"]
    blue = graph["blue"]
    bad = graph["bad"]
    lock_paths = graph["lockPaths"]

    assert isinstance(n, int)
    assert isinstance(side, tuple)
    assert isinstance(edges, set)
    assert isinstance(blue, set)
    assert isinstance(bad, set)
    assert isinstance(lock_paths, tuple)

    assert n == 3164
    assert graph["hN"] == 644
    assert graph["hEdges"] == 838
    assert graph["hBlue"] == 825
    assert graph["hBad"] == 13
    assert len(edges) == 4618
    assert len(blue) == 3975
    assert len(bad) == 643

    classified_blue = {e for e in edges if side[e[0]] != side[e[1]]}
    classified_bad = edges - classified_blue
    assert classified_blue == blue
    assert classified_bad == bad

    full_adj = adjacency(n, edges)
    blue_adj = adjacency(n, blue)
    assert all(full_adj[u].isdisjoint(full_adj[v]) for u, v in edges)

    connected_dist, _ = bfs_counts(blue_adj, 0)
    assert all(d >= 0 for d in connected_dist)

    ell_histogram: Counter[int] = Counter()
    path_count_histogram: Counter[int] = Counter()
    t4 = Fraction(0)
    a_support: dict[Edge, frozenset[Edge]] = {}
    a_vertices: dict[Edge, frozenset[int]] = {}

    for a, b in sorted(bad):
        dist_a, ways_a = bfs_counts(blue_adj, a)
        dist_b, ways_b = bfs_counts(blue_adj, b)
        distance = dist_a[b]
        assert distance >= 0
        path_count = ways_a[b]
        assert path_count > 0

        ell = distance + 1
        ell_histogram[ell] += 1
        path_count_histogram[path_count] += 1

        if (
            dist_a[LOAD_VERTEX] >= 0
            and dist_b[LOAD_VERTEX] >= 0
            and dist_a[LOAD_VERTEX] + dist_b[LOAD_VERTEX] == distance
        ):
            through_count = ways_a[LOAD_VERTEX] * ways_b[LOAD_VERTEX]
            t4 += Fraction(ell * through_count, path_count)

        atom = edge(a, b)
        if atom in CORE_BAD:
            vertices = frozenset(
                v
                for v in range(n)
                if dist_a[v] >= 0
                and dist_b[v] >= 0
                and dist_a[v] + dist_b[v] == distance
            )
            support = frozenset(
                e
                for e in blue
                if dist_a[e[0]] + 1 + dist_b[e[1]] == distance
                or dist_a[e[1]] + 1 + dist_b[e[0]] == distance
            )
            a_vertices[atom] = vertices
            a_support[atom] = support

    assert ell_histogram == Counter({5: 643})
    assert path_count_histogram == Counter({1: 13, 2: 630})
    assert t4 == 3165

    ordered_atoms = tuple(CORE_BAD)
    assert set(a_support) == set(ordered_atoms)
    core_vertices = set().union(*(a_vertices[a] for a in ordered_atoms))
    short_edges = set().union(*(a_support[a] for a in ordered_atoms))
    internal_off_support = {
        e for e in blue if e[0] in core_vertices and e[1] in core_vertices and e not in short_edges
    }
    assert core_vertices == set(range(CORE_N))
    assert short_edges == set(CORE_SUPPORT)
    assert internal_off_support == {CORE_CHORD}

    min_support_by_size: list[int | None] = [None] * (len(ordered_atoms) + 1)
    full_mask = (1 << len(ordered_atoms)) - 1
    for mask in range(1, full_mask + 1):
        union: set[Edge] = set()
        for i, atom in enumerate(ordered_atoms):
            if (mask >> i) & 1:
                union.update(a_support[atom])
        size = mask.bit_count()
        current = min_support_by_size[size]
        if current is None or len(union) < current:
            min_support_by_size[size] = len(union)
        if mask != full_mask:
            assert size <= len(union)

    assert tuple(min_support_by_size) == EXPECTED_MIN_SUPPORT_BY_SIZE
    assert len(ordered_atoms) == 13
    assert len(short_edges) == 12
    assert len(short_edges) < len(ordered_atoms)

    q_certificate = q_maxcut_by_fixed_shared_color()
    assert q_certificate[0]["maxCut"] == 10
    assert q_certificate[1]["maxCut"] == 10
    displayed_q_cut = sum(Q_SIDE[u] != Q_SIDE[v] for u, v in Q_EDGES)
    assert displayed_q_cut == 10

    lock_certificate = check_lock_maxcut_certificate(lock_paths)
    h_maxcut = 825
    global_maxcut = h_maxcut + Q_COPIES * 10
    assert global_maxcut == 3975
    assert global_maxcut == len(blue)
    assert len(edges) - global_maxcut == len(bad) == 643

    gamma = sum(ell * ell * count for ell, count in ell_histogram.items())
    gamma_lower_bound = 25 * len(bad)
    assert gamma == gamma_lower_bound == 16075

    payload = canonical_edge_payload(edges)
    edge_sha256 = hashlib.sha256(payload).hexdigest()
    assert len(payload) == 39069
    assert edge_sha256 == EXPECTED_EDGE_SHA256

    result = {
        "A": {
            "atoms": len(ordered_atoms),
            "core": sorted(core_vertices),
            "inclusionMinimal": True,
            "internalOffSupport": [list(e) for e in sorted(internal_off_support)],
            "minSupportBySize": min_support_by_size[1:],
            "support": len(short_edges),
        },
        "N": n,
        "cut": {
            "BConnected": True,
            "bad": len(bad),
            "blue": len(blue),
            "maxCut": global_maxcut,
        },
        "edgeListEncoding": "sorted u<v as ASCII 'u v\\n'",
        "edgeListSHA256": edge_sha256,
        "edges": len(edges),
        "gammaMinCertificate": {
            "displayedGamma": gamma,
            "lowerBound": gamma_lower_bound,
            "reason": "643 bad edges in every max cut; triangle-free connected-B gives ell>=5",
        },
        "maxCutCertificate": {
            "H": h_maxcut,
            "QCopies": Q_COPIES,
            "QFixedSharedColor": q_certificate,
            "global": global_maxcut,
            "locks": lock_certificate,
        },
        "rows": {
            "allEll5": True,
            "ellHistogram": dict(sorted(ell_histogram.items())),
            "pathCountHistogram": dict(sorted(path_count_histogram.items())),
            "T4": str(t4),
        },
        "triangleFree": True,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
