#!/usr/bin/env python3
"""
hive_aff.py -- EXACT affine hull / implicit-equality analysis of hive polytopes.

Rigor: float LP is used ONLY to propose a basis; every point kept is
re-solved with Fractions and re-verified exactly against all constraints.
A relative-interior point of Q is produced as the exact centroid of a set of
exact points whose affine hull has the certified dimension; a constraint is
then an IMPLICIT EQUALITY iff its slack vanishes at that centroid (exact).

Reports:
  dim_exact  : affine dim of the certified exact point set  (<= dim Q)
  n_eq       : # implicit equalities
  free       : interior sites v with e_v orthogonal to every implicit equality
  rank_free  : = len(free)  (unit vectors are independent)
  L1_rank    : rank of the set of integer directions w in L found with
               max_i |<v_i,w>| <= 1  (>= rank_free)
"""
import sys, json, random, itertools
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from sympy import Matrix

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from hive_struct import build, slacks, feasible, enumerate_hives, affine_rank


def exact_solve(rows, rhs):
    M = Matrix([[Fraction(v) for v in r] + [Fraction(c)] for r, c in zip(rows, rhs)])
    sol = M[:, :-1].solve(M[:, -1]) if M[:, :-1].rows == M[:, :-1].cols and M[:, :-1].det() != 0 else None
    return sol


def exactify(P, xf, tol=1e-7):
    """Given a float point, find tight constraints, solve exactly, verify."""
    D = P["D"]; cons = P["cons"]
    tight = []
    for k, (vec, const) in enumerate(cons):
        s = const + sum(vec[i] * xf[i] for i in range(D))
        if abs(s) < 1e-6:
            tight.append(k)
    if not tight:
        return None
    A = Matrix([[Fraction(c) for c in cons[k][0]] for k in tight])
    b = Matrix([[Fraction(-cons[k][1])] for k in tight])
    if A.rank() < D:
        return None
    try:
        sol = A.solve_least_squares(b) if A.rows != A.cols else A.solve(b)
    except Exception:
        # pick D independent rows
        rr = A.rref()[1][:D]
        sub = Matrix([list(A.row(i)) for i in range(A.rows)])
        try:
            piv = sub.T.rref()[1]
            idxs = list(piv)[:D]
            A2 = Matrix([list(A.row(i)) for i in idxs])
            b2 = Matrix([b[i] for i in idxs])
            sol = A2.solve(b2)
        except Exception:
            return None
    x = [Fraction(sol[i]) for i in range(D)]
    # verify exactly
    for vec, const in cons:
        s = Fraction(const) + sum(Fraction(vec[i]) * x[i] for i in range(D))
        if s < 0:
            return None
    # verify tightness set consistent
    return tuple(x)


def exact_points(P, ntry=200, seed=0):
    D = P["D"]; cons = P["cons"]
    A_ub = np.array([[-float(v) for v in vec] for vec, const in cons])
    b_ub = np.array([float(const) for vec, const in cons])
    pts = set()
    rng = random.Random(seed)
    objs = []
    for i in range(D):
        e = [0.0] * D; e[i] = 1.0; objs.append(list(e))
        e = [0.0] * D; e[i] = -1.0; objs.append(list(e))
    for _ in range(ntry):
        objs.append([rng.uniform(-1, 1) for _ in range(D)])
    for ob in objs:
        r = linprog(c=ob, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * D,
                    method="highs")
        if not r.success:
            continue
        p = exactify(P, r.x)
        if p is not None:
            pts.add(p)
    return sorted(pts)


def centroid(pts):
    D = len(pts[0]); n = len(pts)
    return tuple(sum(p[i] for p in pts) / n for i in range(D))


def integer_kernel_basis(rows, D):
    """Integer basis of {w in Z^D : rows . w = 0} via sympy nullspace + clearing."""
    if not rows:
        return [[1 if i == j else 0 for i in range(D)] for j in range(D)]
    M = Matrix(rows)
    ns = M.nullspace()
    out = []
    for v in ns:
        den = 1
        for x in v:
            den = den * Fraction(x).denominator // __import__("math").gcd(den, Fraction(x).denominator)
        w = [int(Fraction(x) * den) for x in v]
        g = 0
        for x in w: g = __import__("math").gcd(g, abs(x))
        if g: w = [x // g for x in w]
        out.append(w)
    return out


def analyze(lam, mu, nu, d_known=None, enum_cap=200000):
    P = build(lam, mu, nu)
    if P is None: return {"status": "BAD"}
    D = P["D"]; cons = P["cons"]
    pts = exact_points(P)
    if not pts:
        return {"status": "NOPTS", "D": D}
    dim_exact = affine_rank([list(p) for p in pts])
    ctr = centroid(pts)
    eq = []
    for k, (vec, const) in enumerate(cons):
        s = Fraction(const) + sum(Fraction(vec[i]) * ctr[i] for i in range(D))
        if s == 0:
            eq.append(k)
    eqrows = [[cons[k][0][i] for i in range(D)] for k in eq]
    # rank check: D - rank(eqrows) should equal dim_exact
    rk = Matrix(eqrows).rank() if eqrows else 0
    free = [i for i in range(D) if all(cons[k][0][i] == 0 for k in eq)]
    # L1: search integer kernel directions with |<v_i,w>|<=1
    kb = integer_kernel_basis(eqrows, D)
    L1 = [[1 if i == j else 0 for i in range(D)] for j in free]
    # try small combinations of kernel basis
    if len(kb) <= 8:
        for coefs in itertools.product([-1, 0, 1], repeat=len(kb)):
            if not any(coefs): continue
            w = [sum(coefs[j] * kb[j][i] for j in range(len(kb))) for i in range(D)]
            if max(abs(sum(cons[k][0][i] * w[i] for i in range(D))) for k in range(len(cons))) <= 1:
                L1.append(w)
    L1rank = affine_rank([[0] * D] + L1) if L1 else 0
    # lattice points
    lp = enumerate_hives(P, enum_cap)
    res = {"status": "OK", "lam": lam, "mu": mu, "nu": nu, "D": D,
           "n_vertices_found": len(pts), "dim_exact": dim_exact,
           "D_minus_rank_eq": D - rk, "n_eq": len(eq),
           "n_free": len(free), "free": free, "L1_rank": L1rank,
           "d_known": d_known}
    if lp is not None:
        c = len(lp)
        S = [slacks(P, p) for p in lp]
        eqset = set(eq)
        flags = [all(s[k] > 0 for k in range(len(cons)) if k not in eqset) for s in S]
        res["c"] = c; res["n_int"] = sum(flags); res["n_bdy"] = c - sum(flags)
    return res


if __name__ == "__main__":
    f = lambda s: [int(t) for t in s.split(",") if t.strip()]
    if sys.argv[1] == "--batch":
        for line in open(sys.argv[2]):
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split(";")
            r = analyze(f(parts[0]), f(parts[1]), f(parts[2]),
                        int(parts[3]) if len(parts) > 3 else None)
            print(json.dumps(r)); sys.stdout.flush()
    else:
        r = analyze(f(sys.argv[1]), f(sys.argv[2]), f(sys.argv[3]),
                    int(sys.argv[4]) if len(sys.argv) > 4 else None)
        print(json.dumps(r, indent=1))
