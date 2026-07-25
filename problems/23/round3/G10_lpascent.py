"""G10_lpascent.py -- INDEPENDENT second implementation of  max_x psi(H,x).

psi is a MINIMUM of quadratics, hence nonsmooth; ordinary gradient ascent is wrong.
Method used here (valid for max-min):
  * at x compute the ACTIVE (near-active) cut set A;
  * solve an LP for a feasible direction d with sum d = 0, d_v >= 0 wherever x_v = 0,
    maximising s subject to <grad Q_c, d> >= s for every c in A;
  * if s* <= 0 the point is first-order stationary for the max-min problem;
  * otherwise exact-ish line search of t -> min_c Q_c(x+td) over ALL cuts.
Restarts: every induced-C5 concentration point, uniform, random Dirichlet.

Floats only guide the search.  Every reported value is re-derived with Fractions.
"""
import sys, os, math, itertools
import numpy as np
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G10_core import (all_cut_monoedges, psi_exact, induced_c5s, adjacency,
                      cycle, petersen, grotzsch, chvatal, is_triangle_free)

try:
    from scipy.optimize import linprog
except Exception:
    linprog = None


class Psi:
    def __init__(self, n, edges):
        self.n = n
        self.edges = sorted(set((min(u, v), max(u, v)) for u, v in edges))
        self.E = len(self.edges)
        self.NC = 1 << (n - 1)
        A = np.zeros((self.NC, self.E), dtype=np.float64)
        for c in range(self.NC):
            m = c << 1
            for k, (u, v) in enumerate(self.edges):
                if ((m >> u) & 1) == ((m >> v) & 1):
                    A[c, k] = 1.0
        self.A = A
        self.eu = np.array([e[0] for e in self.edges], dtype=np.int64)
        self.ev = np.array([e[1] for e in self.edges], dtype=np.int64)

    def qvals(self, x):
        p = x[self.eu] * x[self.ev]
        return self.A @ p

    def psi(self, x):
        return float(self.qvals(x).min())

    def grads(self, x, idx):
        """gradient rows of Q_c for c in idx : g[c][v] = sum_{u: uv mono in c} x_u"""
        G = np.zeros((len(idx), self.n))
        for r, c in enumerate(idx):
            row = self.A[c]
            nz = np.nonzero(row)[0]
            for k in nz:
                u, v = self.edges[k]
                G[r, u] += x[v]
                G[r, v] += x[u]
        return G

    def qquad(self, d, idx=None):
        p = d[self.eu] * d[self.ev]
        if idx is None:
            return self.A @ p
        return self.A[idx] @ p

    def linevals(self, x, d, ts):
        """min over ALL cuts of Q_c(x+t d), for each t in ts."""
        px = x[self.eu] * x[self.ev]
        pc = x[self.eu] * d[self.ev] + d[self.eu] * x[self.ev]
        pd = d[self.eu] * d[self.ev]
        Qx = self.A @ px
        Qc = self.A @ pc
        Qd = self.A @ pd
        out = []
        for t in ts:
            out.append(float((Qx + t * Qc + t * t * Qd).min()))
        return np.array(out)


def ascend(P, x0, iters=200, tol=1e-12):
    x = np.array(x0, dtype=np.float64)
    x = np.maximum(x, 0.0)
    x = x / x.sum()
    f = P.psi(x)
    for it in range(iters):
        Q = P.qvals(x)
        fmin = Q.min()
        act = np.nonzero(Q <= fmin + max(1e-11, 1e-7 * max(fmin, 1e-12)))[0]
        if len(act) > 400:
            act = act[np.argsort(Q[act])[:400]]
        G = P.grads(x, act)
        n = P.n
        # LP: variables d_0..d_{n-1}, s.   max s
        c = np.zeros(n + 1); c[n] = -1.0
        Aub = np.zeros((len(act), n + 1)); bub = np.zeros(len(act))
        Aub[:, :n] = -G
        Aub[:, n] = 1.0
        Aeq = np.zeros((1, n + 1)); Aeq[0, :n] = 1.0
        beq = np.array([0.0])
        bounds = []
        for v in range(n):
            if x[v] <= 1e-12:
                bounds.append((0.0, 1.0))
            else:
                bounds.append((-1.0, 1.0))
        bounds.append((None, None))
        r = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
        if not r.success:
            break
        s = -r.fun
        d = r.x[:n]
        if s <= 1e-13:
            break
        neg = d < -1e-15
        tmax = 1.0 if not neg.any() else float(np.min(x[neg] / (-d[neg])))
        tmax = min(tmax, 1.0)
        if tmax <= 1e-15:
            break
        ts = np.concatenate([np.linspace(0, tmax, 33)[1:],
                             tmax * np.geomspace(1e-6, 1.0, 20)])
        vals = P.linevals(x, d, ts)
        k = int(np.argmax(vals))
        if vals[k] <= f + 1e-16:
            # golden refine near the small-t end
            ts2 = tmax * np.geomspace(1e-10, 1e-3, 40)
            v2 = P.linevals(x, d, ts2)
            k2 = int(np.argmax(v2))
            if v2[k2] <= f + 1e-18:
                break
            t = ts2[k2]; newf = v2[k2]
        else:
            t = ts[k]; newf = vals[k]
        xn = x + t * d
        xn = np.maximum(xn, 0.0)
        s2 = xn.sum()
        if s2 <= 0:
            break
        xn = xn / s2
        fn = P.psi(xn)
        if fn <= f + 1e-17:
            break
        x, f = xn, fn
    return x, f


