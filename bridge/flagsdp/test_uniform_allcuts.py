"""Stronger test: for EVERY max cut (B-connected, finite Gamma) of each triangle-free graph,
test uniform routing T<=K. Track worst gap and per-Gamma tightness."""
import numpy as np
from itertools import combinations
from flag_engine import enumerate_graphs
from mycielskian_check import all_shortest_geos, Bconnected, edges_of, maxcut_value, gamma_of

def adjset(n,A):
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
near=[]  # (gap, N, Gamma) for gap close to 0
for N in range(5,11):
    for (n,A) in enumerate_graphs(N, triangle_free=True):
        adj=adjset(n,A); E=edges_of(adj)
        if not Bconnected: pass
        mc=maxcut_value(n,E)
        for mask in range(1<<(n-1)):
            c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
            if c!=mc: continue
            side=[(mask>>u)&1 for u in range(n)]
            if not Bconnected(n,adj,side): continue
            G,M=gamma_of(n,adj,side)
            if G is None or not M: continue
            T=load_uniform(n,adj,side,M)
            if T is None: continue
            K=n+(n*n-G); gap=T.max()-K
            checked+=1
            if gap>worst: worst=gap; nworst=(n,G,T.max(),K)
            if gap>1e-9: viol+=1
            if gap>-0.5: near.append((round(gap,4),n,G))
print(f"checked={checked} (graph,maxcut) pairs; violations: {viol}; worst gap={worst:.6f}")
print(f"  worst at {nworst}")
near.sort(reverse=True)
print(f"  tightest 12 gaps (gap,N,Gamma): {near[:12]}")
