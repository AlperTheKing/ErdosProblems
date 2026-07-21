#!/usr/bin/env python3
"""
hive4.py -- DIRECT r=4 hive-polytope engine (the "Reeve dimension" cell).

TARGET
  A counterexample to the King-Tollu-Toumazet (2004) positivity conjecture:
  partitions (lam, mu, nu) with |lam|+|mu|=|nu| whose stretched Littlewood-
  Richardson polynomial P(n) = c(n*nu; n*lam, n*mu) has a strictly NEGATIVE
  coefficient.

WHY r = 4
  Knutson-Tao: c(nu; lam, mu) = #( Q(lam,mu,nu) cap Z^D ), where Q is the hive
  polytope living in the space of the D = (r-1)(r-2)/2 INTERIOR vertices of a
  side-r triangular array, cut out by the three rhombus-inequality families,
  with the boundary fixed by the partial sums of lam (left edge), mu (right
  edge), nu (bottom edge).  Stretching by n DILATES Q by n (the constraint
  matrix is unchanged, the right-hand side is linear in the boundary data), so
  P is the Ehrhart counting function of Q and deg P = dim Q.

  r = 4  ==>  D = 3 EXACTLY.  Dimension 3 is the REEVE DIMENSION: the smallest
  dimension in which an Ehrhart polynomial can have a negative coefficient
  (impossible for d <= 2).  The classical witness is the Reeve tetrahedron
  T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)}: 4 lattice points, h* =
  (1,0,q-1,0), normalized volume q, and linear coefficient a_1 = 2 - q/6 < 0
  for q >= 13.  r = 3 is dim 1 (trivially positive); so r = 4 is the minimal
  live case, and at dim 3 EVERYTHING is computable directly from the polytope
  -- no stretched LR counting is needed anywhere in this module.

RIGOR CONTRACT
  * All arithmetic is exact: Python ints and fractions.Fraction. There is NO
    floating point anywhere in this file. No verdict may rest on a float.
  * Vertices are produced by solving every 3-subset of constraint rows exactly
    and keeping the exactly-feasible solutions; Q is a bounded polytope, so
    this enumerates ALL vertices.
  * The normalized volume is computed twice by independent routes -- exact
    boundary triangulation, and 6 * (leading coefficient of the interpolated
    Ehrhart polynomial) -- and the two must agree or the analysis is flagged.
  * The interpolated P (from L(0..3)) is VERIFIED against directly enumerated
    L(4) and L(5).  A mismatch is reported, never smoothed over.
  * Absence of a negative coefficient proves nothing whatsoever about the
    conjecture and must never be reported as support for it.

CLI
  python hive4.py "lam" "mu" "nu"        one JSON line, full analysis
  python hive4.py --batch FILE          lines "lam;mu;nu" -> dim,c,V,h*,minc,NEG
  python hive4.py --reeve [QMAX]        Reeve T_q unit test, q = 1..QMAX
  python hive4.py --selftest            Reeve test + small hive sanity checks

The mandated cross-engine validation lives in the sibling scripts
validate_hive4.py (400 triples + 60 stretched + Reeve) and validate_dim3.py
(the dim-3 stratum, where negativity is the only possibility).
"""

import argparse
import itertools
import json
import math
import random
import sys
from fractions import Fraction

# --------------------------------------------------------------------------
#  exact linear algebra over Q  (lists of Fraction / int)
# --------------------------------------------------------------------------


def _det3(m):
    """Exact 3x3 determinant."""
    (a, b, c), (d, e, f), (g, h, i) = m
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _solve3(A3, b3):
    """Exact solve of a 3x3 system; None if singular."""
    D = _det3(A3)
    if D == 0:
        return None
    out = []
    for j in range(3):
        M = [[b3[i] if k == j else A3[i][k] for k in range(3)] for i in range(3)]
        out.append(Fraction(_det3(M), D))
    return out


def _rank(rows):
    """Exact row rank over Q of a list of equal-length vectors."""
    if not rows:
        return 0
    M = [[Fraction(x) for x in r] for r in rows]
    ncol = len(M[0])
    r = 0
    for c in range(ncol):
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
                M[i] = [M[i][k] - f * M[r][k] for k in range(ncol)]
        r += 1
        if r == len(M):
            break
    return r


