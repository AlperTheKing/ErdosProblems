"""AUDIT of G8 section 4 (numeric ceiling).  Own optimiser, own cut enumeration.
Protocol required by accepted fact 3: evaluate the induced-C5 uniform point FIRST
(exact Fractions) and check the optimiser matches or beats it.
"""
import sys, itertools
import numpy as np
from fractions import Fraction
from audit_G8_core import and_circulant, edges_of, all_cut_monos, psi_exact


def numeric_max_psi(k, ntrial=300, seed=99):
    n, adjm = and_circulant(k)
    E = edges_of(n, adjm)
    N = 1 << (n - 1)
    masks = np.arange(N, dtype=np.uint32)
    side = np.zeros((n, N), dtype=np.uint8)
    for v in range(1, n):
        side[v] = ((masks >> (v - 1)) & 1).astype(np.uint8)
    mono = np.zeros((len(E), N), dtype=np.uint8)
    for i, (u, v) in enumerate(E):
        mono[i] = (side[u] == side[v])

    monof = mono.astype(np.float64)

    def psi(x):
        w = np.array([x[u] * x[v] for (u, v) in E])
        return float(w.dot(monof).min())

    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    cons = [{'type': 'eq', 'fun': lambda z: float(np.sum(z) - 1.0)}]
    best = (-1.0, None)
    for t in range(ntrial):
        x0 = rng.dirichlet(np.ones(n) * rng.uniform(0.1, 3.0))
        r = minimize(lambda z: -psi(np.clip(z, 0, None)), x0, method='SLSQP',
                     bounds=[(0, 1)] * n, constraints=cons,
                     options={'maxiter': 250, 'ftol': 1e-16})
        x = np.clip(r.x, 0, None)
        s = x.sum()
        if s <= 0:
            continue
        x = x / s
        v = psi(x)
        if v > best[0]:
            best = (v, x.copy())
    return n, E, best


if __name__ == "__main__":
    for k in (3, 4, 5):
        n, adjm = and_circulant(k)
        E = edges_of(n, adjm)
        # exact induced-C5 point first (accepted fact 3 protocol)
        c5 = None
        for S in itertools.combinations(range(n), 5):
            Ss = set(S)
            sub = [(u, v) for (u, v) in E if u in Ss and v in Ss]
            if len(sub) == 5:
                deg = {v: 0 for v in S}
                for (u, v) in sub:
                    deg[u] += 1
                    deg[v] += 1
                if all(d == 2 for d in deg.values()):
                    c5 = S
                    break
        monos = all_cut_monos(n, E)
        x = [Fraction(0)] * n
        for v in c5:
            x[v] = Fraction(1, 5)
        exact = psi_exact(monos, x)
        nn, EE, (v, xx) = numeric_max_psi(k, ntrial=(200 if k <= 4 else 60))
        print(f"And({k}) n={n}: exact psi at induced-C5 point {c5} = {exact} "
              f"({float(exact):.10f});  numeric max over simplex = {v:.10f}  "
              f"{'>= C5 point OK' if v >= float(exact) - 1e-12 else '*** BELOW C5 POINT: LOCAL OPTIMUM ***'}"
              f"  {'*** EXCEEDS 1/25 ***' if v > 0.04 + 1e-9 else ''}")
        sys.stdout.flush()
