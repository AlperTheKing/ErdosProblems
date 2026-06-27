import numpy as np, itertools
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
def C5q_unequal(sizes):
    parts=[]; off=0
    for s in sizes: parts.append(list(range(off,off+s))); off+=s
    n=off; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i+1)%5]:
                adj[a].add(b); adj[b].add(a)
    return n,adj
rows=[]
for sizes in itertools.product(range(1,6),repeat=5):
    if not (6<=sum(sizes)<=14): continue
    if sizes!=tuple(sorted(sizes)): continue
    if len(set(sizes))==1: continue  # skip equal (extremal)
    n,adj=C5q_unequal(sizes)
    r=best_cut(n,adj)
    if r is None: continue
    side,G,M=r; T=load_uniform(n,adj,side,M)
    if T is None: continue
    K=n+(n*n-G); rows.append((T.max()/K, sizes, n, G, K, round(float(T.max()),3)))
rows.sort(reverse=True)
print("top non-equal unequal-C5 ratios maxT/K:")
for r in rows[:8]: print("  ", round(r[0],4), r[1:])
print("any >=1?", any(r[0]>1+1e-9 for r in rows))
