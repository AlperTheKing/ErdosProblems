#!/usr/bin/env python3
"""Sharpness probe #2.  N_k := d! * a_k = sum_j h*_j w_k(j) is an INTEGER,
so "a_k >= 0" is the integer statement N_k >= 0 and the sharpest possible
form is N_k >= (its true minimum).  Measure that minimum over the corpus.
Also: U1 (h*(-s) <= (1+s)^d), U3 (G nonneg), U4 (h*(-1) <= 2^d), U2 (roots).
"""
import csv, collections
from fractions import Fraction as F
from math import factorial
from crit import wrow

rows = []
for r in csv.DictReader(open('hstar_atlas2.tsv'), delimiter='\t'):
    h = tuple(int(x) for x in r['hstar'].split(','))
    rows.append((int(r['d']), r['c'], int(r['M']), h, r['lam'], r['mu'], r['nu']))

print("=== min of the integer N_k = d! a_k, per (d,k) ===")
mn = {}
for d, c, M, h, lam, mu, nu in rows:
    for k in range(1, d):
        W = wrow(d, k)
        N = sum(h[j] * W[j] for j in range(d + 1))
        key = (d, k)
        if key not in mn or N < mn[key][0]:
            mn[key] = (N, h, M, c, lam, mu, nu)
for d in sorted(set(k[0] for k in mn)):
    line = []
    for k in range(1, d):
        line.append("k=%d:%d" % (k, mn[(d, k)][0]))
    print(" d=%2d  " % d + "  ".join(line))
print()
print(" the three globally smallest N_k records:")
srt = sorted(mn.items(), key=lambda kv: kv[1][0])[:6]
for (d, k), (N, h, M, c, lam, mu, nu) in srt:
    print("  d=%d k=%d N=%d  M=%d c=%s h*=%s  (%s|%s|%s)" % (d, k, N, M, c, h, lam, mu, nu))

print()
print("=== normalised: N_k / M  (slack per unit normalised volume) ===")
mn2 = {}
for d, c, M, h, lam, mu, nu in rows:
    for k in range(1, d):
        W = wrow(d, k)
        N = F(sum(h[j] * W[j] for j in range(d + 1)), M)
        key = (d, k)
        if key not in mn2 or N < mn2[key][0]:
            mn2[key] = (N, h, M, c, lam, mu, nu)
glob = sorted(mn2.items(), key=lambda kv: kv[1][0])[:8]
for (d, k), (N, h, M, c, lam, mu, nu) in glob:
    print("  d=%d k=%d N/M=%.4f  M=%d c=%s h*=%s  (%s|%s|%s)" % (d, k, float(N), M, c, h, lam, mu, nu))

print()
print("=== U4: h*(-1) vs 2^d  (single-point form of U1) ===")
mx = {}
for d, c, M, h, lam, mu, nu in rows:
    v = sum((-1) ** j * h[j] for j in range(d + 1))
    if d not in mx or v > mx[d][0]:
        mx[d] = (v, h, lam, mu, nu)
for d in sorted(mx):
    v, h, lam, mu, nu = mx[d]
    print("  d=%2d max h*(-1)=%6d  2^d=%6d  %s   h*=%s" %
          (d, v, 2 ** d, "OK" if v <= 2 ** d else "VIOLATED", h))

print()
print("=== U1 exact: is (1+s)^d - h*(-s) >= 0 on [0,inf)? ===")
import sympy as sp
s = sp.Symbol('s')
bad = []
for d, c, M, h, lam, mu, nu in rows:
    p = sp.Poly(sp.expand((1 + s) ** d - sum(h[j] * (-s) ** j for j in range(d + 1))), s)
    if p.is_zero:
        continue
    # number of real roots in (0, oo) counted with sign changes:
    # p >= 0 on [0,oo) iff p has no root of odd multiplicity in (0,oo) and p(0)>=0
    try:
        n = p.count_roots(0, sp.oo)
    except Exception:
        n = None
    neg = False
    if n:
        # sample: if any exact rational sample is negative -> violated
        for x in [sp.Rational(i, 8) for i in range(1, 200)]:
            if p.eval(x) < 0:
                neg = True
                break
    if neg:
        bad.append((d, h, lam, mu, nu))
print("  violations: %d / %d" % (len(bad), len(rows)))
for b in bad[:6]:
    print("   ", b)


def Gpoly(h):
    d = len(h) - 1
    acc = [0] * d
    def mul(p, c):
        q = [0] * (len(p) + 1)
        for t, a in enumerate(p):
            q[t] += a * c
            q[t + 1] += a
        return q
    for j in range(1, d + 1):
        if h[j] == 0:
            continue
        p = [1]
        for i in range(1, d - j + 1):
            p = mul(p, i)
        for i in range(1, j):
            p = mul(p, -i)
        for t, a in enumerate(p):
            acc[t] += h[j] * a
    return acc


print()
print("=== U3: G(t) = sum_{j>=1} h*_j F_j(t) nonnegative coefficients? ===")
badG = []
for d, c, M, h, lam, mu, nu in rows:
    g = Gpoly(list(h))
    if any(x < 0 for x in g):
        badG.append((d, h, g, lam, mu, nu))
print("  violations: %d / %d" % (len(badG), len(rows)))
for b in badG[:6]:
    print("    d=%d h*=%s G=%s (%s|%s|%s)" % b)
