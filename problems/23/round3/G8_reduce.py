"""G8: reduced coordinates for the Wagner 5-cut inequality, and an independent
second implementation of the product q1q2q3q4q5.

Substitution (Moebius-ladder / antipodal folding).  For a in R^8_{>=0} put
    m_i = a_i + a_{i+4},   a_i = m_i(1+c_i)/2,  a_{i+4} = m_i(1-c_i)/2,  i=0,1,2,3,
so m_i >= 0, c_i in [-1,1], and sum_i m_i = sum_v a_v.  Then EXACTLY

  q3 = a0a1+a4a5 = m_0m_1(1+c_0c_1)/2
  q2 = a1a2+a5a6 = m_1m_2(1+c_1c_2)/2
  q4 = a2a3+a6a7 = m_2m_3(1+c_2c_3)/2
  q1 = a3a4+a7a0 = m_3m_0(1-c_3c_0)/2      <-- the Moebius twist: MINUS sign
  q5 = a0a4+a1a5+a2a6+a3a7 = sum_i m_i^2(1-c_i^2)/4

so   q1q2q3q4q5 = (m_0m_1m_2m_3)^2 * P(c) * S(m,c) / 64
with P(c) = (1+c_0c_1)(1+c_1c_2)(1+c_2c_3)(1-c_3c_0),  S = sum_i m_i^2(1-c_i^2).

The odd number of minus signs around the 4-cycle is exactly the obstruction that
makes And(3) = C8(1,4) non-C5-colourable: the four factors of P cannot all be
simultaneously maximised (sign product must be +1 but is required to be -1).

CONJECTURED (verified numerically + on all integer weightings up to q=32):
   (m_0m_1m_2m_3)^2 P(c) S(m,c) <= 64/5^10   whenever sum m_i = 1.
"""
import sys
from fractions import Fraction
import numpy as np

Q = [((0, 7), (3, 4)), ((1, 2), (5, 6)), ((0, 1), (4, 5)), ((2, 3), (6, 7)),
     ((0, 4), (1, 5), (2, 6), (3, 7))]


def prodq_direct(a):
    p = Fraction(1)
    for pairs in Q:
        p *= sum(a[u] * a[v] for (u, v) in pairs)
    return p


def prodq_reduced(a):
    """same quantity via the (m,c) substitution, exact rationals"""
    m = [a[i] + a[i + 4] for i in range(4)]
    if any(x == 0 for x in m):
        return None
    c = [Fraction(a[i] - a[i + 4], 1) / m[i] for i in range(4)]
    P = (1 + c[0] * c[1]) * (1 + c[1] * c[2]) * (1 + c[2] * c[3]) * (1 - c[3] * c[0])
    S = sum(m[i] ** 2 * (1 - c[i] ** 2) for i in range(4))
    return (m[0] * m[1] * m[2] * m[3]) ** 2 * P * S / 64


def Phi(z):
    m = np.abs(z[:4]); s = m.sum()
    if s <= 0:
        return 0.0
    m = m / s
    c = np.clip(z[4:], -1, 1)
    P = (1 + c[0] * c[1]) * (1 + c[1] * c[2]) * (1 + c[2] * c[3]) * (1 - c[3] * c[0])
    S = float(np.sum(m ** 2 * (1 - c ** 2)))
    return float(np.prod(m) ** 2 * P * S)


if __name__ == "__main__":
    import random
    random.seed(17)
    print("identity check (exact rationals), direct vs reduced:")
    bad = 0
    for t in range(400):
        a = [Fraction(random.randint(0, 9)) for _ in range(8)]
        r = prodq_reduced(a)
        if r is None:
            continue
        if r != prodq_direct(a):
            bad += 1
            print("   MISMATCH", a, prodq_direct(a), r)
    print(f"   mismatches: {bad} / 400   (0 = substitution verified exactly)")

    from scipy.optimize import minimize
    target = 64.0 / 5 ** 10
    rng = np.random.default_rng(23)
    best = (-1.0, None)
    for t in range(6000):
        z0 = np.concatenate([rng.dirichlet(np.ones(4) * rng.uniform(0.2, 3.0)),
                             rng.uniform(-1, 1, 4)])
        r = minimize(lambda z: -Phi(z), z0, method='Nelder-Mead',
                     options={'maxiter': 2000, 'fatol': 1e-18, 'xatol': 1e-12})
        v = Phi(r.x)
        if v > best[0]:
            best = (v, r.x.copy())
    m = np.abs(best[1][:4]); m /= m.sum(); c = np.clip(best[1][4:], -1, 1)
    print(f"\nmax_(m,c) Phi = {best[0]:.12e}   target 64/5^10 = {target:.12e}"
          f"   ratio = {best[0]/target:.9f}")
    print(f"   m = {np.round(m,6)}   c = {np.round(c,6)}")
    print(f"   => max_simplex q1q2q3q4q5 = Phi/64 = {best[0]/64:.9e}, "
          f"25^-5 = {25.0**-5:.9e}")
