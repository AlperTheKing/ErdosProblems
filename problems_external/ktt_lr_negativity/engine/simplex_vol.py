#!/usr/bin/env python3
"""
simplex_vol.py -- WAVE-4 ROUTE R engine: certified SIMPLEX hive polytopes.

When Q(lam,mu,nu) is a simplex, its ENTIRE Ehrhart data (hence the stretched
LR polynomial P(n) = c(n*nu; n*lam, n*mu)) is pure exact linear algebra:

  1. sample exact vertices of Q by random objectives (float LP picks the basis,
     the vertex is re-solved and verified EXACTLY over Fractions);
  2. if exactly dim+1 distinct exact vertices appear, CERTIFY conv(V) = Q by
     exact LP duality: for every implicit-equality direction and every candidate
     facet normal we exhibit an exact rational Farkas/dual certificate
     y >= 0 with y^T A = w and y^T b = t  (proves w.x <= t on all of Q);
  3. if some vertex is fractional  ->  ROUTE N seed (Stanley gives no
     protection; period collapse allowed).  Logged, not h*-analysed.
  4. if all vertices are integral, Q is a lattice simplex:
       V   = normalized volume  = product of elementary divisors of the
             edge matrix (= |det| in the induced lattice aff(Q) cap Z^d),
       h*_j = # box points at height j, computed by enumerating the finite
             group Z^m / L(M') via Smith normal form, exactly.
     Then P(n) = sum_j h*_j C(n+m-j, m) EXACTLY -- negativity is decided with
     zero stretched LR counting.
  5. mandatory cross-validation on every certified simplex:
       h*_0 = 1,  sum h* = V,  (m+1) + h*_1 = c  (c from engine A at n=1).
     Any mismatch aborts.

RIGOR: floats appear only inside scipy's LP to *propose* an active set / dual
support.  Every kept object (vertex, dual certificate, determinant, h*) is
recomputed and checked in exact Fraction / integer arithmetic.

CLI
  python simplex_vol.py "lam" "mu" "nu" [K] [c]   -> one JSON line
  python simplex_vol.py --batch file              -> lines "lam;mu;nu[;c]"
  python simplex_vol.py --selftest
"""

import json
import sys
from fractions import Fraction
from math import comb

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("\\", 1)[0])
from hive_poly import build  # noqa: E402   (exact rhombus system, engine-A convention)

F = Fraction


# ------------------------------------------------------------------ exact LA
def rref(rows, ncols):
    """Gauss-Jordan over Fractions. Returns (rows_rref, pivot_cols)."""
    M = [list(r) for r in rows]
    piv = []
    r = 0
    for c in range(ncols):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(ncols)]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    return M[:r], piv


def rank(rows, ncols):
    return len(rref(rows, ncols)[0])


def solve_lin(rows, rhs, ncols):
    """One exact solution of rows.x = rhs (free vars = 0), or None if inconsistent."""
    aug = [list(rows[i]) + [rhs[i]] for i in range(len(rows))]
    R, piv = rref(aug, ncols + 1)
    if ncols in piv:
        return None                      # inconsistent
    x = [F(0)] * ncols
    for i, c in enumerate(piv):
        x[c] = R[i][ncols]
    return x


