"""G8: the five surviving cuts of And(3) = Wagner = C8(1,4) and the certificate
    psi(x) <= min_j q_j(x) <= (q_1 q_2 q_3 q_4 q_5)^{1/5} <= 1/25 ?

Wagner: Z_8, cycle edges i~i+1, rungs i~i+4.
  q1 = x0x7 + x3x4      (cut {1,3,4,6})
  q2 = x1x2 + x5x6      (cut {1,2,4,7}-ish)
  q3 = x0x1 + x4x5
  q4 = x2x3 + x6x7
  q5 = x0x4 + x1x5 + x2x6 + x3x7   (alternating cut of the 8-cycle)
Each pairs ANTIPODAL cycle edges; q5 collects the rungs.
"""
import sys, itertools, random
from fractions import Fraction
import numpy as np

Q = [((0, 7), (3, 4)), ((1, 2), (5, 6)), ((0, 1), (4, 5)), ((2, 3), (6, 7)),
     ((0, 4), (1, 5), (2, 6), (3, 7))]


def qs(x):
    return [sum(x[u] * x[v] for (u, v) in pairs) for pairs in Q]


def minq(x):
    return min(qs(x))


def prodq(x):
    p = 1.0
    for v in qs(x):
        p *= v
    return p


def maximise(fun, n=8, ntrial=4000, seed=5):
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    best = (-1.0, None)
    cons = [{'type': 'eq', 'fun': lambda z: float(np.sum(z) - 1.0)}]
    for t in range(ntrial):
        x0 = rng.dirichlet(np.ones(n) * rng.uniform(0.1, 3.0))
        r = minimize(lambda z: -fun(np.clip(z, 0, None)), x0, constraints=cons,
                     bounds=[(0, 1)] * n, method='SLSQP',
                     options={'maxiter': 400, 'ftol': 1e-16})
        x = np.clip(r.x, 0, None); s = x.sum()
        if s <= 0:
            continue
        x = x / s
        v = fun(x)
        if v > best[0]:
            best = (v, x.copy())
    return best


if __name__ == "__main__":
    print("target min:  1/25 =", 1 / 25)
    print("target prod: 25^-5 =", 25.0 ** -5)
    v, x = maximise(minq)
    print(f"max_simplex min_j q_j  = {v:.12f}   at {np.round(x,6)}")
    v2, x2 = maximise(prodq)
    print(f"max_simplex prod_j q_j = {v2:.6e}   (25^-5 = {25.0**-5:.6e})  at {np.round(x2,6)}")
    print(f"   ratio prod/25^-5 = {v2/(25.0**-5):.9f}")

    # exhaustive exact check on integer weightings
    print("\nexact integer check: max over a>=0, sum a = q, of 25*min_j q_j(a) - q^2")
    for q in range(1, 26):
        st = {'best': None, 'arg': None}

        def rec(i, rem, cur):
            if i == 7:
                cur.append(rem)
                val = min(sum(cur[u] * cur[v] for (u, v) in pairs) for pairs in Q)
                if st['best'] is None or val > st['best']:
                    st['best'] = val; st['arg'] = list(cur)
                cur.pop()
                return
            for t in range(rem + 1):
                cur.append(t); rec(i + 1, rem - t, cur); cur.pop()
        rec(0, q, [])
        best, barg = st['best'], st['arg']
        flag = "  *** VIOLATION ***" if 25 * best > q * q else ""
        print(f"  q={q:2d}  max min_j q_j = {best:4d}   25*val={25*best:5d}  q^2={q*q:5d}"
              f"  {barg}{flag}")
        sys.stdout.flush()
