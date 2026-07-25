"""H3 helpers: build graphs, emit graph6, exact checks.

Only used to CONSTRUCT candidates; all verification (maxcut, bip, alpha,
triangle-freeness) is done by h3_engine.exe and independently by h3_verify.py.
"""
import itertools, sys


def g6(n, edges):
    """graph6 string for a simple graph on n<=62 vertices, edges = set of (i,j)."""
    E = set()
    for a, b in edges:
        if a == b:
            continue
        E.add((min(a, b), max(a, b)))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in E else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out


def decode_g6(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def circulant(n, S):
    E = set()
    for v in range(n):
        for s in S:
            u = (v + s) % n
            E.add((min(u, v), max(u, v)))
    return E


def cayley(elems, mult, conn):
    """elems: list of group elements (hashable); mult(a,b); conn: set of connectors."""
    idx = {e: i for i, e in enumerate(elems)}
    E = set()
    for e in elems:
        for c in conn:
            f = mult(e, c)
            a, b = idx[e], idx[f]
            if a != b:
                E.add((min(a, b), max(a, b)))
    return E


def is_triangle_free(n, edges):
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    for a, b in edges:
        if adj[a] & adj[b]:
            return False
    return True


def alpha(n, edges):
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    best = 0

    def rec(P, sz):
        nonlocal best
        if sz + bin(P).count('1') <= best:
            return
        if P == 0:
            best = max(best, sz)
            return
        bv, bd = -1, -1
        Q = P
        while Q:
            v = (Q & -Q).bit_length() - 1
            Q &= Q - 1
            d = bin(adj[v] & P).count('1')
            if d > bd:
                bd, bv = d, v
        rec(P & ~(adj[bv] | (1 << bv)), sz + 1)
        rec(P & ~(1 << bv), sz)

    rec((1 << n) - 1, 0)
    return best


if __name__ == "__main__":
    # smoke test: C5, C5[2], C13(1,5)
    tests = [(5, circulant(5, [1])), (10, circulant(10, [1, 4])), (13, circulant(13, [1, 5]))]
    for n, E in tests:
        print(g6(n, E), n, len(E), is_triangle_free(n, E), alpha(n, E))
