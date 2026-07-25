"""audit_Q1_core.py -- INDEPENDENT exact re-implementation for the audit of round7/Q1.md.

Own graph6 decoder (bit-string form), own max-cut (subset DP on e[S]), own
neighbourhood-union family over ALL subsets, own induced-C5 enumeration,
own weighted blow-up evaluator.  Exact integers / fractions.Fraction only.
Floating point is used nowhere except in printed diagnostics tagged (approx).
"""
from fractions import Fraction
from itertools import combinations
import sys

# ---------------------------------------------------------------- graph6


def g6(s):
    """graph6 string -> (n, adjacency bitmasks).  Independent decoder:
    build the whole bit string first, then walk (j,i) in column order."""
    vals = [ord(c) - 63 for c in s]
    n = vals[0]
    bitstr = "".join(format(v, "06b") for v in vals[1:])
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bitstr[k] == "1":
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    assert k <= len(bitstr)
    return n, adj


def edges(n, adj):
    return [(i, j) for j in range(n) for i in range(j) if adj[i] >> j & 1]


def trianglefree(n, adj):
    return all(adj[i] & adj[j] == 0 for (i, j) in edges(n, adj))


def eS_table(n, adj):
    """e[S] = number of edges inside S, for every subset S, by DP."""
    e = [0] * (1 << n)
    for S in range(1, 1 << n):
        v = (S & -S).bit_length() - 1
        R = S & (S - 1)
        e[S] = e[R] + bin(adj[v] & R).count("1")
    return e


def bip(n, adj):
    e = eS_table(n, adj)
    full = (1 << n) - 1
    return min(e[S] + e[full ^ S] for S in range(0, 1 << n, 2))


def fam_union(n, adj):
    """min over ALL index sets I of mono(union_{v in I} N(v)); returns (value, I, N(I))."""
    e = eS_table(n, adj)
    full = (1 << n) - 1
    best = (e[full] + e[0], None, None)          # I = empty  ->  N(I) = empty
    for I in range(1 << n):
        U = 0
        t = I
        while t:
            v = (t & -t).bit_length() - 1
            t &= t - 1
            U |= adj[v]
        val = e[U] + e[full ^ U]
        if val < best[0]:
            best = (val, I, U)
    return best


def fam_union_weighted(n, adj, a):
    """same family, weighted: min over I of sum_{uv mono} a_u a_v (exact)."""
    E = edges(n, adj)
    best = None
    arg = None
    for I in range(1 << n):
        U = 0
        t = I
        while t:
            v = (t & -t).bit_length() - 1
            t &= t - 1
            U |= adj[v]
        val = sum(a[u] * a[v] for (u, v) in E if ((U >> u) & 1) == ((U >> v) & 1))
        if best is None or val < best:
            best, arg = val, (I, U)
    return best, arg


def bip_weighted(n, adj, a):
    """min over ALL 2^n cuts of H of sum_{uv mono} a_u a_v  = bip(H[a]) by base 1."""
    E = edges(n, adj)
    best = None
    arg = None
    for S in range(1 << n):
        val = sum(a[u] * a[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or val < best:
            best, arg = val, S
    return best, arg


def induced_c5(n, adj):
    """all 5-subsets inducing a C5 (= all C5 subgraphs when G is triangle-free)."""
    out = []
    for S in combinations(range(n), 5):
        mask = 0
        for v in S:
            mask |= 1 << v
        if all(bin(adj[v] & mask).count("1") == 2 for v in S):
            # connected?
            comp = 1 << S[0]
            fr = comp
            while fr:
                nx = 0
                t = fr
                while t:
                    v = (t & -t).bit_length() - 1
                    t &= t - 1
                    nx |= adj[v] & mask & ~comp
                comp |= nx
                fr = nx
            if comp == mask:
                out.append(S)
    return out


def blowup_edges(n, adj, a):
    """explicit blow-up as (N, edge list) -- used to re-verify base 1 from scratch."""
    off = [0]
    for x in a:
        off.append(off[-1] + x)
    E = []
    for (i, j) in edges(n, adj):
        for p in range(off[i], off[i + 1]):
            for q in range(off[j], off[j + 1]):
                E.append((p, q))
    return off[-1], E


def bip_edgelist(N, E):
    adj = [0] * N
    for (u, v) in E:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    e = [0] * (1 << N)
    for S in range(1, 1 << N):
        v = (S & -S).bit_length() - 1
        R = S & (S - 1)
        e[S] = e[R] + bin(adj[v] & R).count("1")
    full = (1 << N) - 1
    return min(e[S] + e[full ^ S] for S in range(0, 1 << N, 2))
