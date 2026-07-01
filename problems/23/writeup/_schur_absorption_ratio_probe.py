"""Mine the best battery coefficient in quantitative Schur Absorption-Hall.

For every checked non-majority subset with positive gap

    gap(X) = A - 2*a(X) > 0,

record the exact ratio

    rho(X) / gap(X).

The coefficient gate with constant c is exactly the assertion

    rho(X) >= c * gap(X).

This probe is diagnostic only; it reports the smallest observed ratio on the
same battery as _schur_absorption_coeff_gate.py.
"""

import random
import subprocess
from itertools import combinations
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    if not O:
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    acc["Ocuts"] += 1
    if S is None:
        acc["singular"] += 1
        return
    a = [T[o] - N for o in O]
    rho = [sum(S[i]) for i in range(len(O))]
    A = sum(a)
    for r in range(1, len(O) + 1):
        for X in combinations(range(len(O)), r):
            ax = sum(a[i] for i in X)
            gap = A - 2 * ax
            if gap <= 0:
                continue
            rhox = sum(rho[i] for i in X)
            ratio = rhox / gap
            acc["checks"] += 1
            if acc["best"] is None or ratio < acc["best"][0]:
                acc["best"] = (
                    ratio,
                    name,
                    n,
                    "".join(map(str, side)),
                    tuple(O[i] for i in X),
                    ax,
                    A,
                    [str(x) for x in a],
                    [str(x) for x in rho],
                )


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def main():
    acc = {"Ocuts": 0, "singular": 0, "checks": 0, "best": None}

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']} checks={acc['checks']}", flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj23 = adj_from_edges(m2N, m2E)
    test_cut("MycGrotzsch_N23", m2N, adj23, maxcut_ls(m2N, adj23), acc)

    for q in range(2, 16):
        n, edges, side = glued_c5_chain(q)
        test_cut(f"chain{q}", n, adj_from_edges(n, edges), side, acc)

    for sizes in [
        (2, 1, 2, 1, 2),
        (2, 1, 2, 1, 3),
        (3, 2, 3, 2, 3),
        (4, 3, 4, 3, 4),
        (5, 4, 5, 4, 5),
        (2, 2, 2, 2, 2),
        (3, 3, 3, 3, 3),
    ]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 24:
            gfam(f"blow{sizes}", n, edges, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(island, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    gfam("island", n, edges, acc)

    rng = random.Random(619)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        edges = [(a0, b0) for a0 in range(nn) for b0 in range(a0 + 1, nn) if rng.random() < p]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, acc)

    print("=" * 72)
    print("Ocuts", acc["Ocuts"], "positive-gap checks", acc["checks"], "singular", acc["singular"], "random", made)
    if acc["best"] is not None:
        ratio, name, n, side, X, ax, A, avec, rvec = acc["best"]
        print("min_ratio", str(ratio), "float", float(ratio))
        print("min_case", name, n, side, "X", X, "aX", str(ax), "A", str(A))
        print("a", avec)
        print("rho", rvec)


if __name__ == "__main__":
    main()
