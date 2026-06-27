import flag_engine
from mycielskian_check import gamma_min_cut, edges_of, all_shortest_geos
# Singleton 0/1-Hall: for each vertex v, sum_{e: v on ALL shortest geos of e} h_e <= K.
# Test it, and report the max LHS/K. Also: is the binding singleton a vertex whose
# 'forced bad edges' relate to CD delta_M({v}) <= delta_B({v}) = deg_B(v)?
worst=-9; row=None
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        K=N+(N*N-G)
        HG=[]
        for (u,v) in M:
            geos=all_shortest_geos(N,adj,side,u,v); HG.append((len(geos[0]),[set(P) for P in geos]))
        for v in range(N):
            lhs=sum(h for (h,Plist) in HG if all(v in P for P in Plist))  # v on all geos
            r=lhs/K
            if r>worst: worst=r; row=(N,G,K,v,lhs)
print(f"singleton 0/1-Hall: max[ sum_{{e: v on all geos}} h_e / K ] = {worst:.4f} at {row} (<=1 needed)")
