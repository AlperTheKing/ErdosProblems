"""Probe a pointwise version of the no-bracket NET-containment target.

For a unique row f with path P and P-contained atom intervals J, define

  depth(i) = sum_{J contains i} 1/|cyc(g)|.

For off-path B-components, define cover(i) as the number of component spans
containing i.  Probe whether

  no bracket hub + global/gamma-min max  =>  depth(i) <= cover(i)

This pointwise condition implies the P-contained position-flow certificate
because each component span has |C| at least its span length, so assigning one
unit to every covered position is within capacity.
"""

from __future__ import annotations

from fractions import Fraction as F

from _M_full_detour_counterexample import make_graph as full_detour_graph, maxcut
from _M_tailswitch_gate import build_pd, cutsize, tri_free
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn


def pointwise_violations(n, adj, side):
    if not Bconn(n, adj, side):
        return []
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T, _mu, cyc = st
    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        pset = set(path)
        pos = {v: i for i, v in enumerate(path)}
        depth = [F(0) for _ in path]
        atoms = []
        for g in M:
            if g == f:
                continue
            k = len(cyc[g])
            for q in cyc[g]:
                if set(q) <= pset:
                    js = sorted(pos[v] for v in q)
                    if js[-1] - js[0] == len(js) - 1:
                        lo, hi = js[0], js[-1]
                        atoms.append((lo, hi, F(1, k), g))
                        for i in range(lo, hi + 1):
                            depth[i] += F(1, k)
                        break
        if not atoms:
            continue
        if {lo for lo, _hi, _w, _g in atoms} & {hi for _lo, hi, _w, _g in atoms}:
            continue

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
        spans = []
        for C in comps.values():
            att = {
                pos[x]
                for u in C
                for x in adj[u]
                if x in pset and side[u] != side[x]
            }
            if att:
                spans.append((min(att), max(att), len(C)))

        for i, d in enumerate(depth):
            cover = sum(1 for lo, hi, _size in spans if lo <= i <= hi)
            if d > cover:
                out.append((f, path, i, d, cover, atoms, spans))
                break
    return out


def cases():
    for name, pend, chords in [
        ("nested", 12, [(0, 8), (2, 6)]),
        ("crossing", 12, [(0, 6), (2, 8)]),
        ("chain", 12, [(0, 4), (4, 8), (8, 12)]),
        ("disjoint", 12, [(0, 4), (8, 12)]),
        ("two-left", 12, [(0, 4), (5, 9)]),
    ]:
        n, edges = build_pd(pend, chords)
        yield name, n, sorted(set(edges)), [v % 2 for v in range(n)]

    n, edges, side = full_detour_graph()
    yield "full-detour", n, edges, side

    n0, e0 = build_pd(12, [(0, 8), (2, 6)])
    s0 = [v % 2 for v in range(n0)]
    for m in range(1, 4):
        n, edges, side = n0, list(e0), list(s0)
        for _ in range(m):
            n, edges, side = add_cut_path(n, edges, side, 0, 3, 5)
            n, edges, side = add_cut_path(n, edges, side, 8, 5, 5)
        yield f"two-sided-m{m}", n, sorted(set(edges)), side


def main():
    for name, n, edges, side in cases():
        adj = adj_from_edges(n, edges)
        status, opt, bound = maxcut(n, edges)
        viol = pointwise_violations(n, adj, side)
        print(
            f"{name}: n={n} tri={tri_free(n, adj)} Bconn={Bconn(n, adj, side)} "
            f"cut={cutsize(n, adj, side)} max={opt} bound={bound} status={status} "
            f"viol={len(viol)}"
        )
        for rec in viol[:2]:
            f, path, i, d, cover, atoms, spans = rec
            print(f"  viol f={f} i={i} depth={d} cover={cover}")
            print(f"    atoms={atoms}")
            print(f"    spans={spans}")


if __name__ == "__main__":
    main()
