#!/usr/bin/env python3
"""
hiveR.py -- exact hive-polytope constructor for ARBITRARY side r.

Q(lam,mu,nu) = { h in R^D : A h <= b },  D = (r-1)(r-2)/2 interior entries.
A depends ONLY on r; b is integral and linear/homogeneous in (lam,mu,nu).

Conventions match r4_reeve/hive4.py exactly (BUILD_A.md boundary convention):
  left edge   B[(0,y)]     = lam_1+...+lam_y
  hypotenuse  B[(x,r-x)]   = |lam| + mu_1+...+mu_x
  bottom edge B[(x,0)]     = nu_1+...+nu_x

All arithmetic exact (int / Fraction).  No float decides anything.
"""

import itertools
import math
from fractions import Fraction


def interior(r):
    """Interior lattice points of the side-r triangle, fixed order."""
    return [(x, y) for s in range(2, r) for x in range(1, s) for y in [s - x]
            ] if False else [
        (x, y) for x in range(1, r) for y in range(1, r) if x + y <= r - 1]


def _norm_parts(p, r):
    p = [int(x) for x in p]
    while p and p[-1] == 0:
        p.pop()
    if len(p) > r:
        return None
    p = p + [0] * (r - len(p))
    for i in range(len(p) - 1):
        if p[i] < p[i + 1]:
            return None
    if any(x < 0 for x in p):
        return None
    return p


def rows_symbolic(r):
    """
    Rhombus rows for side r as (coeff-vector on interior coords,
                                dict boundary-vertex -> coefficient)
    encoding the inequality   coeff . h + sum_v bcoef[v] B[v]  <= 0.
    (so b_row = - sum_v bcoef[v] B[v])
    """
    INT = interior(r)
    idx = {v: i for i, v in enumerate(INT)}
    D = len(INT)
    out = []

    def add(plus, minus, tag):
        co = [0] * D
        bc = {}
        for v in plus:
            if v in idx:
                co[idx[v]] -= 1
            else:
                bc[v] = bc.get(v, 0) - 1
        for v in minus:
            if v in idx:
                co[idx[v]] += 1
            else:
                bc[v] = bc.get(v, 0) + 1
        out.append((co, bc, tag))

    for x in range(r + 1):
        for y in range(r + 1):
            if x + y <= r - 2:
                add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)], ("A", x, y))
            if y >= 1 and x + y <= r - 1:
                add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)], ("B", x, y))
            if x >= 1 and x + y <= r - 1:
                add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)], ("C", x, y))
    return out


def boundary_map(r):
    """B[v] as an integer-linear form in the 3r free coordinates
       (lam_1..lam_r, mu_1..mu_r, nu_1..nu_r)."""
    B = {}
    z = [0] * (3 * r)

    def vec():
        return list(z)

    v = vec()
    B[(0, 0)] = vec()
    for y in range(1, r + 1):
        w = vec()
        for i in range(y):
            w[i] = 1
        B[(0, y)] = w
    for x in range(r + 1):
        w = vec()
        for i in range(r):
            w[i] = 1            # |lam|
        for i in range(x):
            w[r + i] += 1       # mu partial sum
        B[(x, r - x)] = w
    for x in range(r + 1):
        w = vec()
        for i in range(x):
            w[2 * r + i] = 1
        B[(x, 0)] = w
    B[(0, 0)] = vec()
    return B


