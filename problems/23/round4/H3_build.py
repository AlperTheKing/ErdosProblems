"""H3: Vega graphs (Brandt-Thomasse, "Dense triangle-free graphs are four-colorable").

Definition extracted verbatim from the paper (page 4):

  "For some integer i >= 2, start with a graph Gamma_i on vertex set {1,...,3i-1} and add an
   edge xy and an induced 6-cycle (a,v,c,u,b,w) such that x is joined to a,b,c and y is joined
   to u,v,w.  The set of neighbors of a,u on the Gamma_i graph is {1,...,i}.  The set of
   neighbors of b,v on the Gamma_i graph is {i+1,...,2i}.  The set of neighbors of c,w on the
   Gamma_i graph is {2i+1,...,3i-1}.  This is the sole Vega graph on 3i+7 vertices.  We denote
   it by Upsilon_i.
   There are two Vega graphs on 3i+6 vertices, obtained from Upsilon_i by a simple vertex
   deletion.  The first one is Upsilon_i - {y}, the second Upsilon_i - {2i} ... Finally, the
   last Vega graph, on 3i+5 vertices, is Upsilon_i - {y,2i}."

  Gamma_i (page 3): "the graph on vertex set {1,2,...,3i-1} where the vertex j has neighbors
   j+i, ..., j+2i-1, these values taken modulo 3i-1."   (= Andrasfai graph And(i))

This module builds them, verifies every claimed property, and emits graph6.
"""
import sys, itertools
from fractions import Fraction

# ---------------------------------------------------------------- Gamma_i / Vega


def gamma(i):
    """Gamma_i = And(i): circulant on Z_{3i-1}, vertex j ~ j+i,...,j+2i-1.
    Returns (n, set of frozenset edges) with vertices labelled 1..3i-1."""
    m = 3 * i - 1
    lab = lambda r: (r - 1) % m + 1          # representative in {1..m}
    E = set()
    for j in range(1, m + 1):
        for s in range(i, 2 * i):
            E.add(frozenset((j, lab(j + s))))
    return m, E


def upsilon(i):
    """Upsilon_i on 3i+7 vertices.  Returns (verts, edges) with string labels."""
    m = 3 * i - 1
    V = [str(j) for j in range(1, m + 1)] + ['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w']
    _, EG = gamma(i)
    E = set(frozenset(str(t) for t in e) for e in EG)
    E.add(frozenset(('x', 'y')))
    # induced 6-cycle (a,v,c,u,b,w)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']
    for k in range(6):
        E.add(frozenset((cyc[k], cyc[(k + 1) % 6])))
    for t in ('a', 'b', 'c'):
        E.add(frozenset(('x', t)))
    for t in ('u', 'v', 'w'):
        E.add(frozenset(('y', t)))
    A = [str(j) for j in range(1, i + 1)]
    B = [str(j) for j in range(i + 1, 2 * i + 1)]
    C = [str(j) for j in range(2 * i + 1, m + 1)]
    for blk, pair in ((A, ('a', 'u')), (B, ('b', 'v')), (C, ('c', 'w'))):
        for j in blk:
            for t in pair:
                E.add(frozenset((j, t)))
    return V, E


def delete(V, E, S):
    V2 = [v for v in V if v not in S]
    E2 = set(e for e in E if not (e & set(S)))
    return V2, E2


def vega_family(i):
    """The four Vega graphs of parameter i, as (name, verts, edges)."""
    V, E = upsilon(i)
    out = [('Ups%d' % i, V, E)]
    out.append(('Ups%d-y' % i, *delete(V, E, {'y'})))
    out.append(('Ups%d-2i' % i, *delete(V, E, {str(2 * i)})))
    out.append(('Ups%d-y-2i' % i, *delete(V, E, {'y', str(2 * i)})))
    return out


# ---------------------------------------------------------------- graph tools

def adjmat(V, E):
    idx = {v: k for k, v in enumerate(V)}
    n = len(V)
    A = [[0] * n for _ in range(n)]
    for e in E:
        p, q = tuple(e)
        A[idx[p]][idx[q]] = A[idx[q]][idx[p]] = 1
    return A


def is_trianglefree(A):
    n = len(A)
    for p in range(n):
        for q in range(p + 1, n):
            if A[p][q]:
                for r in range(q + 1, n):
                    if A[p][r] and A[q][r]:
                        return False, (p, q, r)
    return True, None


