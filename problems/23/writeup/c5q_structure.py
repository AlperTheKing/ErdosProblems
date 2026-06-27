#!/usr/bin/env python3
"""Dump the exact structure of the Gamma-min connected-B max cut of C5[q]:
which edges are bad (M), the side pattern, and #shortest 5-cycles per bad edge and per vertex,
so the hand-formula can be stated exactly."""
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, blow

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

for q in (2,3):
    n,E=blow(q); adj=adj_of(n,E)
    side,G,M,ell=gmin(n,adj,maxcut_all(n,adj))
    # vertex i*q+a is in part i (i=0..4), copy a (a=0..q-1)
    part=[v//q for v in range(n)]
    print(f"=== C5[{q}] N={n} ===")
    print("side pattern by part:", {i:[side[i*q+a] for a in range(q)] for i in range(5)})
    print("Gamma=",G,"N^2=",n*n,"|M|=",len(M))
    # which (part_i,part_j) pairs carry bad edges?
    from collections import Counter
    badparts=Counter((part[u],part[v]) for u,v in M)
    print("bad-edge part-pairs (count):", dict(badparts))
    # for one bad edge, how many shortest 5-cycles, and which vertices they cover
    u,v=M[0]
    Ps=geos(adj,side,u,v)
    print(f"bad edge {M[0]} parts({part[u]},{part[v]}): #shortest-cycles={len(Ps)}, ell={ell[(u,v)]}")
    # vertices in cycles of this edge, by part
    covered=Counter()
    for P in Ps:
        for w in set(P): covered[part[w]]+=1
    print("  per-part coverage over its cycles:", dict(covered))
    # T per vertex by part
    T=[F(0)]*n
    for (a,b) in M:
        Ps=geos(adj,side,a,b); nf=len(Ps); h=ell[(a,b)]; share=F(h,nf)
        cnt=[0]*n
        for P in Ps:
            for w in set(P): cnt[w]+=1
        T=[T[w]+share*cnt[w] for w in range(n)]
    print("  T by part:", {i:sorted(set(str(T[i*q+a]) for a in range(q))) for i in range(5)})
    print()
