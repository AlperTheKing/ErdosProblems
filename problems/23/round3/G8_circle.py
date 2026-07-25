"""G8: the continuum reformulation.

Gamma = graph on the circle R/Z with  x ~ y  iff  circular distance d(x,y) > 1/3.
Gamma is triangle-free (three points pairwise > 1/3 apart would need three arcs each
> 1/3 summing to 1).  And(k) = K_{(3k-1)/k} is EXACTLY Gamma restricted to the
p = 3k-1 equally spaced points (i~j iff |i-j| > p/3 iff |i-j| >= k).

So  sup_k max_x psi(And(k),x)  is the finite-point version of  max_mu psi(Gamma,mu).

Here: G_M = Gamma restricted to M equally spaced points, any M.  Maximise over the
simplex the minimum over ARC cuts only (an UPPER bound for psi, exact whenever the
arc-cut optimality observed in G8_arccuts.py holds).
"""
import sys
import numpy as np
from fractions import Fraction


def graph_M(M):
    """edges of Gamma restricted to M equally spaced points: i~j iff M/3 < |i-j|_circ <= M/2."""
    E = []
    for i in range(M):
        for j in range(i + 1, M):
            d = min((j - i) % M, (i - j) % M)
            if 3 * d > M:
                E.append((i, j))
    return E


def arc_cuts(M):
    """all cyclic-interval cuts, as (side vector) -> mono edge list is built by caller."""
    out = []
    for i in range(M):
        for m in range(1, M):
            side = [0] * M
            for t in range(m):
                side[(i + t) % M] = 1
            out.append(tuple(side))
    return sorted(set(out))


def mono_lists(M, E, cuts):
    res = []
    for side in cuts:
        mono = [(u, v) for (u, v) in E if side[u] == side[v]]
        res.append(mono)
    return res


def psi_arc(monos, x):
    best = None
    for mono in monos:
        s = 0.0
        for (u, v) in mono:
            s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


def local_max(M, pool, x0, iters=400):
    from scipy.optimize import minimize
    cons = []
    for mono in pool:
        a = np.array([e[0] for e in mono], dtype=int)
        b = np.array([e[1] for e in mono], dtype=int)
        def f(z, a=a, b=b):
            return float(np.dot(z[a], z[b])) - z[M]
        def fj(z, a=a, b=b):
            g = np.zeros(M + 1)
            np.add.at(g, a, z[b]); np.add.at(g, b, z[a]); g[M] = -1.0
            return g
        cons.append({'type': 'ineq', 'fun': f, 'jac': fj})
    cons.append({'type': 'eq', 'fun': lambda z: float(np.sum(z[:M]) - 1.0),
                 'jac': lambda z: np.concatenate([np.ones(M), [0.0]])})
    z0 = np.concatenate([x0, [0.0]])
    r = minimize(lambda z: -z[M], z0, jac=lambda z: np.concatenate([np.zeros(M), [-1.0]]),
                 constraints=cons, bounds=[(0.0, 1.0)] * M + [(0.0, 1.0)],
                 method='SLSQP', options={'maxiter': iters, 'ftol': 1e-16})
    x = np.clip(r.x[:M], 0, None); s = x.sum()
    return x / s if s > 0 else x0


def run(M, ntrial=40, seed=3):
    E = graph_M(M)
    cuts = arc_cuts(M)
    monos = mono_lists(M, E, cuts)
    rng = np.random.default_rng(seed)
    best = (-1.0, None)
    for t in range(ntrial):
        if t == 0:
            x = np.ones(M) / M
        elif t == 1:
            x = np.zeros(M)
            for j in range(5):
                x[(j * M) // 5] = 0.2
        else:
            x = rng.dirichlet(np.ones(M) * rng.uniform(0.1, 2.0))
        pool, seen = [], set()
        for it in range(25):
            vals = [(sum(x[u] * x[v] for (u, v) in mono), ci) for ci, mono in enumerate(monos)]
            vals.sort()
            new = 0
            for val, ci in vals[:25]:
                if ci not in seen:
                    seen.add(ci); pool.append(monos[ci]); new += 1
            if new == 0 and it > 0:
                break
            xn = local_max(M, pool, x)
            if np.max(np.abs(xn - x)) < 1e-13:
                x = xn; break
            x = xn
        v = psi_arc(monos, x)
        if v > best[0]:
            best = (v, x.copy())
    return best


if __name__ == "__main__":
    Ms = [int(a) for a in sys.argv[1:]] or list(range(5, 31))
    for M in Ms:
        v, x = run(M, ntrial=(60 if M <= 20 else 30))
        star = "  <-- EXCEEDS 1/25" if v > 0.04 + 1e-9 else ""
        nz = np.sort(x)[::-1]
        print(f"M={M:3d}  max_x min_arc = {v:.10f}   (1/25 = 0.04){star}   support={int((x>1e-7).sum())}"
              f"  top weights {np.round(nz[:7],5)}", flush=True)
