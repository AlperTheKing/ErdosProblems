import sys, numpy as np, itertools
sys.path.insert(0,'.')
from pent_ratio import rho_star, best01
from mycielskian_check import gamma_min_cut, edges_of
from flag_engine import enumerate_graphs
N=10; total=0; gap=0; checked=0
import time; t0=time.time()
for nn,A in enumerate_graphs(N, triangle_free=True):
    if time.time()-t0>500: print("TIMEBOX hit at",checked,"graphs"); break
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    total+=1; checked+=1; K=N+N*N-Gam
    rho,phi=rho_star(N,adj,side,M); b01=best01(N,adj,side,M)
    if rho>b01+1e-6:
        gap+=1; print("GAP",sorted(E),"rho",rho,"b01",b01,"K",K)
print(f"N=10 (partial {checked}): fractional-beats-01 in {gap} graphs")
