"""Exact counterexample to subset-local internal endpoint-flow Hall.

The 13-atom minimal support-deficient core and max-cut lock from
``_codex_ies_3164_counterexample`` are retained.  Instead of one-vertex Q
gadgets, two dense C5 blowups are attached at the endpoints 4 and 8 of the
single internal off-support edge.  Each blowup has sizes

    (t, t^2, 1, t^2, t),  t = 28,

and its singleton middle part is identified with one endpoint.  It adds
``2 t^2 + 2 t`` vertices but contributes load ``5 t^2`` at the attachment.
The two endpoint vertex-slack capacities are therefore both zero.

Each blowup has ``t^2`` explicitly edge-disjoint pentagons, one per edge of
the displayed bad A4-A0 block.  Hence its displayed cut is maximum.  Vertex
gluing makes maximum-cut values additive.  Triangle-freeness then gives the
Gamma lower bound ``25 * badCount``, attained by the displayed all-ell5 cut.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, deque
from fractions import Fraction

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _codex_ies_3164_counterexample import (  # noqa: E402
    ANCHOR,
    CORE_BAD,
    CORE_CHORD,
    CORE_N,
    CORE_SIDE,
    CORE_SUPPORT,
    LOCKS_PER_CORE_VERTEX,
    adjacency,
    bfs_counts,
    canonical_edge_payload,
    check_lock_maxcut_certificate,
    edge,
)


T = 28
ATTACHMENTS = (4, 8)


def add_new(target: set[tuple[int, int]], u: int, v: int) -> None:
    e = edge(u, v)
    assert e not in target
    target.add(e)


def build_locked_core():
    side = list(CORE_SIDE) + [0]
    edges = set(CORE_SUPPORT) | {CORE_CHORD} | set(CORE_BAD)
    blue = set(CORE_SUPPORT) | {CORE_CHORD}
    bad = set(CORE_BAD)
    next_vertex = ANCHOR + 1
    lock_paths = []
    for x in range(CORE_N):
        length = 4 if CORE_SIDE[x] == 0 else 5
        for _ in range(LOCKS_PER_CORE_VERTEX):
            internal = tuple(range(next_vertex, next_vertex + length - 1))
            next_vertex += length - 1
            for step, v in enumerate(internal, 1):
                assert v == len(side)
                side.append(CORE_SIDE[x] ^ (step % 2))
            path = (x,) + internal + (ANCHOR,)
            for u, v in zip(path, path[1:]):
                add_new(edges, u, v)
                add_new(blue, u, v)
            lock_paths.append((x, path))
    assert next_vertex == 644
    assert len(edges) == 838 and len(blue) == 825 and len(bad) == 13
    return side, edges, blue, bad, tuple(lock_paths), next_vertex


def add_c5_blowup(side, edges, blue, bad, next_vertex, attachment):
    sizes = (T, T * T, 1, T * T, T)
    parts = []
    for i, size in enumerate(sizes):
        if i == 2:
            assert size == 1
            parts.append((attachment,))
            continue
        part = tuple(range(next_vertex, next_vertex + size))
        next_vertex += size
        expected_side = CORE_SIDE[attachment] ^ (i % 2)
        for v in part:
            assert v == len(side)
            side.append(expected_side)
        parts.append(part)

    for i in range(5):
        left, right = parts[i], parts[(i + 1) % 5]
        is_bad_block = i == 4
        for u in left:
            for v in right:
                add_new(edges, u, v)
                add_new(bad if is_bad_block else blue, u, v)

    # Explicit t^2 edge-disjoint pentagons indexed by A0 x A4.
    cycles = []
    for i, a0 in enumerate(parts[0]):
        for j, a4 in enumerate(parts[4]):
            index = i * T + j
            cycle = (a0, parts[1][index], attachment, parts[3][index], a4)
            cycles.append(cycle)
    cycle_edges = []
    for cycle in cycles:
        es = {
            edge(cycle[k], cycle[(k + 1) % 5])
            for k in range(5)
        }
        assert es <= edges
        cycle_edges.extend(es)
    assert len(cycles) == T * T
    assert len(cycle_edges) == len(set(cycle_edges)) == 5 * T * T
    return next_vertex, tuple(parts), tuple(cycles)


def support_and_load(n, blue, bad):
    blue_adj = adjacency(n, blue)
    tload = [Fraction(0) for _ in range(n)]
    supports = {}
    vertices = {}
    ell_hist = Counter()
    for a, b in sorted(bad):
        da, wa = bfs_counts(blue_adj, a)
        db, wb = bfs_counts(blue_adj, b)
        distance = da[b]
        assert distance >= 0 and wa[b] > 0
        ell = distance + 1
        ell_hist[ell] += 1
        for v in range(n):
            if da[v] >= 0 and db[v] >= 0 and da[v] + db[v] == distance:
                tload[v] += Fraction(ell * wa[v] * wb[v], wa[b])
        atom = edge(a, b)
        if atom in CORE_BAD:
            vertices[atom] = {
                v for v in range(n)
                if da[v] >= 0 and db[v] >= 0 and da[v] + db[v] == distance
            }
            supports[atom] = {
                e for e in blue
                if da[e[0]] + 1 + db[e[1]] == distance
                or da[e[1]] + 1 + db[e[0]] == distance
            }
    return tload, supports, vertices, ell_hist


def main():
    side, edges, blue, bad, lock_paths, next_vertex = build_locked_core()
    blowups = []
    for attachment in ATTACHMENTS:
        next_vertex, parts, cycles = add_c5_blowup(
            side, edges, blue, bad, next_vertex, attachment
        )
        blowups.append((parts, cycles))

    n = next_vertex
    assert n == 3892
    assert edges == blue | bad and blue.isdisjoint(bad)
    assert len(edges) == 93350
    assert len(blue) == 91769
    assert len(bad) == 1581

    full_adj = adjacency(n, edges)
    assert all(full_adj[u].isdisjoint(full_adj[v]) for u, v in edges)
    blue_adj = adjacency(n, blue)
    dist, _ = bfs_counts(blue_adj, 0)
    assert all(d >= 0 for d in dist)

    load, supports, vertices, ell_hist = support_and_load(n, blue, bad)
    assert ell_hist == Counter({5: 1581})
    assert load[4] == 3935 and load[8] == 3930
    assert max(Fraction(0), Fraction(n) - load[4]) == 0
    assert max(Fraction(0), Fraction(n) - load[8]) == 0

    core = set().union(*(vertices[a] for a in CORE_BAD))
    short = set().union(*(supports[a] for a in CORE_BAD))
    internal = {
        e for e in blue if e[0] in core and e[1] in core and e not in short
    }
    assert core == set(range(CORE_N))
    assert short == set(CORE_SUPPORT)
    assert internal == {CORE_CHORD}

    atoms = tuple(CORE_BAD)
    for mask in range(1, 1 << len(atoms)):
        union = set().union(*(supports[atoms[i]] for i in range(len(atoms))
                              if (mask >> i) & 1))
        if mask != (1 << len(atoms)) - 1:
            assert mask.bit_count() <= len(union)
    assert len(atoms) == 13 and len(short) == 12

    lock_cert = check_lock_maxcut_certificate(lock_paths)
    gadget_edges = 3 * T * T + 2 * T * T * T
    gadget_bad = T * T
    gadget_maxcut = gadget_edges - gadget_bad
    assert gadget_edges == 46256 and gadget_maxcut == 45472
    global_maxcut = 825 + 2 * gadget_maxcut
    assert global_maxcut == len(blue) == 91769
    assert len(edges) - global_maxcut == len(bad)

    gamma = 25 * len(bad)
    assert gamma == 39525
    edge_sha = hashlib.sha256(canonical_edge_payload(edges)).hexdigest()

    print(json.dumps({
        "N": n,
        "edges": len(edges),
        "triangleFree": True,
        "BConnected": True,
        "cut": {"maxCut": global_maxcut, "bad": len(bad)},
        "gamma": {"displayed": gamma, "lowerBound": gamma},
        "rows": {"ellHistogram": dict(ell_hist), "T4": str(load[4]),
                 "T8": str(load[8])},
        "A": {"atoms": 13, "support": 12,
              "internalOffSupport": [list(CORE_CHORD)],
              "endpointCapacity": {"4": "0", "8": "0"},
              "endpointHallDemand": "1"},
        "blowup": {"t": T, "sizes": [T, T*T, 1, T*T, T],
                   "edgeDisjointPentagonsPerCopy": T*T,
                   "maxCutPerCopy": gadget_maxcut},
        "lock": lock_cert,
        "edgeListSHA256": edge_sha,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
