import numpy as np
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
    return n,adj,side,G,M,vid

for q in (2,3,4):
    n,adj,side,G,M,vid=C5q(q); N=n
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    print(f"C5[{q}] N={N} K=N+(N^2-G)={N+(N*N-G)}: load min={T.min():.3f} max={T.max():.3f} (uniform 1/n_geo routing)")
    # per-layer loads
    for i in range(5):
        verts=[vid(i,j) for j in range(q)]
        print(f"   layer V{i}: loads {[round(T[x],3) for x in verts]}")
