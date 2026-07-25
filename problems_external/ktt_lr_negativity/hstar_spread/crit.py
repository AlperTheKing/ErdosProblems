#!/usr/bin/env python3
"""
crit.py -- EXACT per-coefficient negativity criterion for an Ehrhart
polynomial given its h*-vector.  All arithmetic exact (int / Fraction).

THEOREM (derived here, verified numerically below).
Let P(n) = sum_{j=0}^{d} h_j * C(n+d-j, d).  Then for every k,

    a_k := [n^k] P  =  (1/d!) * sum_{j=0}^{d} h_j * w_k(j),
    w_k(j) := e_{d-k}(1-j, 2-j, ..., d-j)          (elementary symmetric)
            = [n^k] prod_{m=1}^{d} (n + m - j).

Equivalent "moment" form.  Put u_j := 2j-(d+1) and let <.> be the h-weighted
average (total mass M = sum_j h_j = normalized volume).  With
Q(y) := prod_{m=1}^{d}(y + m - (d+1)/2) = sum_i q_i y^{d-2i}   (q_0=1;
q_i = (-1)^i e_i of the squares {((d-1)/2)^2, ((d-3)/2)^2, ...}), one has
C(n+d-j,d) = Q(n - u_j/2)/d!, hence

    d! * a_k / M = sum_{p >= 0, p == d-k (mod 2), p <= d-k}
                        (-1/2)^p * C(k+p, k) * q_{(d-k-p)/2} * <u^p>.

Specialisations (match the project's established facts F1):
    k = d-1 :  a_{d-1} < 0  <=>  <u>   > 0
    k = d-2 :  a_{d-2} < 0  <=>  <u^2> < (d+1)/3
"""
from fractions import Fraction
from functools import lru_cache
from math import factorial


def esym(vals, m):
    """Exact elementary symmetric polynomial e_m of a list of ints."""
    e = [1] + [0] * m
    for v in vals:
        for i in range(min(m, len(e) - 1), 0, -1):
            e[i] += e[i - 1] * v
    return e[m]


@lru_cache(maxsize=None)
def wrow(d, k):
    """(w_k(0), ..., w_k(d)) as a tuple of ints."""
    return tuple(esym([m - j for m in range(1, d + 1)], d - k) for j in range(d + 1))


@lru_cache(maxsize=None)
def wmat(d):
    return tuple(wrow(d, k) for k in range(d + 1))


def coeffs_from_hstar(h):
    """Exact monomial coefficients a_0..a_d of P from h*-vector h."""
    d = len(h) - 1
    W = wmat(d)
    f = factorial(d)
    return [Fraction(sum(h[j] * W[k][j] for j in range(d + 1)), f) for k in range(d + 1)]


def hstar_from_values(P, d):
    """h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i) from P(0..d)."""
    from math import comb
    return [sum((-1) ** i * comb(d + 1, i) * P[j - i] for i in range(j + 1))
            for j in range(d + 1)]


def qcoeffs(d):
    """q_i with Q(y) = prod_{m=1}^d (y+m-(d+1)/2) = sum_i q_i y^{d-2i}."""
    # exact with Fractions since half-integers appear when d is even
    poly = [Fraction(1)]  # ascending
    for m in range(1, d + 1):
        c = Fraction(2 * m - d - 1, 2)
        new = [Fraction(0)] * (len(poly) + 1)
        for i, a in enumerate(poly):
            new[i] += a * c
            new[i + 1] += a
        poly = new
    # poly[t] = coeff of y^t ; q_i = poly[d-2i]
    return [poly[d - 2 * i] for i in range(d // 2 + 1)]


def moments(h, pmax):
    """<u^p> for p=0..pmax, exact Fractions.  u_j = 2j-(d+1)."""
    d = len(h) - 1
    M = sum(h)
    out = []
    for p in range(pmax + 1):
        s = sum(h[j] * (2 * j - d - 1) ** p for j in range(d + 1))
        out.append(Fraction(s, M))
    return out


def coeff_from_moments(h, k):
    """a_k via the moment formula (independent recomputation)."""
    from math import comb
    d = len(h) - 1
    M = sum(h)
    q = qcoeffs(d)
    mom = moments(h, d - k)
    tot = Fraction(0)
    for p in range(d - k, -1, -2):
        i = (d - k - p) // 2
        tot += Fraction((-1) ** p, 2 ** p) * comb(k + p, k) * q[i] * mom[p]
    return tot * M / factorial(d)


def ratio_R(h, k):
    """R_k = (negative-weight mass) / (positive-weight mass) for functional w_k.
    a_k >= 0  <=>  R_k <= 1.   Returns None if positive part is 0."""
    d = len(h) - 1
    W = wrow(d, k)
    pos = sum(h[j] * W[j] for j in range(d + 1) if W[j] > 0)
    neg = sum(-h[j] * W[j] for j in range(d + 1) if W[j] < 0)
    if pos == 0:
        return None
    return Fraction(neg, pos)


# ------------------------------------------------------------------ selftest
if __name__ == "__main__":
    from math import comb
    ok = True

    def chk(cond, msg):
        global ok
        if not cond:
            ok = False
            print("FAIL:", msg)

    # 1. Reeve tetrahedron T_q: h* = (1,0,q-1,0), a_1 = 2 - q/6.
    for q in range(1, 40):
        h = [1, 0, q - 1, 0]
        a = coeffs_from_hstar(h)
        chk(a[1] == Fraction(12 - q, 6), f"Reeve q={q} a1={a[1]}")
        chk(a[3] == Fraction(q, 6), f"Reeve q={q} a3")
        chk(a[0] == 1, "Reeve a0")
        chk(coeff_from_moments(h, 1) == a[1], f"Reeve moment form q={q}")
        m = moments(h, 2)
        chk(m[2] == Fraction(16, q), f"Reeve <u^2> q={q} = {m[2]}")
        chk((a[1] < 0) == (m[2] < Fraction(4, 3)), f"Reeve F1 k=d-2 q={q}")
        chk((a[2] < 0) == (m[1] > 0), f"Reeve F1 k=d-1 q={q}")

    # 2. random h*, cross-check the three routes against direct expansion
    import random
    random.seed(7)
    for _ in range(400):
        d = random.randint(1, 9)
        h = [1] + [random.randint(0, 6) for _ in range(d)]
        a = coeffs_from_hstar(h)
        # direct: expand sum h_j C(n+d-j,d) by polynomial arithmetic
        acc = [Fraction(0)] * (d + 1)
        for j, hj in enumerate(h):
            poly = [Fraction(1)]
            for m in range(1, d + 1):
                c = Fraction(m - j)
                new = [Fraction(0)] * (len(poly) + 1)
                for i, x in enumerate(poly):
                    new[i] += x * c
                    new[i + 1] += x
                poly = new
            for t in range(d + 1):
                acc[t] += hj * poly[t] / factorial(d)
        chk(acc == a, f"direct expansion d={d}")
        for k in range(d + 1):
            chk(coeff_from_moments(h, k) == a[k], f"moment form d={d} k={k}")
            r = ratio_R(h, k)
            if r is not None:
                chk((a[k] < 0) == (r > 1), f"ratio form d={d} k={k}")
        # value check at several n
        for n in range(0, 6):
            v = sum(h[j] * comb(n + d - j, d) for j in range(d + 1))
            pv = sum(a[t] * n ** t for t in range(d + 1))
            chk(pv == v, f"value d={d} n={n}")

    print("SELFTEST", "PASS" if ok else "FAIL")
