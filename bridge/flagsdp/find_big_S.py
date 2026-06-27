import numpy as np
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs
def best_01_full(N, geos, he):
    best=-1; ties=[]
    for k in range(1,N+1):
        for S in combinations(range(N),k):
            Sset=set(S)
            num=sum(he[e]*min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(geos)))
            val=num/k
            if val>best+1e-9: best=val; ties=[(k,S)]
            elif abs(val-best)<1e-9: ties.append((k,S))
    return best,ties
N=8
for (n,A) in enumerate_graphs(N,triangle_free=True):
    adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
    res,mc=gamma_min_cut(n,adj,edges_of(adj))
    if not res: continue
    side,G,M=res
    if not M: continue
    geos=[all_shortest_geos(n,adj,side,u,v) for (u,v) in M]
    he=[len(g[0]) for g in geos]
    b,ties=best_01_full(n,geos,he)
    minsz=min(k for k,_ in ties)
    if minsz>=2:
        K=n+n*n-G
        S=[S for k,S in ties if k==minsz][0]
        print("g6/struct: N=%d beta=%d Gam=%d K=%d  R_01=%.3f  min optimal |S|=%d  S=%s sides=%s"%(
            n,len(M),G,K,b,minsz,S,[side[v] for v in S]))
        print("   side=%s  M=%s  he=%s"%(side,M,he))
