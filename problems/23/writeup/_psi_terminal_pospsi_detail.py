"""Drill into the POSITIVE-Psi gated switches at N=9 (the meaningful descent cases) and
reconcile Psi(W) with -phi^T H phi for the matching level-set phi.

For each gated neutral switch W with Psi(W)>0 we print:
  Psi(W), dG=Gamma(after)-Gamma(before), slack=-Psi-dG (>=0 needed),
  and the indicator phi = 1_W (level-set indicator) evaluated phi^T H phi using build_H.
This checks the descent-estimate angle: the claim there was
  Gamma(after)-Gamma(before) <= phi^T H phi   (coarea/Dirichlet),
and the combinatorial form predicts -Psi(W). We compare phi^T H phi to -Psi(W) and to dG.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _hardy_gate import build_H, BETA
from _psi_terminal_descent_gate import (
    adj_from_edges, gamma_of, flip, delta_neutral, psi_and_gate,
)


def phiHphi_indicator(n, adj, side, W):
    """phi = indicator of W (as +/-? ). The descent-estimate uses harmonic extension;
       here we just report 1_W^T H 1_W as a coarse comparison."""
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    H = build_H(n, M, ell, T, cyc, BETA)
    phi = [F(1) if v in set(W) else F(0) for v in range(n)]
    s = F(0)
    for i in range(n):
        if phi[i] == 0:
            continue
        for j in range(n):
            if phi[j] == 0:
                continue
            s += phi[i] * H[i][j] * phi[j]
    return s


def main():
    print("=== POSITIVE-Psi gated neutral switches at N=9 (detail) ===")
    cnt = 0
    shown = 0
    nonzero_dg = 0
    for g6 in subprocess.run([GENG, "-tc", "9"], capture_output=True, text=True).stdout.split():
        n, edges = dec(g6)
        adj = adj_from_edges(n, edges)
        for side in maxcut_all(n, adj):
            if not Bconn(n, adj, side):
                continue
            gamma0 = gamma_of(n, adj, side)
            if gamma0 is None or gamma0 == 0:
                continue
            for mask in range(1, 1 << n):
                W = [v for v in range(n) if (mask >> v) & 1]
                if delta_neutral(n, adj, side, W) != 0:
                    continue
                side2 = flip(side, W)
                g1 = gamma_of(n, adj, side2)
                if g1 is None:
                    continue
                res = psi_and_gate(n, adj, side, W)
                if res is None or not res['ok']:
                    continue
                Psi = res['Psi']
                if Psi <= 0:
                    continue
                cnt += 1
                dG = g1 - gamma0
                if dG != 0:
                    nonzero_dg += 1
                slack = -Psi - dG
                ph = phiHphi_indicator(n, adj, side, W)
                if shown < 20:
                    shown += 1
                    print("  %s side=%s W=%-14s Psi=%s dG=%s slack=%s  1_W^THH1_W=%s  (-Psi=%s)"
                          % (g6, ''.join(map(str, side)), str(tuple(W)),
                             Psi, dG, slack, ph, -Psi))
    print("-" * 72)
    print("total positive-Psi gated switches at N=9:", cnt)
    print("of which dG != 0 (Gamma actually changed):", nonzero_dg)


if __name__ == "__main__":
    main()
