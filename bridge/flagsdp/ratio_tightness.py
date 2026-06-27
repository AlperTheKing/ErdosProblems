#!/usr/bin/env python3
"""Find the graph minimizing U/O (overload-to-underload ratio) among graphs with O>0.
This reveals the BINDING constant in '2O<=U'. If min U/O is exactly 2 somewhere (other than the
degenerate C5 where O=U=0), the factor 2 is essential; if min U/O > 2 strictly on census, the
true aggregate inequality has a better constant and C5 is NOT the binding case for AMI's constant."""
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
Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 9
best=(1e9,None)
for N in range(5,Nmax+1):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A)
        res,mc=gamma_min_cut(N,adj,edges_of(adj))
        if res is None: continue
        side,G,M=res
        if not M: continue
        Tv=uniform_Tv(N,adj,side,M)
        if Tv is None: continue
        O=np.maximum(0.0,Tv-N).sum(); U=np.maximum(0.0,N-Tv).sum()
        if O>1e-9:
            r=U/O
            if r<best[0]: best=(r,(N,G,round(O,3),round(U,3),round(Tv.max(),3)))
print(f"min U/O over census N<={Nmax} (graphs with O>0) = {best[0]:.4f}")
print(f"  witness (N,Gamma,O,U,maxT) = {best[1]}   [2O<=U needs U/O>=2]")
