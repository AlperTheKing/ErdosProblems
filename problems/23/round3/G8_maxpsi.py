"""G8: cutting-plane maximisation of psi(And(k), x) over the simplex.

psi(x) = min over ALL cuts of H of sum_{monochromatic uv} x_u x_v.
Strategy: maintain a pool of cuts; locally maximise min-over-pool with SLSQP;
re-verify against ALL 2^(n-1) cuts (vectorised, exact combinatorics on the cut side);
add violated cuts; repeat.  Report best x found, then re-verify the reported value
exactly with Fractions on a rationalised point.

Numerics GUIDE only.  Exact confirmation is done in G8_exact*.py.
"""
import sys, time
import numpy as np
from fractions import Fraction
from G8_graphs import andrasfai


def bits_table(n):
    """side[v] for every cut mask (vertex 0 fixed to side 0)."""
    N = 1 << (n - 1)
    masks = np.arange(N, dtype=np.uint32)
    side = np.zeros((n, N), dtype=np.uint8)
    for v in range(1, n):
        side[v] = ((masks >> (v - 1)) & 1).astype(np.uint8)
    return side


def full_psi_and_argmin(n, edges, side, x, topk=40):
    N = side.shape[1]
    vals = np.zeros(N, dtype=np.float64)
    for (u, v) in edges:
        w = x[u] * x[v]
        if w == 0.0:
            continue
        mono = (side[u] == side[v])
        vals += w * mono
    m = vals.min()
    idx = np.argpartition(vals, min(topk, N - 1))[:topk]
    idx = idx[np.argsort(vals[idx])]
    return m, idx, vals


def mono_edges_of_mask(n, edges, mask):
    side = [0] * n
    for v in range(1, n):
        side[v] = (mask >> (v - 1)) & 1
    return [(u, v) for (u, v) in edges if side[u] == side[v]]


def local_max(n, pool, x0, iters=300):
    from scipy.optimize import minimize
    cons = []
    for mono in pool:
        a = np.array([e[0] for e in mono], dtype=int)
        b = np.array([e[1] for e in mono], dtype=int)
        def f(z, a=a, b=b):
            return float(np.dot(z[a], z[b])) - z[n]
        def fj(z, a=a, b=b):
            g = np.zeros(n + 1)
            np.add.at(g, a, z[b]); np.add.at(g, b, z[a]); g[n] = -1.0
            return g
        cons.append({'type': 'ineq', 'fun': f, 'jac': fj})
    cons.append({'type': 'eq', 'fun': lambda z: float(np.sum(z[:n]) - 1.0),
                 'jac': lambda z: np.concatenate([np.ones(n), [0.0]])})
    z0 = np.concatenate([x0, [0.0]])
    r = minimize(lambda z: -z[n], z0,
                 jac=lambda z: np.concatenate([np.zeros(n), [-1.0]]),
                 constraints=cons, bounds=[(0.0, 1.0)] * n + [(0.0, 1.0)],
                 method='SLSQP', options={'maxiter': iters, 'ftol': 1e-16})
    x = np.clip(r.x[:n], 0, None)
    s = x.sum()
    return x / s if s > 0 else x0


def run(k, ntrial=60, seed=1, verbose=True):
    n, conn, adj, edges = andrasfai(k)
    side = bits_table(n)
    rng = np.random.default_rng(seed)
    best = (-1.0, None)
    t0 = time.time()
    for t in range(ntrial):
        if t == 0:
            x = np.ones(n) / n
        elif t == 1:
            x = np.zeros(n);
            for v in (0, 1, 2, 3, 4):
                x[v] = 0.2
        else:
            x = rng.dirichlet(np.ones(n) * rng.uniform(0.15, 2.5))
        pool = []
        seen = set()
        for it in range(30):
            m, idx, vals = full_psi_and_argmin(n, edges, side, x)
            new = 0
            for j in idx:
                if int(j) not in seen:
                    seen.add(int(j))
                    pool.append(mono_edges_of_mask(n, edges, int(j)))
                    new += 1
            if new == 0 and it > 0:
                break
            xn = local_max(n, pool, x)
            if np.max(np.abs(xn - x)) < 1e-12:
                x = xn
                break
            x = xn
        m, idx, vals = full_psi_and_argmin(n, edges, side, x)
        if m > best[0]:
            best = (m, x.copy())
            if verbose:
                print(f"  k={k} trial {t}: psi={m:.10f}  x={np.round(x,5)}", flush=True)
    if verbose:
        print(f"And({k}) n={n}: numeric max psi = {best[0]:.12f}   1/25 = 0.04   "
              f"time {time.time()-t0:.1f}s")
        print("   argmax =", np.round(best[1], 6))
    return best


if __name__ == "__main__":
    ks = [int(a) for a in sys.argv[1:]] or [3, 4, 5]
    for k in ks:
        nt = 200 if k <= 4 else (80 if k <= 5 else 30)
        run(k, ntrial=nt, seed=7)
        print()
