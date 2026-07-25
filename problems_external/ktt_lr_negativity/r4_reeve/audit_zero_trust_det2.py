#!/usr/bin/env python3
"""Standalone exact audit of the alleged multiplicity-two r=4 hive vertex.

This deliberately imports no project hive/polytope code.  It builds the
size-four triangular hive from the three rhombus families, enumerates vertices
by Cramer's rule, counts lattice points directly, and computes tangent-cone
extreme rays from all tight inequalities.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd


LAM = (12, 8, 4, 0)
MU = (12, 8, 4, 0)
NU = (18, 14, 10, 6)
TARGET = (Fraction(26), Fraction(32), Fraction(38))
INTERIOR = ((1, 1), (1, 2), (2, 1))


def det3(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def rank(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    out = 0
    for col in range(3):
        pivot = next((r for r in range(out, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[out], a[pivot] = a[pivot], a[out]
        p = a[out][col]
        a[out] = [x / p for x in a[out]]
        for r in range(len(a)):
            if r != out and a[r][col]:
                q = a[r][col]
                a[r] = [a[r][j] - q * a[out][j] for j in range(3)]
        out += 1
    return out


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def primitive(v):
    g = 0
    for x in v:
        g = gcd(g, abs(int(x)))
    return tuple(int(x) // g for x in v) if g else None


def dot(a, x):
    return sum(a[i] * x[i] for i in range(3))


def boundary():
    b = {}
    for y in range(5):
        b[(0, y)] = sum(LAM[:y])
    for x in range(5):
        b[(x, 4 - x)] = sum(LAM) + sum(MU[:x])
    for x in range(5):
        b[(x, 0)] = sum(NU[:x])
    return b


def inequalities():
    """Return named inequalities a.x <= rhs from long-diagonal concavity."""
    bd = boundary()
    pos = {p: i for i, p in enumerate(INTERIOR)}
    ans = []

    def add(name, plus, minus):
        # Hive inequality sum(plus) >= sum(minus).
        a = [0, 0, 0]
        constant = 0
        for p in plus:
            if p in pos:
                a[pos[p]] -= 1
            else:
                constant -= bd[p]
        for p in minus:
            if p in pos:
                a[pos[p]] += 1
            else:
                constant += bd[p]
        if a != [0, 0, 0]:
            ans.append((name, tuple(a), -constant))
        elif constant > 0:
            raise AssertionError(f"boundary violates {name}")

    for x in range(5):
        for y in range(5 - x):
            if x + y <= 2:
                add(f"A({x},{y})", ((x + 1, y), (x, y + 1)),
                    ((x, y), (x + 1, y + 1)))
            if y >= 1 and x + y <= 3:
                add(f"B({x},{y})", ((x, y), (x + 1, y)),
                    ((x, y + 1), (x + 1, y - 1)))
            if x >= 1 and x + y <= 3:
                add(f"C({x},{y})", ((x, y), (x, y + 1)),
                    ((x + 1, y), (x - 1, y + 1)))
    return ans


def solve(rows):
    m = [list(r[1]) for r in rows]
    d = det3(m)
    if not d:
        return None
    rhs = [r[2] for r in rows]
    out = []
    for col in range(3):
        n = [[rhs[i] if j == col else m[i][j] for j in range(3)] for i in range(3)]
        out.append(Fraction(det3(n), d))
    return tuple(out)


def vertices(ineq):
    out = set()
    for rows in combinations(ineq, 3):
        x = solve(rows)
        if x is not None and all(dot(a, x) <= rhs for _, a, rhs in ineq):
            out.add(x)
    return sorted(out)


def extreme_rays(tight_normals):
    out = set()
    for a, b in combinations(tight_normals, 2):
        c = cross(a, b)
        if c == (0, 0, 0):
            continue
        for sign in (1, -1):
            ray = primitive(tuple(sign * q for q in c))
            if all(dot(n, ray) <= 0 for n in tight_normals):
                active = [n for n in tight_normals if dot(n, ray) == 0]
                if rank(active) == 2:
                    out.add(ray)
    return sorted(out)


def main():
    ineq = inequalities()
    verts = vertices(ineq)
    assert TARGET in verts
    assert all(dot(a, TARGET) <= rhs for _, a, rhs in ineq)

    tight = [(name, a) for name, a, rhs in ineq if dot(a, TARGET) == rhs]
    distinct = sorted(set(a for _, a in tight))
    rays = extreme_rays(distinct)
    assert rays == [(0, 1, 1), (1, 0, 1), (1, 1, 0)]
    multiplicity = abs(det3(rays))
    assert multiplicity == 2

    lo = [min(int(v[j]) for v in verts) for j in range(3)]
    hi = [max(int(v[j]) for v in verts) for j in range(3)]
    lattice_points = []
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                p = (x, y, z)
                if all(dot(a, p) <= rhs for _, a, rhs in ineq):
                    lattice_points.append(p)
    assert len(lattice_points) == 50

    print(f"inequalities={len(ineq)} vertices={len(verts)} lattice_points={len(lattice_points)}")
    print(f"target={tuple(int(x) for x in TARGET)} feasible_vertex=YES")
    print("tight_rows=" + ",".join(name for name, _ in tight))
    print(f"distinct_tight_normals={len(distinct)} {distinct}")
    print(f"extreme_rays={rays} primitive_ray_det={multiplicity}")
    print("old_vcheck_filter_ntd_eq_3=" + ("PASS" if len(distinct) == 3 else "SKIP"))


if __name__ == "__main__":
    main()