def is_maximal_tf(A):
    """maximal triangle-free  <=>  triangle-free and diameter <= 2."""
    n = len(A)
    for p in range(n):
        for q in range(p + 1, n):
            if not A[p][q]:
                if not any(A[p][r] and A[q][r] for r in range(n)):
                    return False, (p, q)
    return True, None


def is_twinfree(A):
    n = len(A)
    for p in range(n):
        for q in range(p + 1, n):
            if A[p] == A[q]:
                return False, (p, q)
    return True, None


def kcolorable(A, k):
    n = len(A)
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -sum(A[v]))

    def bt(t):
        if t == n:
            return True
        v = order[t]
        used = set(col[u] for u in range(n) if A[v][u] and col[u] >= 0)
        top = min(k, max([col[order[s]] for s in range(t)] + [-1]) + 2)
        for cc in range(top):
            if cc not in used:
                col[v] = cc
                if bt(t + 1):
                    return True
                col[v] = -1
        return False
    return bt(0)


def chrom(A):
    for k in range(1, 8):
        if kcolorable(A, k):
            return k
    return None


def automorphisms(A):
    """Brute-force automorphism group via degree-refined backtracking (n<=25 practical)."""
    n = len(A)
    deg = [sum(r) for r in A]
    # refine by iterated degree signature
    col = deg[:]
    for _ in range(n):
        newc = [(col[v], tuple(sorted(col[u] for u in range(n) if A[v][u]))) for v in range(n)]
        m = {s: k for k, s in enumerate(sorted(set(newc)))}
        nc = [m[s] for s in newc]
        if nc == col:
            break
        col = nc
    perms = []
    p = [-1] * n
    used = [False] * n

    def bt(t):
        if t == n:
            perms.append(p[:])
            return
        for img in range(n):
            if used[img] or col[img] != col[t]:
                continue
            ok = True
            for s in range(t):
                if A[t][s] != A[img][p[s]]:
                    ok = False
                    break
            if ok:
                p[t] = img
                used[img] = True
                bt(t + 1)
                used[img] = False
                p[t] = -1
    bt(0)
    return perms


def graph6(A):
    n = len(A)
    bits = []
    for j in range(n):
        for k in range(j):
            bits.append(A[k][j])
    while len(bits) % 6:
        bits.append(0)
    out = []
    if n <= 62:
        out.append(chr(n + 63))
    else:
        out.append(chr(126))
        out.append(chr((n >> 12 & 63) + 63))
        out.append(chr((n >> 6 & 63) + 63))
        out.append(chr((n & 63) + 63))
    for t in range(0, len(bits), 6):
        val = 0
        for b in bits[t:t + 6]:
            val = val * 2 + b
        out.append(chr(val + 63))
    return ''.join(out)


def canon_key(A):
    """Canonical form by brute force over all permutations restricted by refinement -
    only used for tiny graphs (isomorphism test between the two 3i+6 graphs)."""
    n = len(A)
    best = None
    for p in itertools.permutations(range(n)):
        bits = tuple(A[p[k]][p[j]] for j in range(n) for k in range(j))
        if best is None or bits < best:
            best = bits
    return best


# ---------------------------------------------------------------- BT weight functions

