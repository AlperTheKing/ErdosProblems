"""Exact bip / maxcut utilities for Erdos #23 (family F1).

All arithmetic is exact integer arithmetic.  bip(G) = e(G) - maxcut(G).
"""
from itertools import combinations


def bip_bruteforce(n, edges):
    """Exact bip of a graph on n vertices given as an edge list (0-indexed)."""
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    m = len(edges)
    best = -1
    # fix vertex 0 in side S
    for S in range(1 << (n - 1)):
        S = (S << 1) | 1
        cut = 0
        for v in range(n):
            if (S >> v) & 1:
                cut += bin(adj[v] & ~S).count('1')
        if cut > best:
            best = cut
    return m - best


def blowup_bip(n, edges, t):
    """min_{S subset V} sum_{ij in E, ij not crossing S} t_i t_j  (Lemma A rhs).

    Exact integer arithmetic; 2^(n-1) subsets."""
    best = None
    for S in range(1 << (n - 1)):
        S = (S << 1) | 1
        tot = 0
        for (u, v) in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += t[u] * t[v]
        if best is None or tot < best:
            best = tot
    return best


def expand(n, edges, t):
    """Explicit vertex-blow-up graph H[t]: returns (N, edge list)."""
    off = [0] * (n + 1)
    for i in range(n):
        off[i + 1] = off[i] + t[i]
    N = off[n]
    E = []
    for (u, v) in edges:
        for a in range(off[u], off[u + 1]):
            for b in range(off[v], off[v + 1]):
                E.append((a, b))
    return N, E


def is_triangle_free(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


def g6_decode(s):
    """graph6 string -> (n, edge list). Handles n <= 62."""
    s = s.strip()
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        x = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    E = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E
