"""Test a proof-shaped inequality for scalar NET in the no-bracket case.

For a unique row f and interval I on P_f:

  net_slack(I) = #{off-path B-components whose span meets I}
                 - E_P(I)

where E_P counts only P-contained atoms intersecting I.

Let H(I) be those active components.  For every Y subset H(I), flip

  S = {path vertices in I} union vertices(Y).

Let Delta(S)=delta_B(S)-delta_M(S), the cut loss.  If

  net_slack(I) >= min_Y Delta(S)

holds whenever there is no bracket hub, then max-cut optimality
(Delta(S)>=0 for every S) implies scalar NET in the no-bracket case.
"""

from __future__ import annotations

from fractions import Fraction as F

from _M_full_detour_counterexample import make_graph as full_detour_graph
from _M_tailswitch_gate import build_pd
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn


def delta(edges, side, S):
    S = set(S)
    db = dm = 0
    for u, v in edges:
        if (u in S) == (v in S):
            continue
        if side[u] != side[v]:
            db += 1
        else:
            dm += 1
    return db - dm


def component_info(n, adj, side, path):
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
    out = []
    for verts in comps.values():
        att = {
            pos[x]
            for u in verts
            for x in adj[u]
            if x in pset and side[u] != side[x]
        }
        if att:
            out.append((min(att), max(att), set(verts), tuple(sorted(att))))
    return out


def probe_case(name, n, edges, side):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side):
        print(name, "not Bconn")
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        print(name, "no struct")
        return
    M, _ell, _T, _mu, cyc = st
    worst = None
    fail = None
    checked = 0
    for f in M:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        pset = set(path)
        pos = {v: i for i, v in enumerate(path)}
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
                        break
        if not atoms:
            continue
        starts = {lo for lo, _hi, _w, _g in atoms}
        ends = {hi for _lo, hi, _w, _g in atoms}
        if starts & ends:
            continue
        comps = component_info(n, adj, side, path)
        L = len(path)
        for a in range(L):
            for b in range(a, L):
                demand = sum(w for lo, hi, w, _g in atoms if not (hi < a or b < lo))
                if demand == 0:
                    continue
                active = [
                    idx for idx, (lo, hi, _verts, _att) in enumerate(comps)
                    if not (hi < a or b < lo)
                ]
                slack = F(len(active)) - demand
                if len(active) > 20:
                    continue
                best = None
                base = {path[i] for i in range(a, b + 1)}
                for mask in range(1 << len(active)):
                    S = set(base)
                    for j, idx in enumerate(active):
                        if (mask >> j) & 1:
                            S |= comps[idx][2]
                    d = delta(edges, side, S)
                    if best is None or d < best:
                        best = d
                checked += 1
                margin = slack - F(best)
                rec = (margin, slack, best, f, path, (a, b), atoms, [(c[0], c[1], len(c[2]), c[3]) for c in comps])
                if worst is None or margin < worst[0]:
                    worst = rec
                if margin < 0 and fail is None:
                    fail = rec
    print(f"{name}: checked={checked} worst={worst[:6] if worst else None} fail={fail[:6] if fail else None}")


def main():
    for name, pend, chords in [
        ("nested", 12, [(0, 8), (2, 6)]),
        ("crossing", 12, [(0, 6), (2, 8)]),
        ("chain", 12, [(0, 4), (4, 8), (8, 12)]),
    ]:
        n, edges = build_pd(pend, chords)
        probe_case(name, n, sorted(set(edges)), [v % 2 for v in range(n)])

    n, edges, side = full_detour_graph()
    probe_case("full-detour", n, edges, side)

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
