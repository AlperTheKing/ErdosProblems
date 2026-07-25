"""ROOT-AGENT falsification probe (Claude, round 3): maximise the ARC-CUT bound over ALL finite
measures on the circle - positions AND weights both free.

Circle graph: x ~ y iff circular distance d(x,y) > 1/3.  For an atomic measure with atoms
p_1 < ... < p_k (cyclic) and weights w, every arc of the circle meets the atom set in a cyclic
interval, so the arc cuts are exactly the k^2 cyclic-interval splits.

        ARCBOUND(p,w) = min over cyclic intervals I of
                        [ sum_{u,v in I, adjacent} w_u w_v + sum_{u,v not in I, adjacent} w_u w_v ].

The arc-cut conjecture says ARCBOUND <= 1/25 for every measure.  This script tries hard to break it
by direct multi-start optimisation over positions and weights (Nelder-Mead on a nonsmooth min, plus
weight-only refinement), for k = 5..9 atoms.  Any point found above 1/25 is re-evaluated in exact
rational arithmetic before being believed.
"""
import numpy as np
from fractions import Fraction as F
from itertools import combinations
import sys

try:
    from scipy.optimize import minimize
except Exception as e:
    print("scipy needed:", e); sys.exit(2)

THIRD = 1.0 / 3.0


def adjacency(p):
    k = len(p)
    A = np.zeros((k, k), dtype=bool)
    for i in range(k):
        for j in range(i + 1, k):
            d = abs(p[i] - p[j]) % 1.0
            d = min(d, 1.0 - d)
            A[i, j] = A[j, i] = (d > THIRD + 1e-12)
    return A


def arcbound(p, w):
    k = len(p)
    order = np.argsort(p % 1.0)
    p = np.asarray(p)[order] % 1.0
    w = np.asarray(w)[order]
    A = adjacency(p)
    best = None
    for i in range(k):
        for l in range(0, k + 1):
            inA = np.zeros(k, dtype=bool)
            for t in range(l):
                inA[(i + t) % k] = True
            s = 0.0
            for u in range(k):
                for v in range(u + 1, k):
                    if A[u, v] and inA[u] == inA[v]:
                        s += w[u] * w[v]
            if best is None or s < best:
                best = s
    return best


def exact_arcbound(pfrac, wfrac):
    """exact rational re-evaluation"""
    k = len(pfrac)
    idx = sorted(range(k), key=lambda i: pfrac[i])
    p = [pfrac[i] for i in idx]
    w = [wfrac[i] for i in idx]
    adj = [[False] * k for _ in range(k)]
    for i in range(k):
        for j in range(i + 1, k):
            d = (p[i] - p[j]) % 1
            d = min(d, 1 - d)
            adj[i][j] = adj[j][i] = (d > F(1, 3))
    best = None
    for i in range(k):
        for l in range(0, k + 1):
            inA = [False] * k
            for t in range(l):
                inA[(i + t) % k] = True
            s = F(0)
            for u, v in combinations(range(k), 2):
                if adj[u][v] and inA[u] == inA[v]:
                    s += w[u] * w[v]
            if best is None or s < best:
                best = s
    return best


def pack(p, w):
    return np.concatenate([p[1:], np.log(np.maximum(w, 1e-12))])


def unpack(z, k):
    p = np.concatenate([[0.0], z[:k - 1]]) % 1.0
    lw = z[k - 1:]
    w = np.exp(lw - lw.max())
    w = w / w.sum()
    return p, w


def run(k, restarts=400, seed=0):
    rng = np.random.default_rng(seed)
    best = (-1, None, None)
    for r in range(restarts):
        if r == 0:                                   # seed with the conjectured extremal
            p0 = np.arange(k) / k if k == 5 else np.sort(rng.random(k))
            w0 = np.ones(k) / k
        else:
            p0 = np.sort(rng.random(k)); p0[0] = 0.0
            w0 = rng.dirichlet(np.ones(k))
        z0 = pack(p0, w0)
        f = lambda z: -arcbound(*unpack(z, k))
        res = minimize(f, z0, method='Nelder-Mead',
                       options={'maxiter': 20000, 'xatol': 1e-10, 'fatol': 1e-14})
        val = -res.fun
        if val > best[0]:
            p, w = unpack(res.x, k)
            best = (val, p.copy(), w.copy())
    return best


if __name__ == '__main__':
    print("target: is max over measures of ARCBOUND equal to 1/25 = 0.04 ?")
    print(f"{'k':>3s} {'best ARCBOUND':>16s} {'vs 1/25':>10s}   positions / weights")
    worst = 0.0
    for k in range(5, 10):
        val, p, w = run(k, restarts=200 if k <= 7 else 120, seed=k)
        worst = max(worst, val)
        flag = "  *** ABOVE 1/25 ***" if val > 0.04 + 1e-9 else ""
        print(f"{k:3d} {val:16.10f} {val * 25:10.6f}{flag}")
        print(f"      p = {np.round(np.sort(p % 1.0), 5)}")
        print(f"      w = {np.round(w[np.argsort(p % 1.0)], 5)}")
        if val > 0.04 + 1e-9:
            # exact re-check on the rounded rational point
            pf = [F(int(round(x * 10000)), 10000) for x in np.sort(p % 1.0)]
            wf = [F(int(round(x * 10000)), 10000) for x in w[np.argsort(p % 1.0)]]
            s = sum(wf)
            wf = [x / s for x in wf]
            ex = exact_arcbound(pf, wf)
            print("      EXACT re-evaluation at the rounded point:", ex, float(ex),
                  ">1/25" if ex > F(1, 25) else "<=1/25")
    print(f"\noverall best {worst:.10f}  (1/25 = 0.0400000000)")
