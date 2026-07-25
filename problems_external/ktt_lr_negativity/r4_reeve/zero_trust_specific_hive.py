#!/usr/bin/env python3
"""Standalone reconstruction of one size-four Knutson-Tao hive.

This audit intentionally imports no project hive/polytope/q2 code.  It builds
the triangular hive from the textbook three rhombus families, enumerates all
vertices and lattice points exactly, and computes the tangent cone at the
specified point.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd


R = 4
LAM = (12, 8, 4, 0)
MU = (12, 8, 4, 0)
NU = (18, 14, 10, 6)
INTERIOR = ((1, 1), (1, 2), (2, 1))
POINT = (26, 32, 38)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det3(m):
    a, b, c = m
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def solve3(rows, rhs):
    d = det3(rows)
    if d == 0:
        return None
    out = []
    for j in range(3):
        m = [list(r) for r in rows]
        for i in range(3):
            m[i][j] = rhs[i]
        out.append(Fraction(det3(m), d))
    return tuple(out)


def rank(rows):
    if not rows:
        return 0
    m = [[Fraction(x) for x in row] for row in rows]
    rr = 0
    for c in range(len(m[0])):
        p = next((i for i in range(rr, len(m)) if m[i][c]), None)
        if p is None:
            continue
        m[rr], m[p] = m[p], m[rr]
        q = m[rr][c]
        m[rr] = [x / q for x in m[rr]]
        for i in range(rr + 1, len(m)):
            if m[i][c]:
                q = m[i][c]
                m[i] = [x - q * y for x, y in zip(m[i], m[rr])]
        rr += 1
    return rr


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def primitive(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    return None if g == 0 else tuple(x // g for x in v)


def boundary():
    b = {}
    acc = 0
    for y in range(R + 1):
        b[(0, y)] = acc
        if y < R:
            acc += LAM[y]
    acc = sum(LAM)
    for x in range(R + 1):
        b[(x, R - x)] = acc
        if x < R:
            acc += MU[x]
    acc = 0
    for x in range(R + 1):
        b[(x, 0)] = acc
        if x < R:
            acc += NU[x]
    b[(0, 0)] = 0
    return b


def build_rows():
    bd = boundary()
    index = {p: i for i, p in enumerate(INTERIOR)}
    rows = []

    def add(name, plus, minus):
        n = [0, 0, 0]
        const = 0
        # plus >= minus, converted to n.h <= rhs
        for p in plus:
            if p in index:
                n[index[p]] -= 1
            else:
                const -= bd[p]
        for p in minus:
            if p in index:
                n[index[p]] += 1
            else:
                const += bd[p]
        rows.append({"name": name, "normal": tuple(n), "rhs": -const,
                     "plus": plus, "minus": minus})

    for x, y in product(range(R + 1), repeat=2):
        if x + y <= R - 2:
            add(f"A({x},{y})", ((x + 1, y), (x, y + 1)),
                ((x, y), (x + 1, y + 1)))
        if y >= 1 and x + y <= R - 1:
            add(f"B({x},{y})", ((x, y), (x + 1, y)),
                ((x, y + 1), (x + 1, y - 1)))
        if x >= 1 and x + y <= R - 1:
            add(f"C({x},{y})", ((x, y), (x, y + 1)),
                ((x + 1, y), (x - 1, y + 1)))
    assert len(rows) == 18
    return bd, rows


def vertices(rows):
    out = set()
    for I in combinations(range(len(rows)), 3):
        m = [rows[i]["normal"] for i in I]
        v = solve3(m, [rows[i]["rhs"] for i in I])
        if v is not None and all(dot(r["normal"], v) <= r["rhs"] for r in rows):
            out.add(v)
    return sorted(out)


def tangent_rays(active_normals):
    rays = set()
    for a, b in combinations(active_normals, 2):
        v = primitive(cross(a, b))
        if v is None:
            continue
        for s in (1, -1):
            w = tuple(s * x for x in v)
            if all(dot(n, w) <= 0 for n in active_normals):
                rays.add(w)
    return sorted(rays)


def main():
    bd, rows = build_rows()
    print("boundary")
    for y in range(R, -1, -1):
        print(" ", [(x, y, bd.get((x, y), "*")) for x in range(R - y + 1)])

    feasible = all(dot(r["normal"], POINT) <= r["rhs"] for r in rows)
    active = [r for r in rows if dot(r["normal"], POINT) == r["rhs"]]
    print(f"point={POINT} feasible={feasible}")
    print(f"active_inequalities={len(active)}")
    for r in active:
        print(f"  {r['name']}: {r['normal']} . h <= {r['rhs']}")

    vs = vertices(rows)
    print(f"vertices={len(vs)} point_is_vertex={tuple(map(Fraction, POINT)) in vs}")
    print("vertex_list=", [tuple(str(x) for x in v) for v in vs])
    lo = [int(min(v[k] for v in vs)) for k in range(3)]
    hi = [int(max(v[k] for v in vs)) for k in range(3)]
    lattice = [p for p in product(*(range(lo[k], hi[k] + 1) for k in range(3)))
               if all(dot(r["normal"], p) <= r["rhs"] for r in rows)]
    print(f"lattice_points={len(lattice)} bounds={list(zip(lo, hi))}")

    distinct = sorted({r["normal"] for r in active})
    rays = tangent_rays(distinct)
    facets = [n for n in distinct if rank([r for r in rays if dot(n, r) == 0]) == 2]
    print(f"active_distinct_normals={len(distinct)} {distinct}")
    print(f"tangent_facet_normals={facets}")
    print(f"primitive_tangent_rays={rays}")
    print(f"abs_det_facet_normals={abs(det3(facets))}")
    print(f"abs_det_primitive_rays={abs(det3(rays))}")
    assert feasible and tuple(map(Fraction, POINT)) in vs
    assert len(lattice) == 50
    assert len(active) == 9 and len(distinct) == 6
    assert facets == [(-1, -1, 1), (-1, 1, -1), (1, -1, -1)]
    assert rays == [(0, 1, 1), (1, 0, 1), (1, 1, 0)]
    assert abs(det3(facets)) == 4 and abs(det3(rays)) == 2
    print("AUDIT=PASS")


if __name__ == "__main__":
    main()
