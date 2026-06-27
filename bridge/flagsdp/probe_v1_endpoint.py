from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs
def analyze(N,adj,side,M):
    geos=[]; he=[]
    for (u,v) in M:
        gs=all_shortest_geos(N,adj,side,u,v); geos.append(gs); he.append(len(gs[0]))
    forced=[set.intersection(*[set(P) for P in gs]) if gs else set() for gs in geos]
    V1=[0]*N; V1ep=[0]*N
    for e,(u,v) in enumerate(M):
        for w in forced[e]: V1[w]+=he[e]
        V1ep[u]+=he[e]; V1ep[v]+=he[e]
    return V1,V1ep
interior_forcing=0; tot=0
for N in range(5,10):
    for (n,A) in enumerate_graphs(N,triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        res,mc=gamma_min_cut(n,adj,edges_of(adj))
        if not res: continue
        side,G,M=res
        if not M: continue
        V1,V1ep=analyze(n,adj,side,M)
        tot+=1
        if any(V1[w]>V1ep[w]+1e-9 for w in range(n)): interior_forcing+=1
print("graphs where some vertex has INTERIOR forcing (V1>endpoint-only): %d/%d"%(interior_forcing,tot))
