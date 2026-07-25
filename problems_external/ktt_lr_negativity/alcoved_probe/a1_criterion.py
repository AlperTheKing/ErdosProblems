#!/usr/bin/env python3
"""
EXACT h*-criterion for the LINEAR Ehrhart coefficient (the coefficient that
actually goes negative in the alcoved counterexamples).

  P(n) = sum_j h*_j * C(n+d-j, d)
  [n^1] C(n+d-j, d) =  H_d                                    (j = 0)
                    =  (-1)^(j-1) / ( d * C(d-1, j-1) )        (1 <= j <= d)

  =>  a_1 = h*_0 * H_d + (1/d) * sum_{j=1..d} (-1)^(j-1) h*_j / C(d-1, j-1)

VALIDATION: Liu-Tsuchiya (arXiv:1806.08403) Table 1 gives, for the order
polytope of P_{7,7} (= ordinal sum of a 7-antichain and a 7-antichain,
dimension 14, h* = A_7(z)^2 with A_k the Eulerian polynomial),
      a_1 = -3041/1430.
This is the minimum-dimensional non-Ehrhart-positive ALCOVED polytope known.
"""
from fractions import Fraction
from math import comb

def a1_from_hstar(h):
    d = len(h) - 1
    Hd = sum(Fraction(1, k) for k in range(1, d+1))
    s = Fraction(h[0]) * Hd
    for j in range(1, d+1):
        s += Fraction((-1)**(j-1) * h[j], d * comb(d-1, j-1))
    return s

def ehrhart_from_hstar(h, n):
    d = len(h) - 1
    return sum(h[j] * comb(n + d - j, d) for j in range(d+1))

def eulerian(k):
    """A_k(z): Eulerian polynomial, h* of the k-cube (= order polytope of a
    k-antichain).  A_k(z) = sum_w z^{des(w)}, w in S_k."""
    A = [1]
    for m in range(2, k+1):
        B = [0]*m
        for i, c in enumerate(A):
            B[i]   += c * (i+1)
            B[i+1] += c * (m-i-1)
        A = B
    return A

def polymul(p, q):
    o = [0]*(len(p)+len(q)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(q):
            o[i+j] += a*b
    return o

# ---- validation on the alcoved (order-polytope) counterexamples -------------
print("A_7 =", eulerian(7))
for (m,n) in [(6,6),(6,7),(7,7),(7,8),(8,8),(9,9),(10,10)]:
    h = polymul(eulerian(m), eulerian(n))
    h = h + [0]*((m+n+1)-len(h))
    d = m+n
    a1 = a1_from_hstar(h)
    print("O(P_%d,%d)  d=%2d  h*deg=%2d  sum h*=%d  a_1 = %-14s %s"
          % (m, n, d, len(polymul(eulerian(m),eulerian(n)))-1, sum(h), a1,
             "NEGATIVE" if a1 < 0 else ""))

exp = Fraction(-3041, 1430)
got = a1_from_hstar(polymul(eulerian(7), eulerian(7)) + [0,0])
print("\nP_{7,7} check against Liu-Tsuchiya Table 1: got %s expected %s -> %s"
      % (got, exp, "MATCH" if got == exp else "MISMATCH"))

# Reeve control: d=3, h*=(1,0,q-1,0), a_1 should be 2 - q/6
for q in (12, 13, 20):
    print("Reeve T_%d  a_1 =" % q, a1_from_hstar([1,0,q-1,0]),
          " expected", Fraction(2) - Fraction(q,6))
