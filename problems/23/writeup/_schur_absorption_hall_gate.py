"""Exact gate for a Schur absorption-Hall strengthening.

For H = diag(N-T)+Lstar and O={T>N}, let S be the Schur complement on O.
Write

    a_o = T(o)-N,
    rho_o = sum_j S[o,j],
    b_o = a_o + rho_o.

Using the harmonic-current identity, b_o is the current absorbed at overloaded
terminal o from the underloaded block when all overloaded terminals are held
at potential 1.

Candidate strengthening:

    for every X subset O with a(X) <= A-a(X),  b(X) >= a(X).

The singleton case implies the strict-majority shunt lemma:
rho_o<0 => b_o<a_o, so a_o>A-a_o.
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
from _Rsize_gate import solve_mat


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
        acc["noO"] += 1
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    acc["Ocuts"] += 1
    acc["Ohist"][len(O)] = acc["Ohist"].get(len(O), 0) + 1
    if S is None:
        acc["singular"] += 1
        if acc["first"] is None:
            acc["first"] = ("singular", name, n, "".join(map(str, side)), O)
        return

    a = [T[o] - N for o in O]
    rho = [sum(S[i]) for i in range(len(O))]
    b = [a[i] + rho[i] for i in range(len(O))]
    A = sum(a)

    # singleton majority inclusion, tracked separately.
    R = [i for i, r in enumerate(rho) if r < 0]
    MAJ = [i for i, ai in enumerate(a) if ai > A - ai]
    acc["Rhist"][len(R)] = acc["Rhist"].get(len(R), 0) + 1
    if not set(R) <= set(MAJ):
        acc["R_not_MAJ"] += 1
        if acc["first"] is None:
            acc["first"] = (
                "R_not_MAJ",
                name,
                n,
                "".join(map(str, side)),
                O,
                [str(x) for x in a],
                [str(x) for x in rho],
            )

    m = len(O)
    checked = 0
    for r in range(1, m + 1):
        for X in combinations(range(m), r):
            aset = sum(a[i] for i in X)
            if aset > A - aset:
                continue
            checked += 1
            bset = sum(b[i] for i in X)
            if bset < aset:
                acc["hall_fail"] += 1
                if acc["first"] is None:
                    acc["first"] = (
                        "hall_fail",
                        name,
                        n,
                        "".join(map(str, side)),
                        O,
                        tuple(O[i] for i in X),
                        str(aset),
                        str(bset),
                        [str(x) for x in a],
                        [str(x) for x in b],
                        [str(x) for x in rho],
                    )
                return
    acc["subset_checks"] += checked


def gfam(name, n, E, acc):
    adj = adj_from_edges(n, E)
    try:
        _gamma, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def main():
    acc = dict(
        Ocuts=0,
        noO=0,
        singular=0,
        hall_fail=0,
        R_not_MAJ=0,
        subset_checks=0,
        Ohist={},
        Rhist={},
        first=None,
    )

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print(
            f"census N={nn}: Ocuts={acc['Ocuts']} hall_fail={acc['hall_fail']} R_not_MAJ={acc['R_not_MAJ']}",
            flush=True,
        )

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

    rng = random.Random(113)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        E = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not E or not is_triangle_free(nn, E):
            continue
        adj = adj_from_edges(nn, E)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, E, acc)

    print("=" * 70)
    print("O-cuts:", acc["Ocuts"], "noO:", acc["noO"], "random graphs:", made)
    print("O hist:", dict(sorted(acc["Ohist"].items())))
    print("R hist:", dict(sorted(acc["Rhist"].items())))
    print("subset Hall checks:", acc["subset_checks"])
    print("singular:", acc["singular"])
    print("R_not_MAJ:", acc["R_not_MAJ"])
    print("hall_fail:", acc["hall_fail"])
    print("first:", acc["first"] or "")
    print(
        "VERDICT:",
        "Schur absorption-Hall holds on this battery"
        if acc["hall_fail"] == 0 and acc["R_not_MAJ"] == 0
        else "FAIL",
    )


if __name__ == "__main__":
    main()
