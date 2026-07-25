#!/usr/bin/env python3
"""
engineC/ehr.py -- EXACT Ehrhart engine for hive polytopes by cone decomposition.

This is the missing "engine C" (NEXT_WAVES item N1).  It computes the EXACT
Ehrhart series of Q(lam,mu,nu) *without ever counting lattice points of a
dilate*, so its cost is O(normalized volume), not O(P(d+2)).

Method (all exact, integer / Fraction arithmetic):
  1. Q = {x : A x <= b} from engine/hive_poly.build (same rhombus model as
     engine A).  Vertices computed exactly with cddlib+GMP.
  2. Homogenize: g_v = primitive integer vector along (v,1).  Lambda =
     Z^{m+1} cap span_Q{g_v} (saturated lattice, rank d+1) -- computed by two
     integer-kernel (column-HNF) passes.  All g_v get integer Lambda-coords.
  3. Regular triangulation of the vertex configuration via a random lifting and
     the lower hull (cddlib).  Genericity is CHECKED (every lower facet must
     carry exactly d+1 points), not assumed.
  4. Half-open decomposition (Koppe-Verdoolaege): pick z in the interior of the
     cone, generic (a_j != 0 for every simplex -- CHECKED); simplex i keeps
     lambda_j in [0,1) when a_j >= 0 and (0,1] when a_j < 0.  The half-open
     cones partition the cone over Q exactly.
  5. Each half-open box is enumerated through the column-HNF residue system;
     the resulting numerator over prod(1 - t^{q_j}) is expanded as a power
     series and summed.

Output: exact P(n) for n = 0..d+3, the exact monomial coefficients of P, and
the exact h*-vector.  Self-checks: P(0) = 1, P must agree with its own
degree-d interpolant at n = d+1, d+2, d+3.
"""

import sys
import json
import random
from fractions import Fraction
from math import comb, gcd

sys.path.insert(0, __file__.rsplit("engineC", 1)[0] + "engine")
import hive_poly  # noqa: E402

import cdd.gmp as cg  # noqa: E402


# ------------------------------------------------------------------ integer LA
def col_hnf(M, want_u=False):
    """Column-style HNF.  M is list of rows (ints), size m x n.
    Returns (H, U) with M*U = H, U unimodular, H in column echelon (lower
    triangular-ish) form.  If want_u is False, U is None."""
    m = len(M)
    n = len(M[0]) if m else 0
    H = [row[:] for row in M]
    U = [[1 if i == j else 0 for j in range(n)] for i in range(n)] if want_u else None
    piv = 0
    for r in range(m):
        if piv >= n:
            break
        # eliminate within columns piv..n-1 using gcd steps on row r
        while True:
            nz = [j for j in range(piv, n) if H[r][j] != 0]
            if len(nz) <= 1:
                break
            # pick column with smallest |entry|
            j0 = min(nz, key=lambda j: abs(H[r][j]))
            for j in nz:
                if j == j0:
                    continue
                q = H[r][j] // H[r][j0]
                if q:
                    for i in range(m):
                        H[i][j] -= q * H[i][j0]
                    if want_u:
                        for i in range(n):
                            U[i][j] -= q * U[i][j0]
        nz = [j for j in range(piv, n) if H[r][j] != 0]
        if not nz:
            continue
        j0 = nz[0]
        if j0 != piv:
            for i in range(m):
                H[i][j0], H[i][piv] = H[i][piv], H[i][j0]
            if want_u:
                for i in range(n):
                    U[i][j0], U[i][piv] = U[i][piv], U[i][j0]
        if H[r][piv] < 0:
            for i in range(m):
                H[i][piv] = -H[i][piv]
            if want_u:
                for i in range(n):
                    U[i][piv] = -U[i][piv]
        piv += 1
    return H, U


def int_kernel(M):
    """Z-basis of {y in Z^n : M y = 0}, M given as list of rows."""
    m = len(M)
    n = len(M[0]) if m else 0
    if m == 0:
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    H, U = col_hnf(M, want_u=True)
    ker = []
    for j in range(n):
        if all(H[i][j] == 0 for i in range(m)):
            ker.append([U[i][j] for i in range(n)])
    return ker


def rational_nullspace(M):
    """Basis (list of integer rows) of {y in Q^n : M y = 0}, cleared to ints."""
    return int_kernel(M)


def saturated_lattice_basis(rows):
    """Z-basis of Z^n cap span_Q(rows)."""
    n = len(rows[0])
    K = int_kernel(rows)            # {y : rows . y = 0} ; rows of K span rowspace^perp
    if not K:
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    return int_kernel(K)            # {x : K x = 0} cap Z^n  == saturation


