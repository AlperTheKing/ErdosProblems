"""Stronger Part-A probe: route each non-P-contained geodesic atom only through
the off-path B-components that the geodesic actually uses.

For a unique row f with path P, each non-P-contained shortest geodesic Q for
g!=f contributes weight 1/|cyc(g)| at each P-position in Q.  The weaker gate
allows that position demand to use any off-path component whose span contains
the position.  This probe restricts each atom (g,Q,i) to components that both
occur on Q and whose span contains i.

This is not a proof script; it is a falsification gate for a more natural
charging lemma.
"""

import subprocess
from collections import deque
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint


def maxflow(cap, src, snk, n):
    flow = F(0)
    while True:
        par = [-1] * n
        par[src] = src
        q = deque([src])
        while q:
            u = q.popleft()
            for v in range(n):
                if par[v] == -1 and cap[u][v] > 0:
                    par[v] = u
                    q.append(v)
        if par[snk] == -1:
            return flow
        v = snk
        bottleneck = None
        while v != src:
            u = par[v]
            bottleneck = cap[u][v] if bottleneck is None else min(bottleneck, cap[u][v])
            v = u
        v = snk
        while v != src:
            u = par[v]
            cap[u][v] -= bottleneck
            cap[v][u] += bottleneck
            v = u
        flow += bottleneck


def kchord(k, clen=4):
    pend = clen * k
    edges = [(i, i + 1) for i in range(pend)]
    nint = pend + 1
    ext = list(range(pend + 1, pend + 1 + nint))
    det = [0] + ext + [pend]
    for a, b in zip(det, det[1:]):
        edges.append((min(a, b), max(a, b)))
    for j in range(k):
        edges.append((clen * j, clen * j + clen))
    edges.append((0, pend))
    return pend + 1 + nint, sorted(set((min(a, b), max(a, b)) for a, b in edges))


def offpath_components(n, adj, side, pset, pos):
    rest = [v for v in range(n) if v not in pset]
    if not rest:
        return {}, []
    parent = {v: v for v in rest}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for u in rest:
        for w in adj[u]:
            if w not in pset and side[u] != side[w]:
                union(u, w)

    groups = {}
    for v in rest:
        groups.setdefault(find(v), set()).add(v)

    comp_of = {}
    comps = []
    for _, comp in groups.items():
        attach = {pos[x] for u in comp for x in adj[u] if x in pset and side[u] != side[x]}
        if not attach:
            continue
        idx = len(comps)
        comps.append((min(attach), max(attach), len(comp), comp))
        for u in comp:
            comp_of[u] = idx
    return comp_of, comps


def check_cut(n, adj, side, name, acc):
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    bad_edges, _ell, _T, _mu, cyc = st
    for f in bad_edges:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        pset = set(path)
        pos = {v: i for i, v in enumerate(path)}
        comp_of, comps = offpath_components(n, adj, side, pset, pos)
        if not comps:
            continue

        atoms = []
        for g in bad_edges:
            if g == f:
                continue
            if any(set(q) <= pset for q in cyc[g]):
                continue
            weight = F(1, len(cyc[g]))
            for q in cyc[g]:
                used = {comp_of[v] for v in q if v in comp_of}
                if not used:
                    continue
                for v in q:
                    if v not in pos:
                        continue
                    i = pos[v]
                    choices = [c for c in used if comps[c][0] <= i <= comps[c][1]]
                    atoms.append((weight, choices, g, tuple(q), i))
        if not atoms:
            continue

        src = 0
        snk = 1
        atom0 = 2
        comp0 = atom0 + len(atoms)
        nn = comp0 + len(comps)
        cap = [[F(0)] * nn for _ in range(nn)]
        total = F(0)
        for j, (weight, choices, _g, _q, _i) in enumerate(atoms):
            cap[src][atom0 + j] = weight
            total += weight
            for c in choices:
                cap[atom0 + j][comp0 + c] = total + 1
        for c, (_lo, _hi, size, _comp) in enumerate(comps):
            cap[comp0 + c][snk] = F(size)

        acc["rows"] += 1
        if maxflow(cap, src, snk, nn) != total:
            acc["infeas"] += 1
            if acc["first"] is None:
                bad_atoms = [(str(w), ch, g, q, i) for w, ch, g, q, i in atoms if not ch]
                acc["first"] = (name, "".join(map(str, side)), f, len(atoms), comps, bad_atoms[:5])


def bridge(b1, b2, u, v):
    n, edges = union_disjoint(b1, b2)
    n1 = b1[0]
    return n, edges + [(u, n1 + v)]


if __name__ == "__main__":
    print("=== Actual-detour noncontained flow gate ===", flush=True)
    acc = {"rows": 0, "infeas": 0, "first": None}

    for clen in (4, 6):
        for k in (3, 6, 9):
            n, edges = kchord(k, clen)
            adj = [set() for _ in range(n)]
            for a, b in edges:
                adj[a].add(b)
                adj[b].add(a)
            side = [v % 2 for v in range(n)]
            r0, i0 = acc["rows"], acc["infeas"]
            check_cut(n, adj, side, f"k{k}c{clen}", acc)
            print(
                f"  kchord k={k} clen={clen} N={n}: rows={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}",
                flush=True,
            )

    for nn in range(7, 11):
        graph6s = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        r0, i0 = acc["rows"], acc["infeas"]
        for graph6 in graph6s:
            n, edges = dec(graph6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check_cut(n, adj, side, graph6, acc)
        print(f"  census N={nn} gamma-min: rows={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}", flush=True)

    for name, (n, edges) in [("C9|brg|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]:
        adj, cuts = gmins(n, edges)
        r0, i0 = acc["rows"], acc["infeas"]
        for side in cuts:
            check_cut(n, adj, side, name, acc)
        print(f"  {name} N={n}: rows={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}", flush=True)

    print(f"\n  TOTAL rows={acc['rows']} INFEASIBLE={acc['infeas']}", flush=True)
    print(f"  FIRST={acc['first']}", flush=True)
