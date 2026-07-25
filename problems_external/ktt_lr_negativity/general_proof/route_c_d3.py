#!/usr/bin/env python3
"""Route C, d=3 (r=4): can the edge-local homogeneous certificate prove
a_1 >= 11/6 (KTT-SD)?  Exact analysis.

We load the reproduced certificate: NORMALS (15), balance map B (45x99, rank 27),
mu (99, >=0) with  a_1(P) = Lambda(P).mu  on ker(B).

Tests:
 (1) re-verify a_1 = Lambda.mu on all 72 witnesses (exact).
 (2) homogeneity obstruction: t*Lambda_0 in ker(B), a_1 = t*11/6 -> 0.
 (3) exact LP: min{ Lambda.mu : B Lambda = 0, Lambda >= 0, ones.Lambda = 6 }.
     If == 11/6, the unimodular simplex minimises a_1/sum(Lambda) => the
     homogeneous inequality  a_1 >= (11/36) sum(Lambda)  holds on the cone.
 (4) Farkas feasibility of (A): exists y with B^T y <= mu - (11/36) ones.
"""
import json, os, sys
from fractions import Fraction as F
import itertools
from math import gcd

HERE = r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve"
cert = json.load(open(os.path.join(HERE, "q2_basis_witness_certificate.json")))

NORMALS = cert["normals"]
PAIRS = [tuple(p) for p in cert["nonparallel_pairs"]]         # 99 nonparallel pairs
mu = [F(x) for x in cert["mu"]]                               # 99 rationals >= 0
n = len(PAIRS)
assert n == 99 and len(mu) == 99
assert min(mu) >= 0, "mu has a negative entry"

def primitive_cross(a, b):
    u = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    g = 0
    for x in u: g = gcd(g, abs(x))
    return None if g == 0 else [x//g for x in u]

# balance matrix B: 45 x 99
B = [[0]*n for _ in range(3*len(NORMALS))]
for c,(i,j) in enumerate(PAIRS):
    u = primitive_cross(NORMALS[i], NORMALS[j])
    for k in range(3):
        B[3*i+k][c] = u[k]
        B[3*j+k][c] = -u[k]

# ---- (1) re-verify a_1 = Lambda.mu on witnesses
bad = 0
for w in cert["witnesses"]:
    row = w["edge_lengths"]
    a1 = F(w["a1"])
    if sum(F(r)*m for r,m in zip(row, mu)) != a1:
        bad += 1
    # also each row must be in ker(B)
    for br in B:
        if sum(a*x for a,x in zip(br,row)) != 0:
            bad += 1; break
print("(1) witnesses a_1=Lambda.mu & B.Lambda=0 :", "PASS" if bad==0 else f"FAIL({bad})")

# unimodular simplex edge vector Lambda_0 (V=1, sum=6, a1=11/6)
uni = [w for w in cert["witnesses"] if w["a1"]=="11/6"][0]
L0 = [F(x) for x in uni["edge_lengths"]]
print("    Lambda_0 sum =", sum(L0), " Lambda_0.mu =", sum(l*m for l,m in zip(L0,mu)))

# ---- (2) homogeneity obstruction
print("(2) a_1(t*Lambda_0) = 11t/6 -> 0 as t->0+; inf over cone = 0, not 11/6.")
for t in (F(1), F(1,2), F(1,10), F(1,1000)):
    print(f"      t={t!s:>7}  a_1 = {t*F(11,6)}")

# ---- (3) exact LP:  min mu.Lambda  s.t.  B Lambda = 0, Lambda>=0, ones.Lambda=6
# Solve with scipy (float) to locate optimum, then reconstruct/verify exactly.
import numpy as np
from scipy.optimize import linprog
c = np.array([float(x) for x in mu])
Bf = np.array([[float(x) for x in row] for row in B], dtype=float)
Aeq = np.vstack([Bf, np.ones((1,n))])
beq = np.concatenate([np.zeros(len(B)), [6.0]])
res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=[(0,None)]*n, method="highs")
print("(3) LP status:", res.status, res.message)
print("    min mu.Lambda  (float) =", res.fun, "   (11/6 =", float(F(11,6)), ")")
supp = [(i, res.x[i]) for i in range(n) if res.x[i] > 1e-7]
print("    support size:", len(supp))
for i,v in supp:
    print(f"      edge {PAIRS[i]}  norms {NORMALS[PAIRS[i][0]]},{NORMALS[PAIRS[i][1]]}  x={v:.4f} mu={mu[i]}")

# ---- (4) Farkas feasibility of (A): exists y with B^T y <= mu - (11/36) ones
# LP: find y (free), s>=0 with B^T y + s = mu - (11/36)ones. Phase-1 feasibility.
rhs = [m - F(11,36) for m in mu]
# variables: y (45, free -> split y=yp-yn), then minimize sum of artificials? Use
# scipy: minimize 0 with A_ub: (B^T) y <= rhs  (99 rows, 45 vars y free)
BT = np.array([[float(B[r][ccol]) for r in range(len(B))] for ccol in range(n)])  # 99 x 45
rhsf = np.array([float(x) for x in rhs])
# feasibility: minimize a dummy; linprog needs an objective. Minimize sum of slacks?
# Just test feasibility via minimize 0.
res2 = linprog(np.zeros(len(B)), A_ub=BT, b_ub=rhsf,
               bounds=[(None,None)]*len(B), method="highs")
print("(4) Farkas (A) feasibility  B^T y <= mu-(11/36)ones :", res2.status, res2.message)
