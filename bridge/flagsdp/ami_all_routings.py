#!/usr/bin/env python3
"""Does AMI hold for the UNIFORM routing (not just LP-opt)?  And does the MIN over routings of
sum_v max(0,T(v)-N) equal the LP relationship?  If AMI holds for uniform routing too, the
aggregation can use the canonical uniform geodesic split (no LP needed) -- important for a proof.

Also: is AMI EQUIVALENT to the GPI, or strictly stronger as a *graph* statement?  The GPI/vertex-load
theorem only needs SOME routing with max-bound. AMI for uniform routing is a concrete sufficient claim.
We already saw uniform AMI holds N<=10. Here we directly stress the C5[q] tight family and a few
near-tight band graphs to record the exact tightness pattern (which vertices overload, by how much)."""
import sys, numpy as np
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos

def to_setadj(n,A): return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]

def uniform_Tv(N,adj,side,M):
    Tv=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0])
        for P in geos:
            for x in P: Tv[x]+=h/len(geos)
    return Tv

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]; G=25*len(M)
    return n,adj,side,G,M

for q in (1,2,3,4):
    n,adj,side,G,M=C5q(q)
    Tv=uniform_Tv(n,adj,side,M)
    ami=np.maximum(0.0,Tv-n).sum(); deficit=n*n-G
    over=[(v,round(Tv[v],3)) for v in range(n) if Tv[v]>n+1e-9]
    print(f"C5[{q}]: N={n} Gamma={G} deficit={deficit} uniform AMI sum max(0,T-N)={ami:.4f} <= deficit={deficit}? {ami<=deficit+1e-9}")
    print(f"        T(v) values: {sorted(set(round(t,3) for t in Tv))}  (all==N={n}? {abs(Tv.max()-Tv.min())<1e-9})")
