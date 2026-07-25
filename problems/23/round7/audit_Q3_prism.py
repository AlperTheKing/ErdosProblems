"""audit_Q3_prism.py -- INDEPENDENT exact audit of Theorem P2-A of round7/Q3.md.

Claim under audit (Q3.md lines 538-554):
    P = pentagonal prism C5 [] K2, x(o_j) = 1/5 - t, x(i_j) = t, t in [0,1/10]
    (i)   psi(P,x) = 1/25 - 2t(1/5-t)   exactly for every t in [0,1/10]
    (ii)  d(P,x)   = 5t(1/5-t)          (claimed attained, "equality by exact B&B")
    (iii) R = d/(1/25-psi) = 5/2        exactly, all t

Method (mine, independent of Q3_pass2_curve.py):
  * psi: enumerate all 2^9 cuts (vertex 0 fixed), each monochromatic mass is
    a*alpha^2 + b*alpha*delta + c*delta^2 with INTEGER a,b,c -> exact polynomial in t.
  * d  : enumerate all 5^9 templates phi (phi(o_0)=0 by rotation invariance of the
    blow-up family), each weighted symmetric difference is a*alpha^2+b*alpha*delta+
    c*delta^2 with integer a,b,c.
  * then minimise each candidate difference exactly over [0,1/10] with sympy
    (rational critical points only).
Everything integer / Fraction / sympy Rational.  No floats.
"""
import itertools, sys
import numpy as np
import sympy as sp

t = sp.symbols('t')
alpha = sp.Rational(1, 5) - t
delta = t

# ---------------- prism -------------------------------------------------
# outer o_j = j (0..4), inner i_j = 5+j
E = []
for j in range(5):
    E.append((j, (j + 1) % 5))
    E.append((5 + j, 5 + (j + 1) % 5))
    E.append((j, 5 + j))
E = sorted((min(a, b), max(a, b)) for a, b in E)
N = 10
assert len(E) == 15
Eset = set(E)


def ptype(u, v):
    """0 = outer-outer, 1 = outer-inner, 2 = inner-inner"""
    return (1 if u >= 5 else 0) + (1 if v >= 5 else 0)


# ---------------- psi: all cuts ----------------------------------------
cut_polys = {}
for S in range(1 << (N - 1)):        # vertex 0 fixed on side 0
    abc = [0, 0, 0]
    for (u, v) in E:
        su = (S >> u) & 1
        sv = (S >> v) & 1
        if su == sv:
            abc[ptype(u, v)] += 1
    cut_polys.setdefault(tuple(abc), 0)
    cut_polys[tuple(abc)] += 1

polys = []
for (a, b, c) in cut_polys:
    polys.append(sp.expand(a * alpha ** 2 + b * alpha * delta + c * delta ** 2))
polys = list(dict.fromkeys(polys))
print("psi: distinct cut coefficient triples:", len(cut_polys), " distinct polynomials:", len(polys))

cand = sp.expand(sp.Rational(1, 25) - 2 * t * (sp.Rational(1, 5) - t))
print("candidate psi(t) =", cand)


def min_on_interval(expr, lo, hi):
    """exact minimum of a polynomial of degree <= 2 on [lo,hi] (rational endpoints)."""
    p = sp.Poly(sp.expand(expr), t)
    pts = [sp.Rational(lo), sp.Rational(hi)]
    for r in sp.solve(sp.diff(expr, t), t):
        if r.is_rational and sp.Rational(lo) <= r <= sp.Rational(hi):
            pts.append(sp.Rational(r))
    vals = [sp.nsimplify(expr.subs(t, q)) for q in pts]
    return min(vals), pts[vals.index(min(vals))]


bad = []
ok_equal = False
for p in polys:
    diff = sp.expand(p - cand)
    if diff == 0:
        ok_equal = True
        continue
    mn, at = min_on_interval(diff, 0, sp.Rational(1, 10))
    if mn < 0:
        bad.append((p, mn, at))
print("candidate is realised by a cut:", ok_equal)
print("cuts dipping strictly below the candidate on [0,1/10]:", len(bad))
for b in bad[:10]:
    print("   ", b)

# ---------------- d: all 5^9 templates, exact ---------------------------
print("enumerating 5^9 templates for the weighted edit distance ...")
K = N - 1
tot = 5 ** K
cols = np.zeros((tot, N), dtype=np.int8)
for j in range(K):
    block = 5 ** j
    pat = np.repeat(np.arange(5, dtype=np.int8), block)
    cols[:, j + 1] = np.tile(pat, tot // (5 * block))
# cols[:,0] = 0 fixed

A = np.zeros(tot, dtype=np.int32)
B = np.zeros(tot, dtype=np.int32)
C = np.zeros(tot, dtype=np.int32)
for u in range(N):
    for v in range(u + 1, N):
        d5 = (cols[:, u].astype(np.int16) - cols[:, v].astype(np.int16)) % 5
        consec = (d5 == 1) | (d5 == 4)
        isedge = (u, v) in Eset
        pay = (~consec) if isedge else consec          # 1 iff pair contributes
        pt = ptype(u, v)
        if pt == 0:
            A += pay
        elif pt == 1:
            B += pay
        else:
            C += pay
trip = np.unique(np.stack([A, B, C], axis=1), axis=0)
print("distinct (A,B,C) template triples:", len(trip))

dcand = sp.expand(5 * t * (sp.Rational(1, 5) - t))
best_expr = None
bad_d = []
hits = 0
for (a, b, c) in trip:
    p = sp.expand(int(a) * alpha ** 2 + int(b) * alpha * delta + int(c) * delta ** 2)
    if sp.expand(p - dcand) == 0:
        hits += 1
        continue
    mn, at = min_on_interval(p - dcand, 0, sp.Rational(1, 10))
    if mn < 0:
        bad_d.append((int(a), int(b), int(c), p, mn, at))
print("templates realising exactly 5t(1/5-t):", hits)
print("templates strictly below 5t(1/5-t) somewhere on [0,1/10]:", len(bad_d))
for b in bad_d[:20]:
    print("   coeffs", b[0], b[1], b[2], " poly", b[3], " min of (p - 5t(1/5-t)) =", b[4], "at t =", b[5])

# where exactly does the claimed d fail?
if bad_d:
    print("\n--- exact d(t) as a lower envelope, sampled at rationals ---")
    for q in [sp.Rational(1, 100), sp.Rational(1, 50), sp.Rational(1, 20),
              sp.Rational(1, 15), sp.Rational(1, 12), sp.Rational(1, 10)]:
        vals = []
        for (a, b, c) in trip:
            vals.append(int(a) * (sp.Rational(1, 5) - q) ** 2 + int(b) * (sp.Rational(1, 5) - q) * q + int(c) * q ** 2)
        m = min(vals)
        print("t =", q, " true d =", m, "  claimed 5t(1/5-t) =", dcand.subs(t, q),
              "  equal:", sp.simplify(m - dcand.subs(t, q)) == 0)
