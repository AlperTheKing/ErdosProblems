#!/usr/bin/env python3
"""The aggregation crux: AMI = sum_v max(0,T(v)-N) <= N^2-Gamma must charge each vertex's OVERLOAD
to the global deficit N^2-Gamma = sum_e (N^2-related)?  Actually N^2-Gamma is a SINGLE scalar, while
the prefix-transport lemma produces PER-(edge,obstruction,prefix) local defects eta(S)>0.

DIAGNOSTIC: is there a per-vertex LOCAL deficit decomposition?  Define the 'co-deficit' at v.
Note N^2 - Gamma = N*N - sum_e h_e^2.  Also sum_v T(v) = Gamma.  So
   sum_v (N - T(v)) = N^2 - Gamma     (EXACT identity!).
i.e. the deficit N^2-Gamma equals sum_v (N - T(v)) = sum of UNDERloads (signed).
Therefore AMI  <=>  sum_v max(0,T(v)-N) <= sum_v (N-T(v)) = sum_v max(0,N-T(v)) - sum_v max(0,T(v)-N).
Let O=sum_v max(0,T-N) (overload), U=sum_v max(0,N-T) (underload). Then sum_v(N-T)=U-O.
AMI says O <= U - O, i.e.  2O <= U,  i.e.  sum overload <= (1/2) sum underload.
EQUIVALENTLY: 2*sum_v max(0,T(v)-N) <= sum_v max(0,N-T(v)).   <-- THE CLEAN FORM OF AMI.

This is a pure statement about the load vector: total overload above N is at most half the total
underload below N. Verify this clean form on census, and record the tightness (C5: O=U=0)."""
import sys, numpy as np
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos

def to_setadj(n,A): return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]
def build(n,adj):
    res,mc=gamma_min_cut(n,adj,edges_of(adj)); return res
def uniform_Tv(N,adj,side,M):
    Tv=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0])
        for P in geos:
            for x in P: Tv[x]+=h/len(geos)
    return Tv

Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 10
worst=(1e9,None); nchk=0
for N in range(5,Nmax+1):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A); b=build(N,adj)
        if b is None: continue
        side,G,M=b
        if not M: continue
        Tv=uniform_Tv(N,adj,side,M)
        if Tv is None: continue
        # exact identity check: sum(N-T) == N^2-Gamma
        assert abs((N-Tv).sum() - (N*N-G))<1e-6
        O=np.maximum(0.0,Tv-N).sum(); U=np.maximum(0.0,N-Tv).sum()
        # clean AMI:  2O <= U
        slack = U - 2*O
        if slack < worst[0]: worst=(slack,(N,G,round(O,4),round(U,4),round(Tv.max(),3)))
        nchk+=1
print(f"census N<={Nmax}: graphs={nchk}")
print(f"  CLEAN AMI (2*overload <= underload):  worst (U-2O) = {worst[0]:.4f}  [holds iff >=0]")
print(f"  witness (N,Gamma,O,U,maxT) = {worst[1]}")
