#!/usr/bin/env python3
"""Bridge probe: relate per-vertex underload (N - T(v)) to a CD/signed-boundary margin at v.

For the uniform routing, T(v) = sum_{e} h_e * (fraction of shortest geos of e through v).
We look for a LOCAL lower bound on the spare capacity  spare(v)=N-T(v)  in terms of cut data at v,
which is what an aggregation must use to charge overload (where T(v)>N) to spare (T(v)<N).

Candidate quantities measured per vertex v (uniform routing):
  T(v)         geodesic congestion
  spare(v)=N-T(v)
  degB(v), degM(v)  (B- and M-degree)
  reach(v) = # vertices NOT routed-reachable... (heuristic)
We test the simplest hoped-for inequalities:
  (i)   T(v) <= N   ALWAYS?  (would make O=0, trivializing AMI)  -- expect FALSE in general
  (ii)  T(v) <= 2N  ALWAYS?  (would bound overload per-vertex by N)
  (iii) per-vertex: overloaded vertices are FEW / structured (record their count & positions).
We record the max T(v)/N over census and the multiset of (T(v)) for the worst graph."""
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

Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 10
max_ratio=(-1,None); max_over_count=(-1,None); any_T_gt_2N=0
for N in range(5,Nmax+1):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A)
        res,mc=gamma_min_cut(N,adj,edges_of(adj))
        if res is None: continue
        side,G,M=res
        if not M: continue
        Tv=uniform_Tv(N,adj,side,M)
        if Tv is None: continue
        r=Tv.max()/N
        if r>max_ratio[0]: max_ratio=(r,(N,G,round(Tv.max(),3),sorted(round(t,2) for t in Tv)))
        oc=int((Tv>N+1e-9).sum())
        if oc>max_over_count[0]: max_over_count=(oc,(N,G,oc))
        if Tv.max()>2*N+1e-9: any_T_gt_2N+=1
print(f"max T(v)/N over census N<={Nmax} = {max_ratio[0]:.4f}")
print(f"   witness (N,Gamma,maxT,sortedT) = {max_ratio[1]}")
print(f"max #overloaded vertices in one graph = {max_over_count[0]}  witness {max_over_count[1]}")
print(f"graphs with some T(v) > 2N : {any_T_gt_2N}  (0 => per-vertex overload always < N)")
