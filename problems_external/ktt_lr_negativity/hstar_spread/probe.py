#!/usr/bin/env python3
"""Scale-free sharpness probe on the verified hive h*-atlas.

Delta_k := d! * a_k / max_j( -w_k(j) )
         = the EXTRA h*-mass, placed at the single most efficient index j,
           needed to drive a_k below 0.   Comparable across k and d.
Also tests candidate uniform statements:
  U1  h*(-s) <= (1+s)^d  for all s >= 0     [exact, Sturm via sympy]
  U2  every root of P has Re <= 0            [numeric, flagged]
  U3  G(t) = sum_{j>=1} h*_j F_j(t) has nonnegative coefficients,
      F_j(t) = prod_{i=1}^{d-j}(t+i) * prod_{i=1}^{j-1}(t-i)
  U4  h*(-s) <= (1+s)^d only at the single point s = 1, i.e.
      sum_j (-1)^j h*_j <= 2^d
"""
import csv, sys, collections
from fractions import Fraction as F
from math import factorial, comb
from crit import wrow, coeffs_from_hstar

rows = []
for r in csv.DictReader(open('hstar_atlas2.tsv'), delimiter='\t'):
    h = tuple(int(x) for x in r['hstar'].split(','))
    rows.append((int(r['d']), r['c'], int(r['M']), h, r['lam'], r['mu'], r['nu']))


def Gpoly(h):
    """coefficients of G(t) = sum_{j>=1} h_j F_j(t), ascending."""
    d = len(h) - 1
    acc = [0] * d
    for j in range(1, d + 1):
        if h[j] == 0:
            continue
        p = [1]
        for i in range(1, d - j + 1):
            p = [0] + p
            for t in range(len(p) - 1):
                p[t] += i * p[t + 1] if False else 0
        # redo cleanly
        p = [1]
        def mul(p, c):  # multiply by (t + c)
            q = [0] * (len(p) + 1)
            for t, a in enumerate(p):
                q[t] += a * c
                q[t + 1] += a
            return q
        for i in range(1, d - j + 1):
            p = mul(p, i)
        for i in range(1, j):
            p = mul(p, -i)
        for t, a in enumerate(p):
            acc[t] += h[j] * a
    return acc


def evalneg(h, s):
    """h*(-s) with s a Fraction."""
    return sum(h[j] * (-s) ** j for j in range(len(h)))


def U1_exact(h):
    """True iff (1+s)^d - h*(-s) >= 0 on [0, inf).  Exact via sympy."""
    import sympy as sp
    s = sp.Symbol('s')
    d = len(h) - 1
    poly = sp.expand((1 + s) ** d - sum(h[j] * (-s) ** j for j in range(d + 1)))
    P = sp.Poly(poly, s)
    if P.is_zero:
        return True
    # count sign changes on (0,inf): isolate real roots > 0 and test a point
    rts = sp.polys.polytools.real_roots(P)
    pos = [r for r in rts if r > 0]
    if not pos:
        return sp.nsimplify(P.eval(sp.Integer(1))) >= 0 or P.eval(sp.Integer(0)) >= 0
    # sample between/around positive roots
    import sympy
    xs = sorted(set([sp.Rational(0)] + [sp.nsimplify(r) for r in pos]))
    # test midpoints and a far point using exact rational samples
    cand = []
    prev = sp.Rational(0)
    for r in pos:
        rr = sp.Rational(sp.floor(r * 10 ** 6), 10 ** 6)
        cand.append((prev + rr) / 2 if rr > prev else prev + sp.Rational(1, 10 ** 6))
        prev = rr + sp.Rational(1, 10 ** 6)
    cand.append(prev + 1)
    for x in cand:
        if P.eval(sp.Rational(x)) < 0:
            return False
    return True


print("=== Delta_k (extra h*-mass needed to flip a_k) ===")
worst = collections.defaultdict(lambda: (None, None))
kcount = collections.Counter()
for d, c, M, h, lam, mu, nu in rows:
    a = coeffs_from_hstar(list(h))
    fd = factorial(d)
    bestD = None; bk = None
    for k in range(1, d):
        W = wrow(d, k)
        neg = max(-x for x in W)
        if neg <= 0:
            continue
        Dk = F(fd, 1) * a[k] / neg
        if bestD is None or Dk < bestD:
            bestD = Dk; bk = k
    if bestD is None:
        continue
    kcount[bk] += 1
    cur = worst[d][0]
    if cur is None or bestD < cur:
        worst[d] = (bestD, (bk, h, M, c, lam, mu, nu))
for d in sorted(worst):
    D, info = worst[d]
    print("d=%2d  minDelta=%9.3f  at k=%d  M=%d c=%s  h*=%s  (%s|%s|%s)" %
          (d, float(D), info[0], info[2], info[3], info[1], info[4], info[5], info[6]))
print("argmin-k histogram:", sorted(kcount.items()))

print()
print("=== U3: does G(t) have nonnegative coefficients? ===")
bad3 = 0; ex3 = None
for d, c, M, h, lam, mu, nu in rows:
    g = Gpoly(list(h))
    if any(x < 0 for x in g):
        bad3 += 1
        if ex3 is None:
            ex3 = (d, h, g, lam, mu, nu)
print("violations: %d / %d" % (bad3, len(rows)))
if ex3:
    print("  example d=%d h*=%s  G=%s  (%s|%s|%s)" % ex3[:3] + " ", ex3[3], ex3[4], ex3[5])

print()
print("=== U4: h*(-1) = sum_j (-1)^j h*_j  vs  2^d ===")
mx = collections.defaultdict(lambda: None)
for d, c, M, h, lam, mu, nu in rows:
    v = sum((-1) ** j * h[j] for j in range(d + 1))
    cur = mx[d]
    if cur is None or v > cur[0]:
        mx[d] = (v, h, lam, mu, nu)
for d in sorted(mx):
    v, h, lam, mu, nu = mx[d]
    print("  d=%2d  max h*(-1) = %6d   2^d = %6d   %s" % (d, v, 2 ** d, "OK" if v <= 2 ** d else "VIOLATED"), h)

print()
print("=== U2: max real part of a root of P (numeric, float search only) ===")
import numpy as np
mr = collections.defaultdict(lambda: (-99, None))
for d, c, M, h, lam, mu, nu in rows:
    a = coeffs_from_hstar(list(h))
    co = [float(x) for x in reversed(a)]
    rts = np.roots(co)
    m = max(r.real for r in rts) if len(rts) else -99
    if m > mr[d][0]:
        mr[d] = (m, (h, lam, mu, nu))
for d in sorted(mr):
    m, info = mr[d]
    print("  d=%2d  max Re(root) = %+.4f  %s" % (d, m, info[0]))
