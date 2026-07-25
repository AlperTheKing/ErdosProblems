"""G10_core.py -- exact primitives for Erdos #23 psi-landscape search.

psi(H,x) = min over cuts S of H of sum_{uv monochromatic} x_u x_v,  x in simplex.
bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v   (integer weights).

Everything here is EXACT (python ints / Fractions).  No floats on any acceptance path.
"""
from fractions import Fraction
from itertools import combinations
import sys


# ---------------------------------------------------------------- graph6 I/O
def g6_to_edges(s):
    """Decode a graph6 string -> (n, sorted edge list)."""
    s = s.strip()
    if not s:
        return None
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:  # n >= 63 encoding
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        rest = data[4:]
    else:
        n = data[0]
        rest = data[1:]
    bits = []
    for d in rest:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def edges_to_g6(n, edges):
    es = set()
    for u, v in edges:
        es.add((min(u, v), max(u, v)))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)] if n < 63 else None
    assert out is not None
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return ''.join(out)


# ---------------------------------------------------------------- basic tests
def adjacency(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def is_triangle_free(n, edges):
    adj = adjacency(n, edges)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


def is_maximal_triangle_free(n, edges):
    """G maximal triangle-free  iff  triangle-free and every non-adjacent pair
    has a common neighbour."""
    if not is_triangle_free(n, edges):
        return False
    adj = adjacency(n, edges)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i] >> j & 1:
                continue
            if not (adj[i] & adj[j]):
                return False
    return True


def induced_c5s(n, edges):
    """All vertex 5-subsets inducing a C5, returned as cyclic orderings (one per set)."""
    adj = adjacency(n, edges)
    out = []
    for S in combinations(range(n), 5):
        mask = 0
        for v in S:
            mask |= 1 << v
        deg = {}
        ok = True
        cnt = 0
        for v in S:
            d = bin(adj[v] & mask).count('1')
            deg[v] = d
            cnt += d
            if d != 2:
                ok = False
                break
        if not ok or cnt != 10:
            continue
        # connected 2-regular on 5 vertices == C5
        start = S[0]
        seen = {start}
        cur = start
        prev = -1
        order = [start]
        for _ in range(4):
            nb = [w for w in S if (adj[cur] >> w) & 1 and w != prev]
            if not nb:
                ok = False
                break
            nxt = nb[0] if nb[0] not in seen else (nb[1] if len(nb) > 1 else None)
            if nxt is None:
                ok = False
                break
            order.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        if ok and len(seen) == 5:
            out.append(tuple(order))
    return out


# ---------------------------------------------------------------- cuts
def all_cut_monoedges(n, edges):
    """For every cut (vertex 0 pinned to side 0) return the list of monochromatic
    edges.  Returns list of length 2^(n-1)."""
    res = []
    for mask in range(1 << (n - 1)):
        m = mask << 1  # bit v set  <=>  v on side 1 ; vertex 0 on side 0
        mono = [(u, v) for (u, v) in edges if ((m >> u) & 1) == ((m >> v) & 1)]
        res.append(mono)
    return res


def bip_blowup(monolists, a):
    """Exact integer bip(H[a]) given precomputed mono-edge lists."""
    best = None
    for mono in monolists:
        s = 0
        for u, v in mono:
            s += a[u] * a[v]
            if best is not None and s >= best:
                break
        else:
            if best is None or s < best:
                best = s
                if best == 0:
                    return 0
    return best


def psi_exact(monolists, x):
    """x: list of Fractions summing to 1.  Returns exact Fraction psi(H,x)."""
    best = None
    for mono in monolists:
        s = Fraction(0)
        for u, v in mono:
            s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


def bip(n, edges):
    """bip(H) = |E| - maxcut(H); exact integer."""
    monolists = all_cut_monoedges(n, edges)
    return min(len(m) for m in monolists)


# ---------------------------------------------------------------- named graphs
def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def petersen():
    e = [(i, (i + 1) % 5) for i in range(5)]
    e += [(i, i + 5) for i in range(5)]
    e += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, e


def mycielski(n, edges):
    """Mycielskian: vertices 0..n-1 original, n..2n-1 copies, 2n apex."""
    e = list(edges)
    for (u, v) in edges:
        e.append((u, v + n))
        e.append((v, u + n))
    for i in range(n):
        e.append((n + i, 2 * n))
    return 2 * n + 1, e


def grotzsch():
    return mycielski(*cycle(5))


def chvatal():
    n = 12
    e = [(0, 1), (0, 4), (0, 6), (0, 9), (1, 2), (1, 5), (1, 7), (2, 3), (2, 6),
         (2, 8), (3, 4), (3, 7), (3, 9), (4, 5), (4, 8), (5, 10), (5, 11),
         (6, 10), (6, 11), (7, 8), (7, 11), (8, 10), (9, 10), (9, 11)]
    return n, e


def circulant(n, conn):
    e = set()
    for i in range(n):
        for c in conn:
            j = (i + c) % n
            if i != j:
                e.add((min(i, j), max(i, j)))
    return n, sorted(e)


def andrasfai(k):
    """And(k): circulant on 3k-1 vertices with connections i-j = 1 mod 3."""
    n = 3 * k - 1
    conn = [c for c in range(1, n // 2 + 1) if c % 3 == 1]
    return circulant(n, conn)


def kneser(m, k):
    verts = list(combinations(range(m), k))
    idx = {v: i for i, v in enumerate(verts)}
    e = []
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            if not (set(verts[i]) & set(verts[j])):
                e.append((i, j))
    return len(verts), e


def cayley(gen_elems, mult, conn):
    """gen_elems: list of group elements (hashable); mult(a,b); conn: set of connectors."""
    idx = {g: i for i, g in enumerate(gen_elems)}
    e = set()
    for g in gen_elems:
        for s in conn:
            h = mult(g, s)
            i, j = idx[g], idx[h]
            if i != j:
                e.add((min(i, j), max(i, j)))
    return len(gen_elems), sorted(e)


if __name__ == '__main__':
    # -------- validation of the primitives
    n, e = cycle(5)
    ml = all_cut_monoedges(n, e)
    x = [Fraction(1, 5)] * 5
    assert psi_exact(ml, x) == Fraction(1, 25), psi_exact(ml, x)
    assert bip(5, e) == 1
    n7, e7 = cycle(7)
    ml7 = all_cut_monoedges(n7, e7)
    assert psi_exact(ml7, [Fraction(1, 7)] * 7) == Fraction(1, 49)
    assert bip(7, e7) == 1
    np_, ep = petersen()
    assert is_triangle_free(np_, ep)
    assert bip(np_, ep) == 3
    ng, eg = grotzsch()
    assert (ng, is_triangle_free(ng, eg)) == (11, True)
    nc, ec = chvatal()
    assert is_triangle_free(nc, ec) and len(ec) == 24
    print('psi(C5,unif) =', psi_exact(ml, x))
    print('psi(C7,unif) =', psi_exact(ml7, [Fraction(1, 7)] * 7))
    print('bip(Petersen) =', bip(np_, ep))
    print('bip(Grotzsch) =', bip(ng, eg))
    print('bip(Chvatal)  =', bip(nc, ec))
    print('induced C5 count in Petersen:', len(induced_c5s(np_, ep)))
    print('CORE OK')
