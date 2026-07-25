"""G9 base library: exact bip / maxcut for small graphs, blow-up bip, C5[n] checks.

All arithmetic is exact integer arithmetic.
"""
from fractions import Fraction
from itertools import combinations


def edges_from_adj(adj):
    n = len(adj)
    return [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] & (1 << v)]


def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def bip_bruteforce(n, edges):
    """min over cuts S of #monochromatic edges. Exact integer. O(2^(n-1) m)."""
    if n == 0:
        return 0
    best = len(edges)
    for S in range(1 << (n - 1)):  # vertex n-1 fixed on side 0
        m = 0
        for (u, v) in edges:
            su = (S >> u) & 1 if u < n - 1 else 0
            sv = (S >> v) & 1 if v < n - 1 else 0
            if su == sv:
                m += 1
                if m >= best:
                    break
        if m < best:
            best = m
    return best


def bip_weighted(n, edges, w):
    """min over cuts of sum of a_u*a_v over monochromatic edges uv. w = list of weights."""
    if n == 0:
        return 0
    best = None
    for S in range(1 << (n - 1)):
        tot = 0
        for (u, v) in edges:
            su = (S >> u) & 1 if u < n - 1 else 0
            sv = (S >> v) & 1 if v < n - 1 else 0
            if su == sv:
                tot += w[u] * w[v]
                if best is not None and tot >= best:
                    break
        if best is None or tot < best:
            best = tot
    return best


def blowup(n, edges, w):
    """Return (N, edge list) of the blow-up with part sizes w."""
    off = []
    c = 0
    for i in range(n):
        off.append(c)
        c += w[i]
    E = []
    for (u, v) in edges:
        for a in range(w[u]):
            for b in range(w[v]):
                E.append((off[u] + a, off[v] + b))
    return c, E, off


C5_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


def parse_graph6(s):
    """Return (n, edges) from a graph6 string."""
    data = [ord(ch) - 63 for ch in s]
    if data[0] < 63:
        n = data[0]
        idx = 1
    else:
        raise ValueError("large graph6 not supported")
    bits = []
    for b in data[idx:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    edges = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]:
                edges.append((i, j))
            p += 1
    return n, edges


def degrees(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def is_triangle_free(n, edges):
    adj = adj_from_edges(n, edges)
    for (u, v) in edges:
        if adj[u] & adj[v]:
            return False
    return True


def is_maximal_triangle_free(n, edges):
    if not is_triangle_free(n, edges):
        return False
    adj = adj_from_edges(n, edges)
    for u in range(n):
        for v in range(u + 1, n):
            if not (adj[u] >> v) & 1:
                if not (adj[u] & adj[v]):
                    return False
    return True
