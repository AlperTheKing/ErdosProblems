"""Depth scaling probe for the Schur Jacobi harvest relaxation.

The finite-depth Jacobi-6 certificate passes the small acceptance battery but
fails on larger nonuniform C5 blowups.  This script measures how the minimum
passing Jacobi depth grows on the canonical family

    sizes = [k+1, k, k+1, k, k+1]
    side pattern by parts = [1, 0, 1, 0, 0].

It also computes the full harmonic harvest margin when requested, confirming
that the target harvest remains true while fixed low depth may fail.
"""

import argparse
from fractions import Fraction as F

from _Rsize_gate import solve_mat
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _hardy_gate import BETA, build_H
from _wf_deficit_farkas import odd_blowup


def canonical_side(sizes):
    pattern = [1, 0, 1, 0, 0]
    side = []
    for bit, size in zip(pattern, sizes):
        side.extend([bit] * size)
    return side


def harmonic_psi(H, U, T, n):
    Huu = [[H[a][b] for b in U] for a in U]
    rhs = [[F(n) - T[u]] for u in U]
    sol = solve_mat(Huu, rhs)
    if sol is None:
        return None
    return {U[i]: sol[i][0] for i in range(len(U))}


def prepare_instance(k):
    sizes = [k + 1, k, k + 1, k, k + 1]
    n, edges = odd_blowup(5, sizes)
    adj = adj_from_edges(n, edges)
    side = canonical_side(sizes)
    st = struct_for_side(n, adj, side)
    if st is None:
        raise RuntimeError(f"struct_for_side failed for k={k}")
    M, ell, T, _mu, cyc = st
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    return sizes, n, side, H, S, T, O, U


def jacobi_margins(H, S, T, O, U, n, max_depth):
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

    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))] if S is not None else [None] * len(O)
    minority = [i for i, ao in enumerate(a) if ao <= A - ao]

    phi = {u: F(0) for u in U}
    out = []
    for depth in range(1, max_depth + 1):
        phi = {
            u: (
                deficit[u] + sum(c * phi[w] for w, c in conduct_U[u].items())
            ) / denom[u]
            if denom[u]
            else F(0)
            for u in U
        }
        min_margin = None
        min_o = None
        for i in minority:
            o = O[i]
            neigh = [u for u in U if -H[o][u] > 0]
            cU = sum(-H[o][u] for u in neigh)
            e = cU - a[i]
            I = sum((-H[o][u]) * phi[u] for u in neigh)
            margin = 25 * (I - a[i]) - 4 * e
            if min_margin is None or margin < min_margin:
                min_margin = margin
                min_o = o
        out.append((depth, min_margin, min_o))

    full = None
    if S is not None:
        full_min = None
        full_o = None
        target_min = None
        target_o = None
        for i in minority:
            o = O[i]
            cU = sum(-H[o][u] for u in U if -H[o][u] > 0)
            e = cU - a[i]
            margin = 25 * rho[i] - 4 * e
            target = 25 * rho[i] - (A - 2 * a[i])
            if full_min is None or margin < full_min:
                full_min = margin
                full_o = o
            if target_min is None or target < target_min:
                target_min = target
                target_o = o
        full = (full_min, full_o, target_min, target_o)

    return out, full, len(minority), len(O)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k-min", type=int, default=4)
    parser.add_argument("--k-max", type=int, default=14)
    parser.add_argument("--depth", type=int, default=80)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    for k in range(args.k_min, args.k_max + 1):
        sizes, n, _side, H, S, T, O, U = prepare_instance(k)
        margins, full, minority_count, O_count = jacobi_margins(
            H, S, T, O, U, n, args.depth
        )
        first_pass = next((d for d, m, _o in margins if m is not None and m >= 0), None)
        d6 = next((m for d, m, _o in margins if d == 6), None)
        dlast, mlast, olast = margins[-1]
        print(
            "k",
            k,
            "N",
            n,
            "sizes",
            sizes,
            "O",
            O_count,
            "minority",
            minority_count,
            "first_pass",
            first_pass,
            "d6",
            float(d6) if d6 is not None else None,
            "dlast",
            dlast,
            float(mlast) if mlast is not None else None,
            "o_last",
            olast,
            flush=True,
        )
        if args.full and full is not None:
            print(
                "  full_harvest",
                float(full[0]),
                "o",
                full[1],
                "exact",
                full[0],
                flush=True,
            )
            print(
                "  direct_target",
                float(full[2]),
                "o",
                full[3],
                "exact",
                full[2],
                flush=True,
            )


if __name__ == "__main__":
    main()
