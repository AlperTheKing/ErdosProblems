"""Examine the N=10 graph where fractional toll beats 0/1, to characterize the biased-pentagonal failure."""
import sys, numpy as np
sys.path.insert(0,'.')
from pent_ratio import rho_star, best01
from mycielskian_check import gamma_min_cut, edges_of, all_shortest_geos

N=10
E=[(0,4),(0,6),(1,5),(1,7),(1,9),(2,6),(2,7),(2,8),(3,7),(3,8),(3,9),(4,8),(4,9),(5,8),(6,9)]
adj=[set() for _ in range(N)]
for u,v in E: adj[u].add(v); adj[v].add(u)
r,mc=gamma_min_cut(N,adj,edges_of(adj))
side,Gam,M=r; K=N+N*N-Gam
print(f"Gamma={Gam} K={K} beta={len(M)} maxcut={mc}")
print("bad edges M:",M)
he={e:len(all_shortest_geos(N,adj,side,*e)[0]) for e in M}
print("h_e:",he)
rho,phi=rho_star(N,adj,side,M)
print(f"rho*(frac)={rho:.4f}  best01={best01(N,adj,side,M):.4f}")
print("fractional maximizer phi*:",phi.round(4).tolist())
print("nonzero phi* support:",[(v,round(phi[v],4)) for v in range(N) if phi[v]>1e-7])
# show the geodesic structure of each bad edge restricted to phi-support
for e in M:
    geos=all_shortest_geos(N,adj,side,*e)
    cheap=min(sum(phi[v] for v in P) for P in geos)
    print(f"  edge {e}: h={he[e]} #geos={len(geos)} min toll-cost={cheap:.4f}")
