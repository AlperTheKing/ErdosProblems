"""(E5), done properly.

A SIMPLE vertex v of a hive polytope Q(g) has a simplicial tangent cone with
exactly 3 facets, so its cone equals C_S for a triple S of rhombus rows that
are tight at v.  Rows t outside S may also be tight PROVIDED they are
redundant for C_S (C_S contained in {d_t.x <= 0}); a tight non-redundant row
would cut the cone down and change it.

So: for each triple S with cone multiplicity m(C_S) > 1, the question
"is a simple vertex with cone C_S realisable?" is exactly the feasibility of

    d_t . v_S(g) <  b_t   for every NON-redundant t not in S     (strict)
    d_t . v_S(g) <= b_t   for every REDUNDANT   t not in S
    g >= 1   (dim Q = 3 forces every gap positive)

which is a rational LP in the 9 gaps because b is linear in g on the full
18-row system.

Decision is EXACT: a feasible point is verified with Fractions; infeasibility
is certified by exact Farkas multipliers u >= 0, u != 0 with u^T R >= 0
componentwise (then 0 <= (u^T R).g = sum u_i (R_i.g) < 0 for g >= 1, absurd).
"""
import itertools, sys, os, json
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt4
import numpy as np
from scipy.optimize import linprog
from e5 import DS, NB, M, rows_for, cone_mult

def classify(S):
    """(strict_rows, loose_rows) index lists among t not in S"""
    rays = kt4.cone_rays(DS, S)
    strict, loose = [], []
    for t in range(NB):
        if t in S: continue
        if all(kt4.dot(DS[t], r) <= 0 for r in rays):
            loose.append(t)
        else:
            strict.append(t)
    return strict, loose, rays

def build(S):
    Rall, D = rows_for(S)          # rows indexed by t not in S, in order
    idx = [t for t in range(NB) if t not in S]
    strict, loose, rays = classify(S)
    Rs = [Rall[i] for i, t in enumerate(idx) if t in strict]
    Rl = [Rall[i] for i, t in enumerate(idx) if t in loose]
    return Rs, Rl, rays

def lp_feas(S, gmin=1):
    Rs, Rl, rays = build(S)
    nS = len(Rs)
    Aub = []; bub = []
    for r in Rs:
        Aub.append([float(x) for x in r] + [1.0]); bub.append(0.0)
    for r in Rl:
        Aub.append([float(x) for x in r] + [0.0]); bub.append(0.0)
    bounds = [(gmin, 1e7)] * 9 + [(0, 1)]
    c = [0.0] * 9 + [-1.0]
    res = linprog(c, A_ub=Aub, b_ub=bub, bounds=bounds, method="highs")
    return res, Rs, Rl

def exact_verify(S, g):
    Rs, Rl, rays = build(S)
    ok_s = all(sum(r[j] * g[j] for j in range(9)) < 0 for r in Rs)
    ok_l = all(sum(r[j] * g[j] for j in range(9)) <= 0 for r in Rl)
    return ok_s and ok_l

def farkas(S):
    """exact u >= 0, u != 0, supported on the STRICT rows (loose rows may be
       used too but then need coefficient sign care -- we use strict rows only
       plus loose rows, both give R_i.g <= 0, and we need at least one strict
       row with u_i > 0), with u^T R >= 0 componentwise."""
    Rs, Rl, rays = build(S)
    R = Rs + Rl
    ns = len(Rs)
    m = len(R)
    # maximise sum of the STRICT-row multipliers subject to u^T R >= 0, 0<=u<=1
    Aub = []; bub = []
    for j in range(9):
        Aub.append([-float(R[i][j]) for i in range(m)]); bub.append(0.0)
    c = [-1.0] * ns + [0.0] * (m - ns)
    res = linprog(c, A_ub=Aub, b_ub=bub, bounds=[(0, 1)] * m, method="highs")
    if res.status != 0 or -res.fun <= 1e-9:
        return None
    for den in (1, 2, 3, 4, 6, 12, 24, 60, 120, 720, 2520, 27720, 10 ** 6, 10 ** 9):
        u = [Fraction(int(round(x * den)), den) for x in res.x]
        if any(x < 0 for x in u): continue
        if sum(u[:ns]) <= 0: continue
        good = True
        for j in range(9):
            if sum(u[i] * R[i][j] for i in range(m)) < 0:
                good = False; break
        if good:
            return u, ns, m
    return None

if __name__ == "__main__":
    gmin = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    tri = []
    for S in itertools.combinations(range(NB), 3):
        if kt4.det3([list(DS[i]) for i in S]) == 0: continue
        m, nr = cone_mult(S)
        if m is not None and m > 1:
            tri.append((S, m))
    print("non-unimodular triples:", len(tri), " gmin =", gmin)
    feas = []; cert = []; undecided = []
    for S, m in tri:
        res, Rs, Rl = lp_feas(S, gmin)
        got = False
        if res.status == 0 and res.x[9] > 1e-9:
            for mult in (1, 2, 3, 4, 6, 12, 24, 120, 720, 5040, 10 ** 4, 10 ** 6):
                gi = [int(round(x * mult)) for x in res.x[:9]]
                if all(v >= gmin for v in gi) and exact_verify(S, gi):
                    feas.append((S, m, gi)); got = True; break
            if not got:
                undecided.append((S, m, "lp_feasible_but_no_exact_point", list(res.x[:9])))
                got = True
        if got: continue
        f = farkas(S)
        if f is None:
            undecided.append((S, m, "no_certificate", None))
        else:
            cert.append((S, m, f[0]))
    print("REALISABLE non-unimodular simple vertex cones:", len(feas))
    for f in feas[:20]: print("   ", f)
    print("PROVEN IMPOSSIBLE (exact Farkas certificate):", len(cert))
    print("UNDECIDED:", len(undecided))
    for u in undecided[:20]: print("   ", u[0], u[1], u[2])
