"""Dump the smallest PMS margin row from the N=10 census.

This is an inspection helper for the OC-PMS route.  It records the equality
atom data that `_codex_ocpms_gate.py` reports only as `cen10`.
"""

import subprocess
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_ocpms_gate import kcomp


def scan(g6):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    best = None
    _, cuts = gmins(n, E)
    for side in cuts:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        for f in M:
            L = ell[f]
            for P in cyc[f]:
                R = sum(T[v] for v in P)
                if R <= L * n:
                    continue
                C = kcomp(n, M, cyc, set(P))
                comp_edges = [g for g in M if any(set(Q) <= C for Q in cyc[g])]
                if not (L == 5 and len(C) == n and all(ell[g] == 5 for g in comp_edges)):
                    continue
                Pset = set(P)
                I = sum(
                    F(1, len(cyc[g])) * sum(len(Pset & set(Q)) for Q in cyc[g])
                    for g in M
                )
                Def = n * n - 25 * len(M)
                margin = F(2) * Def - 75 * (I - n)
                rec = (margin, g6, n, tuple(P), f, tuple(M), I, Def, side, E, T, cyc)
                if best is None or margin < best[0]:
                    best = rec
    return best


def main():
    best = None
    for g6 in subprocess.run([GENG, "-tc", "10"], capture_output=True, text=True).stdout.split():
        rec = scan(g6)
        if rec is not None and (best is None or rec[0] < best[0]):
            best = rec
    if best is None:
        print("no overloaded pentagonal rows")
        return
    margin, g6, n, P, f, M, I, Def, side, E, T, cyc = best
    print("margin", margin)
    print("g6", g6)
    print("n", n)
    print("row", P)
    print("bad_edge", f)
    print("M", M, "m", len(M))
    print("I", I, "Def", Def)
    print("side", "".join(map(str, side)))
    print("E", sorted(E))
    print("T", [str(t) for t in T])
    for g in M:
        print("cyc", g, "count", len(cyc[g]), "rows", [tuple(q) for q in cyc[g]])


if __name__ == "__main__":
    main()
