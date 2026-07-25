#!/usr/bin/env python3
"""Exact rational / integer linear algebra used by the r=5 certificate build.

Everything here is exact (Fraction or int).  No floating point anywhere.
"""
from fractions import Fraction
from math import gcd


# ---------------------------------------------------------------- rref/rank
def rref(rows):
    """Reduced row echelon form over Q.  Returns tuple of tuples (nonzero rows)."""
    M = [[Fraction(x) for x in r] for r in rows]
    if not M:
        return ()
    ncol = len(M[0])
    r = 0
    for c in range(ncol):
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
                M[i] = [M[i][k] - f * M[r][k] for k in range(ncol)]
        r += 1
        if r == len(M):
            break
    return tuple(tuple(row) for row in M[:r])


def rank(rows):
    return len(rref(rows))


def rank_mod(rows, p=2147483647):
    """Rank of the rational matrix reduced mod a large prime p.

    rank_mod <= rational rank always (rank can only drop mod p), so
    rank_mod == r certifies rational rank >= r.  Fast: no fraction blowup.
    Rows may contain Fractions; each is reduced mod p (denominator inverted).
    """
    M = []
    for row in rows:
        r = []
        for x in row:
            fx = Fraction(x)
            r.append((fx.numerator % p) * pow(fx.denominator % p, p - 2, p) % p)
        M.append(r)
    ncol = len(M[0]) if M else 0
    rr = 0
    for c in range(ncol):
        piv = None
        for i in range(rr, len(M)):
            if M[i][c] % p != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rr], M[piv] = M[piv], M[rr]
        inv = pow(M[rr][c], p - 2, p)
        M[rr] = [(x * inv) % p for x in M[rr]]
        for i in range(len(M)):
            if i != rr and M[i][c] % p != 0:
                f = M[i][c]
                M[i] = [(M[i][k] - f * M[rr][k]) % p for k in range(ncol)]
        rr += 1
        if rr == len(M):
            break
    return rr


def pivots(R, n):
    piv = []
    for row in R:
        for c in range(n):
            if row[c] != 0:
                piv.append(c)
                break
    return piv


def kernel_basis(rows, n):
    """Basis of {x in Q^n : rows . x = 0}."""
    R = rref(rows)
    piv = pivots(R, n)
    free = [c for c in range(n) if c not in piv]
    out = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for i, row in enumerate(R):
            v[piv[i]] = -row[f]
        out.append(v)
    return out


# ------------------------------------------------------------- primitivity
def prim(v):
    """Primitive integer vector proportional to v (sign preserved)."""
    den = 1
    for x in v:
        d = Fraction(x).denominator
        den = den * d // gcd(den, d)
    w = [int(Fraction(x) * den) for x in v]
    g = 0
    for x in w:
        g = gcd(g, abs(x))
    if g:
        w = [x // g for x in w]
    return tuple(w)


def canon_line(v):
    """Primitive representative of the LINE R v (first nonzero entry > 0)."""
    w = prim(v)
    for x in w:
        if x != 0:
            if x < 0:
                w = tuple(-y for y in w)
            break
    return w


# --------------------------------------------------------------- solve/det
def solve_square(Asub, bsub, d):
    """Exact solve of a d x d system; None if singular."""
    M = [[Fraction(Asub[i][j]) for j in range(d)] + [Fraction(bsub[i])]
         for i in range(d)]
    for c in range(d):
        p = None
        for i in range(c, d):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for i in range(d):
            if i != c and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][k] - f * M[c][k] for k in range(d + 1)]
    return [M[i][d] for i in range(d)]


def det_frac(M):
    k = len(M)
    T = [[Fraction(x) for x in row] for row in M]
    D = Fraction(1)
    for c in range(k):
        p = None
        for i in range(c, k):
            if T[i][c] != 0:
                p = i
                break
        if p is None:
            return Fraction(0)
        if p != c:
            T[c], T[p] = T[p], T[c]
            D = -D
        D *= T[c][c]
        pv = T[c][c]
        T[c] = [x / pv for x in T[c]]
        for i in range(c + 1, k):
            if T[i][c] != 0:
                f = T[i][c]
                T[i] = [T[i][x] - f * T[c][x] for x in range(k)]
    return D


def det_int_bareiss(M):
    """Exact integer determinant (fraction-free Bareiss)."""
    n = len(M)
    M = [list(map(int, row)) for row in M]
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def invert(M, k):
    T = [[Fraction(M[i][j]) for j in range(k)]
         + [Fraction(1) if i == j else Fraction(0) for j in range(k)]
         for i in range(k)]
    for c in range(k):
        p = None
        for i in range(c, k):
            if T[i][c] != 0:
                p = i
                break
        if p is None:
            raise ValueError('singular')
        T[c], T[p] = T[p], T[c]
        pv = T[c][c]
        T[c] = [x / pv for x in T[c]]
        for i in range(k):
            if i != c and T[i][c] != 0:
                f = T[i][c]
                T[i] = [T[i][x] - f * T[c][x] for x in range(2 * k)]
    return [[T[i][k + j] for j in range(k)] for i in range(k)]


