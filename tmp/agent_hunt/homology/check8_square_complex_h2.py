#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 8: second homology of the swap-square complex.

Every rotor transition changes the selected multiplicity vector m by the
boundary of ONE oriented swap square (x, m_old, y, m_new):
    delta m = [x m_new] + [m_new y] - [x m_old] - [m_old y]
            = d2( square ),
so around any rotor  sum_i d2(sq_i, eps_i) = 0, i.e. the signed square usage
sigma is in ker d2 of the 2-complex  X = F* + (swap squares as 2-cells).
If ker d2 = 0 over Z (boundaries independent), every rotor has sigma = 0:
each square is used net-zero (equally often in both orientations) -- the
"interleaved inverse pair" / commutator type, like the 8-vtx toy rotor.

This computes rank over Q (fractions, exact) and over GF(2) of the boundary
matrix for (a) ALL squares of F*, (b) only DB-realizable swap squares (the
2-cells a rotor can actually use: transposed middles inside one atom's row
family), for both fixtures.  ker dimension = #squares - rank.
"""
import sys
from fractions import Fraction
from itertools import combinations
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_atoms_v3 import find_circuits_v3
from fixture_264_variants import find as find_variant

def all_squares(fx):
    adj = fx['adj']
    out = []
    for u, w in combinations(range(fx['n']), 2):
        if fx['color'].get(u) != fx['color'].get(w) or w in adj[u]:
            continue
        cn = sorted(adj[u] & adj[w])
        for c1, c2 in combinations(cn, 2):
            out.append((c1, u, c2, w))   # 4-cycle c1-u-c2-w
    return out

def swap_squares(fx, circ):
    """squares realizable as a one-middle detour within one chosen atom's family"""
    chosen = set(map(tuple, circ))
    sqs = set()
    for a in chosen:
        fam = fx['rows'][a]
        for r1 in fam:
            for r2 in fam:
                if r1 == r2:
                    continue
                diff = [p for p in range(5) if r1[p] != r2[p]]
                if len(diff) == 1 and diff[0] in (1, 2, 3):
                    p = diff[0]
                    x, y = r1[p-1], r1[p+1]
                    u, w = sorted((r1[p], r2[p]))
                    c1, c2 = sorted((x, y))
                    sqs.add((c1, u, c2, w))
    return sorted(sqs)

def boundary_matrix(fx, squares):
    edges = sorted(tuple(sorted(e)) for e in fx['edges'])
    eidx = {e: i for i, e in enumerate(edges)}
    rows = []
    for (c1, u, c2, w) in squares:
        vec = [0] * len(edges)
        # oriented boundary: +c1u +uc2 -c2w -wc1  (a 4-cycle as 1-chain with signs
        # chosen so it equals (new pair) - (old pair) for the swap u->w)
        vec[eidx[tuple(sorted((c1, u)))]] += 1
        vec[eidx[tuple(sorted((u, c2)))]] += 1
        vec[eidx[tuple(sorted((c2, w)))]] -= 1
        vec[eidx[tuple(sorted((w, c1)))]] -= 1
        rows.append(vec)
    return rows

def rank_Q(mat):
    m = [[Fraction(x) for x in row] for row in mat]
    R = len(m)
    if R == 0:
        return 0
    C = len(m[0])
    r = 0
    for c in range(C):
        piv = None
        for i in range(r, R):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = 1 / m[r][c]
        m[r] = [x * inv for x in m[r]]
        for i in range(R):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
        if r == R:
            break
    return r

def rank_F2(mat):
    rows = []
    for row in mat:
        v = 0
        for i, x in enumerate(row):
            if x % 2:
                v |= 1 << i
        rows.append(v)
    r = 0
    for c in range(max(len(row) for row in mat) if mat else 0):
        piv = None
        for i in range(r, len(rows)):
            if (rows[i] >> c) & 1:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        r += 1
    return r

if __name__ == '__main__':
    for tag in ('298', '264'):
        fx = build(tag)
        if tag == '298':
            subs = find_circuits_v3(fx, cap=1)
        else:
            subs, _ = find_variant(fx, (0,), cap=1)
        circ = sorted(map(tuple, subs[0]))
        sq_all = all_squares(fx)
        sq_swap = swap_squares(fx, circ)
        for label, sqs in (("ALL F* squares", sq_all), ("DB swap squares", sq_swap)):
            mat = boundary_matrix(fx, sqs)
            rq = rank_Q(mat)
            r2 = rank_F2(mat)
            print(f"[{tag}] {label}: n={len(sqs)} rankQ={rq} kerQ={len(sqs)-rq} "
                  f"rankF2={r2} kerF2={len(sqs)-r2}")
        # cycle rank of F* for context
        n = fx['n']; e = len(fx['edges'])
        print(f"[{tag}] F*: n={n} e={e} cycle rank={e - n + 1} (connected)")