def _affine_rank(pts):
    """dim of the affine hull of pts (exact)."""
    if not pts:
        return -1
    p0 = pts[0]
    return _rank([[p[k] - p0[k] for k in range(len(p0))] for p in pts[1:]])


def _dot(a, x):
    return sum(ai * xi for ai, xi in zip(a, x))


def _sub(p, q):
    return [p[k] - q[k] for k in range(len(p))]


def _cross(u, v):
    return [
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    ]


# --------------------------------------------------------------------------
#  the r = 4 hive polytope
# --------------------------------------------------------------------------

# interior vertices of the side-4 triangular array, in fixed coordinate order
INTERIOR4 = [(1, 1), (1, 2), (2, 1)]


def _norm_parts(p, r):
    """pad/trim a partition to length r; validate weakly decreasing, >= 0."""
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


def build_hive4(lam, mu, nu):
    """
    Build Q(lam,mu,nu) for r = 4 as {h in R^3 : A h <= b}, h indexed by
    INTERIOR4 = [(1,1),(1,2),(2,1)].

    Returns dict:
      ok        False iff the boundary data already violates a rhombus
                inequality involving no interior vertex (=> Q empty)
      A, b      integer constraint rows / right-hand sides (Q = {A h <= b})
      reason    when not ok
    Boundary convention identical to engine A (BUILD_A.md):
      left edge   B[(0,y)] = lam_1+...+lam_y
      hypotenuse  B[(x,4-x)] = |lam| + mu_1+...+mu_x
      bottom edge B[(x,0)] = nu_1+...+nu_x
    """
    r = 4
    lam = _norm_parts(lam, r)
    mu = _norm_parts(mu, r)
    nu = _norm_parts(nu, r)
    if lam is None or mu is None or nu is None:
        return {"ok": False, "reason": "bad_partition", "A": [], "b": []}
    if sum(lam) + sum(mu) != sum(nu):
        return {"ok": False, "reason": "weight_mismatch", "A": [], "b": []}

    def ps(p, k):
        return sum(p[:k])

    B = {}
    for y in range(r + 1):
        B[(0, y)] = ps(lam, y)
    for x in range(r + 1):
        B[(x, r - x)] = sum(lam) + ps(mu, x)
    for x in range(r + 1):
        B[(x, 0)] = ps(nu, x)
    B[(0, 0)] = 0

    idx = {v: i for i, v in enumerate(INTERIOR4)}
    A, b = [], []
    ok = True
    reason = None

    def add(plus, minus):
        """impose  sum(plus) >= sum(minus), i.e.  sum(minus)-sum(plus) <= 0."""
        nonlocal ok, reason
        co = [0, 0, 0]
        const = 0
        for v in plus:
            if v in idx:
                co[idx[v]] -= 1
            else:
                const -= B[v]
        for v in minus:
            if v in idx:
                co[idx[v]] += 1
            else:
                const += B[v]
        if co == [0, 0, 0]:
            if const > 0:
                ok = False
                if reason is None:
                    reason = "boundary_rhombus_violated"
            return
        A.append(co)
        b.append(-const)

    for x in range(r + 1):
        for y in range(r + 1):
            if x + y <= r - 2:  # (A)
                add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= r - 1:  # (B)
                add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= r - 1:  # (C)
                add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])

    return {"ok": ok, "reason": reason, "A": A, "b": b, "lam": lam, "mu": mu, "nu": nu}


# --------------------------------------------------------------------------
#  generic exact polytope machinery in R^3  ( Q = {A h <= b} , bounded )
# --------------------------------------------------------------------------


_CRAMER_CACHE = {}


def _adjugate3(M):
    """Integer adjugate of a 3x3 integer matrix: M^{-1} = adj(M)/det(M)."""
    def minor(r, c):
        rows = [x for x in range(3) if x != r]
        cols = [x for x in range(3) if x != c]
        return (M[rows[0]][cols[0]] * M[rows[1]][cols[1]]
                - M[rows[0]][cols[1]] * M[rows[1]][cols[0]])
    # adj[r][c] = cofactor(c, r)
    return [[(-1) ** (r + c) * minor(c, r) for c in range(3)] for r in range(3)]