def build_hive(lam, mu, nu, r):
    """Return dict(ok, A, b, reason).  Q = {h : A h <= b}."""
    lam = _norm_parts(lam, r)
    mu = _norm_parts(mu, r)
    nu = _norm_parts(nu, r)
    if lam is None or mu is None or nu is None:
        return {"ok": False, "reason": "bad_partition", "A": [], "b": []}
    if sum(lam) + sum(mu) != sum(nu):
        return {"ok": False, "reason": "weight_mismatch", "A": [], "b": []}

    def ps(p, k):
        return sum(p[:k])

    Bv = {}
    for y in range(r + 1):
        Bv[(0, y)] = ps(lam, y)
    for x in range(r + 1):
        Bv[(x, r - x)] = sum(lam) + ps(mu, x)
    for x in range(r + 1):
        Bv[(x, 0)] = ps(nu, x)
    Bv[(0, 0)] = 0

    A, b = [], []
    ok, reason = True, None
    D = len(interior(r))
    for co, bc, tag in rows_symbolic(r):
        const = sum(c * Bv[v] for v, c in bc.items())
        if all(c == 0 for c in co):
            if const > 0:
                ok = False
                reason = reason or "boundary_rhombus_violated"
            continue
        A.append(co)
        b.append(-const)
    return {"ok": ok, "reason": reason, "A": A, "b": b,
            "lam": lam, "mu": mu, "nu": nu}


def fixed_A(r):
    """The r-dependent constraint matrix (rows with a nonzero interior part),
       together with the integer matrix Dm mapping (lam,mu,nu) -> b."""
    rs = [t for t in rows_symbolic(r) if any(c != 0 for c in t[0])]
    Bm = boundary_map(r)
    A = [t[0] for t in rs]
    Dm = []
    for co, bc, tag in rs:
        w = [0] * (3 * r)
        for v, c in bc.items():
            for i in range(3 * r):
                w[i] -= c * Bm[v][i]
        Dm.append(w)          # b_row = Dm_row . (lam,mu,nu)
    tags = [t[2] for t in rs]
    return A, Dm, tags


# ---------------------------------------------------------------- exact utils

def rank_q(rows):
    if not rows:
        return 0
    M = [[Fraction(x) for x in r] for r in rows]
    nc = len(M[0])
    r = 0
    for c in range(nc):
        piv = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / pv
                M[i] = [M[i][k] - f * M[r][k] for k in range(nc)]
        r += 1
        if r == len(M):
            break
    return r


def det_int(M):
    """Exact integer determinant (Bareiss)."""
    n = len(M)
    M = [row[:] for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            piv = None
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    piv = i
                    break
            if piv is None:
                return 0
            M[k], M[piv] = M[piv], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
            M[i][k] = 0
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def smith_invariants(M):
    """Invariant factors (elementary divisors d_1|d_2|...) of an integer matrix."""
    A = [row[:] for row in M]
    m, n = len(A), len(A[0])
    res = []
    si = 0
    sj = 0
    while si < m and sj < n:
        # find pivot = smallest nonzero abs
        piv = None
        best = None
        for i in range(si, m):
            for j in range(sj, n):
                if A[i][j] != 0 and (best is None or abs(A[i][j]) < best):
                    best = abs(A[i][j])
                    piv = (i, j)
        if piv is None:
            break
        pi, pj = piv
        A[si], A[pi] = A[pi], A[si]
        for row in A:
            row[si], row[pj] = row[pj], row[si]
        # reduce
        while True:
            done = True
            for i in range(si + 1, m):
                if A[i][si] != 0:
                    q = A[i][si] // A[si][si]
                    for j in range(si, n):
                        A[i][j] -= q * A[si][j]
                    if A[i][si] != 0:
                        A[si], A[i] = A[i], A[si]
                        done = False
            for j in range(sj + 1, n):
                if A[si][j] != 0:
                    q = A[si][j] // A[si][si]
                    for i in range(si, m):
                        A[i][j] -= q * A[i][si]
                    if A[si][j] != 0:
                        for i in range(si, m):
                            A[i][si], A[i][j] = A[i][j], A[i][si]
                        done = False
            if done:
                break
        res.append(abs(A[si][si]))
        si += 1
        sj += 1
    # enforce divisibility
    for i in range(len(res)):
        for j in range(i + 1, len(res)):
            a, b = res[i], res[j]
            if a == 0:
                res[i], res[j] = b, a
                continue
            if b % a:
                g = math.gcd(a, b)
                res[i], res[j] = g, a * b // g
    return res
