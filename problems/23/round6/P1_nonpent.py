"""How much room is left after the pentagon lemma?

The pentagon lemma settles every measure whose support admits a 5-block decomposition with
edge-free consecutive blocks.  This script maximises the TRUE arc-cut minimum over measures
whose support is NOT pentagonal, to find out how close to 1/25 the remaining case can get.

Method: random supports on Gamma_q, keep the non-pentagonal ones, maximise min over all arc
cuts (max-min of quadratic forms, SLSQP), drop any optimum whose positive-weight support has
become pentagonal, re-verify the survivors exactly.
"""
import sys
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize

from P1_engine import Meas, TARGET
from P1_pentagon import is_pentagonal

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)


def arc_cut_masks(sup, q):
    """all arc cuts of the support (as boolean masks over the support list)"""
    n = len(sup)
    out = []
    for i in range(n):
        inI = [False] * n
        for L in range(n + 1):
            if L:
                inI[(i + L - 1) % n] = True
            out.append(tuple(inI))
    return sorted(set(out))


def run(q, size, tries):
    best = []
    for _ in range(tries):
        sup = sorted(rng.choice(q, size=size, replace=False).tolist())
        mu0 = Meas([F(k, q) for k in sup], [F(1, size)] * size)
        if is_pentagonal(mu0):
            continue
        n = size
        E = [(i, j) for i in range(n) for j in range(i + 1, n) if mu0.adj[i][j]]
        if not E:
            continue
        masks = arc_cut_masks(sup, q)
        M = []
        for mk in masks:
            row = np.zeros(len(E))
            for k, (i, j) in enumerate(E):
                row[k] = 1.0 if mk[i] == mk[j] else 0.0
            M.append(row)          # keep the all-zero rows: an arc cut of value 0 is REAL
        M = np.array(M)
        if not M.any(axis=1).all():
            continue               # some arc cut is identically 0 -> ARCBOUND = 0, uninteresting
        ei = np.array([e[0] for e in E]); ej = np.array([e[1] for e in E])

        def negt(z):
            return -z[-1]

        def cons(z):
            x = z[:-1]
            return M @ (x[ei] * x[ej]) - z[-1]

        bestloc = (-1, None)
        for _ in range(3):
            x0 = rng.random(n) + 0.3
            x0 /= x0.sum()
            z0 = np.append(x0, 0.0)
            r = minimize(negt, z0, method='SLSQP',
                         bounds=[(0, 1)] * n + [(0, 0.1)],
                         constraints=[{'type': 'ineq', 'fun': cons},
                                      {'type': 'eq', 'fun': lambda z: z[:-1].sum() - 1}],
                         options={'maxiter': 400, 'ftol': 1e-14})
            xx = np.maximum(r.x[:-1], 0)
            if xx.sum() <= 0:
                continue
            xx /= xx.sum()
            vv = float((M @ (xx[ei] * xx[ej])).min())
            if vv > bestloc[0]:
                bestloc = (vv, xx)
        val, x = bestloc
        if x is None:
            continue
        keep = [k for k in range(n) if x[k] > 1e-7]
        if len(keep) < n:
            mu1 = Meas([F(sup[k], q) for k in keep], [F(int(round(x[k] * 10**9)), 10**9)
                                                      for k in keep])
            if is_pentagonal(mu1):
                continue
        best.append((val, q, sup, x.copy()))
    best.sort(reverse=True, key=lambda t: t[0])
    return best[:5]


if __name__ == '__main__':
    allbest = []
    for q in (8, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24):
        for size in range(5, min(q, 11) + 1):
            allbest += run(q, size, 60)
    allbest.sort(reverse=True, key=lambda t: t[0])
    print("largest arc-cut minima found on NON-pentagonal supports (1/25 = 0.04):\n")
    seen = set()
    shown = 0
    for val, q, sup, x in allbest:
        key = (q, tuple(sup))
        if key in seen:
            continue
        seen.add(key)
        keep = [k for k in range(len(sup)) if x[k] > 1e-7]
        mu = Meas([F(sup[k], q) for k in keep],
                  [F(int(round(x[k] * 10 ** 9)), 10 ** 9) for k in keep])
        arc = mu.arcbound()
        pen = is_pentagonal(mu)
        print(f"  float {val:.6f}  exact(rationalised) {float(arc):.6f}  q={q} "
              f"sup={[sup[k] for k in keep]}  pentagonal={pen}  W={float(mu.W):.5f}")
        shown += 1
        if shown >= 12:
            break
