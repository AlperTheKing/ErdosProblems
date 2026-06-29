"""Exact-gate spare strengthenings of the noncontained-capacity lemma.

For a unique row f with path P and interval I, let D_noncont(I) be the demand
coming from bad rows g!=f with no shortest geodesic wholly contained in P.
Let cap(I) be the total size of off-path B-components whose span intersects I.

Probe:
    D_noncont(I) > 0  ==>  D_noncont(I) + 1 <= cap(I).

Stronger probe, suggested by the local equality class:
    D_noncont(I) > 0  ==>  D_noncont(I) + (|P_f|-4) <= cap(I).

This is stronger than _noncont_cap_gate.py and is intended as a falsification
gate for the possible endpoint/root spare unit in Part A.  Here |P_f| is the
number of vertices in the unique shortest B-geodesic for f, equal to ell(f).
"""

import subprocess
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski, union_disjoint
from _noncont_cap_gate import kchord


def check_cut(n, adj, side, name, acc):
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    bad_edges, _ell, _T, _mu, cyc = st
    pf = {}
    for g in bad_edges:
        paths = cyc[g]
        weight = F(1, len(paths))
        data = {}
        for path in paths:
            for v in path:
                data[v] = data.get(v, F(0)) + weight
        pf[g] = data

    for f in bad_edges:
        if len(cyc[f]) != 1:
            continue
        path_f = cyc[f][0]
        pset = set(path_f)
        pos = {v: i for i, v in enumerate(path_f)}
        L = len(path_f)

        nc_at = [F(0)] * L
        for g in bad_edges:
            if g == f:
                continue
            if any(set(path) <= pset for path in cyc[g]):
                continue
            for v, mass in pf[g].items():
                if v in pset:
                    nc_at[pos[v]] += mass

        rest = [v for v in range(n) if v not in pset]
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

        comps = {}
        for v in rest:
            comps.setdefault(find(v), set()).add(v)

        spans = []
        for comp in comps.values():
            attach = {pos[x] for u in comp for x in adj[u] if x in pset and side[u] != side[x]}
            if attach:
                spans.append((min(attach), max(attach), len(comp), tuple(sorted(comp))))

        for a in range(L):
            total = F(0)
            for b in range(a, L):
                total += nc_at[b]
                if total == 0:
                    continue
                cap = sum(size for lo, hi, size, _comp in spans if not (hi < a or lo > b))
                slack = F(cap) - total
                length_slack = slack - (L - 4)
                acc["tested"] += 1
                if acc["min"] is None or slack < acc["min"][0]:
                    acc["min"] = (slack, name, "".join(map(str, side)), f, (a, b), str(total), cap)
                if acc["length_min"] is None or length_slack < acc["length_min"][0]:
                    acc["length_min"] = (
                        length_slack,
                        name,
                        "".join(map(str, side)),
                        f,
                        L,
                        (a, b),
                        str(total),
                        cap,
                    )
                if total + 1 > cap:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = (name, "".join(map(str, side)), f, (a, b), str(total), cap, spans)
                if total + (L - 4) > cap:
                    acc["length_viol"] += 1
                    if acc["length_first"] is None:
                        acc["length_first"] = (
                            name,
                            "".join(map(str, side)),
                            f,
                            L,
                            (a, b),
                            str(total),
                            cap,
                            spans,
                        )


def bridge(b1, b2, u, v):
    n, edges = union_disjoint(b1, b2)
    n1 = b1[0]
    return n, edges + [(u, n1 + v)]


if __name__ == "__main__":
    print("=== Noncontained spare gates ===", flush=True)
    print("  spare-unit: D_noncont>0 => D_noncont+1 <= cap", flush=True)
    print("  length-sensitive: D_noncont>0 => D_noncont+(|P_f|-4) <= cap", flush=True)
    acc = {
        "tested": 0,
        "viol": 0,
        "first": None,
        "min": None,
        "length_viol": 0,
        "length_first": None,
        "length_min": None,
    }

    for clen in (4, 6):
        for k in (3, 6, 9):
            n, edges = kchord(k, clen)
            adj = [set() for _ in range(n)]
            for a, b in edges:
                adj[a].add(b)
                adj[b].add(a)
            side = [v % 2 for v in range(n)]
            t0, v0, lv0 = acc["tested"], acc["viol"], acc["length_viol"]
            check_cut(n, adj, side, f"k{k}c{clen}-parity", acc)
            print(
                "  kchord k={} clen={} N={}: tested={} VIOL={} LEN_VIOL={}".format(
                    k,
                    clen,
                    n,
                    acc["tested"] - t0,
                    acc["viol"] - v0,
                    acc["length_viol"] - lv0,
                ),
                flush=True,
            )

    for nn in range(7, 12):
        graph6s = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        t0, v0, lv0 = acc["tested"], acc["viol"], acc["length_viol"]
        for graph6 in graph6s:
            n, edges = dec(graph6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check_cut(n, adj, side, graph6, acc)
        print(
            f"  census N={nn} gamma-min: tested={acc['tested']-t0} VIOL={acc['viol']-v0} LEN_VIOL={acc['length_viol']-lv0}",
            flush=True,
        )

    for name, (n, edges) in [
        ("C7|brg|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C9|brg|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
    ]:
        adj, cuts = gmins(n, edges)
        t0, v0, lv0 = acc["tested"], acc["viol"], acc["length_viol"]
        for side in cuts:
            check_cut(n, adj, side, name, acc)
        print(
            f"  {name} N={n}: tested={acc['tested']-t0} VIOL={acc['viol']-v0} LEN_VIOL={acc['length_viol']-lv0}",
            flush=True,
        )

    print(f"\n  TOTAL tested={acc['tested']} VIOL={acc['viol']} LEN_VIOL={acc['length_viol']}", flush=True)
    print(f"  MIN={acc['min']}", flush=True)
    print(f"  LENGTH_MIN={acc['length_min']}", flush=True)
    print(f"  FIRST={acc['first']}", flush=True)
    print(f"  LENGTH_FIRST={acc['length_first']}", flush=True)
