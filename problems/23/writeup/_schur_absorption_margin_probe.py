"""Exact diagnostic for near-tight Schur absorption-Hall subsets.

This is not an acceptance gate.  It reuses the current Hardy/Schur objects and
records the smallest margins

    b(X) - a(X)

among subsets with a(X) <= A-a(X).
"""

import subprocess
from itertools import combinations
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def consider(name, n, adj, side, best):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    if not O:
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    if S is None:
        return
    a = [T[o] - N for o in O]
    rho = [sum(S[i]) for i in range(len(O))]
    b = [a[i] + rho[i] for i in range(len(O))]
    A = sum(a)
    for r in range(1, len(O) + 1):
        for X in combinations(range(len(O)), r):
            ax = sum(a[i] for i in X)
            if ax > A - ax:
                continue
            bx = sum(b[i] for i in X)
            margin = bx - ax
            record = (
                margin,
                name,
                n,
                "".join(map(str, side)),
                tuple(O[i] for i in X),
                str(ax),
                str(A),
                [str(x) for x in a],
                [str(x) for x in b],
                [str(x) for x in rho],
            )
            best.append(record)
            best.sort(key=lambda z: z[0])
            del best[12:]


def gfam(name, n, E, best):
    adj = adj_from_edges(n, E)
    try:
        _gamma, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        consider(name, n, adj, side, best)


def main():
    best = []
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, best)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, best)
    m2N, m2E = mycielski(grN, grE)
    adj23 = adj_from_edges(m2N, m2E)
    consider("MycGrotzsch_N23", m2N, adj23, maxcut_ls(m2N, adj23), best)

    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        consider(f"chain{q}", n, adj_from_edges(n, E), side, best)

    for sizes in [
        (2, 1, 2, 1, 2),
        (2, 1, 2, 1, 3),
        (3, 2, 3, 2, 3),
        (4, 3, 4, 3, 4),
        (5, 4, 5, 4, 5),
        (2, 2, 2, 2, 2),
        (3, 3, 3, 3, 3),
    ]:
        n, E = odd_blowup(5, list(sizes))
        if n <= 24:
            gfam(f"blow{sizes}", n, E, best)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(island, g15)
    n, E = add_edges((n, E), [(0, 5)])
    gfam("island", n, E, best)

    print("closest absorption-Hall margins")
    for rec in best:
        margin, name, n, side, X, ax, A, a, b, rho = rec
        print("-" * 72)
        print("margin", margin, "float", float(margin))
        print("case", name, "n", n, "side", side, "X", X, "aX", ax, "A", A)
        print("a", a)
        print("b", b)
        print("rho", rho)


if __name__ == "__main__":
    main()
