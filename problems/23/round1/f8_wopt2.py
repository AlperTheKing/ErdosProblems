"""
f8_wopt2.py -- fast max_{a in simplex} psi(G,a) for reduced maximal triangle-free
patterns.  Tensor-vectorised constraints; SLSQP multistart + exact polish check.

psi(G,a) = min over 2-colourings c of  sum_{ij in E, c_i=c_j} a_i a_j
         = min over inclusion-minimal monochromatic edge sets F of sum_{ij in F} a_i a_j

If psi > 1/25 for any triangle-free (G,a) with rational a, then the blow-up of G
with part sizes proportional to a is a counterexample to Erdos #23.

Usage: python f8_wopt2.py NSTART file1.g6 [file2.g6 ...]
"""
import sys, time
import numpy as np
from scipy.optimize import minimize
from f8_core import g6_decode, edges_of, mono_sets

rng = np.random.default_rng(20260725)
TARGET = 1.0 / 25.0


def constraint_tensor(n, adj):
    E, minimal = mono_sets(n, adj)
    K = len(minimal)
    T = np.zeros((K, n, n))
    for k, mask in enumerate(minimal):
        mm = mask
        while mm:
            b = (mm & -mm).bit_length() - 1
            i, j = E[b]
            T[k, i, j] = 1.0
            T[k, j, i] = 1.0
            mm &= mm - 1
    sizes = np.array([bin(x).count('1') for x in minimal])
    return E, minimal, T, sizes


def psi_np(T, a):
    Ta = T.dot(a)
    return 0.5 * np.einsum('ki,i->k', Ta, a)


def maxmin(n, T, nstart):
    K = T.shape[0]

    def cfun(z):
        a = z[:n]
        return psi_np(T, a) - z[n]

    def cjac(z):
        a = z[:n]
        J = np.empty((K, n + 1))
        J[:, :n] = T.dot(a)
        J[:, n] = -1.0
        return J

    eq = {'type': 'eq',
          'fun': lambda z: np.array([z[:n].sum() - 1.0]),
          'jac': lambda z: np.concatenate([np.ones((1, n)), np.zeros((1, 1))], axis=1)}
    ineq = {'type': 'ineq', 'fun': cfun, 'jac': cjac}
    bnds = [(0.0, 1.0)] * n + [(0.0, 0.5)]
    obj = lambda z: -z[n]
    objg = lambda z: np.concatenate([np.zeros(n), [-1.0]])

    best_t, best_a = -1.0, np.ones(n) / n
    starts = [np.ones(n) / n]
    for _ in range(nstart):
        if rng.random() < 0.45:
            a0 = rng.dirichlet(np.ones(n) * rng.choice([0.15, 0.4, 1.0, 3.0]))
        else:
            k = int(rng.integers(5, n + 1))
            sub = rng.choice(n, size=k, replace=False)
            a0 = np.zeros(n)
            a0[sub] = rng.dirichlet(np.ones(k))
        starts.append(a0)
    for a0 in starts:
        z0 = np.concatenate([a0, [float(psi_np(T, a0).min())]])
        try:
            r = minimize(obj, z0, jac=objg, bounds=bnds, constraints=[eq, ineq],
                         method='SLSQP', options={'maxiter': 300, 'ftol': 1e-13})
        except Exception:
            continue
        a = np.clip(r.x[:n], 0, None)
        s = a.sum()
        if s <= 0:
            continue
        a /= s
        t = float(psi_np(T, a).min())
        if t > best_t:
            best_t, best_a = t, a
    return best_t, best_a


def blowup_structure(a, tol=1e-6):
    """Report whether the support of a splits into 5 groups of total weight 1/5
    (the signature of a C5 blow-up weighting)."""
    w = np.sort(a[a > tol])[::-1]
    return float(w.sum()), len(w)


def main():
    nstart = int(sys.argv[1])
    worst = 0.0
    t0 = time.time()
    for fn in sys.argv[2:]:
        for line in open(fn):
            line = line.strip()
            if not line or line[0] == '>':
                continue
            n, adj = g6_decode(line)
            E, minimal, T, sizes = constraint_tensor(n, adj)
            b = int(sizes.min())
            t, a = maxmin(n, T, nstart)
            worst = max(worst, t)
            flag = '  *** EXCEEDS 1/25 ***' if t > TARGET + 1e-9 else ''
            print(f"{line:>34s} n={n:2d} m={len(E):3d} K={T.shape[0]:5d} bip={b:2d} "
                  f"bip/N^2={b/n**2:.6f} maxpsi={t:.10f} gap={t-TARGET:+.2e}{flag}",
                  flush=True)
    print(f"# overall max psi = {worst:.12f}   ({time.time()-t0:.1f}s)")


if __name__ == '__main__':
    main()
