"""Hard h_blowup(3) Schur-failure side: compare rho with neutral flips."""

from fractions import Fraction as F

from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, gamma_of
from _hardy_gate import BETA, build_H
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import schur_on_O


def degs(adj, side):
    blue = [0] * len(adj)
    bad = [0] * len(adj)
    for u in range(len(adj)):
        for v in adj[u]:
            if side[u] == side[v]:
                bad[u] += 1
            else:
                blue[u] += 1
    return blue, bad


def main():
    n, edges, _ = h_blowup(3)
    adj = adj_from_edges(n, edges)
    side = [int(c) for c in "111111111111111100000000000"]
    M, ell, T, _mu, cyc = struct_for_side(n, adj, side)
    H = build_H(n, M, ell, T, cyc, BETA)
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    S = schur_on_O(H, O, U)
    rho = [sum(S[i]) for i in range(len(O))]
    blue, bad = degs(adj, side)
    G0 = gamma_of(n, adj, side)
    print("Gamma", G0, "O", O)
    print("v T-N rho blue bad neutral DeltaGamma")
    for i, o in enumerate(O):
        flipped = side[:]
        flipped[o] ^= 1
        G1 = gamma_of(n, adj, flipped)
        dG = None if G1 is None else G1 - G0
        print(o, T[o] - N, rho[i], blue[o], bad[o], blue[o] == bad[o], dG)


if __name__ == "__main__":
    main()
