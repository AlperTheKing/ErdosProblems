from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs
def V1_all(N,adj,side,M):
    geos=[]; he=[]
    for (u,v) in M:
        gs=all_shortest_geos(N,adj,side,u,v); geos.append(gs); he.append(len(gs[0]))
    forced=[set.intersection(*[set(P) for P in gs]) if gs else set() for gs in geos]
    V1=[0]*N
    for e in range(len(M)):
        for w in forced[e]: V1[w]+=he[e]
    return V1
worst_ratio=0; viol=0
for N in range(5,10):
    for (n,A) in enumerate_graphs(N,triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        res,mc=gamma_min_cut(n,adj,edges_of(adj))
        if not res: continue
        side,G,M=res
        if not M: continue
        V1=V1_all(n,adj,side,M); K=n+n*n-G
        r=max(V1)/K
        if r>worst_ratio: worst_ratio=r
        if max(V1)>K+1e-9: viol+=1
print("max_w V1(w)/K over census N<=9 = %.4f ; violations(V1>K) = %d"%(worst_ratio,viol))
