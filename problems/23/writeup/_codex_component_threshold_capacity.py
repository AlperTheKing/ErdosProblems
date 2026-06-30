"""Probe a component threshold-capacity lemma for the NET position-flow proof.

For an off-path B-component C relative to a unique path P, let attachments to
P be counted with multiplicity by path position.  For each threshold t between
x_t and x_{t+1}, set

  left_C(t)  = # attachment edges from C to positions <= t
  right_C(t) = # attachment edges from C to positions > t

The candidate coarea capacity is

  sum_t min(left_C(t), right_C(t)) <= |C|.

If true, it explains why one component of size |C| can pay multiple parallel
corridors after scalar component-count NET fails.
"""

from __future__ import annotations

from _M_full_detour_counterexample import make_graph as full_detour_graph
from _M_tailswitch_gate import build_pd
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn


def component_threshold_records(n, adj, side, path):
    pset = set(path)
    pos = {v: i for i, v in enumerate(path)}
    rest = [v for v in range(n) if v not in pset]
    parent = {v: v for v in rest}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u in rest:
        for v in adj[u]:
            if v in pset:
                continue
            if side[u] != side[v]:
                parent[find(u)] = find(v)
    comps = {}
    for v in rest:
        comps.setdefault(find(v), set()).add(v)

    records = []
    for C in comps.values():
        attachments = []
        for u in C:
            for x in adj[u]:
                if x in pset and side[u] != side[x]:
                    attachments.append(pos[x])
        if not attachments:
            continue
        total = 0
        terms = []
        for t in range(len(path) - 1):
            left = sum(1 for a in attachments if a <= t)
            right = len(attachments) - left
            m = min(left, right)
            total += m
            if m:
                terms.append((t, left, right, m))
        records.append((len(C), sorted(attachments), total, terms))
    return records


def probe_case(name, n, edges, side):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    bad = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        for size, att, total, terms in component_threshold_records(n, adj, side, cyc[f][0]):
            if total > size:
                bad.append((f, size, att, total, terms))
    print(f"{name}: bad={len(bad)}")
    for rec in bad[:3]:
        print("  ", rec[:4])


def main():
    for name, pend, chords in [
        ("nested", 12, [(0, 8), (2, 6)]),
        ("crossing", 12, [(0, 6), (2, 8)]),
        ("chain", 12, [(0, 4), (4, 8), (8, 12)]),
        ("disjoint", 12, [(0, 4), (8, 12)]),
    ]:
        n, edges = build_pd(pend, chords)
        probe_case(name, n, sorted(set(edges)), [v % 2 for v in range(n)])

    n, edges, side = full_detour_graph()
    probe_case("full-detour", n, edges, side)
    probe_case("full-detour-merged", n, sorted(set(edges) | {(13, 27)}), side)

    n0, e0 = build_pd(12, [(0, 8), (2, 6)])
    s0 = [v % 2 for v in range(n0)]
    for m in range(1, 4):
        n, edges, side = n0, list(e0), list(s0)
        for _ in range(m):
            n, edges, side = add_cut_path(n, edges, side, 0, 3, 5)
            n, edges, side = add_cut_path(n, edges, side, 8, 5, 5)
        probe_case(f"two-sided-m{m}", n, sorted(set(edges)), side)


if __name__ == "__main__":
    main()
