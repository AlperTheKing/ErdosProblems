"""(E5) attack.  For every triple S of rhombus directions whose cone C_S is
NON-UNIMODULAR (multiplicity m > 1), decide exactly whether some hive
right-hand side realises v_S as a vertex of Q with EXACTLY the rows of S tight.

b is linear in the 9-gap vector g (representative lam4 = mu4 = 0,
nu4 = (Aw+Bw-Cw)/4; rational nu4 only translates Q, and scaling g by 4 makes
it integral), so this is a rational LP feasibility question in 9 variables.
Search with floats, DECIDE with exact Fraction arithmetic + Farkas certificate.
"""
import itertools, sys, os, math, json
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
import numpy as np
from scipy.optimize import linprog

# ---- fixed direction list and the linear map g -> b -------------------------
def bvec(g):
    a1, a2, a3, b1, b2, b3, c1, c2, c3 = g
    Aw = a1 + 2 * a2 + 3 * a3; Bw = b1 + 2 * b2 + 3 * b3
    Cw = c1 + 2 * c2 + 3 * c3
    n4 = Fraction(Aw + Bw - Cw, 4)
    lam = [a1 + a2 + a3, a2 + a3, a3, 0]
    mu = [b1 + b2 + b3, b2 + b3, b3, 0]
    nu = [n4 + c1 + c2 + c3, n4 + c2 + c3, n4 + c3, n4]
    B = kt4._bnd(lam, mu, nu)
    A, b, bad = kt4.rows_from_boundary(B)
    return A, b            # FULL 18 rows: b is exactly linear in g

DS, _ = bvec((1,) * 9)
NB = len(DS)

# M[t][j] : b_t = sum_j M[t][j] * g_j   (linear, verified below)
M = []
cols = []
for j in range(9):
    e = [0] * 9; e[j] = 1
    d2, bb = bvec(tuple(e))
    assert d2 == DS
    cols.append(bb)
M = [[cols[j][t] for j in range(9)] for t in range(NB)]
# verify linearity exactly on random vectors
import random
random.seed(1)
for _ in range(50):
    g = tuple(random.randint(0, 30) for _ in range(9))
    d2, bb = bvec(g)
    assert d2 == DS
    for t in range(NB):
        assert bb[t] == sum(M[t][j] * g[j] for j in range(9)), (t, g)
# reduce_rows takes a min over duplicate directions -- confirm no direction is
# duplicated with a DIFFERENT rhs (else b would only be piecewise linear)
print("rows:", NB, " distinct directions:", len(set(DS)), " b linear in g: VERIFIED exactly on 50 random g")

def cone_mult(S):
    rays = kt4.cone_rays(DS, S)
    if len(rays) != 3:
        return None, len(rays)
    return abs(kt4.det3([list(r) for r in rays])), 3

# ---- enumerate the non-unimodular triples ----------------------------------
tri = []
for S in itertools.combinations(range(NB), 3):
    D = kt4.det3([list(DS[i]) for i in S])
    if D == 0:
        continue
    m, nr = cone_mult(S)
    tri.append((S, D, m, nr))
nonuni = [t for t in tri if t[2] is not None and t[2] > 1]
hist = {}
for S, D, m, nr in tri:
    hist[m] = hist.get(m, 0) + 1
print("nonsingular triples:", len(tri), " cone-multiplicity histogram:", hist)
print("non-unimodular cones:", len(nonuni))

# ---- LP: exactly-S-tight feasibility ---------------------------------------
def rows_for(S):
    """strict rows  R . g < 0  expressing 'd_t . v_S(g) < b_t' for t not in S"""
    Amat = [list(DS[i]) for i in S]
    D = kt4.det3(Amat)
    adj = kt4.adj3(Amat)
    sgn = 1 if D > 0 else -1
    out = []
    for t in range(NB):
        if t in S:
            continue
        # numerator  d_t . adj . b_S  vs  b_t * D
        row = [Fraction(0)] * 9
        for j in range(9):
            bs = [M[S[q]][j] for q in range(3)]
            nv = [sum(adj[r][q] * bs[q] for q in range(3)) for r in range(3)]
            row[j] = (DS[t][0] * nv[0] + DS[t][1] * nv[1] + DS[t][2] * nv[2]
                      - M[t][j] * D)
        out.append([sgn * x for x in row])   # need  row . g < 0
    return out, D

def feasible(S):
    """max eps s.t. R.g <= -eps, g >= 1, eps <= 1, g <= 1e6 ; float search"""
    Rw, D = rows_for(S)
    n = 10   # g (9) + eps
    Aub = []; bub = []
    for r in Rw:
        Aub.append([float(x) for x in r] + [1.0]); bub.append(0.0)
    bounds = [(1, 1e6)] * 9 + [(0, 1)]
    c = [0.0] * 9 + [-1.0]
    res = linprog(c, A_ub=Aub, b_ub=bub, bounds=bounds, method="highs")
    return res, Rw

def exact_check(S, g):
    """exact: is v_S a vertex of Q(g) with exactly S tight?"""
    Rw, D = rows_for(S)
    ok = all(sum(r[j] * g[j] for j in range(9)) < 0 for r in Rw)
    return ok

if __name__ == "__main__":
    hits = []
    for S, D, m, nr in nonuni:
        res, Rw = feasible(S)
        if res.status == 0 and res.x[9] > 1e-9:
            gf = res.x[:9]
            # rationalise: scale to integers
            sc = 1
            for mult in (1, 2, 3, 4, 6, 12, 24, 60, 120, 360, 720, 5040):
                gi = [int(round(x * mult)) for x in gf]
                if all(v >= 1 for v in gi) and exact_check(S, gi):
                    hits.append((S, m, gi)); break
            else:
                hits.append((S, m, None))
    print("FEASIBLE non-unimodular triples:", len(hits))
    for h in hits[:40]:
        print("   S=", h[0], " m=", h[1], " g=", h[2])
    if not hits:
        print("NO non-unimodular vertex cone is realisable (float LP);"
              " exact Farkas certificates required to close it.")
