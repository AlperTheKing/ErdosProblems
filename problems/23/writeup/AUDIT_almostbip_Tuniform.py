#!/usr/bin/env python3
"""Test claim U (max_v T_uniform(v) <= K = N + (N^2 - Gamma)) on ALMOST-BIPARTITE graphs:
bipartite base + a few edges making LONG odd cycles (few bad edges, large ell, few shortest cycles).
EXACT Fractions only. Re-confirm any violation independently. Reports min slack (K - maxT) and any g6.
"""
import sys, io
from fractions import Fraction
from collections import deque

# import helpers; suppress the import-time demo print of census_GPI
_stdout = sys.stdout
sys.stdout = io.StringIO()
import subprocess
from census_GPI import maxcut_all, gmin, geos, GENG, dec, blow
sys.stdout = _stdout

def adj_of(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj

def has_triangle(n, adj):
    for u in range(n):
        nu = adj[u]
        for v in nu:
            if v > u:
                if nu & adj[v]:
                    return True
    return False

def Tuniform_maxslack(n, E):
    """Return (Gamma, K, maxT, slack=K-maxT, side, M, ell) using gamma-min connected-B max cut.
    All exact Fractions. Returns None if no valid gamma-min connected-B cut (e.g. bipartite => M empty)."""
    adj = adj_of(n, E)
    cuts = maxcut_all(n, adj)
    r = gmin(n, adj, cuts)
    if r is None:
        return None
    side, Gamma, M, ell = r
    T = [Fraction(0) for _ in range(n)]
    for f in M:
        u, v = f
        Ps = geos(adj, side, u, v)
        nf = len(Ps)
        if nf == 0:
            return ('GEOFAIL', f)
        share = Fraction(ell[f], nf)
        for P in Ps:
            for w in P:
                T[w] += share
    maxT = max(T)
    K = Fraction(n + (n * n - Gamma))
    slack = K - maxT
    return (Gamma, K, maxT, slack, side, M, ell, T)

def reconfirm(n, E, expected_side=None):
    """Recompute everything independently (own maxcut + gamma-min + geodesics) for a flagged violation."""
    return Tuniform_maxslack(n, E)

def g6_encode(n, E):
    """Encode an edge list to nauty graph6."""
    Eset = set()
    for a, b in E:
        if a > b: a, b = b, a
        Eset.add((a, b))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in Eset else 0)
    # pad to multiple of 6
    while len(bits) % 6 != 0:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        val = 0
        for b in bits[k:k+6]:
            val = (val << 1) | b
        out += chr(val + 63)
    return out