def maxpsi(n, edges, nrand=40, seed=0, iters=200, verbose=False):
    P = Psi(n, edges)
    rng = np.random.default_rng(seed)
    starts = []
    for cyc in induced_c5s(n, edges):
        x = np.zeros(n);
        for v in cyc:
            x[v] = 0.2
        starts.append(x)
    starts.append(np.ones(n) / n)
    for _ in range(nrand):
        starts.append(rng.dirichlet(np.ones(n)))
    for _ in range(nrand):
        k = int(rng.integers(3, n + 1))
        sub = rng.choice(n, size=k, replace=False)
        x = np.zeros(n); x[sub] = rng.dirichlet(np.ones(k))
        starts.append(x)
    best = (-1.0, None)
    for x0 in starts:
        x, f = ascend(P, x0, iters=iters)
        if f > best[0]:
            best = (f, x)
    return best[1], best[0], P


DEFAULT_DENOMS = tuple(sorted(set(
    [5, 25, 50, 100, 200, 500, 1000, 2000, 5000, 7, 49, 9, 81, 11, 121, 13, 169,
     105, 315, 693, 1155, 2520, 5040, 27720, 45045, 360360] +
    [k for k in range(3, 61)] + [12 * k for k in range(1, 40)])))


def exact_check(n, edges, x, denom_list=DEFAULT_DENOMS):
    """Round the float maximiser to rationals with several denominators and
    evaluate psi EXACTLY.  Returns (best Fraction value, weight vector)."""
    ml = all_cut_monoedges(n, edges)
    best = (Fraction(-1), None)
    for D in denom_list:
        a = [int(round(xi * D)) for xi in x]
        s = sum(a)
        if s == 0:
            continue
        # fix rounding drift
        while s > D:
            i = max(range(n), key=lambda j: a[j]); a[i] -= 1; s -= 1
        while s < D:
            i = max(range(n), key=lambda j: (x[j] * D - a[j])); a[i] += 1; s += 1
        xv = [Fraction(ai, D) for ai in a]
        val = psi_exact(ml, xv)
        if val > best[0]:
            best = (val, tuple(a), D)
    return best


if __name__ == '__main__':
    assert linprog is not None, 'scipy required'
    tests = [('C5', cycle(5), Fraction(1, 25)),
             ('C7', cycle(7), Fraction(1, 49)),
             ('C9', cycle(9), Fraction(1, 81)),
             ('C11', cycle(11), Fraction(1, 121))]
    for nm, (n, e), expect in tests:
        x, f, P = maxpsi(n, e, nrand=15, seed=1)
        ex = exact_check(n, e, x)
        print('%-4s float max psi = %.10f   exact rounded = %s   expected %s   %s'
              % (nm, f, ex[0], expect, 'OK' if ex[0] == expect else 'MISMATCH'))
    for nm, (n, e) in [('Petersen', petersen()), ('Grotzsch', grotzsch()), ('Chvatal', chvatal())]:
        x, f, P = maxpsi(n, e, nrand=25, seed=2)
        ex = exact_check(n, e, x)
        print('%-9s float max psi = %.10f  exact %s = %.10f   1/25 = %.10f  %s'
              % (nm, f, ex[0], float(ex[0]), 0.04,
                 'ABOVE-1/25' if ex[0] > Fraction(1, 25) else ('EQ' if ex[0] == Fraction(1, 25) else 'below')))
