"""
f8_wopt3.py -- working-set (cutting-plane) version of the max-min search.

For a pattern H let  M  be the antichain of inclusion-minimal monochromatic edge
sets.  For ANY subset W of M,
        max_a min_{F in W} q_F(a)   >=   max_a psi(H,a),
so an upper bound obtained on a small working set already settles the question.
We start with the |W| smallest sets, optimise, then add the sets that are
violated at the optimiser, and repeat.

Usage: python f8_wopt3.py NSTART W0 file.g6 [file2.g6 ...]
"""
import sys, time
import numpy as np
from scipy.optimize import minimize
from f8_core import g6_decode, edges_of, mono_sets

rng = np.random.default_rng(4242)
TARGET = 1.0 / 25.0


def tensors(n, E, masks):
    K = len(masks)
    T = np.zeros((K, n, n))
    for k, mask in enumerate(masks):
        mm = mask
        while mm:
            b = (mm & -mm).bit_length() - 1
            i, j = E[b]
            T[k, i, j] = 1.0
            T[k, j, i] = 1.0
            mm &= mm - 1
    return T


def psi_np(T, a):
    return 0.5 * np.einsum('ki,i->k', T.dot(a), a)


def maxmin(n, T, nstart):
    K = T.shape[0]
    cfun = lambda z: psi_np(T, z[:n]) - z[n]

    def cjac(z):
        J = np.empty((K, n + 1))
        J[:, :n] = T.dot(z[:n])
        J[:, n] = -1.0
        return J
    eq = {'type': 'eq', 'fun': lambda z: np.array([z[:n].sum() - 1.0]),
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
            a0 = np.zeros(n); a0[sub] = rng.dirichlet(np.ones(k))
        starts.append(a0)
    for a0 in starts:
        z0 = np.concatenate([a0, [float(psi_np(T, a0).min())]])
        try:
            r = minimize(obj, z0, jac=objg, bounds=bnds, constraints=[eq, ineq],
                         method='SLSQP', options={'maxiter': 250, 'ftol': 1e-13})
        except Exception:
            continue
        a = np.clip(r.x[:n], 0, None); s = a.sum()
        if s <= 0:
            continue
        a /= s
        t = float(psi_np(T, a).min())
        if t > best_t:
            best_t, best_a = t, a
    return best_t, best_a


def main():
    nstart, W0 = int(sys.argv[1]), int(sys.argv[2])
    worst, t0, cnt = 0.0, time.time(), 0
    for fn in sys.argv[3:]:
        for line in open(fn):
            line = line.strip()
            if not line or line[0] == '>':
                continue
            n, adj = g6_decode(line)
            E, minimal = mono_sets(n, adj)
            sizes = np.array([bin(x).count('1') for x in minimal])
            order = np.argsort(sizes, kind='stable')
            allmasks = [minimal[i] for i in order]
            Tall = tensors(n, E, allmasks)
            widx = list(range(min(W0, len(allmasks))))
            for rounds in range(6):
                T = Tall[widx]
                t, a = maxmin(n, T, nstart)
                q = psi_np(Tall, a)
                if t <= TARGET + 1e-9:
                    break
                viol = np.argsort(q)[:25]
                new = [int(i) for i in viol if int(i) not in widx]
                if not new:
                    break
                widx = widx + new
            cnt += 1
            worst = max(worst, t)
            flag = '  *** EXCEEDS 1/25 ***' if t > TARGET + 1e-9 else ''
            print(f"{line:>36s} n={n:2d} m={len(E):3d} |M|={len(allmasks):5d} |W|={len(widx):4d} "
                  f"bip={int(sizes.min()):2d} UB(max psi)={t:.10f} gap={t-TARGET:+.2e}{flag}", flush=True)
    print(f"# {cnt} patterns, overall max = {worst:.12f}  ({time.time()-t0:.1f}s)")


if __name__ == '__main__':
    main()