def bt_weights(i, name):
    """Integer weights from Theorem 3 of Brandt-Thomasse.  Returns (dict, claimed_deg,
    claimed_total)."""
    m = 3 * i - 1
    W = {}
    if name == 'Ups%d' % i:
        for j in range(1, m + 1):
            W[str(j)] = 3
        W['1'] = 1; W[str(2 * i)] = 1
        W['x'] = 1; W['y'] = 1
        W['c'] = 3 * i - 3; W['w'] = 3 * i - 3
        for t in ('u', 'v', 'a', 'b'):
            W[t] = 3 * i - 2
        return W, 9 * i - 6, 27 * i - 19
    if name == 'Ups%d-y' % i:
        for j in range(1, m + 1):
            W[str(j)] = 3
        W['1'] = 1; W[str(2 * i)] = 1
        W['x'] = 2
        W['w'] = 3 * i - 4
        for t in ('u', 'v', 'c'):
            W[t] = 3 * i - 3
        for t in ('a', 'b'):
            W[t] = 3 * i - 2
        return W, 9 * i - 7, 27 * i - 22
    if name == 'Ups%d-2i' % i:
        for j in range(1, m + 1):
            W[str(j)] = 3
        W['1'] = 2; W[str(i)] = 2
        W['x'] = 1; W['y'] = 1
        for t in ('b', 'v', 'c', 'w'):
            W[t] = 3 * i - 3
        for t in ('u', 'a'):
            W[t] = 3 * i - 2
        W.pop(str(2 * i))
        return W, 9 * i - 7, 27 * i - 22
    if name == 'Ups%d-y-2i' % i:
        for j in range(1, m + 1):
            W[str(j)] = 3
        W['x'] = 2; W['1'] = 2; W[str(i)] = 2
        for t in ('v', 'w'):
            W[t] = 3 * i - 4
        for t in ('u', 'b', 'c'):
            W[t] = 3 * i - 3
        W['a'] = 3 * i - 2
        W.pop(str(2 * i))
        return W, 9 * i - 8, 27 * i - 25
    raise ValueError(name)


# ---------------------------------------------------------------- main

def report(imax=8):
    lines = []
    g6lines = []
    names = []
    for i in range(2, imax + 1):
        for name, V, E in vega_family(i):
            A = adjmat(V, E)
            n = len(V)
            tf, wit = is_trianglefree(A)
            mtf, wit2 = is_maximal_tf(A)
            twf, wit3 = is_twinfree(A)
            ch = chrom(A)
            W, cdeg, ctot = bt_weights(i, name)
            assert set(W) == set(V), (name, set(W) ^ set(V))
            tot = sum(W.values())
            degs = set()
            for v in V:
                degs.add(sum(W[u] for u in V if A[V.index(v)][V.index(u)]))
            reg = (len(degs) == 1)
            d = degs.pop() if reg else None
            delta = Fraction(min([sum(W[u] for u in V if A[V.index(v)][V.index(u)]) for v in V]), tot)
            lines.append(dict(i=i, name=name, n=n, m=len(E), tf=tf, mtf=mtf, twf=twf, chi=ch,
                              regular=reg, wdeg=d, wtot=tot, claimed_deg=cdeg,
                              claimed_tot=ctot, delta=delta, gt13=(delta > Fraction(1, 3)),
                              minweight=min(W.values())))
            g6lines.append(graph6(A))
            names.append('%s n=%d m=%d chi=%d delta=%s' % (name, n, len(E), ch, delta))
    return lines, g6lines, names


if __name__ == '__main__':
    imax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    lines, g6, names = report(imax)
    hdr = ('%-12s %3s %3s %4s  %-3s %-4s %-4s %-4s %-4s %-6s %-7s %-9s %-6s' %
           ('name', 'i', 'n', 'm', 'tf', 'mtf', 'twf', 'chi', 'reg', 'wdeg', 'wtot', 'delta', '>1/3'))
    print(hdr)
    ok = True
    for L in lines:
        good = (L['tf'] and L['mtf'] and L['twf'] and L['chi'] == 4 and L['regular']
                and L['wdeg'] == L['claimed_deg'] and L['wtot'] == L['claimed_tot']
                and L['gt13'] and L['minweight'] > 0)
        ok &= good
        print('%-12s %3d %3d %4d  %-3s %-4s %-4s %-4d %-4s %-6d %-7d %-9s %-6s %s' %
              (L['name'], L['i'], L['n'], L['m'], L['tf'], L['mtf'], L['twf'], L['chi'],
               L['regular'], L['wdeg'], L['wtot'], L['delta'], L['gt13'],
               '' if good else '  <-- MISMATCH claimed deg %d tot %d' % (L['claimed_deg'], L['claimed_tot'])))
    print('ALL CLAIMS VERIFIED:', ok)
    with open('E:/Projects/ErdosProblems/problems/23/round4/H3_vega.g6', 'w') as f:
        f.write('\n'.join(g6) + '\n')
    with open('E:/Projects/ErdosProblems/problems/23/round4/H3_vega_names.txt', 'w') as f:
        f.write('\n'.join(names) + '\n')
    print('wrote H3_vega.g6 (%d graphs)' % len(g6))
