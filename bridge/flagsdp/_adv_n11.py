import sys, numpy as np, time
sys.path.insert(0,'.')
from mycielskian_check import gamma_min_cut, edges_of
from flag_engine import enumerate_graphs
from pent_ratio import rho_star, best01

N=11
viol=0; total=0; minslack_pos=1.0; gapcount=0; t0=time.time()
worst_gap=(0,)
for nn,A in enumerate_graphs(N, triangle_free=True):
    if time.time()-t0>560: print("timebox at",total); break
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    total+=1; K=N+N*N-Gam
    rho,phi=rho_star(N,adj,side,M)
    if rho>K+1e-6: viol+=1
    sl=(K-rho)/K
    if N*N-Gam>0: minslack_pos=min(minslack_pos,sl)
    b01=best01(N,adj,side,M)
    if rho>b01+1e-6:
        gapcount+=1
        if rho-b01>worst_gap[0]: worst_gap=(rho-b01,rho,b01,Gam)
print(f"N=11: scanned {total} graphs; GPI(rho*<=K) violations={viol}")
print(f"  frac-beats-0/1 graphs={gapcount}; worst (gap,rho,b01,Gamma)={worst_gap}")
print(f"  min normalized slack among deficit>0 = {minslack_pos:.5f}")
