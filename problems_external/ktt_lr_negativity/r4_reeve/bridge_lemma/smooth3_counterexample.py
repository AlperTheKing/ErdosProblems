#!/usr/bin/env python3
"""Exact test: does unimodularity of every vertex cone force a_1 >= 0 for a
lattice 3-polytope?  Family: Cayley polytope Q_N = conv(P0 x {0}, P1 x {1})
with P0 = [0,N]x[0,1], P1 = [0,1]x[0,N].

H-representation (derived, then verified against the V-representation):
   z >= 0,  z <= 1,  x >= 0,  y >= 0,  x + (N-1) z <= N,  y - (N-1) z <= 1.

Everything is exact (Fraction / integer).  No floating point anywhere.
"""
from fractions import Fraction as F
from itertools import combinations, product


def facets(N):
    # rows (a,b,c,rhs) meaning a*x+b*y+c*z <= rhs
    return [(0, 0, -1, 0),
            (0, 0, 1, 1),
            (-1, 0, 0, 0),
            (0, -1, 0, 0),
            (1, 0, N - 1, N),
            (0, 1, -(N - 1), 1)]


def det3(u, v, w):
    return (u[0] * (v[1] * w[2] - v[2] * w[1])
            - u[1] * (v[0] * w[2] - v[2] * w[0])
            + u[2] * (v[0] * w[1] - v[1] * w[0]))


def solve3(rows):
    """rows: 3 tuples (a,b,c,rhs).  Return exact solution or None."""
    A = [[F(r[0]), F(r[1]), F(r[2])] for r in rows]
    b = [F(r[3]) for r in rows]
    # gaussian elimination
    idx = list(range(3))
    for col in range(3):
        piv = None
        for r in range(col, 3):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        b[col] = b[col] / pv
        for r in range(3):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][k] - f * A[col][k] for k in range(3)]
                b[r] = b[r] - f * b[col]
    return (b[0], b[1], b[2])


def vertices_and_smoothness(N):
    Fs = facets(N)
    verts = {}
    for tri in combinations(range(6), 3):
        rows = [Fs[i] for i in tri]
        if det3(rows[0][:3], rows[1][:3], rows[2][:3]) == 0:
            continue
        p = solve3(rows)
        if p is None:
            continue
        if all(sum(Fs[i][k] * p[k] for k in range(3)) <= Fs[i][3] for i in range(6)):
            verts.setdefault(p, set()).update(tri)
    report = []
    for p, tights in sorted(verts.items()):
        tight = sorted(i for i in range(6)
                       if sum(Fs[i][k] * p[k] for k in range(3)) == Fs[i][3])
        simple = (len(tight) == 3)
        d = None
        if simple:
            d = abs(det3(*[Fs[i][:3] for i in tight]))
        integral = all(x.denominator == 1 for x in p)
        report.append((tuple(int(x) if x.denominator == 1 else x for x in p),
                       tight, simple, d, integral))
    return report


def lattice_count(N, t):
    """|tQ cap Z^3| by direct enumeration, exact integers."""
    tot = 0
    for z in range(0, t + 1):          # 0 <= z <= t
        # x >= 0, x <= N*t - (N-1)*z
        xmax = N * t - (N - 1) * z
        # y >= 0, y <= t + (N-1)*z
        ymax = t + (N - 1) * z
        if xmax < 0 or ymax < 0:
            continue
        tot += (xmax + 1) * (ymax + 1)
    return tot


def interior_count(N, t):
    tot = 0
    for z in range(1, t):
        xmax = N * t - (N - 1) * z
        ymax = t + (N - 1) * z
        # strict inequalities
        cx = max(0, xmax - 1)   # x in 1..xmax-1  -> xmax-1 values
        cy = max(0, ymax - 1)
        tot += cx * cy
    return tot


def interpolate_cubic(vals):
    """vals = [L(0),L(1),L(2),L(3)] -> exact coefficients a0..a3."""
    import itertools
    # solve Vandermonde exactly
    rows = [[F(t) ** k for k in range(4)] + [F(vals[t])] for t in range(4)]
    n = 4
    for col in range(n):
        piv = next(r for r in range(col, n) if rows[r][col] != 0)
        rows[col], rows[piv] = rows[piv], rows[col]
        pv = rows[col][col]
        rows[col] = [x / pv for x in rows[col]]
        for r in range(n):
            if r != col and rows[r][col] != 0:
                f = rows[r][col]
                rows[r] = [rows[r][k] - f * rows[col][k] for k in range(n + 1)]
    return [rows[k][n] for k in range(n)]


def edge_lengths(N):
    """total lattice length of edges, from the V-rep (Cayley structure)."""
    from math import gcd
    P0 = [(0, 0), (N, 0), (N, 1), (0, 1)]
    P1 = [(0, 0), (1, 0), (1, N), (0, N)]
    tot = 0
    for i in range(4):
        a, b = P0[i], P0[(i + 1) % 4]
        tot += gcd(abs(a[0] - b[0]), abs(a[1] - b[1]))
        a, b = P1[i], P1[(i + 1) % 4]
        tot += gcd(abs(a[0] - b[0]), abs(a[1] - b[1]))
    for i in range(4):
        d = (P1[i][0] - P0[i][0], P1[i][1] - P0[i][1], 1)
        tot += gcd(gcd(abs(d[0]), abs(d[1])), 1)
    return tot


print("N  a0 a1 a2 a3  |  6a1   V=6a3   c   i   3(c+i)-V   allvertsSmooth")
for N in range(1, 15):
    rep = vertices_and_smoothness(N)
    ok = all(r[2] and r[3] == 1 and r[4] for r in rep)
    vals = [lattice_count(N, t) for t in range(6)]
    a = interpolate_cubic(vals[:4])
    # confirm the cubic reproduces L(4), L(5)
    def ev(t):
        return sum(a[k] * F(t) ** k for k in range(4))
    assert ev(4) == vals[4] and ev(5) == vals[5], (N, vals)
    assert a[0] == 1
    V = 6 * a[3]
    c = vals[1]
    i = interior_count(N, 1)
    # Ehrhart reciprocity check: L(-1) = (-1)^3 * #interior
    assert ev(-1) == -i, (N, ev(-1), i)
    assert 6 * a[1] == 3 * (c + i) - V, N
    print(f"{N:3d} {a[0]} {str(a[1]):>8} {str(a[2]):>6} {str(a[3]):>7} | "
          f"{str(6*a[1]):>6} {str(V):>6} {c:>5} {i:>5} "
          f"{str(3*(c+i)-V):>7}   {ok}  nverts={len(rep)} sum_edge_len={edge_lengths(N)}")

print()
print("detail for N=10 (smallest counterexample):")
for r in vertices_and_smoothness(10):
    print("   vertex", r[0], "tight facets", r[1], "simple", r[2],
          "|det(normals)|", r[3], "integral", r[4])
