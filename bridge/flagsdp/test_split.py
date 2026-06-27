"""Decompose T_unif(w)=E(w)+I(w): endpoint load E(w)=sum_{e~w} h_e, interior I(w).
Test a candidate provable bound. On C5[q] all w have E=N? Let's see, and test
the cut-Hall consequence E(w)=sum_{e~w}h_e <= K (singleton-toll GPI, a NECESSARY cond)."""
import numpy as np
from flag_engine import enumerate_graphs
from mycielskian_check import all_shortest_geos, Bconnected, edges_of, maxcut_value, gamma_of
def adjset(n,A):
    adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (A[i]>>j)&1: adj[i].add(j)
    return adj
def split(N,adj,side,M):
    E=np.zeros(N); I=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v); g=len(geos); h=len(geos[0])
        cnt=np.zeros(N)
        for P in geos:
            for x in P: cnt[x]+=1
        for x in range(N):
            if cnt[x]==0: continue
            frac=cnt[x]/g
            if x==u or x==v: E[x]+=h*frac  # frac=1
            else: I[x]+=h*frac
    return E,I
# C5[q]
def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]
    return n,adj,side,M
for q in (2,3):
    n,adj,side,M=C5q(q); E,I=split(n,adj,side,M)
    print(f"C5[{q}] N={n}: E(per layer V0..V4)=", [round(E[i*q],3) for i in range(5)], "I=",[round(I[i*q],3) for i in range(5)])
# census: does endpoint-load E(w) ever exceed K? (singleton GPI necessary cond)
viol=0; worstE=-1; cnt=0
for N in range(5,10):
    for (n,A) in enumerate_graphs(N,triangle_free=True):
        adj=adjset(n,A); Ee=edges_of(adj); mc=maxcut_value(n,Ee)
        for mask in range(1<<(n-1)):
            c=sum(1 for (u,v) in Ee if ((mask>>u)&1)!=((mask>>v)&1))
            if c!=mc: continue
            side=[(mask>>u)&1 for u in range(n)]
            if not Bconnected(n,adj,side): continue
            G,M=gamma_of(n,adj,side)
            if G is None or not M: continue
            E,I=split(n,adj,side,M); K=n+(n*n-G); cnt+=1
            r=E.max()/K
            if r>worstE: worstE=r
            if E.max()>K+1e-9: viol+=1
print(f"endpoint-only E(w)<=K: checked={cnt} viol={viol} worst E.max/K={worstE:.4f}")