def _cramer_data(A):
    """
    Cache the (3-subset -> integer Cramer solver) table for a constraint matrix.
    For r = 4 the matrix A is IDENTICAL for every (lam, mu, nu) -- only b moves
    -- so this table is built once for the entire census.
    Each entry is (i, j, k, D, adj) with D > 0 and x = adj @ (b_i,b_j,b_k) / D.
    """
    key = tuple(tuple(r) for r in A)
    got = _CRAMER_CACHE.get(key)
    if got is not None:
        return got
    combos = []
    for i, j, k in itertools.combinations(range(len(A)), 3):
        M = [A[i], A[j], A[k]]
        D = _det3(M)
        if D == 0:
            continue
        adj = _adjugate3(M)
        if D < 0:
            D = -D
            adj = [[-x for x in row] for row in adj]
        combos.append((i, j, k, D, adj))
    _CRAMER_CACHE[key] = combos
    return combos


def vertices(A, b):
    """
    All vertices of Q = {x in R^3 : A x <= b}, exact Fractions.
    Q is assumed BOUNDED (certified by is_bounded), so every vertex is the
    unique solution of some 3 linearly independent tight rows; enumerating all
    3-subsets is therefore complete.
    Pure integer arithmetic: the candidate is kept in the form num/D and the
    feasibility test  a . (num/D) <= rhs  is done as  a . num <= rhs * D
    (legitimate because D > 0 by construction).
    Returns a sorted, de-duplicated list of 3-vectors of Fraction.
    """
    seen = {}
    for i, j, k, D, adj in _cramer_data(A):
        b3 = (b[i], b[j], b[k])
        n0 = adj[0][0] * b3[0] + adj[0][1] * b3[1] + adj[0][2] * b3[2]
        n1 = adj[1][0] * b3[0] + adj[1][1] * b3[1] + adj[1][2] * b3[2]
        n2 = adj[2][0] * b3[0] + adj[2][1] * b3[1] + adj[2][2] * b3[2]
        feasible = True
        for row, rhs in zip(A, b):
            if row[0] * n0 + row[1] * n1 + row[2] * n2 > rhs * D:
                feasible = False
                break
        if feasible:
            seen[(Fraction(n0, D), Fraction(n1, D), Fraction(n2, D))] = True
    return [list(v) for v in sorted(seen.keys())]


def denominators(verts):
    return sorted({c.denominator for v in verts for c in v})


def facets(A, b, verts):
    """
    Facets of Q as (normal_row, [vertex indices]) with the vertex set having
    affine rank exactly 2.  De-duplicated by vertex set.
    """
    out = {}
    for row, rhs in zip(A, b):
        S = [i for i, v in enumerate(verts) if _dot(row, v) == rhs]
        if len(S) < 3:
            continue
        if _affine_rank([verts[i] for i in S]) != 2:
            continue
        key = frozenset(S)
        if key not in out:
            out[key] = (row, S)
    return list(out.values())


def _centroid(pts):
    n = len(pts)
    return [sum(p[k] for p in pts) / Fraction(n) for k in range(3)]


def _angular_order(pts2d):
    """Exact CCW angular sort of 2-D exact points around the origin."""
    import functools

    def half(p):
        return 0 if (p[1] > 0 or (p[1] == 0 and p[0] > 0)) else 1

    def cmp(p, q):
        hp, hq = half(p), half(q)
        if hp != hq:
            return -1 if hp < hq else 1
        cr = p[0] * q[1] - p[1] * q[0]
        if cr > 0:
            return -1
        if cr < 0:
            return 1
        return 0

    return sorted(range(len(pts2d)), key=functools.cmp_to_key(lambda i, j: cmp(pts2d[i], pts2d[j])))


