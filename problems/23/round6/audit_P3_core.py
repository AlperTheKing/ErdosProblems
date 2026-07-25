"""audit_P3_core.py -- INDEPENDENT re-implementation for the audit of round6/P3.md.

Nothing is imported from P3_*.py.  Own graph structures (dict of frozensets), own graph6
decoder, own max-cut (full 2^(n-1) enumeration over the support), own weight enumerator,
own arc families.  All arithmetic is exact integer / Fraction.
"""
from fractions import Fraction as F
from itertools import combinations
import sys

SPECIALS = ['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w']


# ---------------------------------------------------------------- construction (from BT text)
def gamma_adj(i):
    """Gamma_i on {1..3i-1}: vertex j has neighbours j+i,...,j+2i-1 (mod 3i-1)."""
    L = 3 * i - 1
    adj = {j: set() for j in range(1, L + 1)}
    for j in range(1, L + 1):
        for d in range(i, 2 * i):
            k = (j - 1 + d) % L + 1
            if k != j:
                adj[j].add(k)
                adj[k].add(j)
    return adj


def upsilon_adj(i):
    """Upsilon_i = Gamma_i + edge xy + induced 6-cycle (a,v,c,u,b,w),
       x~a,b,c ; y~u,v,w ; N_Gamma(a)=N_Gamma(u)={1..i} ; (b,v)={i+1..2i} ; (c,w)={2i+1..3i-1}."""
    L = 3 * i - 1
    adj = gamma_adj(i)
    for s in SPECIALS:
        adj[s] = set()

    def add(p, q):
        adj[p].add(q)
        adj[q].add(p)

    add('x', 'y')
    for t in 'abc':
        add('x', t)
    for t in 'uvw':
        add('y', t)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']
    for k in range(6):
        add(cyc[k], cyc[(k + 1) % 6])
    X = list(range(1, i + 1))
    Y = list(range(i + 1, 2 * i + 1))
    Z = list(range(2 * i + 1, L + 1))
    for t in ('a', 'u'):
        for j in X:
            add(t, j)
    for t in ('b', 'v'):
        for j in Y:
            add(t, j)
    for t in ('c', 'w'):
        for j in Z:
            add(t, j)
    return adj, (X, Y, Z)


def delete(adj, verts):
    adj = {k: set(v) for k, v in adj.items()}
    for t in verts:
        for nb in adj[t]:
            adj[nb].discard(t)
        del adj[t]
    return adj


def paper_weights(i, variant):
    """the four regular weight functions of Theorem 3, verbatim."""
    L = 3 * i - 1
    if variant == '':
        w = {'x': 1, 'y': 1, 1: 1, 2 * i: 1, 'c': 3 * i - 3, 'w': 3 * i - 3,
             'u': 3 * i - 2, 'v': 3 * i - 2, 'a': 3 * i - 2, 'b': 3 * i - 2}
    elif variant == '-y':
        w = {1: 1, 2 * i: 1, 'x': 2, 'w': 3 * i - 4, 'u': 3 * i - 3, 'v': 3 * i - 3,
             'c': 3 * i - 3, 'a': 3 * i - 2, 'b': 3 * i - 2}
    elif variant == '-2i':
        w = {'x': 1, 'y': 1, 1: 2, i: 2, 'b': 3 * i - 3, 'v': 3 * i - 3, 'c': 3 * i - 3,
             'w': 3 * i - 3, 'u': 3 * i - 2, 'a': 3 * i - 2}
    elif variant == '-y-2i':
        w = {'x': 2, 1: 2, i: 2, 'v': 3 * i - 4, 'w': 3 * i - 4, 'u': 3 * i - 3,
             'b': 3 * i - 3, 'c': 3 * i - 3, 'a': 3 * i - 2}
    return w


def vega_family(i):
    """(name, adj, order, weights) for the four members."""
    U, _ = upsilon_adj(i)
    out = []
    for variant, dele in [('', []), ('-y', ['y']), ('-2i', [2 * i]), ('-y-2i', ['y', 2 * i])]:
        adj = delete(U, dele)
        order = sorted(t for t in adj if isinstance(t, int)) + [s for s in SPECIALS if s in adj]
        spec = paper_weights(i, variant)
        w = {t: spec.get(t, 3) for t in order}
        out.append(('Ups_%d%s' % (i, variant), adj, order, w))
    return out


# ---------------------------------------------------------------- graph predicates
def edges(adj):
    return sorted((min(u, v, key=str), max(u, v, key=str)) for u in adj for v in adj[u]
                  if str(u) < str(v))


def triangle_free(adj):
    for u in adj:
        for v in adj[u]:
            if adj[u] & adj[v]:
                return False
    return True


