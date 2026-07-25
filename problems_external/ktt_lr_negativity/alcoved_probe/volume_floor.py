#!/usr/bin/env python3
"""
EXACT NECESSARY CONDITION (volume floor) for ANY negative Ehrhart coefficient.

Write P(n) = sum_{j=0}^{d} h*_j C(n+d-j, d) and w_k[j] := [n^k] C(n+d-j, d)
(exact rationals).  Then a_k = sum_j h*_j w_k[j], with h*_0 = 1 and h*_j >= 0.
Hence

    a_k < 0   =>   sum_{j>=1} h*_j * max(0, -w_k[j])  >  w_k[0]
              =>   V * max_j(-w_k[j])                 >  w_k[0]      (V = sum h*)
              =>   V  >  w_k[0] / max_{j>=1} (-w_k[j])   =:  Vfloor(d, k)

V = sum_j h*_j = normalized volume (d! * vol).  So NO polytope of dimension d
with normalized volume below min_k Vfloor(d,k) can have a negative Ehrhart
coefficient -- in particular no hive polytope, whatever the rank.

d = (r-1)(r-2)/2 for a rank-r hive.
"""
from fractions import Fraction
from math import comb

def wrow(d, k):
    """w_k[j] = [n^k] C(n+d-j, d), exact, for j = 0..d."""
    out = []
    for j in range(d+1):
        # poly = prod_{i=0}^{d-1} (n + (d-j-i)) / d!
        p = [Fraction(1)]
        for i in range(d):
            s = Fraction(d - j - i)
            q = [Fraction(0)]*(len(p)+1)
            for t,c in enumerate(p):
                q[t]   += c*s
                q[t+1] += c
            p = q
        out.append(p[k] / Fraction(comb(d, d)) / Fraction(1) / Fraction(_fact(d)))
    return out

def _fact(n):
    r = 1
    for i in range(2, n+1): r *= i
    return r

print("  r    d   k   V_floor(d,k)          (min over k in bold)")
for r in range(4, 11):
    d = (r-1)*(r-2)//2
    if d < 3: continue
    best = None
    rows = []
    for k in range(1, d-1):          # only middle coefficients can be negative
        w = wrow(d, k)
        neg = max((-w[j] for j in range(1, d+1)), default=Fraction(0))
        if neg <= 0:
            rows.append((k, None)); continue
        vf = w[0]/neg
        rows.append((k, vf))
        if best is None or vf < best[1]: best = (k, vf)
    print("  r=%-2d d=%-3d  min-k=%-3d  V_floor = %s  ~= %.3g"
          % (r, d, best[0], best[1], float(best[1])))
    for k, vf in rows:
        if vf is not None and float(vf) < 5*float(best[1]):
            print("            k=%-3d V_floor = %-28s ~= %.4g" % (k, vf, float(vf)))

print()
print("Cross-check: the alcoved counterexamples must clear their own floor.")
import a1_criterion as ac
for (m,n) in [(7,7),(7,8),(8,8)]:
    h = ac.polymul(ac.eulerian(m), ac.eulerian(n)); d = m+n
    h = h + [0]*((d+1)-len(h))
    V = sum(h)
    w = wrow(d,1); neg = max(-w[j] for j in range(1,d+1))
    print("  O(P_%d,%d) d=%2d  V=%-16d V_floor(d,1)=%.4g   clears=%s"
          % (m,n,d,V, float(w[0]/neg), V > w[0]/neg))
