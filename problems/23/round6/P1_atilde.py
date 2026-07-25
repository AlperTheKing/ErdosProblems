"""Candidate combined statement:

    (P)  mu pentagonal      ==>  ARCBOUND <= 1/25            [PROVED, pentagon lemma]
    (Q)  mu not pentagonal  ==>  Atilde   <= 1/25            [candidate, tested here]

Atilde = A_sigma for sigma = mu = W - 2 sum_e w_e D_mu(e), the mass-coordinate half-arc average
(Theorem 1 of P1.md), which is a proved upper bound for ARCBOUND for EVERY measure.
Together (P) and (Q) would close the arc-cut conjecture.

This script hill-climbs Atilde over the simplex of Gamma_q, keeping only non-pentagonal
supports, and re-checks every candidate exactly.
"""
import sys
from fractions import Fraction as F
import numpy as np

from P1_engine import Meas, TARGET, gamma, WITNESSES
from P1_pentagon import is_pentagonal
from P1_sigma import A_sigma, sigma_mu

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 3)


def atilde_float(pos, x, adj):
    """W - 2 sum_e w_e D_mu(e), floats; pos sorted, x weights, adj boolean matrix"""
    n = len(x)
    csum = np.concatenate([[0.0], np.cumsum(x)])
    tot = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                continue
            S = (csum[j] - csum[i]) - x[i] / 2 - x[j] / 2 + x[i] / 2 + x[j] / 2
            # mass strictly between + half of each endpoint:
            S = (csum[j] - csum[i + 1]) + x[i] / 2 + x[j] / 2
            D = min(S, 1 - S)
            tot += x[i] * x[j] * (1 - 2 * D)
    return tot


def climb(q, size, iters=800):
    sup = sorted(rng.choice(q, size=size, replace=False).tolist())
    mu0 = Meas([F(k, q) for k in sup], [F(1, size)] * size)
    if is_pentagonal(mu0):
        return None
    adj = mu0.adj
    pos = np.array([k / q for k in sup])
    x = rng.random(size) + 0.4
    x /= x.sum()
    cur = atilde_float(pos, x, adj)
    step = 0.08
    for it in range(iters):
        i, j = rng.choice(size, size=2, replace=False)
        d = step * rng.random() * min(x[i], 0.5)
        y = x.copy()
        y[i] -= d
        y[j] += d
        v = atilde_float(pos, y, adj)
        if v > cur:
            x, cur = y, v
        if it % 200 == 199:
            step *= 0.6
    return cur, q, sup, x


if __name__ == '__main__':
    print("witness table first (Atilde vs 1/25, and pentagonality):")
    rows = [(nm, gamma(m, w)) for nm, m, w in WITNESSES]
    rows.append(("CE Wagner G20 (item-7 killer)",
                 Meas([F(k, 20) for k in (0, 1, 6, 7, 12, 13, 14, 19)], [F(1, 8)] * 8)))
    for nm, mu in rows:
        at = A_sigma(mu, sigma_mu(mu))
        pen = is_pentagonal(mu)
        flag = '' if at <= TARGET else '   <-- Atilde > 1/25'
        print(f"  {nm:32s} pentagonal={str(pen):5s} Atilde={float(at):.6f} "
              f"ARC={float(mu.arcbound()):.6f}{flag}")

    print("\nhill-climbing Atilde over NON-pentagonal supports "
          "(a value > 0.04 would refute the candidate):")
    best = (-1, None)
    for q in (8, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26):
        for size in range(5, min(q, 11) + 1):
            for _ in range(25):
                r = climb(q, size)
                if r is None:
                    continue
                v, qq, sup, x = r
                if v > best[0]:
                    best = (v, qq, sup, x)
    v, q, sup, x = best
    keep = [k for k in range(len(sup)) if x[k] > 1e-9]
    mu = Meas([F(sup[k], q) for k in keep],
              [F(int(round(x[k] * 10 ** 9)), 10 ** 9) for k in keep])
    at = A_sigma(mu, sigma_mu(mu))
    print(f"\n  best float Atilde on a non-pentagonal support: {v:.6f}")
    print(f"  q={q} sup={sup} weights={[round(float(t),5) for t in x]}")
    print(f"  exact at the rationalised point: Atilde={at}={float(at):.6f}  "
          f"pentagonal={is_pentagonal(mu)}  ARCBOUND={float(mu.arcbound()):.6f}")
    print(f"  {'CANDIDATE SURVIVES (<= 1/25)' if at <= TARGET else '*** CANDIDATE REFUTED ***'}")
