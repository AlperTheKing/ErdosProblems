"""Exact gate for the finite-depth Schur Jacobi harvest certificate.

For a gamma-minimal connected-B maximum cut, build

    H = diag(N - T) + Lstar.

Let O={v:T(v)>N}, U=V\\O.  On U define Jacobi lower iterates

    phi_0(u) = 0
    phi_{k+1}(u) =
        (N-T(u) + sum_{w in U, w!=u} c_uw phi_k(w)) / D_u,

where c_uv=max(0,-H[u][v]) and

    D_u = N-T(u) + sum_{w in U,w!=u} c_uw + sum_{p in O} c_up.

The gate checks, for every minority overloaded o,

    25 * (I_k(o) - a_o) >= 4 * (cU_o - a_o),

where I_k(o)=sum_u c_ou phi_k(u), a_o=T(o)-N, and
cU_o=sum_u c_ou.

All arithmetic is exact Fraction arithmetic.  This is a computational gate,
not a proof.
"""

import argparse
import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _Rsize_gate import solve_mat
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def frac_float(x):
    return float(x) if x is not None else None


def harmonic_psi(H, O, U, T, n):
    Huu = [[H[a][b] for b in U] for a in U]
    rhs = [[F(n) - T[u]] for u in U]
    sol = solve_mat(Huu, rhs)
    if sol is None:
        return None
    return {U[i]: sol[i][0] for i in range(len(U))}


def push_min(items, key, rec, limit=10):
    items.append((key, rec))
    items.sort(key=lambda x: x[0])
    del items[limit:]


def jacobi_iterates(H, O, U, T, n, steps):
    N = F(n)
    conduct_U = {
        u: {w: -H[u][w] for w in U if w != u and -H[u][w] > 0}
        for u in U
    }
    denom = {}
    deficit = {}
    for u in U:
        deficit[u] = N - T[u]
        cO = sum(-H[u][oo] for oo in O if -H[u][oo] > 0)
        cUU = sum(conduct_U[u].values())
        denom[u] = deficit[u] + cO + cUU

    phi = {u: F(0) for u in U}
    for _ in range(steps):
        phi = {
            u: (
                deficit[u] + sum(c * phi[w] for w, c in conduct_U[u].items())
            ) / denom[u]
            if denom[u]
            else F(0)
            for u in U
        }
    return phi


def test_cut(name, n, adj, side, steps, acc):
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
    psi = harmonic_psi(H, O, U, T, n)
    acc["Ocuts"] += 1
    if S is None or psi is None:
        acc["singular"] += 1
        return

    phi = jacobi_iterates(H, O, U, T, n, steps)
    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    side_s = "".join(map(str, side))

    for i, o in enumerate(O):
        if a[i] > A - a[i]:
            acc["majority"] += 1
            continue
        acc["minority"] += 1
        neigh = [u for u in U if -H[o][u] > 0]
        cU = sum(-H[o][u] for u in neigh)
        e = cU - a[i]
        I_exact = sum((-H[o][u]) * psi[u] for u in neigh)
        I_step = sum((-H[o][u]) * phi[u] for u in neigh)
        margin = 25 * (I_step - a[i]) - 4 * e
        harvest_margin = 25 * rho[i] - 4 * e
        rec = {
            "name": name,
            "n": n,
            "side": side_s,
            "o": o,
            "O": tuple(O),
            "a": a[i],
            "A": A,
            "rho": rho[i],
            "cU": cU,
            "e": e,
            "I_step": I_step,
            "I_exact": I_exact,
            "margin": margin,
            "harvest_margin": harvest_margin,
        }
        push_min(acc["weak"], margin, rec)
        if margin < 0:
            acc["fail"].append(rec)


def gfam(name, n, edges, steps, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, steps, acc)


def fmt_rec(rec):
    return {
        "name": rec["name"],
        "n": rec["n"],
        "side": rec["side"],
        "o": rec["o"],
        "O": rec["O"],
        "a": frac_float(rec["a"]),
        "A": frac_float(rec["A"]),
        "rho": frac_float(rec["rho"]),
        "cU": frac_float(rec["cU"]),
        "e": frac_float(rec["e"]),
        "I_step": frac_float(rec["I_step"]),
        "I_exact": frac_float(rec["I_exact"]),
        "margin": frac_float(rec["margin"]),
        "harvest_margin": frac_float(rec["harvest_margin"]),
    }


def run_battery(args):
    acc = {
        "Ocuts": 0,
        "singular": 0,
        "minority": 0,
        "majority": 0,
        "fail": [],
        "weak": [],
    }

    for nn in range(args.min_n, args.max_n + 1):
        g6s = subprocess.run(
            [GENG, "-tc", str(nn)], capture_output=True, text=True
        ).stdout.split()
        for g6 in g6s[:: args.census_stride]:
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, args.steps, acc)
        print(
            f"census N={nn}: Ocuts={acc['Ocuts']} minority={acc['minority']}",
            flush=True,
        )

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, args.steps, acc)
    m2N, m2E = mycielski(grN, grE)
    adj23 = adj_from_edges(m2N, m2E)
    test_cut(
        "MycGrotzsch_N23",
        m2N,
        adj23,
        maxcut_ls(m2N, adj23),
        args.steps,
        acc,
    )

    for q in range(2, 16):
        n, edges, side = glued_c5_chain(q)
        test_cut(f"chain{q}", n, adj_from_edges(n, edges), side, args.steps, acc)

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
            gfam(f"blow{sizes}", n, edges, args.steps, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(island, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    gfam("island", n, edges, args.steps, acc)

    rng = random.Random(args.seed)
    made = 0
    tries = 0
    while made < args.random and tries < args.random * 400:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        edges = [
            (a, b)
            for a in range(nn)
            for b in range(a + 1, nn)
            if rng.random() < p
        ]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, args.steps, acc)

    print("=" * 72)
    print(
        "steps",
        args.steps,
        "Ocuts",
        acc["Ocuts"],
        "singular",
        acc["singular"],
        "random",
        made,
    )
    print("minority", acc["minority"], "majority", acc["majority"])
    print("fail", len(acc["fail"]))
    if acc["weak"]:
        val, rec = acc["weak"][0]
        print("min_margin", val, "float", float(val))
        print("min_record", fmt_rec(rec))
    if acc["fail"]:
        print("first_fail", fmt_rec(acc["fail"][0]))
    return acc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--census-stride", type=int, default=1)
    parser.add_argument("--random", type=int, default=120)
    parser.add_argument("--seed", type=int, default=917)
    return parser.parse_args()


if __name__ == "__main__":
    run_battery(parse_args())