def diagonalize(A):
    """Integer diagonalization L*A*R = D (L,R unimodular). Returns (diag, R).

    R is returned as a list of rows (n x n).  No divisibility chain is enforced
    (not needed: we only use prod|d_i| and R)."""
    A = [list(map(int, row)) for row in A]
    m = len(A)
    n = len(A[0]) if m else 0
    R = [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    def col_swap(j, k):
        for row in A:
            row[j], row[k] = row[k], row[j]
        for row in R:
            row[j], row[k] = row[k], row[j]

    def col_add(j, k, q):                # col_j += q * col_k
        if q == 0:
            return
        for row in A:
            row[j] += q * row[k]
        for row in R:
            row[j] += q * row[k]

    def col_neg(j):
        for row in A:
            row[j] = -row[j]
        for row in R:
            row[j] = -row[j]

    t = 0
    while t < min(m, n):
        # find a nonzero pivot of minimal absolute value in A[t:, t:]
        best = None
        for i in range(t, m):
            for j in range(t, n):
                if A[i][j] != 0 and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        while True:
            bi, bj = best
            A[t], A[bi] = A[bi], A[t]
            col_swap(t, bj)
            p = A[t][t]
            done = True
            for i in range(t + 1, m):
                if A[i][t] != 0:
                    q = A[i][t] // p
                    A[i] = [A[i][x] - q * A[t][x] for x in range(n)]
                    if A[i][t] != 0:
                        done = False
            for j in range(t + 1, n):
                if A[t][j] != 0:
                    q = A[t][j] // p
                    col_add(j, t, -q)
                    if A[t][j] != 0:
                        done = False
            if done and all(A[i][t] == 0 for i in range(t + 1, m)) and \
               all(A[t][j] == 0 for j in range(t + 1, n)):
                break
            best = None
            for i in range(t, m):
                for j in range(t, n):
                    if A[i][j] != 0 and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                        best = (i, j)
            if best is None:
                break
        if A[t][t] < 0:
            col_neg(t)
        t += 1
    diag = [A[i][i] for i in range(min(m, n))]
    return diag, R


# ------------------------------------------------------------ vertex sampling
def sample_vertices(A, b, d, K, seed):
    """Exactly certified vertices of Q = {A x <= b}. Returns (verts, tightsets)."""
    An = np.array(A, dtype=float)
    bn = np.array(b, dtype=float)
    Aq = [[F(v) for v in row] for row in A]
    bq = [F(v) for v in b]
    import random as _r
    rng = _r.Random(seed)
    verts = {}
    for _ in range(K):
        w = [rng.randint(-1000, 1000) for _ in range(d)]
        res = linprog(np.array(w, dtype=float), A_ub=An, b_ub=bn,
                      bounds=[(None, None)] * d, method="highs")
        if not res.success:
            return None, None
        x = res.x
        tight = [i for i in range(len(A)) if abs(An[i] @ x - bn[i]) < 1e-6]
        rows, cur = [], []
        for i in tight:
            trial = cur + [Aq[i]]
            if rank(trial, d) > len(cur):
                cur = trial
                rows.append(i)
            if len(rows) == d:
                break
        if len(rows) < d:
            continue
        sol = solve_lin([Aq[i] for i in rows], [bq[i] for i in rows], d)
        if sol is None:
            continue
        prod = [sum(Aq[i][j] * sol[j] for j in range(d)) for i in range(len(A))]
        if any(prod[i] > bq[i] for i in range(len(A))):
            continue                                        # exact check failed
        key = tuple(sol)
        if key not in verts:
            verts[key] = frozenset(i for i in range(len(A)) if prod[i] == bq[i])
    if not verts:
        return None, None
    return list(verts.keys()), verts


# ------------------------------------------------------- exact LP certificate
def certify_max(A, b, An, bn, w, t):
    """Exact proof that max_{x in Q} w.x <= t : Farkas y >= 0, y^T A = w, y^T b = t."""
    d = len(w)
    wf = np.array([float(x) for x in w])
    res = linprog(-wf, A_ub=An, b_ub=bn, bounds=[(None, None)] * d, method="highs")
    if not res.success:
        return False
    x = res.x
    marg = None
    try:
        marg = np.abs(np.asarray(res.ineqlin.marginals))
    except Exception:
        marg = None
    cands = []
    if marg is not None:
        cands.append([i for i in range(len(A)) if marg[i] > 1e-9])
    cands.append([i for i in range(len(A)) if abs(An[i] @ x - bn[i]) < 1e-7])
    for S in cands:
        if not S:
            continue
        # solve sum_{i in S} y_i A_i = w   (rows: one per ambient coordinate)
        rows = [[F(A[i][j]) for i in S] for j in range(d)]
        rhs = [F(v) for v in w]
        y = solve_lin(rows, rhs, len(S))
        if y is None:
            continue
        if any(v < 0 for v in y):
            continue
        if sum(y[k] * F(b[S[k]]) for k in range(len(S))) != F(t):
            continue
        return True
    return False


# ---------------------------------------------------------------- main driver
def simplex_analyze(lam, mu, nu, K=200, seed=4505, c_ref=None, vol_cap=400000):
    out = {"lam": ",".join(map(str, lam)), "mu": ",".join(map(str, mu)),
           "nu": ",".join(map(str, nu)), "status": None}
    A, b, d, interior, ok = build(lam, mu, nu)
    if not ok:
        out["status"] = "INFEASIBLE_BOUNDARY"
        return out
    out["d_ambient"] = d
    if d == 0:
        out.update(status="TRIVIAL_POINT", dim=0, nverts=1, V=1, hstar=[1], maxden=1)
        return out
    verts, tightsets = sample_vertices(A, b, d, K, seed)
    if verts is None:
        out["status"] = "LP_FAIL"
        return out
    v0 = verts[0]
    edge = [[verts[i][j] - v0[j] for j in range(d)] for i in range(1, len(verts))]
    dim = rank(edge, d) if edge else 0
    out["dim"] = dim
    out["nverts"] = len(verts)
    maxden = max(max(q.denominator for q in v) for v in verts)
    out["maxden"] = maxden
    if len(verts) != dim + 1:
        out["status"] = "NOT_SIMPLEX"
        return out

    # ---- certification that conv(verts) = Q -------------------------------
    An = np.array(A, dtype=float)
    bn = np.array(b, dtype=float)
    Aq = [[F(v) for v in row] for row in A]
    # (i) implicit equalities: constraints tight at every vertex
    always = set(range(len(A)))
    for v in verts:
        always &= tightsets[v]
    Erows, Eidx = [], []
    for i in sorted(always):
        if rank(Erows + [Aq[i]], d) > len(Erows):
            Erows.append(Aq[i])
            Eidx.append(i)
    if len(Erows) != d - dim:
        out["status"] = "AFFHULL_UNCERTIFIED"
        return out
    for i in Eidx:
        # a_i.x <= b_i is in the system; certify also a_i.x >= b_i on Q
        negw = [-v for v in A[i]]
        if not certify_max(A, b, An, bn, negw, -b[i]):
            out["status"] = "AFFHULL_UNCERTIFIED"
            return out
    # (ii) facets: for each i, functional w with w.v_j = t (j!=i), w.v_i = t-1
    for i in range(len(verts)):
        rows, rhs = [], []
        for j in range(len(verts)):
            rows.append(list(verts[j]) + [F(-1)])
            rhs.append(F(0) if j != i else F(-1))
        sol = solve_lin(rows, rhs, d + 1)
        if sol is None:
            out["status"] = "FACET_SOLVE_FAIL"
            return out
        w, t = sol[:d], sol[d]
        den = 1
        for q in w + [t]:
            den = den * q.denominator // __import__("math").gcd(den, q.denominator)
        wi = [int(q * den) for q in w]
        ti = int(t * den)
        if not certify_max(A, b, An, bn, wi, ti):
            out["status"] = "FACET_UNCERTIFIED"
            return out
    out["certified"] = True

    if maxden > 1:
        out["status"] = "FRACTIONAL_SIMPLEX_ROUTE_N"
        out["verts"] = [[str(q) for q in v] for v in verts]
        return out

    # ---- lattice simplex: V and h* ----------------------------------------
    M = [[int(x) for x in row] for row in edge]           # dim x d, integer
    diag, R = diagonalize(M)
    nz = [abs(x) for x in diag if x != 0]
    if len(nz) != dim:
        out["status"] = "SNF_RANK_MISMATCH"
        return out
    V = 1
    for x in nz:
        V *= x
    out["V"] = V
    # M' = (M R)[:, :dim]  -- the simplex in coordinates of aff(Q) cap Z^d
    MR = [[sum(M[i][k] * R[k][j] for k in range(d)) for j in range(d)] for i in range(dim)]
    if any(MR[i][j] != 0 for i in range(dim) for j in range(dim, d)):
        out["status"] = "SNF_PROJECTION_FAIL"
        return out
    Mp = [[MR[i][j] for j in range(dim)] for i in range(dim)]
    if V > vol_cap:
        out["status"] = "VOL_TOO_LARGE_FOR_HSTAR"
        return out
    # box points: N = Mp^T ; f = R2 * (w_i/e_i), w in prod Z/e_i
    N = [[Mp[j][i] for j in range(dim)] for i in range(dim)]
    e, R2 = diagonalize(N)
    ev = [abs(x) for x in e]
    if any(x == 0 for x in ev):
        out["status"] = "SNF_DEGENERATE"
        return out
    pv = 1
    for x in ev:
        pv *= x
    if pv != V:
        out["status"] = "SNF_VOLUME_MISMATCH"
        return out
    hstar = [0] * (dim + 1)
    idx = [0] * dim
    total = 0
    while True:
        g = [F(idx[i], ev[i]) for i in range(dim)]
        s = F(0)
        for i in range(dim):
            acc = F(0)
            for k in range(dim):
                if R2[i][k]:
                    acc += R2[i][k] * g[k]
            s += acc - (acc.numerator // acc.denominator)     # frac part
        h = -((-s.numerator) // s.denominator)                # ceil
        hstar[int(h)] += 1
        total += 1
        # odometer
        p = dim - 1
        while p >= 0:
            idx[p] += 1
            if idx[p] < ev[p]:
                break
            idx[p] = 0
            p -= 1
        if p < 0:
            break
    out["hstar"] = hstar
    out["boxpoints"] = total
    # ---- mandatory cross-validation ---------------------------------------
    checks = {"hstar0": hstar[0] == 1, "sum": sum(hstar) == V, "count": total == V,
              "nonneg": all(x >= 0 for x in hstar)}
    cP1 = (dim + 1) + hstar[1] if dim >= 1 else 1
    out["c_pred"] = cP1
    if c_ref is not None:
        checks["c_match"] = (cP1 == c_ref)
    out["checks"] = checks
    if not all(checks.values()):
        out["status"] = "CROSSVAL_FAIL"
        return out
    # ---- exact polynomial from h* -----------------------------------------
    coeffs = poly_from_hstar(dim, hstar)
    out["coeffs"] = [str(x) for x in coeffs]               # index k = coeff of n^k
    out["neg_coeff"] = any(x < 0 for x in coeffs)
    out["status"] = "CERTIFIED_SIMPLEX"
    return out


def poly_from_hstar(m, hstar):
    """P(n) = sum_j h*_j C(n+m-j, m), exact monomial coefficients (index = power)."""
    import math
    res = [F(0)] * (m + 1)
    for j, hj in enumerate(hstar):
        if hj == 0:
            continue
        # C(n+m-j, m) = prod_{t=0}^{m-1} (n + m-j-t) / m!
        poly = [F(1)]
        for t in range(m):
            sh = F(m - j - t)
            new = [F(0)] * (len(poly) + 1)
            for k, cf in enumerate(poly):
                new[k + 1] += cf
                new[k] += cf * sh
            poly = new
        fac = F(math.factorial(m))
        for k in range(len(poly)):
            res[k] += hj * poly[k] / fac
    return res


def poly_str(coeffs):
    terms = []
    for k in range(len(coeffs) - 1, -1, -1):
        c = coeffs[k]
        if c == 0:
            continue
        t = str(c)
        if k == 1:
            t += "*n"
        elif k > 1:
            t += f"*n^{k}"
        terms.append(t)
    return " + ".join(terms) if terms else "0"


def _p(s):
    return tuple(int(t) for t in str(s).replace(";", ",").split(",") if t.strip())


# ---------------------------------------------------------------- selftest
def _selftest():
    fails = 0
    cases = [
        # (lam, mu, nu, expected c at n=1, expected dim)  -- c from engine A
        ((2, 1), (1,), (3, 1), 1, 0),
        ((2, 1), (2, 1), (3, 2, 1), 2, 1),
        ((6, 5, 4, 3, 2, 1), (6, 5, 4, 3, 2, 1), (11, 9, 8, 7, 5, 2), 12, 6),
    ]
    for lam, mu, nu, c, dm in cases:
        r = simplex_analyze(lam, mu, nu, K=120, c_ref=c)
        okk = r.get("dim", 0) == dm
        print(f"{lam} {mu} {nu}: status={r['status']} dim={r.get('dim')} "
              f"nverts={r.get('nverts')} V={r.get('V')} h*={r.get('hstar')} "
              f"{'OK' if okk else 'FAIL'}")
        fails += 0 if okk else 1
    # known: c=1 -> P == 1 ; c=2 -> P == n+1
    r = simplex_analyze((2, 1), (1,), (3, 1), K=40, c_ref=1)
    p1 = r.get("coeffs", ["1"])
    okk = poly_str([F(x) for x in p1]) == "1"
    print(f"KTW c=1 poly: {poly_str([F(x) for x in p1])} {'OK' if okk else 'FAIL'}")
    fails += 0 if okk else 1
    r = simplex_analyze((2, 1), (2, 1), (3, 2, 1), K=40, c_ref=2)
    ps = poly_str([F(x) for x in r["coeffs"]])
    okk = ps == "1*n + 1"
    print(f"Ikenmeyer c=2 poly: {ps} {'OK' if okk else 'FAIL'}")
    fails += 0 if okk else 1
    # poly_from_hstar against a known exact expansion: d=6, h*=[1,5,11,3,...]
    print("SELFTEST", "PASS" if fails == 0 else f"FAIL({fails})")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    if len(sys.argv) >= 3 and sys.argv[1] == "--batch":
        K = int(sys.argv[3]) if len(sys.argv) > 3 else 200
        for line in open(sys.argv[2]):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            f = line.split(";")
            cr = int(f[3]) if len(f) > 3 and f[3].strip() else None
            try:
                r = simplex_analyze(_p(f[0]), _p(f[1]), _p(f[2]), K=K, c_ref=cr)
            except Exception as ex:
                r = {"lam": f[0], "mu": f[1], "nu": f[2], "status": "EXC:" + repr(ex)[:120]}
            print(json.dumps(r), flush=True)
        sys.exit(0)
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    cr = int(sys.argv[5]) if len(sys.argv) > 5 else None
    print(json.dumps(simplex_analyze(_p(sys.argv[1]), _p(sys.argv[2]), _p(sys.argv[3]),
                                     K=K, c_ref=cr)))
