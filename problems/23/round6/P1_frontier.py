"""Calibration of what is left after the pentagon lemma.

(a) EQUALITY CASE: a balanced blow-up of C5 is pentagonal with q_i = 1/5 and has
    ARCBOUND = 1/25 exactly -- the lemma is tight exactly there.
(b) The residual class ("positive-weight support not pentagonal") is NOT bounded away from
    1/25: put weight eps on the atoms that break pentagonality and the measure is a C5 in
    disguise.  Explicit family below.
(c) So the useful calibration is over ROBUSTLY non-pentagonal measures (every weight >= floor).
    Maximise the true arc-cut minimum there.
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize

from P1_engine import Meas, TARGET
from P1_pentagon import is_pentagonal, pentagon_bound

print("(a) EQUALITY CASE -- balanced blow-ups of C5")
for name, q, sup in [("C5 itself (G5)", 5, [0, 1, 2, 3, 4]),
                     ("C5 blown up 2x on G25", 25, [0, 1, 5, 6, 10, 11, 15, 16, 20, 21]),
                     ("C5 blown up 3x on G50", 50, [0, 1, 2, 10, 11, 12, 20, 21, 22,
                                                    30, 31, 32, 40, 41, 42])]:
    mu = Meas([F(k, q) for k in sup], [F(1, len(sup))] * len(sup))
    pb = pentagon_bound(mu)
    print(f"   {name:22s} n={mu.n:2d} pentagonal={pb is not None} "
          f"q={[str(t) for t in pb[2]] if pb else None}")
    print(f"   {'':22s} pentagon bound={pb[0]} = {float(pb[0]):.8f}   "
          f"ARCBOUND={mu.arcbound()} = {float(mu.arcbound()):.8f}   "
          f"{'TIGHT at 1/25' if mu.arcbound() == TARGET else ''}")

print("\n(b) the residual class is NOT bounded away from 1/25.")
print("    V8 support {0,1,6,7,12,13,14,19}/20 is non-pentagonal, but the five atoms")
print("    {0,1,7,12,14} induce a C5 there (a pentagonal sub-configuration), so loading")
print("    them and leaving weight eps on {6,13,19} keeps the support non-pentagonal while")
print("    the measure converges to the extremal C5:")
V8 = [0, 1, 6, 7, 12, 13, 14, 19]        # the item-7 witness support (non-pentagonal)
heavy = [0, 1, 7, 12, 14]                # induced C5 inside V8
for eps in (F(1, 10), F(1, 100), F(1, 1000), F(1, 10 ** 6)):
    w = [eps if k not in heavy else (1 - 3 * eps) / 5 for k in V8]
    mu = Meas([F(k, 20) for k in V8], w)
    print(f"   eps={str(eps):10s} support pentagonal={is_pentagonal(mu)}  "
          f"ARCBOUND={float(mu.arcbound()):.8f}   (1/25 = 0.04)")
mu5 = Meas([F(k, 20) for k in heavy], [F(1, 5)] * 5)
print(f"   eps=0 limit (the five heavy atoms alone): pentagonal={is_pentagonal(mu5)}  "
      f"ARCBOUND={mu5.arcbound()} = {float(mu5.arcbound()):.8f}")

print("\n(c) robustly non-pentagonal: every weight >= 1/(3n); maximise the arc-cut minimum")
rng = np.random.default_rng(5)


def maxmin(q, sup, floor_frac=F(1, 3)):
    n = len(sup)
    mu0 = Meas([F(k, q) for k in sup], [F(1, n)] * n)
    if is_pentagonal(mu0):
        return None
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if mu0.adj[i][j]]
    if not E:
        return None
    masks = set()
    for i in range(n):
        inI = [False] * n
        for L in range(n + 1):
            if L:
                inI[(i + L - 1) % n] = True
            masks.add(tuple(inI))
    M = np.array([[1.0 if mk[i] == mk[j] else 0.0 for (i, j) in E] for mk in masks])
    ei = np.array([e[0] for e in E]); ej = np.array([e[1] for e in E])
    lo = float(floor_frac) / n
    best = (-1, None)
    for _ in range(4):
        x0 = rng.random(n) + 0.5
        x0 /= x0.sum()
        r = minimize(lambda z: -z[-1], np.append(x0, 0.0), method='SLSQP',
                     bounds=[(lo, 1)] * n + [(0, 0.1)],
                     constraints=[{'type': 'ineq',
                                   'fun': lambda z: M @ (z[:-1][ei] * z[:-1][ej]) - z[-1]},
                                  {'type': 'eq', 'fun': lambda z: z[:-1].sum() - 1}],
                     options={'maxiter': 500, 'ftol': 1e-14})
        x = np.maximum(r.x[:-1], lo)
        x /= x.sum()
        v = float((M @ (x[ei] * x[ej])).min())
        if v > best[0]:
            best = (v, x)
    return best


results = []
for q in (8, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24):
    for size in range(5, min(q, 10) + 1):
        for _ in range(40):
            sup = sorted(rng.choice(q, size=size, replace=False).tolist())
            r = maxmin(q, sup)
            if r is None or r[1] is None:
                continue
            v, x = r
            results.append((v, q, sup, x))
results.sort(reverse=True, key=lambda t: t[0])
seen = set()
shown = 0
print("   top robustly non-pentagonal configurations (weights bounded below by 1/(3n)):")
for v, q, sup, x in results:
    if (q, tuple(sup)) in seen:
        continue
    seen.add((q, tuple(sup)))
    mu = Meas([F(k, q) for k in sup], [F(int(round(t * 10 ** 9)), 10 ** 9) for t in x])
    print(f"     {float(mu.arcbound()):.6f}  q={q:3d} sup={sup}  n={mu.n} "
          f"W={float(mu.W):.5f}  pentagonal={is_pentagonal(mu)}")
    if shown == 0:
        print(f"       exact weights of the best one: "
              f"{[str(t) for t in mu.wt]}")
        print(f"       exact ARCBOUND = {mu.arcbound()}   A = {mu.A}   b0 = {mu.bound(0)}")
    shown += 1
    if shown >= 10:
        break
print("   (1/25 = 0.04; 1/32 = 0.03125)")