def normalized_volume(A, b, verts):
    """
    V = 3! * vol(Q), EXACT.  Boundary triangulation: every facet polygon is
    fan-triangulated after an exact angular sort, and each boundary triangle is
    coned to the centroid c of the vertex set (c is in Q by convexity), giving
    a tiling of Q by tetrahedra.  V = sum |det(p-c, q-c, r-c)|.
    Returns Fraction 0 if dim Q < 3.
    """
    if len(verts) < 4 or _affine_rank(verts) < 3:
        return Fraction(0)
    c = _centroid(verts)
    total = Fraction(0)
    for row, S in facets(A, b, verts):
        P = [verts[i] for i in S]
        fc = _centroid(P)
        e1 = None
        for p in P:
            d = _sub(p, fc)
            if any(x != 0 for x in d):
                e1 = d
                break
        e2 = _cross([Fraction(t) for t in row], e1)
        coords = [(_dot(_sub(p, fc), e1), _dot(_sub(p, fc), e2)) for p in P]
        order = _angular_order(coords)
        for t in range(1, len(order) - 1):
            p = P[order[0]]
            q = P[order[t]]
            rr = P[order[t + 1]]
            total += abs(_det3([_sub(p, c), _sub(q, c), _sub(rr, c)]))
    return total


def is_bounded(A):
    """
    EXACT certificate that {x : A x <= 0} = {0}, i.e. every polytope
    {x : A x <= b} with this A is bounded.
    Method: the lineality space is ker(A); if rank(A) < 3 the cone contains a
    line and is non-trivial.  Otherwise the cone is pointed, so it is
    non-trivial iff it has an extreme ray, and every extreme ray of a pointed
    cone in R^3 is the (1-dimensional) intersection of the kernels of two
    linearly independent rows.  All 2-subsets are tested exactly.
    """
    key = tuple(tuple(r) for r in A)
    got = _BOUNDED_CACHE.get(key)
    if got is not None:
        return got
    res = _is_bounded_uncached(A)
    _BOUNDED_CACHE[key] = res
    return res


_BOUNDED_CACHE = {}


def _is_bounded_uncached(A):
    if _rank(A) < 3:
        return False
    m = len(A)
    for i, j in itertools.combinations(range(m), 2):
        d = _cross(A[i], A[j])  # integer cross product
        if all(x == 0 for x in d):
            continue  # rows parallel: kernel intersection is 2-dimensional,
            # but then a third row is needed; covered by other pairs since
            # rank(A) = 3 forces some independent pair through any candidate ray
        for s in (1, -1):
            ray = [s * x for x in d]
            if all(_dot(row, ray) <= 0 for row in A):
                return False
    return True


