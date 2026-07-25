"""max_a psi(H,a): SLSQP on the epigraph form with the FULL colouring set (no
truncation), plus an exact rational check that the induced-C5 weighting attains
1/25 (Lemma 6).  Reports:
   lb_C5   : exact 1/25 witness found?  (rigorous lower bound check)
   maxfound: largest EXACT psi(H,a) seen anywhere (rigorous lower bound on max_a psi)
   hit     : fraction of random starts converging to >= 1/25 - 1e-9
"""
import glob, os, sys, time
from fractions import Fraction
from itertools import combinations
import numpy as np
from scipy.optimize import minimize
from audit_f8_lib import g6dec, edges, psi_int

D = os.path.dirname(os.path.abspath(__file__))
TARGET = 1.0 / 25.0
rng = np.random.default_rng(777)
NST = int(sys.argv[1]) if len(sys.argv) > 1 else 30
FILES = sys.argv[2:] if len(sys.argv) > 2 else sorted(glob.glob(os.path.join(D, 'f8_rmtf_*.g6')))


def rows_of(n, adj):
    E = edges(n, adj)
    side = np.arange(1 << (n - 1), dtype=np.int64) << 1
    M = np.empty((1 << (n - 1), len(E)), dtype=bool)
    for k, (i, j) in enumerate(E):
        M[:, k] = (((side >> i) ^ (side >> j)) & 1) == 0
    return E, np.unique(M, axis=0)


def induced_c5_value(n, adj):
    """exact psi at the weighting 1/5 on an induced C5 (Lemma 6 witness)"""
    for c in combinations(range(n), 5):
        sub = [[(adj[u] >> v) & 1 for v in c] for u in c]
        deg = [sum(r) for r in sub]
        if deg != [2] * 5:
            continue
        # connected 2-regular on 5 vertices = C5
        a = [Fraction(0)] * n
        for v in c:
            a[v] = Fraction(1, 5)
        E = edges(n, adj)
        # exact psi with these weights: min over all colourings
        best = None
        for s in range(1 << (n - 1)):
            side = s << 1
            t = Fraction(0)
            for (i, j) in E:
                if ((side >> i) ^ (side >> j)) & 1 == 0:
                    t += a[i] * a[j]
            if best is None or t < best:
                best = t
        return best, c
    return None, None


def run(n, adj):
    E, Mb = rows_of(n, adj)
    m = len(E)
    I = np.array([e[0] for e in E])
    J = np.array([e[1] for e in E])
    M = Mb.astype(float)

    def q(a):
        return M @ (a[I] * a[J])

    def jac(a):
        # d/da_v sum_{ij in F} a_i a_j
        Gi = np.zeros((M.shape[0], n))
        P = M                                # rows x m
        np.add.at(Gi.T, I, (P * a[J]).T)
        np.add.at(Gi.T, J, (P * a[I]).T)
        return Gi

    cons = [{'type': 'eq', 'fun': lambda z: np.array([z[:n].sum() - 1.0]),
             'jac': lambda z: np.hstack([np.ones((1, n)), np.zeros((1, 1))])},
            {'type': 'ineq', 'fun': lambda z: q(z[:n]) - z[n],
             'jac': lambda z: np.hstack([jac(z[:n]), -np.ones((M.shape[0], 1))])}]
    bnds = [(0.0, 1.0)] * n + [(0.0, 0.5)]
    best, hits = 0.0, 0
    starts = [np.ones(n) / n]
    for _ in range(NST):
        al = float(rng.choice([0.15, 0.4, 1.0, 3.0]))
        if rng.random() < 0.45:
            sup = rng.choice(n, size=int(rng.integers(5, n + 1)), replace=False)
            v = np.zeros(n)
            v[sup] = rng.dirichlet(np.ones(len(sup)) * al)
        else:
            v = rng.dirichlet(np.ones(n) * al)
        starts.append(v)
    for a0 in starts:
        z0 = np.concatenate([a0, [q(a0).min()]])
        try:
            r = minimize(lambda z: -z[n], z0, jac=lambda z: np.concatenate([np.zeros(n), [-1.0]]),
                         bounds=bnds, constraints=cons, method='SLSQP',
                         options={'maxiter': 200, 'ftol': 1e-14})
        except Exception:
            continue
        a = np.clip(r.x[:n], 0, None)
        s = a.sum()
        if s <= 0:
            continue
        a /= s
        v = float(q(a).min())
        best = max(best, v)
        hits += (v >= TARGET - 1e-9)
    return best, hits / (NST + 1)


gmax, t0 = 0.0, time.time()
for fn in FILES:
    k = int(fn.rsplit('_', 1)[1].split('.')[0])
    lines = [l.strip() for l in open(fn) if l.strip()]
    if not lines:
        continue
    mx, mnhit, over, lb_ok = 0.0, 1.0, [], 0
    for l in lines:
        n, adj = g6dec(l)
        b, h = run(n, adj)
        mx, mnhit = max(mx, b), min(mnhit, h)
        if b > TARGET + 1e-9:
            over.append((l, b))
        if k <= 13:
            val, c = induced_c5_value(n, adj)
            lb_ok += (val == Fraction(1, 25))
    gmax = max(gmax, mx)
    print(f"n={k:2d} {len(lines):4d} patterns  maxfound={mx:.12f} (excess {mx-TARGET:+.3e}) "
          f"min-hit={mnhit:.3f}  inducedC5-gives-exactly-1/25: {lb_ok}/{len(lines) if k<=13 else 0}"
          + (f"  *** OVER {over}" if over else ""), flush=True)
print(f"\nglobal max exact psi found = {gmax:.12f}  ({time.time()-t0:.0f}s)")
