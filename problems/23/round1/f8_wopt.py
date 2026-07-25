"""
f8_wopt.py -- for every graph in a graph6 file compute
    bip(G)  (exact, uniform weights)   and
    max_{a in simplex} psi(G,a)        (multistart SLSQP, then exact polish)

Usage:  python f8_wopt.py file1.g6 [file2.g6 ...]
"""
import sys, math, itertools
import numpy as np
from scipy.optimize import minimize, linprog
from fractions import Fraction
from f8_core import g6_decode, edges_of, mono_sets, bip_exact

rng = np.random.default_rng(20260725)


def build(n, adj):
    E, minimal = mono_sets(n, adj)
    # each minimal mask -> list of (i,j)
    cons = []
    for mask in minimal:
        lst = []
        mm = mask
        while mm:
            k = (mm & -mm).bit_length() - 1
            lst.append(E[k])
            mm &= mm - 1
        cons.append(lst)
    return E, minimal, cons


def q_all(cons, a):
    return np.array([sum(a[i] * a[j] for (i, j) in c) for c in cons])


def maxmin(n, cons, nstart=200, seeds=None):
    """maximise t  s.t.  q_c(a) >= t for all c,  sum a = 1, a >= 0."""
    K = len(cons)
    # precompute constraint matrices as index arrays
    Cidx = [np.array(c, dtype=int).reshape(-1, 2) for c in cons]

    def negobj(z):
        return -z[n]

    def negobj_grad(z):
        g = np.zeros(n + 1)
        g[n] = -1.0
        return g

    def cfun(z):
        a = z[:n]
        return np.array([np.sum(a[C[:, 0]] * a[C[:, 1]]) for C in Cidx]) - z[n]

    def cjac(z):
        a = z[:n]
        J = np.zeros((K, n + 1))
        for r, C in enumerate(Cidx):
            for (i, j) in C:
                J[r, i] += a[j]
                J[r, j] += a[i]
            J[r, n] = -1.0
        return J

    eq = {'type': 'eq',
          'fun': lambda z: np.array([z[:n].sum() - 1.0]),
          'jac': lambda z: np.concatenate([np.ones((1, n)), np.zeros((1, 1))], axis=1)}
    ineq = {'type': 'ineq', 'fun': cfun, 'jac': cjac}
    bnds = [(0.0, 1.0)] * n + [(0.0, 1.0)]

    best_t, best_a = -1.0, None
    starts = []
    starts.append(np.ones(n) / n)
    if seeds:
        starts.extend(seeds)
    for _ in range(nstart):
        # mixture of dense and sparse Dirichlet starts
        if rng.random() < 0.5:
            a0 = rng.dirichlet(np.ones(n) * rng.choice([0.2, 0.5, 1.0, 3.0]))
        else:
            k = rng.integers(3, n + 1)
            sub = rng.choice(n, size=int(k), replace=False)
            a0 = np.zeros(n)
            a0[sub] = rng.dirichlet(np.ones(int(k)))
        starts.append(a0)
    for a0 in starts:
        z0 = np.concatenate([a0, [min(q_all(cons, a0))]])
        try:
            r = minimize(negobj, z0, jac=negobj_grad, bounds=bnds,
                         constraints=[eq, ineq], method='SLSQP',
                         options={'maxiter': 400, 'ftol': 1e-14})
        except Exception:
            continue
        a = np.clip(r.x[:n], 0, None)
        s = a.sum()
        if s <= 0:
            continue
        a = a / s
        t = float(np.min(q_all(cons, a)))
        if t > best_t:
            best_t, best_a = t, a
    return best_t, best_a


def main():
    results = []
    for fn in sys.argv[1:]:
        for line in open(fn):
            line = line.strip()
            if not line or line[0] == '>':
                continue
            n, adj = g6_decode(line)
            E, minimal, cons = build(n, adj)
            b = min(len(c) for c in cons)
            t, a = maxmin(n, cons, nstart=int(sys.argv[0] and 250))
            results.append((t, n, b, line, a))
            print(f"{line:>28s} n={n:2d} m={len(E):3d} bip={b:3d} "
                  f"bip/N^2={b/n**2:.6f}  maxpsi={t:.9f}  "
                  f"{'*** EXCEEDS 1/25 ***' if t > 0.04 + 1e-9 else ''}",
                  flush=True)
    results.sort(reverse=True)
    print("\n=== TOP by max_a psi ===")
    for t, n, b, g6, a in results[:25]:
        print(f"  psi={t:.9f}  n={n} bip={b} {g6}  a={np.round(a,6).tolist()}")


if __name__ == '__main__':
    main()