# ------------------------------------------------------------ Smith normal
def smith(M, rows, cols):
    """Smith normal form.  Returns (S, U, V) with S = U M V, U,V unimodular."""
    A = [row[:] for row in M]
    U = [[1 if i == j else 0 for j in range(rows)] for i in range(rows)]
    V = [[1 if i == j else 0 for j in range(cols)] for i in range(cols)]

    def swap_rows(i, j):
        A[i], A[j] = A[j], A[i]
        U[i], U[j] = U[j], U[i]

    def swap_cols(i, j):
        for r in A:
            r[i], r[j] = r[j], r[i]
        for r in V:
            r[i], r[j] = r[j], r[i]

    def addrow(i, j, q):
        A[i] = [A[i][k] + q * A[j][k] for k in range(cols)]
        U[i] = [U[i][k] + q * U[j][k] for k in range(rows)]

    def addcol(i, j, q):
        for r in A:
            r[i] += q * r[j]
        for r in V:
            r[i] += q * r[j]

    t = 0
    while t < min(rows, cols):
        piv = None
        for i in range(t, rows):
            for j in range(t, cols):
                if A[i][j] != 0:
                    piv = (i, j)
                    break
            if piv:
                break
        if piv is None:
            break
        swap_rows(t, piv[0])
        swap_cols(t, piv[1])
        while True:
            done = True
            for i in range(t + 1, rows):
                if A[i][t]:
                    addrow(i, t, -(A[i][t] // A[t][t]))
                    if A[i][t]:
                        swap_rows(t, i)
                        done = False
            for j in range(t + 1, cols):
                if A[t][j]:
                    addcol(j, t, -(A[t][j] // A[t][t]))
                    if A[t][j]:
                        swap_cols(t, j)
                        done = False
            if done:
                break
        t += 1
    return A, U, V


def saturation_index(rows):
    """[sat(L):L] for the lattice L spanned by the integer rows (rows independent)."""
    r = len(rows)
    c = len(rows[0])
    S, _U, _V = smith([list(map(int, row)) for row in rows], r, c)
    idx = 1
    for i in range(r):
        idx *= abs(S[i][i])
    return idx


# --------------------------------------------------------- exact phase-1 LP
def in_cone(gens, target):
    """Exact: does target lie in cone{gens} (nonnegative span)?"""
    m = len(target)
    n = len(gens)
    if n == 0:
        return all(Fraction(t) == 0 for t in target)
    A = [[Fraction(gens[j][i]) for j in range(n)] for i in range(m)]
    b = [Fraction(t) for t in target]
    for i in range(m):
        if b[i] < 0:
            A[i] = [-x for x in A[i]]
            b[i] = -b[i]
    NN = n + m
    T = [A[i] + [Fraction(1) if k == i else Fraction(0) for k in range(m)] + [b[i]]
         for i in range(m)]
    basis = list(range(n, NN))
    cost = [Fraction(0)] * (NN + 1)
    for i in range(m):
        for k in range(NN + 1):
            cost[k] += T[i][k]
    for k in range(n, NN):
        cost[k] = Fraction(0)
    while True:
        e = -1
        for k in range(n):
            if cost[k] > 0:
                e = k
                break
        if e < 0:
            break
        lv, best = -1, None
        for i in range(m):
            if T[i][e] > 0:
                ratio = T[i][NN] / T[i][e]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[lv]):
                    best, lv = ratio, i
        if lv < 0:
            return False
        pv = T[lv][e]
        T[lv] = [x / pv for x in T[lv]]
        for i in range(m):
            if i != lv and T[i][e] != 0:
                f = T[i][e]
                T[i] = [T[i][k] - f * T[lv][k] for k in range(NN + 1)]
        f = cost[e]
        if f != 0:
            cost = [cost[k] - f * T[lv][k] for k in range(NN + 1)]
        basis[lv] = e
    return cost[NN] == 0


def solve_nonneg(Acols, rhs):
    """Exact phase-1 simplex for {x >= 0 : Acols . x = rhs}.

    Acols is a list of columns (each of length m).  Returns the solution vector
    x (list of Fractions, length len(Acols)) or None if infeasible.
    """
    m = len(rhs)
    n = len(Acols)
    A = [[Fraction(Acols[j][i]) for j in range(n)] for i in range(m)]
    b = [Fraction(t) for t in rhs]
    for i in range(m):
        if b[i] < 0:
            A[i] = [-x for x in A[i]]
            b[i] = -b[i]
    NN = n + m
    T = [A[i] + [Fraction(1) if k == i else Fraction(0) for k in range(m)] + [b[i]]
         for i in range(m)]
    basis = list(range(n, NN))
    cost = [Fraction(0)] * (NN + 1)
    for i in range(m):
        for k in range(NN + 1):
            cost[k] += T[i][k]
    for k in range(n, NN):
        cost[k] = Fraction(0)
    while True:
        e = -1
        for k in range(n):
            if cost[k] > 0:
                e = k
                break
        if e < 0:
            break
        lv, best = -1, None
        for i in range(m):
            if T[i][e] > 0:
                ratio = T[i][NN] / T[i][e]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[lv]):
                    best, lv = ratio, i
        if lv < 0:
            return None
        pv = T[lv][e]
        T[lv] = [x / pv for x in T[lv]]
        for i in range(m):
            if i != lv and T[i][e] != 0:
                f = T[i][e]
                T[i] = [T[i][k] - f * T[lv][k] for k in range(NN + 1)]
        f = cost[e]
        if f != 0:
            cost = [cost[k] - f * T[lv][k] for k in range(NN + 1)]
        basis[lv] = e
    if cost[NN] != 0:
        return None
    x = [Fraction(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = T[i][NN]
    return x


def interpolate(values):
    """Exact Lagrange interpolation of the polynomial through (i, values[i])."""
    n = len(values)
    coeffs = [Fraction(0)] * n
    for i in range(n):
        # basis polynomial prod_{j != i} (x - j)/(i - j)
        num = [Fraction(1)]
        den = Fraction(1)
        for j in range(n):
            if j == i:
                continue
            num = poly_mul(num, [Fraction(-j), Fraction(1)])
            den *= Fraction(i - j)
        f = Fraction(values[i]) / den
        for t, c in enumerate(num):
            coeffs[t] += f * c
    return coeffs


def poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out
