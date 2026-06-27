"""Search census for graphs/cuts with high Gamma/N^2 (near the extremal boundary where K->N).
Report uniform-routing slack ratio maxT/K there -- this is where the bound is tight."""
import numpy as np
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

rows=[]
for N in range(5,11):
    for (n,A) in enumerate_graphs(N, triangle_free=True):
        adj=adjset(n,A); E=edges_of(adj); mc=maxcut_value(n,E)
        seen=set()
        for mask in range(1<<(n-1)):
            c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
            if c!=mc: continue
            side=tuple((mask>>u)&1 for u in range(n))
            if not Bconnected(n,adj,list(side)): continue
            G,M=gamma_of(n,adj,list(side))
            if G is None or not M: continue
            T=load_uniform(n,adj,list(side),M)
            if T is None: continue
            K=n+(n*n-G)
            ratio=T.max()/K
            rows.append((G/(n*n), ratio, n, G, round(T.max(),3), K))
# top by Gamma/N^2 (excluding exact 1.0 = C5q) then by ratio
rows.sort(key=lambda r:(-r[0], -r[1]))
print("Highest Gamma/N^2 (gamma_ratio, maxT/K, N, Gamma, maxT, K):")
nonext=[r for r in rows if r[0]<0.999]
for r in rows[:6]: print("  ext/near:",[round(x,4) if isinstance(x,float) else x for x in r])
print("Highest maxT/K among NON-extremal (Gamma<N^2):")
nonext.sort(key=lambda r:-r[1])
for r in nonext[:8]: print("  ",[round(x,4) if isinstance(x,float) else x for x in r])