def lattice_count(A, b, n, box):
    """
    #( n*Q cap Z^3 ) by exact enumeration.  n*Q = {x : A x <= n*b}.
    Coordinates 0 and 1 are looped over exact integer intervals derived from
    the rows that do not involve the later coordinates; coordinate 2 is counted
    in closed form.  Pure integer arithmetic (A, b integral; box exact).
    """
    if n == 0:
        return 1
    bb = [x * n for x in b]

    # rows grouped by highest coordinate actually used
    R0 = [(a, r) for a, r in zip(A, bb) if a[1] == 0 and a[2] == 0]
    R1 = [(a, r) for a, r in zip(A, bb) if a[1] != 0 and a[2] == 0]
    R2 = [(a, r) for a, r in zip(A, bb) if a[2] != 0]

    # integer floor / ceil: for integers p and q > 0, floor = p//q,
    # ceil(p/q) = -((-p)//q); for q < 0, p/q = (-p)/(-q).
    lo0 = math.ceil(box[0][0] * n)
    hi0 = math.floor(box[0][1] * n)
    for a, r in R0:
        if a[0] > 0:
            v = r // a[0]
            if v < hi0:
                hi0 = v
        else:
            v = -(r // (-a[0]))
            if v > lo0:
                lo0 = v
    total = 0
    b1lo0, b1hi0 = math.ceil(box[1][0] * n), math.floor(box[1][1] * n)
    b2lo0, b2hi0 = math.ceil(box[2][0] * n), math.floor(box[2][1] * n)
    for h0 in range(lo0, hi0 + 1):
        lo1, hi1 = b1lo0, b1hi0
        for a, r in R1:
            rem = r - a[0] * h0
            if a[1] > 0:
                v = rem // a[1]
                if v < hi1:
                    hi1 = v
            else:
                v = -(rem // (-a[1]))
                if v > lo1:
                    lo1 = v
            if lo1 > hi1:
                break
        if lo1 > hi1:
            continue
        for h1 in range(lo1, hi1 + 1):
            lo2, hi2 = b2lo0, b2hi0
            for a, r in R2:
                rem = r - a[0] * h0 - a[1] * h1
                if a[2] > 0:
                    v = rem // a[2]
                    if v < hi2:
                        hi2 = v
                else:
                    v = -(rem // (-a[2]))
                    if v > lo2:
                        lo2 = v
                if lo2 > hi2:
                    break
            if hi2 >= lo2:
                total += hi2 - lo2 + 1
    return total


def bounding_box(verts):
    return [
        (min(v[k] for v in verts), max(v[k] for v in verts)) for k in range(3)
    ]


def interpolate(vals):
    """
    Exact Lagrange interpolation through (i, vals[i]) for i = 0..len(vals)-1.
    Returns coefficient list [a_0, a_1, ...] (ascending), Fractions.
    """
    k = len(vals)
    coeffs = [Fraction(0)] * k
    for i in range(k):
        # basis polynomial prod_{j != i} (t - j) / (i - j)
        num = [Fraction(1)]
        den = Fraction(1)
        for j in range(k):
            if j == i:
                continue
            num = _polymul(num, [Fraction(-j), Fraction(1)])
            den *= Fraction(i - j)
        f = Fraction(vals[i]) / den
        for t, cc in enumerate(num):
            coeffs[t] += f * cc
    return coeffs


def _polymul(p, q):
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, c in enumerate(q):
            out[i + j] += a * c
    return out


def polyval(coeffs, t):
    s = Fraction(0)
    for c in reversed(coeffs):
        s = s * t + c
    return s


def hstar_from_L(L, d):
    """
    h*-vector of a d-dimensional polytope from its Ehrhart values L(0..d):
      h*_j = sum_{i=0}^{j} (-1)^i C(d+1, i) L(j-i),  j = 0..d.
    """
    return [
        sum((-1) ** i * math.comb(d + 1, i) * L[j - i] for i in range(j + 1))
        for j in range(d + 1)
    ]


def trim(coeffs):
    c = list(coeffs)
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c


def analyze_polytope(A, b, label=""):
    """
    Full exact Ehrhart analysis of Q = {A x <= b} in R^3.
    Returns a dict; see module docstring items (a)-(g).
    """
    out = {"label": label}
    if not is_bounded(A):
        raise ValueError("constraint matrix does not certify boundedness")
    V = vertices(A, b)
    out["n_vertices"] = len(V)
    if not V:
        # Q = {} ==> nQ = {} for every n >= 1, so the Ehrhart function, and
        # hence the stretched LR polynomial, is identically zero.
        out["empty"] = True
        out["dim"] = -1
        out["L"] = [0] * 6
        out["c"] = 0
        out["poly"] = [Fraction(0)]
        out["min_coeff"] = Fraction(0)
        out["neg"] = False
        out["hstar"] = [0]
        out["volume_normalized"] = Fraction(0)
        out["verified"] = True
        return out
    out["empty"] = False
    out["vertices"] = [[str(c) for c in v] for v in V]
    out["denominators"] = denominators(V)
    out["max_denominator"] = max(out["denominators"])
    d = _affine_rank(V)
    out["dim"] = d
    Vol = normalized_volume(A, b, V)
    out["volume_normalized"] = Vol

    box = bounding_box(V)
    out["box"] = [[str(lo), str(hi)] for lo, hi in box]
    L = [lattice_count(A, b, n, box) if n > 0 else 1 for n in range(6)]
    out["L"] = L
    out["c"] = L[1]

    P = interpolate(L[:4])  # degree <= 3 through L(0..3)
    ok4 = polyval(P, 4) == L[4]
    ok5 = polyval(P, 5) == L[5]
    out["verified"] = bool(ok4 and ok5)
    out["verify_detail"] = {"P(4)": str(polyval(P, 4)), "L(4)": L[4],
                            "P(5)": str(polyval(P, 5)), "L(5)": L[5]}
    Pt = trim(P)
    out["poly"] = Pt
    out["deg_P"] = len(Pt) - 1
    out["min_coeff"] = min(Pt)
    out["neg"] = bool(min(Pt) < 0)
    out["neg_indices"] = [i for i, c in enumerate(Pt) if c < 0]

    dh = max(d, 0)
    out["hstar"] = hstar_from_L(L, dh)
    out["hstar_neg"] = bool(any(x < 0 for x in out["hstar"]))

    # cross-check: leading coefficient of P must be vol = V/3!  when dim = 3
    if d == 3:
        lead = P[3]
        out["vol_crosscheck"] = bool(lead * 6 == Vol)
    else:
        out["vol_crosscheck"] = bool(Vol == 0)
    out["deg_eq_dim"] = bool(out["deg_P"] == d or (d <= 0 and out["deg_P"] == 0))
    return out


def analyze(lam, mu, nu):
    """Full exact analysis of the r=4 hive polytope Q(lam,mu,nu)."""
    H = build_hive4(lam, mu, nu)
    if not H["ok"]:
        return {
            "lam": list(lam), "mu": list(mu), "nu": list(nu),
            "empty": True, "dim": -1, "c": 0, "L": [0] * 6,
            "poly": [Fraction(0)], "min_coeff": Fraction(0), "neg": False,
            "hstar": [0], "volume_normalized": Fraction(0), "verified": True,
            "reason": H.get("reason"), "n_vertices": 0,
        }
    res = analyze_polytope(H["A"], H["b"], label="hive4")
    res["lam"], res["mu"], res["nu"] = H["lam"], H["mu"], H["nu"]
    return res


# --------------------------------------------------------------------------
#  Reeve tetrahedron  T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)}
# --------------------------------------------------------------------------


def reeve_hrep(q):
    """
    Exact H-representation of T_q:
        -z          <= 0
        -q*y +   z  <= 0
        -q*x +   z  <= 0
       q*x + q*y - z <= q
    (verified in reeve_test by re-deriving the vertex set).
    """
    A = [[0, 0, -1], [0, -q, 1], [-q, 0, 1], [q, q, -1]]
    b = [0, 0, 0, q]
    return A, b


def reeve_test(qmax=20, verbose=True):
    """
    Unit-test the Ehrhart machinery on T_q, q = 1..qmax, BYPASSING hives.
    Requires, exactly:
      * 4 vertices, the expected ones
      * L(1) = 4 lattice points
      * normalized volume = q  (both by triangulation and 6*leading coeff)
      * h* = (1, 0, q-1, 0)
      * P = q/6 t^3 + t^2 + (2 - q/6) t + 1
      * a_1 < 0  iff  q >= 13
    Returns (all_ok, rows).
    """
    rows = []
    all_ok = True
    for q in range(1, qmax + 1):
        A, b = reeve_hrep(q)
        r = analyze_polytope(A, b, label="reeve_T_%d" % q)
        expect_v = sorted(
            [tuple(Fraction(x) for x in v) for v in
             [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, q)]]
        )
        got_v = sorted(tuple(Fraction(s) for s in v) for v in r["vertices"])
        P = r["poly"]
        expP = [Fraction(1), Fraction(2) - Fraction(q, 6), Fraction(1), Fraction(q, 6)]
        expP = trim(expP)
        checks = {
            "vertices": got_v == expect_v,
            "dim3": r["dim"] == 3,
            "L1_is_4": r["c"] == 4,
            "vol": r["volume_normalized"] == q,
            "vol_crosscheck": r["vol_crosscheck"],
            "hstar": r["hstar"] == [1, 0, q - 1, 0],
            "poly": P == expP,
            "verified_at_4_5": r["verified"],
            "a1_sign": (P[1] < 0) == (q >= 13),
        }
        ok = all(checks.values())
        all_ok &= ok
        rows.append({
            "q": q, "ok": ok, "hstar": r["hstar"],
            "a1": str(P[1] if len(P) > 1 else Fraction(0)),
            "neg": r["neg"], "V": str(r["volume_normalized"]),
            "L": r["L"], "failed": [k for k, v in checks.items() if not v],
        })
        if verbose:
            print("q=%-3d ok=%-5s h*=%-14s a1=%-10s NEG=%-5s V=%-4s L(1..3)=%s%s"
                  % (q, ok, r["hstar"], rows[-1]["a1"], r["neg"],
                     rows[-1]["V"], r["L"][1:4],
                     "" if ok else "  FAILED:" + ",".join(rows[-1]["failed"])))
    return all_ok, rows


# --------------------------------------------------------------------------
#  formatting / CLI
# --------------------------------------------------------------------------


def _fmt_frac(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def _pstr(p):
    return ",".join(_fmt_frac(c) for c in p)


def json_line(res):
    d = dict(res)
    for k in ("poly", "min_coeff", "volume_normalized"):
        if k in d:
            if isinstance(d[k], list):
                d[k] = [_fmt_frac(x) for x in d[k]]
            else:
                d[k] = _fmt_frac(d[k])
    return json.dumps(d, sort_keys=True, default=str)


def batch_line(lam, mu, nu, res):
    return "%s;%s;%s | dim=%d c=%s V=%s hstar=[%s] minc=%s %s%s" % (
        ",".join(map(str, lam)), ",".join(map(str, mu)), ",".join(map(str, nu)),
        res["dim"], res["c"], _fmt_frac(res["volume_normalized"]),
        ",".join(map(str, res["hstar"])), _fmt_frac(res["min_coeff"]),
        "NEG" if res["neg"] else "pos",
        "" if res.get("verified", True) else " !!INTERP_FAIL",
    )


def parse_partition(s):
    s = s.strip()
    if s in ("", "0", "-"):
        return []
    return [int(t) for t in s.replace(" ", ",").split(",") if t != ""]


def main(argv):
    ap = argparse.ArgumentParser(description="direct r=4 hive-polytope Ehrhart engine")
    ap.add_argument("parts", nargs="*", help='"lam" "mu" "nu"')
    ap.add_argument("--batch", help='file of "lam;mu;nu" lines')
    ap.add_argument("--reeve", nargs="?", const=20, type=int, help="Reeve unit test up to q")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.reeve is not None:
        ok, _ = reeve_test(args.reeve)
        print("REEVE UNIT TEST:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    if args.selftest:
        ok, _ = reeve_test(20, verbose=False)
        print("reeve q=1..20:", "PASS" if ok else "FAIL")
        # hive sanity: a c=1 triple must give P == 1
        r = analyze([1], [1], [1, 1])
        ok2 = r["c"] == 1 and trim(r["poly"]) == [Fraction(1)]
        print("hive c=1 (1;1;11) P==1:", "PASS" if ok2 else "FAIL", r["poly"])
        # a c=2 triple: P = n+1
        r2 = analyze([2, 1], [2, 1], [3, 2, 1])
        ok3 = r2["c"] == 2 and trim(r2["poly"]) == [Fraction(1), Fraction(1)]
        print("hive c=2 (21;21;321) P==n+1:", "PASS" if ok3 else "FAIL", r2["poly"])
        allok = ok and ok2 and ok3
        print("SELFTEST:", "PASS" if allok else "FAIL")
        return 0 if allok else 1

    if args.batch:
        with open(args.batch) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                a, bb, cc = line.split(";")[:3]
                lam, mu, nu = parse_partition(a), parse_partition(bb), parse_partition(cc)
                res = analyze(lam, mu, nu)
                print(batch_line(lam, mu, nu, res))
        return 0

    if len(args.parts) != 3:
        ap.print_help()
        return 2
    lam, mu, nu = (parse_partition(s) for s in args.parts)
    print(json_line(analyze(lam, mu, nu)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
