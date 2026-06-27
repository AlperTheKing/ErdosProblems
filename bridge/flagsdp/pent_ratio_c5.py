"""Run the rho* (fractional) vs best-0/1 test on the TIGHT extremal C5[q] and a few named graphs."""
import sys, numpy as np
sys.path.insert(0,'.')
from pent_ratio import rho_star, best01
from mycielskian_check import all_shortest_geos

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]; G=25*len(M)
    return n,adj,side,G,M

for q in (2,3):
    n,adj,side,G,M=C5q(q); K=n+n*n-G
    rho,phi=rho_star(n,adj,side,M); b01=best01(n,adj,side,M)
    print(f"C5[{q}]: N={n} Gamma={G} K={K}  rho*(frac)={rho:.5f} best01={b01:.5f} "
          f"frac>01? {rho>b01+1e-6}  rho*<=K? {rho<=K+1e-6}")
    nz=phi[phi>1e-7]
    is_cut = nz.size>0 and (nz.max()-nz.min())<1e-6*max(1,nz.max())
    print(f"   rho* maximizer phi* is scaled-cut(0/1)? {is_cut}  distinct levels={sorted(set(round(x,4) for x in nz))[:8]}")
