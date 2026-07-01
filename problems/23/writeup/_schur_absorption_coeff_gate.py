"""Exact gate for a quantitative Schur Absorption-Hall strengthening.

Bare Absorption-Hall:

    a(X) <= A-a(X)  ==>  rho(X) >= 0.

This gate tests the natural 25-normalized strengthening

    a(X) <= A-a(X)  ==>  rho(X) >= (A-2a(X))/25.

The coefficient 1/25 is suggested by the singleton diagnostics and by the
global Erdős constant.  A failure would keep bare AH alive but kill this
proof-friendly quantitative route.
"""

import random
import sys
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
from _Rsize_gate import solve_mat


def parse_coeff():
    if len(sys.argv) <= 1:
        return F(1, 25)
    raw = sys.argv[1]
    if "/" in raw:
        p, q = raw.split("/", 1)
        return F(int(p), int(q))
    return F(raw)


COEFF = parse_coeff()


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def schur_on_O(H, O, U):
    if not O:
        return []
    Huu = [[H[a][b] for b in U] for a in U]
    Huo = [[H[a][b] for b in O] for a in U]
    Hoo = [[H[a][b] for b in O] for a in O]
    Hou = [[H[a][b] for b in U] for a in O]
    X = solve_mat(Huu, Huo)
    if X is None:
        return None
    return [
        [Hoo[i][j] - sum(Hou[i][t] * X[t][j] for t in range(len(U))) for j in range(len(O))]
        for i in range(len(O))
    ]


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
    acc["Ohist"][len(O)] = acc["Ohist"].get(len(O), 0) + 1
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
            if gap < 0:
                continue
            rhox = sum(rho[i] for i in X)
            margin = rhox - COEFF * gap
            acc["checks"] += 1
            if acc["min_margin"] is None or margin < acc["min_margin"][0]:
                acc["min_margin"] = (
                    margin,
                    name,
                    n,
                    "".join(map(str, side)),
                    tuple(O[i] for i in X),
                    ax,
                    A,
                    [str(x) for x in a],
                    [str(x) for x in rho],
                )
            if margin < 0:
                acc["fail"] += 1
                if acc["first"] is None:
                    acc["first"] = acc["min_margin"]
                return


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def main():
    acc = dict(Ocuts=0, singular=0, checks=0, fail=0, first=None, min_margin=None, Ohist={})

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']} checks={acc['checks']} fail={acc['fail']}", flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj23 = adj_from_edges(m2N, m2E)
    test_cut("MycGrotzsch_N23", m2N, adj23, maxcut_ls(m2N, adj23), acc)

    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        test_cut(f"chain{q}", n, adj_from_edges(n, E), side, acc)

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
            gfam(f"blow{sizes}", n, E, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(island, g15)
    n, E = add_edges((n, E), [(0, 5)])
    gfam("island", n, E, acc)

    rng = random.Random(619)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        E = [(a0, b0) for a0 in range(nn) for b0 in range(a0 + 1, nn) if rng.random() < p]
        if not E or not is_triangle_free(nn, E):
            continue
        adj = adj_from_edges(nn, E)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, E, acc)

    print("=" * 72)
    print("coefficient", COEFF)
    print("Ocuts", acc["Ocuts"], "checks", acc["checks"], "singular", acc["singular"], "random", made)
    print("Ohist", dict(sorted(acc["Ohist"].items())))
    print("fail", acc["fail"], "first", acc["first"] or "")
    if acc["min_margin"] is not None:
        margin, name, n, side, X, ax, A, avec, rvec = acc["min_margin"]
        print("min_margin", str(margin), "float", float(margin))
        print("min_case", name, n, side, "X", X, "aX", str(ax), "A", str(A))
        print("a", avec)
        print("rho", rvec)
    print("VERDICT", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
