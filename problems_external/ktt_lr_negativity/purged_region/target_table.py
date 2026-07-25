#!/usr/bin/env python3
"""Exact target table: minimum V = Sum h* admitting a strictly negative
monomial coefficient, as a function of (d, h*_1) and of (d, h*_1, s=deg h*).

[n^k]P = (1/d!) sum_j h*_j e_{d-k}(d-j, d-j-1, ..., 1-j).
All integer arithmetic.  Extra mass beyond h*_0 = 1 and the fixed h*_1 goes to
the index j minimising the weight (a single index is optimal for one linear
constraint), so the minimum is exact, not a bound.
"""
from fractions import Fraction
from math import comb


def esym(vals, m):
    e = [0] * (len(vals) + 1)
    e[0] = 1
    for v in vals:
        for i in range(len(vals), 0, -1):
            e[i] += e[i - 1] * v
    return e[m]


def weights(d, k):
    # w_j = e_{d-k}( d-j, d-j-1, ..., 1-j )
    return [esym([d - j - i for i in range(d)], d - k) for j in range(d + 1)]


def minV(d, a, smax=None):
    """min Sum h* with h*_0=1, h*_1=a, deg h* <= smax, some [n^k]P < 0."""
    best = None
    for k in range(1, d):                      # k=0 gives 1; k=d gives V/d! > 0
        w = weights(d, k)
        f = w[0] + a * w[1]
        hi = d if smax is None else min(d, smax)
        for j in range(2, hi + 1):
            if w[j] >= 0:
                continue
            need = f + 1
            m = 0 if need <= 0 else -(-need // (-w[j]))
            V = 1 + a + m
            if best is None or V < best[0]:
                best = (V, k, j, m)
    return best


def check_poly(d, h):
    """monomial coefficients of P from h*"""
    co = [Fraction(0)] * (d + 1)
    for j, hj in enumerate(h):
        if hj == 0:
            continue
        # C(n+d-j,d) = (1/d!) prod_{i=0}^{d-1} (n + d-j-i)
        vals = [d - j - i for i in range(d)]
        for k in range(d + 1):
            co[k] += Fraction(hj * esym(vals, d - k), 1)
    return [c / __import__('math').factorial(d) for c in co]


print("=== unrestricted deg h*: min V per (d, h*_1) ===")
print("d  " + "  ".join("h1=%d" % a for a in range(5)))
for d in range(2, 13):
    row = []
    for a in range(5):
        r = minV(d, a)
        row.append("-" if r is None else str(r[0]))
    print("%-3d" % d + "  ".join("%5s" % x for x in row))

print()
print("=== deg h* <= 2 (the only regime observed at h*_1 <= 2) ===")
print("d  " + "  ".join("h1=%d" % a for a in range(5)))
for d in range(2, 13):
    row = []
    for a in range(5):
        r = minV(d, a, smax=2)
        row.append("-" if r is None else str(r[0]))
    print("%-3d" % d + "  ".join("%5s" % x for x in row))

print()
print("=== cheapest witness h* at h*_1 = 0, unrestricted s ===")
for d in range(2, 13):
    r = minV(d, 0)
    if r is None:
        print(d, "none")
        continue
    V, k, j, m = r
    h = [0] * (d + 1)
    h[0] = 1
    h[j] = m
    co = check_poly(d, h)
    print("d=%-2d V=%-3d h*=%s  neg at n^%d  coeff=%s" % (d, V, h, k, co[k]))

print()
print("=== sanity: Reeve T13 h*=(1,0,12,0) d=3 ===")
print(check_poly(3, [1, 0, 12, 0]))
print("=== sanity: hive refuter h*=(1,0,1,0,0) d=4 ===")
print(check_poly(4, [1, 0, 1, 0, 0]))