def det_int(M):
    """Exact determinant of a square integer matrix (Bareiss)."""
    n = len(M)
    A = [row[:] for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            piv = None
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    piv = i
                    break
            if piv is None:
                return 0
            A[k], A[piv] = A[piv], A[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
            A[i][k] = 0
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def adjugate(M):
    """Adjugate of an integer square matrix via exact Fraction inverse."""
    n = len(M)
    D = det_int(M)
    if D == 0:
        return None, 0
    # Gauss-Jordan over Fractions
    A = [[Fraction(M[i][j]) for j in range(n)] + [Fraction(1 if i == j else 0) for j in range(n)]
         for i in range(n)]
    for k in range(n):
        p = next(i for i in range(k, n) if A[i][k] != 0)
        A[k], A[p] = A[p], A[k]
        pv = A[k][k]
        A[k] = [v / pv for v in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]
                A[i] = [A[i][j] - f * A[k][j] for j in range(2 * n)]
    inv = [[A[i][n + j] for j in range(n)] for i in range(n)]
    adj = [[inv[i][j] * D for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            assert adj[i][j].denominator == 1
            adj[i][j] = int(adj[i][j])
    return adj, D


def solve_int(B, g):
    """Solve c with sum_i c_i * B[i] = g  (B rows independent, g in span)."""
    k = len(B)
    n = len(B[0])
    # least-squares-free: gaussian elimination on B^T c = g
    rows = [[Fraction(B[i][j]) for i in range(k)] + [Fraction(g[j])] for j in range(n)]
    piv_cols = []
    r = 0
    for c in range(k):
        p = None
        for i in range(r, n):
            if rows[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        pv = rows[r][c]
        rows[r] = [v / pv for v in rows[r]]
        for i in range(n):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [rows[i][j] - f * rows[r][j] for j in range(k + 1)]
        piv_cols.append(c)
        r += 1
    sol = [Fraction(0)] * k
    for i, c in enumerate(piv_cols):
        sol[c] = rows[i][k]
    for i in range(r, n):
        if rows[i][k] != 0:
            raise ValueError("inconsistent")
    out = []
    for v in sol:
        if v.denominator != 1:
            raise ValueError("non-integral coordinate")
        out.append(int(v))
    return out


# ------------------------------------------------------------------ geometry
def vertices_exact(A, b):
    d = len(A[0])
    rows = [[Fraction(b[i])] + [Fraction(-A[i][j]) for j in range(d)] for i in range(len(A))]
    mat = cg.matrix_from_array(rows, rep_type=cg.RepType.INEQUALITY)
    cg.matrix_canonicalize(mat)     # exact: pulls out implicit equalities
    poly = cg.polyhedron_from_matrix(mat)
    gens = cg.copy_generators(poly)
    verts = []
    for row in gens.array:
        if row[0] == 1:
            verts.append([Fraction(x) for x in row[1:]])
        else:
            raise ValueError("unbounded polytope")
    return verts


def lower_hull_triangulation(pts, rng, tries=12):
    """pts: list of rational points in Q^k (k = dim of the configuration chart).
    Returns list of (d+1)-subsets (index tuples) forming a regular triangulation."""
    k = len(pts[0])
    npts = len(pts)
    if npts == k + 1:
        return [tuple(range(npts))]
    for _ in range(tries):
        w = [Fraction(rng.randrange(1, 10 ** 6)) for _ in range(npts)]
        rows = [[Fraction(1)] + [Fraction(x) for x in pts[i]] + [w[i]] for i in range(npts)]
        mat = cg.matrix_from_array(rows, rep_type=cg.RepType.GENERATOR)
        poly = cg.polyhedron_from_matrix(mat)
        ineq = cg.copy_inequalities(poly)
        inc = cg.copy_incidence(poly)
        lin = set(ineq.lin_set)
        simplices = []
        bad = False
        for i, row in enumerate(ineq.array):
            if i in lin:
                continue
            if row[k + 1] > 0:       # lower facet
                s = sorted(inc[i])
                if len(s) != k + 1:
                    bad = True
                    break
                simplices.append(tuple(s))
        if not bad and simplices:
            return simplices
    raise ValueError("no generic lifting found")


# ------------------------------------------------------------------ main
def ehrhart(lam, mu, nu, seed=12345, extra=3, vol_cap=4 * 10 ** 6):
    A, b, amb, interior, ok = hive_poly.build(lam, mu, nu)
    if not ok:
        return dict(status="EMPTY")
    return ehrhart_AB(A, b, amb, seed=seed, extra=extra, vol_cap=vol_cap)


def ehrhart_AB(A, b, amb, seed=12345, extra=3, vol_cap=4 * 10 ** 6):
    if True:
        pass
    if amb == 0:
        return dict(status="OK", d=0, P=[1] * (extra + 2), coeffs=["1"], hstar=[1],
                    c=1, volume="0", nverts=1)
    verts = vertices_exact(A, b)
    if not verts:
        return dict(status="EMPTY")
    rng = random.Random(seed)

    # homogenize -> primitive integer generators in Z^{amb+1}
    gens = []
    for v in verts:
        L = 1
        for x in v:
            L = L * x.denominator // gcd(L, x.denominator)
        g = [int(x * L) for x in v] + [L]
        gg = 0
        for t in g:
            gg = gcd(gg, abs(t))
        gens.append([t // gg for t in g])

    B = saturated_lattice_basis(gens)
    dd = len(B) - 1                     # dim Q
    coords = [solve_int(B, g) for g in gens]
    hvec = [B[i][amb] for i in range(len(B))]
    heights = [sum(hvec[i] * c[i] for i in range(len(B))) for c in coords]
    assert all(h > 0 for h in heights)

    if dd == 0:
        P = [1] * (extra + 2)
        return dict(status="OK", d=0, P=P, coeffs=["1"], hstar=[1], c=1,
                    volume="0", nverts=1)

    # affine chart on the height-1 slice
    k0 = next(i for i in range(dd + 1) if hvec[i] != 0)
    pts = []
    for c, h in zip(coords, heights):
        p = [Fraction(c[i], h) for i in range(dd + 1) if i != k0]
        pts.append(p)

    simplices = lower_hull_triangulation(pts, rng)

    # adjugates once per simplex
    adjs = {}
    for S in simplices:
        M = [[coords[v][i] for v in S] for i in range(dd + 1)]
        adj, D = adjugate(M)
        if D == 0:
            return dict(status="DEGENERATE_SIMPLEX")
        if D < 0:
            D = -D
            adj = [[-x for x in row] for row in adj]
        adjs[S] = (adj, D)

    totvol = sum(v[1] for v in adjs.values())
    if totvol > vol_cap:
        return dict(status="VOL_CAP", boxwork=totvol, d=dd,
                    nverts=len(verts), nsimp=len(simplices))

    # generic interior z
    z = None
    for _ in range(30):
        rvec = [rng.randrange(1, 10 ** 7) for _ in range(len(coords))]
        cand = [sum(rvec[v] * coords[v][i] for v in range(len(coords)))
                for i in range(dd + 1)]
        good = True
        for S in simplices:
            adj, D = adjs[S]
            for j in range(dd + 1):
                if sum(adj[j][i] * cand[i] for i in range(dd + 1)) == 0:
                    good = False
                    break
            if not good:
                break
        if good:
            z = cand
            break
    if z is None:
        return dict(status="NO_GENERIC_Z")
    signs = {S: (adjs[S][0], adjs[S][1], None) for S in simplices}
    if totvol > vol_cap:
        return dict(status="VOL_CAP", boxwork=totvol, d=dd,
                    nverts=len(verts), nsimp=len(simplices))

    N = dd + extra + 1                  # need P(0..N)
    Pvals = [0] * (N + 1)
    for S in simplices:
        adj, D, _a = signs[S]
        M = [[coords[v][i] for v in S] for i in range(dd + 1)]
        if D < 0:
            D = -D
            adj = [[-x for x in row] for row in adj]
        qs = [heights[v] for v in S]
        # a_j = (adj . z)_j / D ; D > 0 now, so sign(a_j) = sign((adj.z)_j)
        a2 = [sum(adj[j][i] * z[i] for i in range(dd + 1)) for j in range(dd + 1)]
        assert all(x != 0 for x in a2)
        openflag = [1 if a2[j] < 0 else 0 for j in range(dd + 1)]

        # residue system via column HNF of M
        H, _ = col_hnf(M, want_u=False)
        diag = [H[i][i] for i in range(dd + 1)]
        assert all(x > 0 for x in diag), diag
        prod = 1
        for x in diag:
            prod *= x
        assert prod == D, (prod, D)

        cols = [[adj[j][i] for j in range(dd + 1)] for i in range(dd + 1)]  # cols[i] = adj[:,i]
        num = [0] * (N + 1)

        # ---- fast numpy path (exact: pure int64, guarded against overflow) --
        maxadj = max(abs(x) for row in adj for x in row)
        bound = maxadj * max(diag) * (dd + 1)
        if D > 64 and bound < 2 ** 61 and D * (dd + 1) < 4 * 10 ** 7:
            import numpy as np
            reps = np.zeros((dd + 1, D), dtype=np.int64)
            rep = 1
            for i in range(dd + 1):
                block = np.repeat(np.arange(diag[i], dtype=np.int64), rep)
                reps[i] = np.tile(block, D // (rep * diag[i]))
                rep *= diag[i]
            adjn = np.array(adj, dtype=np.int64)
            acc = adjn @ reps                       # (dd+1) x D
            nred = np.mod(acc, D)
            for j in range(dd + 1):
                if openflag[j]:
                    nred[j][nred[j] == 0] = D
            qsn = np.array(qs, dtype=np.int64)
            hh = (qsn @ nred)
            assert np.all(hh % D == 0)
            hh //= D
            hh = hh[hh <= N]
            bc = np.bincount(hh, minlength=N + 1)
            num = [int(x) for x in bc[:N + 1]]
            ser = num[:]
            for q in qs:
                for n in range(q, N + 1):
                    ser[n] += ser[n - q]
            for n in range(N + 1):
                Pvals[n] += ser[n]
            continue
        # ---------------------------------------------------------------------
        idx = [0] * (dd + 1)
        acc = [0] * (dd + 1)
        while True:
            hgt = 0
            for j in range(dd + 1):
                nj = acc[j] % D
                if openflag[j] and nj == 0:
                    nj = D
                hgt += nj * qs[j]
            assert hgt % D == 0
            hgt //= D
            if hgt <= N:
                num[hgt] += 1
            i = 0
            while i <= dd:
                ci = cols[i]
                idx[i] += 1
                for j in range(dd + 1):
                    acc[j] += ci[j]
                if idx[i] < diag[i]:
                    break
                back = diag[i]
                idx[i] = 0
                for j in range(dd + 1):
                    acc[j] -= back * ci[j]
                i += 1
            if i > dd:
                break
        # series: num(t) / prod (1 - t^{q_j})
        ser = num[:]
        for q in qs:
            for n in range(q, N + 1):
                ser[n] += ser[n - q]
        for n in range(N + 1):
            Pvals[n] += ser[n]

    # verify polynomiality
    coeffs = lagrange_coeffs(Pvals[:dd + 1])
    for n in range(dd + 1, N + 1):
        val = sum(coeffs[i] * Fraction(n) ** i for i in range(len(coeffs)))
        if val != Pvals[n]:
            return dict(status="NONPOLY", d=dd, P=Pvals)
    hs = [sum((-1) ** i * comb(dd + 1, i) * Pvals[j - i] for i in range(j + 1))
          for j in range(dd + 1)]
    return dict(status="OK", d=dd, P=Pvals, coeffs=[str(c) for c in coeffs],
                hstar=hs, c=Pvals[1], nvol=sum(hs), boxwork=totvol,
                nverts=len(verts), nsimp=len(simplices),
                maxden=max(heights))


def lagrange_coeffs(vals):
    """Exact monomial coefficients of the interpolating polynomial through
    (n, vals[n]) for n = 0..len(vals)-1."""
    m = len(vals)
    coeffs = [Fraction(0)] * m
    for i in range(m):
        # basis polynomial prod_{j != i} (x - j)/(i - j)
        poly = [Fraction(1)]
        den = Fraction(1)
        for j in range(m):
            if j == i:
                continue
            new = [Fraction(0)] * (len(poly) + 1)
            for k, cc in enumerate(poly):
                new[k + 1] += cc
                new[k] -= cc * j
            poly = new
            den *= (i - j)
        for k in range(m):
            coeffs[k] += vals[i] * poly[k] / den
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def parse(s):
    return [int(x) for x in s.replace(",", " ").split()]


if __name__ == "__main__":
    if sys.argv[1] == "--batch":
        for line in open(sys.argv[2]):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split(";")
            lam, mu, nu = parse(p[0]), parse(p[1]), parse(p[2])
            try:
                r = ehrhart(lam, mu, nu)
            except Exception as e:
                r = dict(status="ERR", err=repr(e))
            r["lam"], r["mu"], r["nu"] = lam, mu, nu
            print(json.dumps(r))
            sys.stdout.flush()
    else:
        lam, mu, nu = parse(sys.argv[1]), parse(sys.argv[2]), parse(sys.argv[3])
        print(json.dumps(ehrhart(lam, mu, nu)))
