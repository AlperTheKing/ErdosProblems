"""
Does CD (delta_M(S) <= delta_B(S) for ALL S) imply the 0/1 cut-Hall
   sum_e h_e * min_P |P cap S| <= K |S|,  K=N+(N^2-Gamma) ?
And more sharply: is the GPI's worst phi explained by CD?

We test, on census band-max graphs, the 0/1 Hall directly, and also a candidate
'CD-charged' bound: for a vertex set S, each bad edge e with both endpoints' B-geodesics
forced to cross S contributes. Compare LHS sum_e h_e min_P|P cap S| to K|S| and to the
CD-quantity sum_S? We just empirically locate the binding S and see its relation to a max-cut shore.
"""
import numpy as np, itertools
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
import flag_engine

def he_geos(N,adj,side,M):
    out=[]
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v); out.append((len(geos[0]),[set(P) for P in geos]))
    return out

def deltaM_deltaB(N,adj,side,M,S):
    Sset=set(S)
    dM=sum(1 for (u,v) in M if ((u in Sset)!=(v in Sset)))
    dB=sum(1 for u in range(N) for v in adj[u] if v>u and side[u]!=side[v] and ((u in Sset)!=(v in Sset)))
    return dM,dB

if __name__=="__main__":
    worst=0; worstinfo=None
    cdviol=0
    for N in range(5,11):
        for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
            adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
            E=edges_of(adj)
            res,mc=gamma_min_cut(N,adj,E)
            if res is None: continue
            side,G,M=res
            if not M: continue
            K=N+(N*N-G)
            HG=he_geos(N,adj,side,M)
            # CD check (since it's a max cut it must hold; verify)
            for mask in range(1,1<<N):
                S=[v for v in range(N) if (mask>>v)&1]
                dM,dB=deltaM_deltaB(N,adj,side,M,S)
                if dM>dB: cdviol+=1
            # 0/1 Hall worst ratio
            for mask in range(1,1<<N):
                S=set(v for v in range(N) if (mask>>v)&1); s=len(S)
                tot=sum(h*min(len(P&S) for P in Plist) for (h,Plist) in HG)
                r=tot/(K*s)
                if r>worst:
                    worst=r; worstinfo=(N,G,K,s,r,sorted(S))
    print(f"CD violations across census (should be 0): {cdviol}")
    print(f"worst 0/1 Hall ratio = {worst:.6f}  info(N,G,K,|S|,ratio,S)={worstinfo}")
