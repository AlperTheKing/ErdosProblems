"""Probe the live NET theorem shape on synthetic regression families.

The broad statement

    no bracket hub => P-contained position-flow feasible

is false on the old nested/crossing parity cuts.  Those cuts are not global
max cuts.  This script reports no-bracket position-flow failures and verifies
the max-cut value of the displayed cut.

This is deliberately small and exact; it is a local audit before asking Claude
to run the same predicate on the full battery.
"""

from __future__ import annotations

from collections import deque
from fractions import Fraction as F

from _M_full_detour_counterexample import maxcut
from _M_tailswitch_gate import build_pd, cutsize, tri_free
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn


def maxflow(cap, src, snk):
    n = len(cap)
    flow = F(0)
    while True:
        par = [-1] * n
        par[src] = src
        q = deque([src])
        while q and par[snk] < 0:
            u = q.popleft()
            for v, c in enumerate(cap[u]):
                if par[v] < 0 and c > 0:
                    par[v] = u
                    q.append(v)
        if par[snk] < 0:
            return flow
        aug = None
        v = snk
        while v != src:
            u = par[v]
            aug = cap[u][v] if aug is None else min(aug, cap[u][v])
            v = u
        v = snk
        while v != src:
            u = par[v]
            cap[u][v] -= aug
            cap[v][u] += aug
            v = u
        flow += aug


def contained_flow_failures(n, adj, side):
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
        pos = {v: i for i, v in enumerate(path)}
        pset = set(path)
        load = [F(0) for _ in path]
        chords = []
        for g in M:
            if g == f:
                continue
            k = len(cyc[g])
            for q in cyc[g]:
                if set(q) <= pset:
                    js = sorted(pos[v] for v in q)
                    if js[-1] - js[0] == len(js) - 1:
                        lo, hi = js[0], js[-1]
                        chords.append((lo, hi, g))
                        for i in range(lo, hi + 1):
                            load[i] += F(1, k)
                        break
        if not chords:
            continue
        starts = {lo for lo, _hi, _g in chords}
        ends = {hi for _lo, hi, _g in chords}
        if starts & ends:
            continue

        rest = [v for v in range(n) if v not in pset]
        par = {v: v for v in rest}

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x

        for u in rest:
            for w in adj[u]:
                if w not in pset and side[u] != side[w]:
                    par[find(u)] = find(w)
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

        active_positions = [i for i, x in enumerate(load) if x > 0]
        total = sum((load[i] for i in active_positions), F(0))
        if total == 0:
            continue
        src = 0
        snk = 1
        p0 = 2
        c0 = p0 + len(active_positions)
        cap = [[F(0) for _ in range(c0 + len(spans))] for __ in range(c0 + len(spans))]
        for j, i in enumerate(active_positions):
            cap[src][p0 + j] = load[i]
        for j, (lo, hi, size) in enumerate(spans):
            cap[c0 + j][snk] = F(size)
            for k, i in enumerate(active_positions):
                if lo <= i <= hi:
                    cap[p0 + k][c0 + j] = total + 1
        flow = maxflow(cap, src, snk)
        if flow < total:
            out.append((f, path, chords, spans, total, flow))
    return out


def scalar_net_failures(n, adj, side):
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
        pos = {v: i for i, v in enumerate(path)}
        pset = set(path)
        atoms = []
        for g in M:
            if g == f:
                continue
            k = len(cyc[g])
            for q in cyc[g]:
                if set(q) <= pset:
                    js = sorted(pos[v] for v in q)
                    if js[-1] - js[0] == len(js) - 1:
                        atoms.append((js[0], js[-1], F(1, k), g))
        if not atoms:
            continue

        rest = [v for v in range(n) if v not in pset]
        par = {v: v for v in rest}

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x

        for u in rest:
            for w in adj[u]:
                if w not in pset and side[u] != side[w]:
                    par[find(u)] = find(w)
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
                spans.append((min(att), max(att)))

        for a in range(len(path)):
            for b in range(a, len(path)):
                demand = sum(w for lo, hi, w, _g in atoms if not (hi < a or b < lo))
                cap = sum(1 for lo, hi in spans if not (hi < a or b < lo))
                if demand > cap:
                    out.append((f, path, (a, b), demand, cap, atoms, spans))
                    return out
    return out


def cases():
    for name, pend, chords in [
        ("nested", 12, [(0, 8), (2, 6)]),
        ("crossing", 12, [(0, 6), (2, 8)]),
        ("chain", 12, [(0, 4), (4, 8), (8, 12)]),
    ]:
        n, edges = build_pd(pend, chords)
        yield name, n, sorted(set(edges)), [v % 2 for v in range(n)]

    n, edges = build_pd(12, [(0, 8), (2, 6)])
    side = [v % 2 for v in range(n)]
    n, edges, side = add_cut_path(n, list(edges), side, 0, 12, 14)
    yield "full-detour", n, sorted(set(edges)), side

    n0, e0 = build_pd(12, [(0, 8), (2, 6)])
    s0 = [v % 2 for v in range(n0)]
    for m in range(1, 4):
        n, edges, side = n0, list(e0), list(s0)
        for _ in range(m):
            n, edges, side = add_cut_path(n, edges, side, 0, 3, 5)
            n, edges, side = add_cut_path(n, edges, side, 8, 5, 5)
        yield f"two-sided-detour-m{m}", n, sorted(set(edges)), side


def main():
    for name, n, edges, side in cases():
        adj = adj_from_edges(n, edges)
        fails = contained_flow_failures(n, adj, side)
        net_fails = scalar_net_failures(n, adj, side)
        base = cutsize(n, adj, side)
        status, opt, bound = maxcut(n, edges)
        print(
            f"{name}: n={n} tri={tri_free(n, adj)} Bconn={Bconn(n, adj, side)} "
            f"cut={base} max={opt} bound={bound} status={status} "
            f"flow_failures={len(fails)} net_failures={len(net_fails)}"
        )
        for f, path, interval, demand, cap, atoms, spans in net_fails:
            print(f"  NET fail f={f} I={interval} demand={demand} cap={cap}")
            print(f"    path={path}")
            print(f"    atoms={atoms}")
            print(f"    spans={spans}")
        for f, path, chords, spans, total, flow in fails:
            print(f"  FLOW fail f={f} total={total} flow={flow}")
            print(f"    path={path}")
            print(f"    chords={chords}")
            print(f"    spans={spans}")


if __name__ == "__main__":
    main()