def maximal_tf(adj):
    if not triangle_free(adj):
        return False
    V = list(adj)
    for p, q in combinations(V, 2):
        if q in adj[p]:
            continue
        if not (adj[p] & adj[q]):
            return False
    return True


def twin_free(adj):
    seen = set()
    for t in adj:
        k = frozenset(adj[t])
        if k in seen:
            return False
        seen.add(k)
    return True


def chrom(adj, cap=6):
    V = sorted(adj, key=lambda t: -len(adj[t]))
    n = len(V)
    idx = {t: k for k, t in enumerate(V)}
    nb = [[idx[t] for t in adj[V[k]]] for k in range(n)]

    def ok(k):
        col = [-1] * n

        def rec(p, used):
            if p == n:
                return True
            forb = {col[j] for j in nb[p] if col[j] >= 0}
            for c in range(min(used + 1, k)):
                if c in forb:
                    continue
                col[p] = c
                if rec(p + 1, max(used, c + 1)):
                    return True
                col[p] = -1
            return False
        return rec(0, 0)
    for k in range(1, cap + 1):
        if ok(k):
            return k
    return None


def odd_girth(adj):
    best = None
    for s in adj:
        dist = {s: 0}
        order = [s]
        p = 0
        while p < len(order):
            cur = order[p]
            p += 1
            for t in adj[cur]:
                if t not in dist:
                    dist[t] = dist[cur] + 1
                    order.append(t)
        for u in adj:
            for v in adj[u]:
                if str(u) < str(v) and u in dist and v in dist and dist[u] == dist[v]:
                    L = 2 * dist[u] + 1
                    if best is None or L < best:
                        best = L
    return best


def has_induced_c5(adj):
    V = list(adj)
    for S in combinations(V, 5):
        SS = set(S)
        degs = [len(adj[t] & SS) for t in S]
        if all(d == 2 for d in degs):
            # 2-regular on 5 vertices == C5
            return True
    return False


# ---------------------------------------------------------------- graph6
def g6_decode(s):
    """returns n, set of edges as (i,j) with i<j, 0-indexed."""
    b = [ord(ch) - 63 for ch in s]
    n = b[0]
    assert n <= 62
    bits = []
    for byte in b[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    E = set()
    p = 0
    for j in range(n):
        for i in range(j):
            if bits[p]:
                E.add((i, j))
            p += 1
    return n, E


# ---------------------------------------------------------------- exact bip / psi
def bip_exact(order, adj, a):
    """min over all cuts of sum_{mono uv} a_u a_v.  Exhaustive over the support."""
    sup = [t for t in order if a[t] > 0]
    s = len(sup)
    if s <= 1:
        return 0
    idx = {t: k for k, t in enumerate(sup)}
    E = []
    for p, q in combinations(sup, 2):
        if q in adj[p]:
            E.append((idx[p], idx[q], a[p] * a[q]))
    if not E:
        return 0
    best = None
    for mask in range(1 << (s - 1)):
        tot = 0
        for (p, q, wt) in E:
            if ((mask >> p) & 1) == ((mask >> q) & 1):
                tot += wt
        if best is None or tot < best:
            best = tot
    return best


def mono_of(order, adj, a, side):
    """side = set of vertices on one side."""
    tot = 0
    for p, q in combinations(order, 2):
        if q in adj[p] and ((p in side) == (q in side)):
            tot += a[p] * a[q]
    return tot


# ---------------------------------------------------------------- arc families
def arcs_of(order, positions, L):
    """all cyclic-interval traces on the circle positions 1..L (missing positions skipped)."""
    at = {}
    for t in order:
        if positions.get(t) is not None:
            at[positions[t]] = t
    out = set()
    for s in range(1, L + 1):
        for ln in range(0, L + 1):
            A = frozenset(at[(s - 1 + k) % L + 1] for k in range(ln) if (s - 1 + k) % L + 1 in at)
            out.add(A)
    return sorted(out, key=lambda z: (len(z), sorted(map(str, z))))


def arcplus(order, positions, L, specials):
    """ARCPLUS = arc x arbitrary subset of the specials."""
    A = arcs_of(order, positions, L)
    out = []
    ns = len(specials)
    for arc in A:
        for T in range(1 << ns):
            S = set(arc)
            for k in range(ns):
                if (T >> k) & 1:
                    S.add(specials[k])
            out.append(frozenset(S))
    return list(set(out))


def famin(order, adj, a, fam):
    best = None
    for S in fam:
        v = mono_of(order, adj, a, S)
        if best is None or v < best:
            best = v
    return best
