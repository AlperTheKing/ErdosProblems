# Adversarial: is the rho*-maximizer ALWAYS in the "pentagonal hat" cone?
# A 'hat' per the strategy is supported on a single B-geodesic with profile 1,2,...,2,1 (symmetric),
# normalized e.g. (1/4,1/2,1/4) for h=... Actually for the C5-tight facet it's 3 vertices (1,2,1)/4.
# The honest checkable question: at the N=10 worst graph, what is the support/profile of phi*,
# and does it match a hat on a SHARED geodesic of two bad edges?
import sys, numpy as np
sys.path.insert(0,'.')
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs
from pent_ratio import rho_star, best01

N=10
recs=[]
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    rho,phi=rho_star(N,adj,side,M)
    b01=best01(N,adj,side,M)
    if rho>b01+1e-6:
        nz={i:round(float(phi[i]),4) for i in range(N) if phi[i]>1e-7}
        # find geodesics covering the support
        supp=set(nz)
        covering=[]
        for e in M:
            for P in all_shortest_geos(N,adj,side,*e):
                if supp & set(P):
                    covering.append((e,tuple(P), tuple(round(float(phi[v]),3) for v in P)))
        recs.append((Gam,rho,b01,nz,covering))
print(f"N=10: {len(recs)} graphs where fractional strictly beats 0/1")
for Gam,rho,b01,nz,cov in recs[:3]:
    print(f"\n Gamma={Gam} rho*={rho} best01={b01}")
    print(f"   phi* support+levels: {nz}")
    print(f"   distinct nonzero levels: {sorted(set(nz.values()))}")
    # check profile: is it (1/4,1/2,1/4)-like = ratio 1:2:1 ?
    vals=sorted(nz.values())
    print(f"   #support={len(nz)}")
