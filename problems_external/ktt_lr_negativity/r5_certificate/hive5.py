#!/usr/bin/env python3
"""The FIXED size-5 hive constraint matrix A_5, its primitive normals, and an
exact lattice-point counter.

Boundary convention identical to the validated engines (engine/BUILD_A.md and
r4_reeve/hive4.py):

    left edge   B[(0,y)]     = lam_1 + ... + lam_y
    hypotenuse  B[(x,r-x)]   = |lam| + mu_1 + ... + mu_x
    bottom edge B[(x,0)]     = nu_1 + ... + nu_x

Interior slots for r = 5 (D = (r-1)(r-2)/2 = 6):

    (1,1) (1,2) (1,3) (2,1) (2,2) (3,1)

Every rhombus inequality becomes  row . h <= rhs  with row in {0,+1,-1}^6.
A_5 has 30 rows with a nonzero interior part; they realise 27 distinct
primitive outward normals.
"""
import itertools
from math import gcd

R = 5
INTERIOR5 = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1)]
D = 6


def interior_slots(r):
    return [(x, y) for x in range(1, r) for y in range(1, r) if x + y <= r - 1]


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


def rhombus_specs(r):
    """(plus_vertices, minus_vertices, family, position) for every rhombus."""
    out = []
    for x in range(r + 1):
        for y in range(r + 1):
            if x + y <= r - 2:
                out.append((((x + 1, y), (x, y + 1)), ((x, y), (x + 1, y + 1)),
                            'A', (x, y)))
            if y >= 1 and x + y <= r - 1:
                out.append((((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y - 1)),
                            'B', (x, y)))
            if x >= 1 and x + y <= r - 1:
                out.append((((x, y), (x, y + 1)), ((x + 1, y), (x - 1, y + 1)),
                            'C', (x, y)))
    return out


def hive_rows(r):
    """FIXED coefficient rows in interior coordinates + rhs bookkeeping."""
    slots = interior_slots(r)
    idx = {v: i for i, v in enumerate(slots)}
    dd = len(slots)
    rows, bcoef, tags, boundary_only = [], [], [], []
    for plus, minus, fam, pos in rhombus_specs(r):
        co = [0] * dd
        bnd = {}
        for v in plus:
            if v in idx:
                co[idx[v]] -= 1
            else:
                bnd[v] = bnd.get(v, 0) + 1
        for v in minus:
            if v in idx:
                co[idx[v]] += 1
            else:
                bnd[v] = bnd.get(v, 0) - 1
        if all(c == 0 for c in co):
            boundary_only.append((fam, pos, bnd))
            continue
        rows.append(tuple(co))
        bcoef.append(bnd)
        tags.append((fam, pos))
    return rows, {'slots': slots, 'D': dd, 'bcoef': bcoef, 'tags': tags,
                  'boundary_only': boundary_only,
                  'n_rhombus_total': len(rhombus_specs(r))}


def primitive(v):
    g = 0
    for x in v:
        g = gcd(g, abs(int(x)))
    if g == 0:
        return tuple(0 for _ in v)
    return tuple(int(x) // g for x in v)


# ------------------------------------------------------------- fixed r=5 data
A5, META5 = hive_rows(5)
NORMALS5 = sorted(set(primitive(row) for row in A5))
NORMAL_INDEX5 = {n: i for i, n in enumerate(NORMALS5)}


def build_hive5(lam, mu, nu):
    """Q(lam,mu,nu) = {h in R^6 : A5 h <= b}.  Integer b."""
    r = 5
    lam = _norm_parts(lam, r)
    mu = _norm_parts(mu, r)
    nu = _norm_parts(nu, r)
    if lam is None or mu is None or nu is None:
        return {'ok': False, 'reason': 'bad_partition'}
    if sum(lam) + sum(mu) != sum(nu):
        return {'ok': False, 'reason': 'weight_mismatch'}
    ps = lambda p, k: sum(p[:k])
    B = {}
    for y in range(r + 1):
        B[(0, y)] = ps(lam, y)
    for x in range(r + 1):
        B[(x, r - x)] = sum(lam) + ps(mu, x)
    for x in range(r + 1):
        B[(x, 0)] = ps(nu, x)
    B[(0, 0)] = 0
    b = [sum(c * B[v] for v, c in bnd.items()) for bnd in META5['bcoef']]
    ok = True
    for fam, pos, bnd in META5['boundary_only']:
        if sum(c * B[v] for v, c in bnd.items()) < 0:
            ok = False
    return {'ok': ok, 'A': list(A5), 'b': b, 'slots': META5['slots'],
            'lam': lam, 'mu': mu, 'nu': nu}


BIG = 1 << 40


def lattice_count(A, b, d=D, order=None):
    """#{h in Z^d : A h <= b}, exact integer interval propagation."""
    if order is None:
        order = list(range(d))
    pos = {c: i for i, c in enumerate(order)}
    byhigh = [[] for _ in range(d)]
    for a, r0 in zip(A, b):
        nz = [j for j in range(d) if a[j] != 0]
        if not nz:
            if r0 < 0:
                return 0
            continue
        byhigh[max(pos[j] for j in nz)].append((a, r0))
    h = [0] * d
    total = 0

    def rec(k):
        nonlocal total
        ck = order[k]
        lo, hi = -BIG, BIG
        for a, r0 in byhigh[k]:
            rem = r0 - sum(a[order[j]] * h[order[j]] for j in range(k))
            c = a[ck]
            if c > 0:
                v = rem // c
                if v < hi:
                    hi = v
            else:
                v = -(rem // (-c))
                if v > lo:
                    lo = v
            if lo > hi:
                return
        if lo <= -BIG or hi >= BIG:
            raise RuntimeError('unbounded at level %d (coord %d)' % (k, ck))
        if k == d - 1:
            total += hi - lo + 1
            return
        for val in range(lo, hi + 1):
            h[ck] = val
            rec(k + 1)
        h[ck] = 0

    rec(0)
    return total


def emit_atlas():
    import hashlib
    import json
    txt = json.dumps({'rows': [list(x) for x in A5],
                      'normals': [list(x) for x in NORMALS5],
                      'slots': [list(s) for s in META5['slots']],
                      'tags': [[t[0], list(t[1])] for t in META5['tags']]},
                     sort_keys=True)
    return txt, hashlib.sha256(txt.encode()).hexdigest()


if __name__ == '__main__':
    import json
    import os
    txt, sha = emit_atlas()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'A5_atlas.json'), 'w') as f:
        f.write(txt)
    print('r=5  D=%d  interior slots=%s' % (D, META5['slots']))
    print('rhombus inequalities total     = %d' % META5['n_rhombus_total'])
    print('rows with nonzero interior part= %d' % len(A5))
    print('pure-boundary rows             = %d' % len(META5['boundary_only']))
    print('distinct primitive normals     = %d' % len(NORMALS5))
    ent = set()
    for row in A5:
        ent |= set(row)
    print('entry set                      = %s' % sorted(ent))
    opp = sum(1 for i in range(len(NORMALS5)) for j in range(i + 1, len(NORMALS5))
              if all(NORMALS5[i][t] == -NORMALS5[j][t] for t in range(D)))
    print('antiparallel normal pairs      = %d' % opp)
    print('nonparallel unordered pairs    = %d'
          % (len(NORMALS5) * (len(NORMALS5) - 1) // 2 - opp))
    print('atlas_sha256                   = %s' % sha)
    for n in NORMALS5:
        print('   ', n)
