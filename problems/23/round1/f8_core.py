"""
f8_core.py -- core routines for the F8 disproof hunt on Erdos #23.

Setting.  For a graph G and a weight vector a >= 0 on V(G) with sum(a)=1 put

    psi(G,a) = min over 2-colourings c:V->{0,1} of   sum_{ij in E, c_i=c_j} a_i a_j .

Facts used (proved in f8.md):
  * psi(G, uniform) = bip(G)/N^2.
  * For the balanced/unbalanced blow-up G[a_1..a_n] (a_i integers, N = sum a_i)
    bip(G[a]) / N^2 = psi(G, a/N)  exactly.
  * hence  sup over triangle-free graphs of bip/N^2  =  sup over triangle-free (G,a) of psi(G,a).

Routines here compute psi exactly for rational a, enumerate the antichain of
minimal monochromatic edge sets, and run the max-min optimisation over a.
"""
import itertools, math
from fractions import Fraction

# ---------------------------------------------------------------- graph6 I/O
def g6_decode(s):
    s = s.strip()
    assert s and s[0] != '>'
    p = [ord(ch) - 63 for ch in s]
    n = p[0]
    assert n <= 62, "n>62 not supported"
    bits = []
    for byte in p[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def g6_encode(n, adj):
    assert n <= 258047
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6:
        bits.append(0)
    if n <= 62:
        out = [chr(n + 63)]
    else:
        out = [chr(126), chr(((n >> 12) & 63) + 63), chr(((n >> 6) & 63) + 63), chr((n & 63) + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return ''.join(out)


def edges_of(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1 and (adj[i] & adj[j]):
                return False
    return True


def is_maximal_tf(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if not (adj[i] >> j) & 1 and (adj[i] & adj[j]) == 0:
                return False
    return True


def is_twin_free(n, adj):
    return len(set(adj)) == n


# ------------------------------------------------- monochromatic-set antichain
def mono_sets(n, adj):
    """All monochromatic edge sets over 2^(n-1) colourings, as bitmasks over
    the edge list; returns (edges, list_of_masks_minimal_antichain)."""
    import numpy as np
    E = edges_of(n, adj)
    m = len(E)
    assert m <= 62
    col = (np.arange(1 << (n - 1), dtype=np.int64)) << 1   # vertex 0 colour 0
    mask = np.zeros(1 << (n - 1), dtype=np.int64)
    for k, (i, j) in enumerate(E):
        same = (((col >> i) ^ (col >> j)) & 1) == 0
        mask |= same.astype(np.int64) << k
    seen = np.unique(mask)
    pc = np.array([bin(int(x)).count('1') for x in seen])
    order = np.argsort(pc, kind='stable')
    seen = seen[order]
    minimal = []
    acc = np.zeros(0, dtype=np.int64)
    for x in seen:
        xi = int(x)
        if acc.size == 0 or not np.any((acc & xi) == acc):
            minimal.append(xi)
            acc = np.append(acc, xi)
    return E, minimal


def mono_sets_any_m(n, adj):
    """Same as mono_sets but works for any number of edges (boolean matrix form).
    Returns (edges, list of minimal monochromatic sets given as tuples of edge
    indices), sorted by size."""
    import numpy as np
    E = edges_of(n, adj)
    m = len(E)
    col = (np.arange(1 << (n - 1), dtype=np.int64)) << 1
    M = np.empty((1 << (n - 1), m), dtype=bool)
    for k, (i, j) in enumerate(E):
        M[:, k] = (((col >> i) ^ (col >> j)) & 1) == 0
    M = np.unique(M, axis=0)
    sz = M.sum(1)
    M = M[np.argsort(sz, kind='stable')]
    acc = np.zeros((0, m), dtype=bool)
    out = []
    for r in range(M.shape[0]):
        x = M[r]
        if acc.shape[0] == 0 or not np.any(~np.any(acc & ~x, axis=1)):
            acc = np.vstack([acc, x])
            out.append(tuple(np.flatnonzero(x).tolist()))
    return E, out


def bip_exact(n, adj):
    """bip(G) = min number of monochromatic edges over all bipartitions."""
    E, minimal = mono_sets(n, adj)
    return min(bin(x).count('1') for x in minimal), E, minimal


def psi_rational(E, minimal, a):
    """psi for exact (Fraction) weights a."""
    best = None
    for mask in minimal:
        s = Fraction(0)
        mm = mask
        while mm:
            k = (mm & -mm).bit_length() - 1
            i, j = E[k]
            s += a[i] * a[j]
            mm &= mm - 1
        if best is None or s < best:
            best = s
    return best
