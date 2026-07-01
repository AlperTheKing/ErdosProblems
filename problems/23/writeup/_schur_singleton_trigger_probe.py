"""Exact diagnostics for the singleton Schur trigger.

Live proof target:

    rho_o < 0  ==>  a_o > A/2,

where O={T>N}, a_o=T(o)-N, A=sum_O a_o, S is the Schur complement of
H=diag(N-T)+Lstar onto O, rho_o=sum_j S_oj, and b_o=a_o+rho_o.

This probe looks for stronger pointwise fingerprints:

* minority ratio min b_o/a_o for a_o <= A/2;
* minority shunt min rho_o/(A-2a_o);
* relation with Schur conductance boundary c(o,O\\o);
* raw Hardy diagonal H_oo and Schur diagonal S_oo.

Everything is exact Fraction; floats are printed only as diagnostics.
"""

import random
import subprocess
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


def maybe_min(acc, key, value, rec):
    if value is None:
        return
    if acc[key] is None or value < acc[key][0]:
        acc[key] = (value, rec)


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
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    b = [a[i] + rho[i] for i in range(len(O))]
    R = [i for i, r in enumerate(rho) if r < 0]
    acc["Rhist"][len(R)] = acc["Rhist"].get(len(R), 0) + 1

    for i, o in enumerate(O):
        c_boundary = sum(-S[i][j] for j in range(len(O)) if j != i)
        rec = {
            "name": name,
            "n": n,
            "side": "".join(map(str, side)),
            "o": o,
            "O": tuple(O),
            "a": a[i],
            "A": A,
            "rho": rho[i],
            "b": b[i],
            "Hdiag": H[o][o],
            "Sdiag": S[i][i],
            "c_boundary": c_boundary,
        }
        if a[i] <= A - a[i]:
            acc["minority_vertices"] += 1
            maybe_min(acc, "min_b_over_a", b[i] / a[i], rec)
            gap = A - 2 * a[i]
            if gap > 0:
                maybe_min(acc, "min_rho_over_gap", rho[i] / gap, rec)
            maybe_min(acc, "min_rho_minority", rho[i], rec)
            # Conductance-normalized shunt: is rho bounded below by a fraction of
            # the Schur conductance from o to other overloaded terminals?
            if c_boundary > 0:
                maybe_min(acc, "min_rho_over_c", rho[i] / c_boundary, rec)
        else:
            acc["majority_vertices"] += 1
            maybe_min(acc, "min_majority_rho", rho[i], rec)


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def print_min(label, item):
    if item is None:
        print(label, "None")
        return
    value, rec = item
    print(label, str(value), "float", float(value))
    print("  rec", {k: (str(v) if isinstance(v, F) else v) for k, v in rec.items()})


def main():
    acc = dict(
        Ocuts=0,
        singular=0,
        minority_vertices=0,
        majority_vertices=0,
        Rhist={},
        min_b_over_a=None,
        min_rho_over_gap=None,
        min_rho_minority=None,
        min_rho_over_c=None,
        min_majority_rho=None,
    )

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']} Rhist={dict(sorted(acc['Rhist'].items()))}", flush=True)

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

    rng = random.Random(907)
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
    print("Ocuts", acc["Ocuts"], "singular", acc["singular"], "random", made)
    print("Rhist", dict(sorted(acc["Rhist"].items())))
    print("minority_vertices", acc["minority_vertices"], "majority_vertices", acc["majority_vertices"])
    print_min("min minority b/a", acc["min_b_over_a"])
    print_min("min minority rho/(A-2a)", acc["min_rho_over_gap"])
    print_min("min minority rho", acc["min_rho_minority"])
    print_min("min minority rho/c_boundary", acc["min_rho_over_c"])
    print_min("min majority rho", acc["min_majority_rho"])


if __name__ == "__main__":
    main()
