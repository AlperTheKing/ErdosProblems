"""audit_P3_delta.py -- adversarial audit of P3.md claim (e):
   "max psi over the delta>1/3 polytope P(H) is attained at the paper's regular weight function,
    the maximum over the whole Vega family is 29/841 = 0.0344828 (Grotzsch), so V1' carries a
    uniform 13.8% margin and the Vega graphs are not the hard case."

P3 ran its DELTA engine on the FOUR i=2 graphs only, at denominators 29/58/87/116 (32/64, 35/70).
For i >= 3 only the single point omega_reg was evaluated.  Here I

  1. check that P(H) is full-dimensional (exact Chebyshev radius by LP, then exact rational
     certificate),
  2. maximise psi over P(H) numerically (multi-start projected ascent) for i = 2,3,4 and verify
     every candidate EXACTLY with Fractions,
  3. report whether anything beats psi(omega_reg) and whether anything beats 29/841.
"""
import sys, random
from fractions import Fraction as F
from itertools import combinations
import numpy as np
from audit_P3_core import vega_family, bip_exact

random.seed(20260725)
np.random.seed(20260725)


def setup(name, adj, order):
    n = len(order)
    idx = {t: k for k, t in enumerate(order)}
    E = [(idx[p], idx[q]) for p, q in combinations(order, 2) if q in adj[p]]
    N = np.zeros((n, n))
    for (p, q) in E:
        N[p, q] = N[q, p] = 1.0
    # all cuts with vertex 0 on side 0
    masks = np.arange(1 << (n - 1), dtype=np.int64)
    side = ((masks[:, None] >> np.arange(n - 1)[None, :]) & 1).astype(np.int8)
    side = np.concatenate([np.zeros((side.shape[0], 1), dtype=np.int8), side], axis=1)
    monoidx = []
    for (p, q) in E:
        monoidx.append(side[:, p] == side[:, q])
    monoidx = np.array(monoidx)          # |E| x ncuts boolean
    return n, idx, E, N, monoidx


def psi_num(w, E, monoidx):
    prod = np.array([w[p] * w[q] for (p, q) in E])
    vals = prod @ monoidx
    return vals.min()


def psi_exact(order, adj, wfrac):
    """exact psi for a rational weight vector normalised to sum 1: scale to integers."""
    den = 1
    for v in wfrac.values():
        den = den * v.denominator // np.gcd(den, v.denominator)
    a = {t: int(wfrac[t] * den) for t in order}
    q = sum(a.values())
    return F(bip_exact(order, adj, a), q * q)


def feasible(w, N):
    return (N @ w).min() * 3.0 > 1.0


def chebyshev(n, N):
    """max t s.t. (N w)_v >= 1/3 + t, sum w = 1, w >= 0.  Returns (t*, w*) via scipy."""
    from scipy.optimize import linprog
    # variables (w, t); maximise t
    c = np.zeros(n + 1); c[-1] = -1.0
    A_ub = np.zeros((n, n + 1)); b_ub = np.zeros(n)
    for v in range(n):
        A_ub[v, :n] = -N[v]
        A_ub[v, -1] = 1.0
        b_ub[v] = -1.0 / 3.0
    A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
    b_eq = np.array([1.0])
    bounds = [(0, None)] * n + [(None, None)]
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    return (r.x[-1], r.x[:n]) if r.success else (None, None)


def maximise(name, adj, order, wreg, tries=400, steps=4000):
    n, idx, E, N, monoidx = setup(name, adj, order)
    t, wc = chebyshev(n, N)
    wr = np.array([float(wreg[t_]) for t_ in order]); wr /= wr.sum()
    best = psi_num(wr, E, monoidx); bestw = wr.copy()
    reg = best
    for trial in range(tries):
        if trial == 0:
            w = wr.copy()
        elif trial == 1 and wc is not None:
            w = np.maximum(wc, 0); w /= w.sum()
            if not feasible(w, N):
                w = wr.copy()
        else:
            for _ in range(200):
                w = wr * np.exp(np.random.randn(n) * (0.05 + 0.5 * random.random()))
                w /= w.sum()
                if feasible(w, N):
                    break
            else:
                w = wr.copy()
        cur = psi_num(w, E, monoidx)
        step = 0.05
        for it in range(steps):
            j = random.randrange(n); k = random.randrange(n)
            if j == k:
                continue
            d = step * random.random() * w[j]
            w2 = w.copy(); w2[j] -= d; w2[k] += d
            if w2[j] < 0:
                continue
            if not feasible(w2, N):
                continue
            v2 = psi_num(w2, E, monoidx)
            if v2 > cur:
                w, cur = w2, v2
            if it % 500 == 499:
                step *= 0.6
        if cur > best:
            best, bestw = cur, w.copy()
    return n, t, reg, best, bestw, E, monoidx, N


TARGET = F(29, 841)
print('AUDIT of P3.md claim (e).   1/25 = %.7f   29/841 = %.7f' % (1 / 25, float(TARGET)))
print()
rows = []
for i in (2, 3, 4):
    for (name, adj, order, wreg) in vega_family(i):
        n = len(order)
        if n > 19:
            continue
        n, t, reg, best, bestw, E, monoidx, N = maximise(name, adj, order, wreg,
                                                         tries=120 if n <= 13 else 40,
                                                         steps=3000)
        # exact verification of the numerical champion: round to denominator D and check
        exact_best = None; exact_w = None
        for D in (2520, 27720, 360360):
            a = np.round(bestw * D).astype(np.int64)
            if a.sum() != D:
                a[int(np.argmax(a))] += D - a.sum()
            if (a < 0).any():
                continue
            aa = dict(zip(order, [int(z) for z in a]))
            deg = {v: sum(aa[u] for u in adj[v]) for v in order}
            if min(3 * deg[v] for v in order) <= D:
                continue                      # rounding fell out of the polytope
            val = F(bip_exact(order, adj, aa), D * D)
            if exact_best is None or val > exact_best:
                exact_best, exact_w = val, aa
        wregf = {t_: F(wreg[t_], sum(wreg.values())) for t_ in order}
        exreg = psi_exact(order, adj, wregf)
        rows.append((name, n, t, float(exreg), reg, best, exact_best))
        print('%-11s n=%2d  chebyshev_t=%+.6f | psi(omega_reg)=%-12s=%.7f | '
              'numeric max over P=%.7f | exact-verified point=%s (%.7f)'
              % (name, n, t if t is not None else float('nan'), str(exreg), float(exreg),
                 best, str(exact_best), float(exact_best) if exact_best else float('nan')))
        if exact_best is not None and exact_best > TARGET:
            print('    *** EXACT POINT IN P(H) BEATS 29/841 ***  w =', [exact_w[t_] for t_ in order])
        if best > float(TARGET) + 1e-9:
            print('    *** numeric max exceeds 29/841 by %.3e ***' % (best - float(TARGET)))
        if best > 1 / 25 + 1e-12:
            print('    *** numeric max EXCEEDS 1/25 -- would be an Erdos-23 counterexample ***')
        sys.stdout.flush()
print()
print('summary: numeric max over P(H) vs 29/841 = %.7f' % float(TARGET))
for r in rows:
    print('  %-11s psi_reg=%.7f  numericmax=%.7f  beats29/841=%s  beats1/25=%s'
          % (r[0], r[3], r[5], r[5] > float(TARGET) + 1e-9, r[5] > 1 / 25 + 1e-12))
