"""audit_G9_core.py -- INDEPENDENT re-implementation for the G9 audit.

Written from scratch; does NOT import G9_lib or any G9_* module.
Design choices deliberately different from the target's:
  * graph6 decoder builds an adjacency-matrix list-of-lists (not bitmasks) first,
    then derives bitmasks, so a bit-order bug would show up as a degree mismatch.
  * max-cut / bip is computed by iterating over the *side-0 set* and counting
    monochromatic edges with popcount over adjacency masks (target used an
    edge-list loop with early break, or a subset-sum DP).
  * blow-up bip is computed by enumerating ALL 2^(h-1) cuts of the pattern H and
    summing a_u a_v over monochromatic edges -- the "odd subset of C5" shortcut
    used by the target is NEVER used; it is instead *checked* against this.
All arithmetic is exact Python integers / Fractions.
"""
from fractions import Fraction
from itertools import product


# ---------------------------------------------------------------- graph6
def g6_decode(s):
    """graph6 -> (n, adjacency matrix as list of lists of 0/1). n <= 62 only."""
    s = s.strip()
    d = [ord(c) - 63 for c in s]
    n = d[0]
    if n > 62:
        raise ValueError("only n<=62 supported")
    bits = []
    for b in d[1:]:
        bits.extend(((b >> k) & 1) for k in (5, 4, 3, 2, 1, 0))
    need = n * (n - 1) // 2
    if len(bits) < need:
        raise ValueError("graph6 too short: %s" % s)
    M = [[0] * n for _ in range(n)]
    p = 0
    # graph6 column-major order: for j=1..n-1, for i=0..j-1
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                M[i][j] = M[j][i] = 1
            p += 1
    return n, M


def masks_of(n, M):
    return [sum(1 << j for j in range(n) if M[i][j]) for i in range(n)]


def edge_list(n, M):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if M[i][j]]


def deg_list(n, M):
    return [sum(M[i]) for i in range(n)]


def triangle_free(n, M):
    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j]:
                for k in range(j + 1, n):
                    if M[i][k] and M[j][k]:
                        return False
    return True


def maximal_triangle_free(n, M):
    if not triangle_free(n, M):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if not M[i][j]:
                if not any(M[i][k] and M[j][k] for k in range(n)):
                    return False
    return True


# ---------------------------------------------------------------- exact bip
def bip_exhaustive(n, M):
    """bip(G) = |E| - maxcut(G) = min over cuts of #monochromatic edges.
    Exhaustive over all 2^(n-1) bipartitions (vertex 0 pinned to side A).
    Counting method: popcount of adj-mask intersected with each side."""
    if n == 0:
        return 0
    adj = masks_of(n, M)
    best = None
    full = (1 << n) - 1
    for S in range(1 << (n - 1)):          # S ranges over subsets of {1..n-1}
        A = (S << 1) | 1                   # side A always contains vertex 0
        B = full ^ A
        mono = 0
        x = A
        while x:
            v = (x & -x).bit_length() - 1
            mono += bin(adj[v] & A).count("1")
            x &= x - 1
        y = B
        while y:
            v = (y & -y).bit_length() - 1
            mono += bin(adj[v] & B).count("1")
            y &= y - 1
        mono //= 2
        if best is None or mono < best:
            best = mono
    return best


def delete_vertex(n, M, v):
    keep = [u for u in range(n) if u != v]
    return len(keep), [[M[a][b] for b in keep] for a in keep]


def delete_set(n, M, S):
    S = set(S)
    keep = [u for u in range(n) if u not in S]
    return len(keep), [[M[a][b] for b in keep] for a in keep]


# ---------------------------------------------------------------- blow-ups
def blowup_bip_exact(h, Hedges, a):
    """bip(H[a]) = min over ALL cuts of H of sum_{uv monochromatic} a_u a_v.
    Full 2^(h-1) enumeration; no parity shortcut."""
    best = None
    for S in range(1 << (h - 1)):
        side = [(S >> i) & 1 if i < h - 1 else 0 for i in range(h)]
        tot = 0
        for (u, v) in Hedges:
            if side[u] == side[v]:
                tot += a[u] * a[v]
        if best is None or tot < best:
            best = tot
    return best


def build_blowup(h, Hedges, a):
    """explicit graph of H[a] as (n, adjacency matrix), plus part index per vertex."""
    off, c = [], 0
    for x in a:
        off.append(c)
        c += x
    n = c
    M = [[0] * n for _ in range(n)]
    part = [0] * n
    for i in range(h):
        for p in range(a[i]):
            part[off[i] + p] = i
    for (u, v) in Hedges:
        for p in range(a[u]):
            for q in range(a[v]):
                M[off[u] + p][off[v] + q] = 1
                M[off[v] + q][off[u] + p] = 1
    return n, M, off, part


C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
