"""Probe the cut-metric/pentagonal angle on C5[q].
For C5[q]: vertices in 5 classes V0..V4 (cyclic B-bipartite cycle). All bad edges between V0,V4.
Each bad edge e=(a in V4, b in V0) has h_e=5; shortest B-geodesics are 0_b-1_*-2_*-3_*-4_a paths.
We want to find a 'biased pentagonal facet': a functional that is tight (equality) on C5[q]
and dominates the GPI integrand. Let me first SEE the exact geodesic structure and the per-vertex
load at the optimum, to understand what dual phi the LP uses.
"""
import numpy as np
from mycielskian_check import all_shortest_geos

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]; G=25*len(M)
    return n,adj,side,M,vid

for q in (2,3):
    n,adj,side,M,vid=C5q(q)
    print(f"\n=== C5[{q}] n={n} beta={len(M)} ===")
    e0=M[0]
    geos=all_shortest_geos(n,adj,side,*e0)
    print(f"  bad edge {e0}: #shortest-geos={len(geos)} each len={len(geos[0])}")
    # class of each vertex
    cls={vid(i,j):i for i in range(5) for j in range(q)}
    for P in geos[:6]:
        print("   ", [cls[v] for v in P], P)
