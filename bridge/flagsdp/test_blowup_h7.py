"""Probe larger structures where uniform routing could fail: 
(1) C7[q] blowups (h=7), (2) C5[q] with unequal part sizes (asymmetric hubs),
(3) the C5[q]-peel witnesses. Track T<=K under uniform routing."""
import numpy as np
from mycielskian_check import all_shortest_geos, gamma_of, Bconnected, edges_of, maxcut_value

def load_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None,None
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T, None

def Cm_blowup(m, sizes):
    """C_m with part i of size sizes[i]; bipartite cut alternating; bad seam where parity breaks (m odd)."""
    parts=[]; off=0
    for s in sizes: parts.append(list(range(off,off+s))); off+=s
    n=off; adj=[set() for _ in range(n)]
    for i in range(m):
        for a in parts[i]:
            for b in parts[(i+1)%m]:
                adj[a].add(b); adj[b].add(a)
    return n,adj,parts

def best_cut(n,adj):
    E=edges_of(adj); mc=maxcut_value(n,E); best=None
    for mask in range(1<<(n-1)):
        c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
        if c!=mc: continue
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        G,M=gamma_of(n,adj,side)
        if G is None or not M: continue
        if best is None or G<best[1]: best=(side,G,M)
    return best

# C7[q] for small q
print("=== C7[q] blowups (h should be 7) ===")
for q in (1,2,3):
    n,adj,parts=Cm_blowup(7,[q]*7)
    r=best_cut(n,adj)
    if r is None: print(f"C7[{q}] N={n}: no valid cut"); continue
    side,G,M=r; T,_=load_uniform(n,adj,side,M)
    K=n+(n*n-G)
    print(f"C7[{q}] N={n} Gamma={G} K={K} maxT={T.max():.4f} gap={T.max()-K:.4f} (h=Gamma/beta^.5? beta={len(M)})")

print("=== C5 unequal parts (asymmetric) ===")
for sizes in [[3,1,1,1,1],[1,1,1,1,3],[2,1,1,1,2],[4,1,1,1,1],[3,2,1,1,1]]:
    n,adj,parts=Cm_blowup(5,sizes)
    r=best_cut(n,adj)
    if r is None: print(f"C5{sizes} N={n}: no valid cut"); continue
    side,G,M=r; T,_=load_uniform(n,adj,side,M)
    K=n+(n*n-G)
    print(f"C5{sizes} N={n} Gamma={G} K={K} maxT={T.max():.4f} gap={T.max()-K:.4f} beta={len(M)} argmaxT={int(T.argmax())}")
