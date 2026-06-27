"""Test the UNIFORM routing x_{e,P}=1/|P_e| against K=N+(N^2-Gamma) on the
full triangle-free connected-B census via gamma_min_cut (matches lp_vload setup)."""
import numpy as np
from flag_engine import enumerate_graphs, edges_of as fe_edges
from mycielskian_check import gamma_min_cut, all_shortest_geos, Bconnected, edges_of

def adjset_from_A(n,A):
    adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (A[i]>>j)&1: adj[i].add(j)
    return adj

def load_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T

worst=-1e9; nworst=None; checked=0; viol=0
for N in range(5,12):
    for (n,A) in enumerate_graphs(N, triangle_free=True):
        adj=adjset_from_A(n,A)
        E=edges_of(adj)
        res,mc=gamma_min_cut(n,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        T=load_uniform(n,adj,side,M)
        if T is None: continue
        K=n+(n*n-G)
        gap=T.max()-K
        checked+=1
        if gap>worst: worst=gap; nworst=(n,G,T.max(),K,A)
        if gap>1e-9: viol+=1
print(f"checked={checked} routings; uniform-routing violations of T<=K: {viol}")
n,G,Tm,K,A=nworst
print(f"  WORST gap=maxT-K = {worst:.6f} at N={n} Gamma={G} maxT={Tm:.4f} K={K}")
print(f"  edges={fe_edges(n,A)}")
