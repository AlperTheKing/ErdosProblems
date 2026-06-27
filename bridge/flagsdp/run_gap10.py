import probe_int_gap as P
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of
worst_frac=0; worst_gap=0; ce=[]; cnt=0; argmax=None
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        cnt+=1
        rf,phi=P.Rfrac(N,adj,side,G,M)
        if rf>worst_frac: worst_frac=rf
        if rf>1+1e-6: ce.append((N,G,rf))
        r01,S=P.R01(N,adj,side,G,M)
        gap=rf-r01
        if gap>worst_gap:
            worst_gap=gap; argmax=(N,G,rf,r01,gap)
            print("new max gap",argmax)
print("scanned",cnt,"worst_frac",worst_frac,"worst_gap",worst_gap,"argmax",argmax)
print("CE>1:",ce)
