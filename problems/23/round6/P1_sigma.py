"""The sigma-family of arc-cut bounds  (repairs the refuted item 7).

THEOREM (proved in P1.md, section 3).  Let mu be a probability measure on R/Z, let
sigma be ANY non-atomic probability measure on R/Z, and for an edge e = {x,y} (i.e. a pair
with d(x,y) > 1/3) let  D_sigma(e) = min( sigma(arc_1), sigma(arc_2) ) in [0,1/2] be the
smaller of the sigma-masses of the two arcs bounded by x and y.  Then

        ARCBOUND(mu)  <=  A_sigma(mu) := sum_e w_e (1 - 2 D_sigma(e)),      w_e = x_i x_j,

because A_sigma is the average of genuine arc cuts: take the arc between the sigma-quantiles
t and t+1/2 with t uniform.

    sigma = Lebesgue  gives the old A = W - 2T (item 5 of the chain).
    sigma = mu        gives the new  Atilde = W - 2 * sum_e w_e D_mu(e).
    the best sigma is the optimum of an LP (concave piecewise-linear in sigma).

For an atomic mu with atoms p_0 < ... < p_{n-1} a non-atomic sigma is described, as far as
A_sigma is concerned, by the masses s_i = sigma(gap between p_i and p_{i+1}), s in the simplex;
sigma = mu is the choice s_i = (x_i + x_{i+1})/2.  ANY rational s gives an EXACT rational
certificate, so the LP only has to guess -- the acceptance path stays exact.
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog

from P1_engine import Meas, TARGET, gamma, WITNESSES


def edges(mu):
    return [(i, j) for i in range(mu.n) for j in range(i + 1, mu.n) if mu.adj[i][j]]


def A_sigma(mu, s):
    """exact: s = list of n gap masses (s_i = sigma of the gap (p_i, p_{i+1})), sum 1."""
    assert sum(s) == 1, sum(s)
    n = mu.n
    tot = F(0)
    for i, j in edges(mu):
        Dp = sum(s[k] for k in range(i, j))          # gaps inside the forward arc p_i -> p_j
        D = min(Dp, 1 - Dp)
        tot += mu.wt[i] * mu.wt[j] * (1 - 2 * D)
    return tot


def sigma_mu(mu):
    """the gap vector of sigma = mu (symmetric/quantile convention)"""
    n = mu.n
    return [(mu.wt[i] + mu.wt[(i + 1) % n]) / 2 for i in range(n)]


def sigma_leb(mu):
    """the gap vector of sigma = Lebesgue"""
    n, P = mu.n, mu.pos
    return [(P[(i + 1) % n] - P[i]) % 1 for i in range(n)]


def best_sigma(mu, exact_den=10 ** 6):
    """LP for  max_s sum_e w_e min(S_e, 1-S_e); returns (rational s, exact A_sigma)."""
    n = mu.n
    E = edges(mu)
    ne = len(E)
    if ne == 0:
        s = [F(1, n)] * n
        return s, F(0)
    # variables: s_0..s_{n-1}, t_0..t_{ne-1};  maximise sum w_e t_e
    c = np.zeros(n + ne)
    for k, (i, j) in enumerate(E):
        c[n + k] = -float(mu.wt[i] * mu.wt[j])
    Aub, bub = [], []
    for k, (i, j) in enumerate(E):
        row = np.zeros(n + ne)          # t_e - S_e <= 0
        row[n + k] = 1
        for g in range(i, j):
            row[g] -= 1
        Aub.append(row); bub.append(0.0)
        row = np.zeros(n + ne)          # t_e + S_e <= 1
        row[n + k] = 1
        for g in range(i, j):
            row[g] += 1
        Aub.append(row); bub.append(1.0)
    Aeq = np.zeros((1, n + ne)); Aeq[0, :n] = 1
    r = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=Aeq, b_eq=[1.0],
                bounds=[(0, 1)] * n + [(0, 0.5)] * ne, method='highs')
    s = np.maximum(r.x[:n], 0)
    s = s / s.sum()
    sr = [F(int(round(v * exact_den)), exact_den) for v in s]
    sr[0] += 1 - sum(sr)                                  # exact renormalisation
    if sr[0] < 0:                                         # pathological rounding
        sr = [F(1, n)] * n
    return sr, A_sigma(mu, sr)


def report(tag, mu):
    aL = A_sigma(mu, sigma_leb(mu))
    aM = A_sigma(mu, sigma_mu(mu))
    s, aB = best_sigma(mu)
    arc = mu.arcbound()
    best = min(aL, aM, aB)
    flag = 'OK' if best <= TARGET else '*** EXCEEDS 1/25 ***'
    print(f"{tag:30s} W={float(mu.W):.6f}  A_leb={float(aL):.6f}  A_mu={float(aM):.6f}  "
          f"A_LPsigma={float(aB):.6f}  min={float(best):.6f}  ARC={float(arc):.6f}  {flag}")
    assert aL >= arc and aM >= arc and aB >= arc, (tag, "sigma bound below ARCBOUND!")
    return best, aM, aL, arc


if __name__ == '__main__':
    print("sigma-family bounds on the round-5 witnesses, the two hard cases, and the")
    print("Gamma_20/Wagner witness that refutes item 7\n")
    rows = []
    for name, m, w in WITNESSES:
        rows.append((name, gamma(m, w)))
    rows.append(("CE Wagner on G20 (item-7 killer)",
                 Meas([F(k, 20) for k in (0, 1, 6, 7, 12, 13, 14, 19)], [F(1, 8)] * 8)))
    rows.append(("CE Wagner equally spaced G8", gamma(8, [1] * 8)))
    worst = None
    for tag, mu in rows:
        best, aM, aL, arc = report(tag, mu)
        if worst is None or best > worst[1]:
            worst = (tag, best)
    print(f"\nworst min over the sigma-family: {worst[0]}  {worst[1]} = {float(worst[1]):.6f}"
          f"   (1/25 = 0.04)")
