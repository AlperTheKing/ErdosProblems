"""Probe level-set witnesses for the hard h_blowup(3) Schur failure.

The hard side is a connected-B maximum cut but not Gamma-minimal.  This probe
uses it as a microscope: if Schur absorption-Hall fails for a subset X, do
simple harmonic level sets W = X union {u in U : h_u > t} expose a negative
Hardy set energy 1_W^T H 1_W?
"""

from itertools import combinations
from fractions import Fraction as F

from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _hardy_gate import BETA, build_H
from _Rsize_gate import solve_mat
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import schur_on_O


def qform(H, W):
    W = list(W)
    return sum(H[i][j] for i in W for j in W)


def main():
    n, edges, _inherited = h_blowup(3)
    adj = adj_from_edges(n, edges)
    side = [int(c) for c in "111111111111111100000000000"]
    M, ell, T, _mu, cyc = struct_for_side(n, adj, side)
    H = build_H(n, M, ell, T, cyc, BETA)
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    S = schur_on_O(H, O, U)
    a = [T[o] - N for o in O]
    rho = [sum(S[i]) for i in range(len(O))]
    A = sum(a)

    Huu = [[H[u][v] for v in U] for u in U]
    rhs = [[-sum(H[u][o] for o in O)] for u in U]
    sol = solve_mat(Huu, rhs)
    hU = [row[0] for row in sol]
    thresholds = sorted(set(hU + [F(0), F(1)]))

    print("hard-H3 O", O)
    print("a", [str(x) for x in a])
    print("rho", [str(x) for x in rho])
    print("hU min/max", min(hU), max(hU), "thresholds", len(thresholds))
    best = None
    for r in range(1, len(O) + 1):
        for Xidx in combinations(range(len(O)), r):
            ax = sum(a[i] for i in Xidx)
            if ax > A - ax:
                continue
            rhox = sum(rho[i] for i in Xidx)
            if rhox >= 0:
                continue
            X = {O[i] for i in Xidx}
            for t in thresholds:
                W = set(X)
                W.update(u for u, hu in zip(U, hU) if hu > t)
                val = qform(H, W)
                rec = (val, tuple(sorted(X)), str(ax), str(rhox), str(t), len(W))
                if best is None or val < best[0]:
                    best = rec
    print("best negative-level candidate:", best)

    # Also test the all-O superlevel sets for comparison.
    best_all = None
    for t in thresholds:
        W = set(O)
        W.update(u for u, hu in zip(U, hU) if hu > t)
        val = qform(H, W)
        rec = (val, str(t), len(W))
        if best_all is None or val < best_all[0]:
            best_all = rec
    print("best all-O level candidate:", best_all)


if __name__ == "__main__":
    main()
