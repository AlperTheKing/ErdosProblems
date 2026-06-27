import numpy as np
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos
def to_setadj(n,A): return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]
# Does every bad edge have a shortest B-geodesic (so uniform routing is well-defined)? And re-verify 2O<=U
# with full slack distribution, plus min U/O over genuine-overload graphs (strategy claims 4.5).
tot=0; no_geo=0; worst=1e9; ratios=[]
for N in range(5,11):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A); res,mc=gamma_min_cut(N,adj,edges_of(adj))
        if res is None: continue
        side,G,M=res
        if not M: continue
        Tv=np.zeros(N); ok=True
        for (u,v) in M:
            g=all_shortest_geos(N,adj,side,u,v)
            if not g: ok=False; break
            h=len(g[0])
            for P in g:
                for x in P: Tv[x]+=h/len(g)
        if not ok: no_geo+=1; continue
        tot+=1
        O=np.maximum(0,Tv-N).sum(); U=np.maximum(0,N-Tv).sum()
        worst=min(worst,U-2*O)
        if O>1e-6: ratios.append(U/O)
print("census N<=10: routable graphs=%d, bad-edge-without-geodesic graphs=%d"%(tot,no_geo))
print("min (U-2O)=%.6f (AMI holds iff >=0); min U/O over O>0 graphs = %.4f (strategy claimed 4.5)"%(worst, min(ratios) if ratios else float('nan')))
