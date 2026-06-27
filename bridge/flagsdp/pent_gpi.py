"""
Cut-metric angle: TEST separability of m_phi on C5[q].
Each bad edge e=(u in V4, v in V0); geodesics pick one vertex per class 4,3,2,1,0.
Conjecture: m_phi(e) = phi[u]+phi[v] + sum_{c in 1,2,3} min_{w in V_c} phi[w].
"""
import numpy as np, random
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
    return n,adj,side,M,vid

random.seed(0)
for q in (2,3,4):
    n,adj,side,M,vid=C5q(q)
    for trial in range(3):
        phi=np.array([random.random() for _ in range(n)])
        ok=True
        for e in M:
            geos=all_shortest_geos(n,adj,side,*e)
            mphi=min(sum(phi[v] for v in P) for P in geos)
            u,v=e
            sep=phi[u]+phi[v]+sum(min(phi[vid(c,j)] for j in range(q)) for c in (1,2,3))
            if abs(mphi-sep)>1e-9:
                ok=False; print(f"q={q} edge{e}: mphi={mphi:.4f} sep={sep:.4f} MISMATCH")
        if ok: print(f"q={q} trial{trial}: m_phi SEPARABLE (product structure) CONFIRMED")
