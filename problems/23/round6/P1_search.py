"""Falsification search for  (STAR)   min(A, B) <= 1/25.

A(x)   = sum over edges of x_i x_j (1 - 2 d_ij)                        [half-arc average]
B_p(x) = mass of edges avoiding the closed 1/3-window starting at p    [1/3-arc cut at window p]
B(x)   = min_p B_p(x)

Both are quadratic forms on the simplex over the grid Gamma_q, so this is a max-min of
quadratic forms; SLSQP from many random starts, then EXACT rational re-verification of every
finalist that gets anywhere near 1/25.

Usage:  python P1_search.py [q ...]
"""
import sys
import numpy as np
from fractions import Fraction as F
from scipy.optimize import minimize

from P1_engine import Meas, TARGET

rng = np.random.default_rng(20260725)


def forms(q):
    """edge list with (1-2d) weights, and the window-avoidance masks."""
    pos = np.arange(q) / q
    E = []
    for i in range(q):
        for j in range(i + 1, q):
            dd = min((j - i) % q, (i - j) % q) / q
            if dd > 1 / 3 + 1e-15:
                E.append((i, j, dd))
    ei = np.array([e[0] for e in E])
    ej = np.array([e[1] for e in E])
    ed = np.array([e[2] for e in E])
    w = q // 3          # window p contains indices p..p+w  (offset/q <= 1/3)
    avoid = np.zeros((q, len(E)), dtype=bool)
    for p in range(q):
        inI = np.zeros(q, dtype=bool)
        for t in range(w + 1):
            inI[(p + t) % q] = True
        avoid[p] = ~inI[ei] & ~inI[ej]
    return ei, ej, ed, avoid


def make_objs(q):
    ei, ej, ed, avoid = forms(q)
    coefA = 1 - 2 * ed

    def vals(x):
        pe = x[ei] * x[ej]
        A = float(pe @ coefA)
        Bs = avoid @ pe
        return A, Bs

    return vals, (ei, ej, ed, avoid)


def search(q, tries=400, verbose=False):
    vals, (ei, ej, ed, avoid) = make_objs(q)
    coefA = 1 - 2 * ed
    best = (-1, None)
    for t in range(tries):
        k = rng.integers(3, min(q, 12) + 1)
        sup = rng.choice(q, size=k, replace=False)
        x0 = np.zeros(q)
        x0[sup] = rng.random(k) + 0.2
        x0 /= x0.sum()
        z0 = np.append(x0, 0.0)

        def negt(z):
            return -z[-1]

        def cons_f(z):
            x = z[:-1]
            pe = x[ei] * x[ej]
            A = pe @ coefA
            Bs = avoid @ pe
            return np.append(np.append(Bs, A) - z[-1], [1 - x.sum()])

        m = len(avoid) + 1
        cons = [{'type': 'ineq', 'fun': lambda z: cons_f(z)[:m]},
                {'type': 'eq', 'fun': lambda z: cons_f(z)[m]}]
        bnds = [(0, 1)] * q + [(0, 0.2)]
        try:
            r = minimize(negt, z0, bounds=bnds, constraints=cons, method='SLSQP',
                         options={'maxiter': 300, 'ftol': 1e-12})
        except Exception:
            continue
        x = np.maximum(r.x[:-1], 0)
        s = x.sum()
        if s <= 0:
            continue
        x /= s
        A, Bs = vals(x)
        v = min(A, Bs.min())
        if v > best[0]:
            best = (v, x.copy())
            if verbose:
                print(f"   q={q} try={t} min(A,B)={v:.8f}")
    return best


def exact_check(q, x, tol=1e-9):
    """rationalise the float optimum on Gamma_q and verify exactly."""
    w = [F(int(round(v * 10 ** 9)), 10 ** 9) for v in x]
    mu = Meas([F(k, q) for k in range(q)], w)
    return mu


if __name__ == '__main__':
    qs = [int(a) for a in sys.argv[1:]] or [5, 7, 8, 11, 12, 15, 18, 20, 24, 25, 30, 35, 40, 45, 60]
    print("maximising min(A,B) over the simplex on Gamma_q   (target: never exceeds 1/25 = 0.04)")
    overall = (-1, None, None)
    for q in qs:
        v, x = search(q, tries=250 if q <= 30 else 150)
        mu = exact_check(q, x)
        ex = min(mu.A, mu.B)
        print(f"q={q:3d}  float max min(A,B) = {v:.8f}   exact at rationalised point: "
              f"{float(ex):.8f}  {'<= 1/25 OK' if ex <= TARGET else '*** EXCEEDS ***'}"
              f"   [W={float(mu.W):.5f} n={mu.n}]")
        if v > overall[0]:
            overall = (v, q, x)
    print(f"\nglobal float maximum over all q: {overall[0]:.8f} at q={overall[1]}  (1/25 = 0.04)")
    xs = overall[2]
    nz = [(i, xi) for i, xi in enumerate(xs) if xi > 1e-6]
    print("support (index/q, weight):", [(f"{i}/{overall[1]}", round(w, 6)) for i, w in nz])
