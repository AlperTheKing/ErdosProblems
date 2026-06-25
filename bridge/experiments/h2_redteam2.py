#!/usr/bin/env python3
"""
RED TEAM 2 for Erdos #23 H2 (peeling lemma).
H2(n): every triangle-free G on 5n vtx admits a 5-set S with beta(G)-beta(G-S) <= 2n-1.
We test EXPLICIT triangle-free candidates on N=15 (n=3, target 5) and N=20 (n=4, target 7).
A counterexample = beta>=band AND min over all C(N,5) 5-sets of drop > 2n-1.
beta via EXACT brute MaxCut (2^N), no heuristics.
"""
import itertools, sys

def maxcut(N, adjmask, verts):
    """exact MaxCut on induced subgraph `verts` (list of vtx ids). adjmask = list of bitmasks over 0..N-1."""
    m = len(verts)
    if m <= 1:
        return 0, 0
    idx = {v:i for i,v in enumerate(verts)}
    badj = [0]*m
    E = 0
    for v in verts:
        for w in range(N):
            if (adjmask[v]>>w)&1 and w in idx and v < w:
                ia, ib = idx[v], idx[w]
                badj[ia] |= (1<<ib); badj[ib] |= (1<<ia)
                E += 1
    best = 0
    for half in range(1 << (m-1)):
        side1 = half << 1
        cut = 0
        x = side1
        while x:
            low = x & (-x)
            vv = low.bit_length()-1
            cut += bin(badj[vv] & ~side1).count('1')
            x ^= low
        if cut > best:
            best = cut
    return best, E

def build(N, edges):
    adjmask = [0]*N
    for (u,v) in edges:
        adjmask[u] |= (1<<v); adjmask[v] |= (1<<u)
    return adjmask

def has_triangle(N, adjmask):
    for u in range(N):
        for v in range(u+1, N):
            if (adjmask[u]>>v)&1:
                if adjmask[u] & adjmask[v]:
                    return True
    return False

def beta(N, adjmask, verts):
    mc, E = maxcut(N, adjmask, verts)
    return E - mc

def analyze(name, N, edges, claimed_beta=None):
    n = N//5
    target = 2*n-1
    adjmask = build(N, edges)
    tri = has_triangle(N, adjmask)
    allv = list(range(N))
    bG = beta(N, adjmask, allv)
    res = {'name':name,'N':N,'n':n,'target':target,'triangle_free':not tri,'beta':bG,'claimed_beta':claimed_beta,'E':sum(bin(m).count('1') for m in adjmask)//2}
    if tri:
        res['verdict'] = 'INVALID (has triangle)'
        return res
    # min over all 5-sets of drop
    mn = None; arg = None
    for S in itertools.combinations(allv, 5):
        Sset = set(S)
        rem = [v for v in allv if v not in Sset]
        d = bG - beta(N, adjmask, rem)
        if mn is None or d < mn:
            mn = d; arg = S
    res['min_drop'] = mn
    res['argmin'] = arg
    res['H2_holds'] = (mn <= target)
    res['margin'] = mn - target  # >0 => VIOLATION
    res['verdict'] = 'H2 VIOLATION!!!' if mn > target else 'H2 holds'
    return res

if __name__ == "__main__":
    pass
