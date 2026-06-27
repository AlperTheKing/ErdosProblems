"""Stress the uniform routing on engineered larger graphs that mix near-extremal C5[q]
cores with asymmetry: 
 (A) C5[q] with one extra apex-like vertex joined to a full part (creates a hub),
 (B) two C5 sharing an edge/vertex,
 (C) C5[q] union C5[q'] glued on a shared part.
Use a fixed reasonable cut (the natural C5 5-coloring) rather than brute max-cut search."""
import numpy as np
from mycielskian_check import all_shortest_geos, gamma_of, Bconnected, edges_of, maxcut_value

def load_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T

def best_cut(n,adj,cap=None):
    E=edges_of(adj); mc=maxcut_value(n,E); best=None
    rng=range(1<<(n-1))
    for mask in rng:
        c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
        if c!=mc: continue
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        G,M=gamma_of(n,adj,side)
        if G is None or not M: continue
        if best is None or G<best[1]: best=(side,G,M)
    return best

def C5q_unequal(sizes):
    parts=[]; off=0
    for s in sizes: parts.append(list(range(off,off+s))); off+=s
    n=off; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i+1)%5]:
                adj[a].add(b); adj[b].add(a)
    return n,adj,parts

# Unequal C5 blowups: these have Gamma<N^2 so are genuine non-extremal but C5-like
print("=== unequal C5[sizes] (brute best cut) ===")
import itertools
worst=(-9,None)
for sizes in itertools.product(range(1,5),repeat=5):
    if sum(sizes)>13 or sum(sizes)<6: continue
    if sizes!=tuple(sorted(sizes)): continue  # dedupe rotations partially
    n,adj,parts=C5q_unequal(sizes)
    if n>13: continue
    r=best_cut(n,adj)
    if r is None: continue
    side,G,M=r; T=load_uniform(n,adj,side,M)
    if T is None: continue
    K=n+(n*n-G); ratio=T.max()/K
    if ratio>worst[0]: worst=(ratio,(sizes,n,G,K,round(T.max(),3)))
    if T.max()-K>1e-9:
        print(f"  VIOLATION sizes={sizes} N={n} G={G} K={K} maxT={T.max():.4f}")
print(f"  worst ratio among unequal C5 blowups: {worst[0]:.4f} at {worst[1]}")
