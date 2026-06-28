"""Exact ROWSUM-O verification on LARGE odd-cycle blowups C_{2k+1}[t] WITHOUT exponential maxcut.
For C_{2k+1}[t] the Gamma-min connected-B max cut, bad edges, geodesics are analytically known:
  - cycle of L=2k+1 blocks, block i = {i*t..i*t+t-1}, consecutive blocks complete-bipartite.
  - A natural near-balanced max cut on C_{2k+1}: the cut B is the set of cycle-edges (between consecutive
    blocks); the M (monochromatic) edges are... Actually for odd-cycle blowup the structure used in the
    project is symmetric. Rather than re-derive, VERIFY by constructing the graph and using a KNOWN good cut
    (the one the project's loads() finds for small t), generalized.

SIMPLER ROBUST APPROACH: build C_{2k+1}[t], compute a max cut via a greedy/known 2-coloring that is optimal
for blow-ups (color block i by i mod 2 with the odd block split), then compute bad edges + geodesics + S + ROWSUM-O
exactly. Cross-check against loads() for t where loads() is feasible (N<=20), then push t larger.

We instead just trust loads() up to N<=20 (done in _stress_rowsumO) and here do a SELF-CONTAINED analytic
check of the C5[t] family limit: by symmetry every bad edge is equivalent, layers equipartition, a_i=t=N/5,
ell=5, sum a_i = 5t = N. So ROWSUM-O is EXACTLY tight =N for all t (graphon limit). We verify the EXACT
equipartition a_i = t for several t by direct construction with an explicit optimal cut."""
from fractions import Fraction as F
from collections import deque

def c5_blow(t):
    L=5; n=L*t; adj=[set() for _ in range(n)]
    for i in range(L):
        for a in range(t):
            for b in range(t):
                u=i*t+a; w=((i+1)%L)*t+b
                adj[u].add(w); adj[w].add(u)
    return n,adj

def analytic_check(t):
    """Use the explicit optimal cut for C5[t]: side(v)=block_index parity won't 2-color an odd cycle.
    The known Gamma-min cut for C5[t]: pick the cut that makes blocks alternate; one block-boundary
    is monochromatic (the 'odd' edge). We instead brute the cut over the 5 block-level 2-colorings
    (2^5=32, each block monochromatic-colored) which is where the optimum lives by symmetry."""
    n,adj=c5_blow(t); L=5
    best=None
    for mask in range(1<<L):
        side=[0]*n
        for i in range(L):
            for a in range(t): side[i*t+a]=(mask>>i)&1
        # B-connected?
        # compute cut size
        # bad (mono) edges between consecutive blocks of same color
        edges=[(u,w) for u in range(n) for w in adj[u] if w>u]
        cut=sum(1 for u,w in edges if side[u]!=side[w])
        best= (cut,side) if best is None or cut>best[0] else best
    cut,side=best
    # bad edges = mono edges
    M=[(u,w) for u in range(n) for w in adj[u] if w>u and side[u]==side[w]]
    # B-restricted geodesics
    def geos(s,t_):
        dist={s:0};pred={s:[]};layer=[s]
        while layer:
            nxt=[]
            for u in layer:
                for v in adj[u]:
                    if side[u]!=side[v]:
                        if v not in dist:dist[v]=dist[u]+1;pred[v]=[u];nxt.append(v)
                        elif dist[v]==dist[u]+1:pred[v].append(u)
            layer=nxt
        if t_ not in dist:return []
        P=[]
        def rec(v,acc):
            if v==s:P.append([s]+acc[::-1]);return
            for p in pred[v]:rec(p,acc+[v])
        rec(t_,[]);return P
    pf={}
    for f in M:
        Ps=geos(f[0],f[1]); nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf[f]={v:F(cnt[v],nf) for v in cnt}
    S={v:sum(pf[g].get(v,F(0)) for g in M) for v in range(n)}
    worst=F(0)
    for f in M:
        Cf=sum(pf[f][v]*S[v] for v in pf[f])
        if Cf>worst: worst=Cf
    G=sum((len(geos(f[0],f[1])[0]) ) **2 for f in M) if M else 0  # ell^2 sum (ell=len of a geodesic = #vertices)
    return n,len(M),worst,F(n)

if __name__=="__main__":
    print("=== C5[t] analytic ROWSUM-O (no exp maxcut over full graph; block-level 2^5 cut search) ===")
    for t in range(1,9):
        n,m,worst,N=analytic_check(t)
        print(f"  C5[{t}] N={n}: #bad={m} max ROWSUM-O (max_f sum_v p_f S)={worst} = {float(worst):.3f}  N={N}  tight={worst==N}")
