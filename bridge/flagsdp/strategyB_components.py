"""STRATEGY B: per-B-component decomposition of Gamma.
Each bad edge uv lies within ONE B-component (u,v same component since d_B(u,v)<inf).
Let components be K_1..K_p with vertex sets of size n_1..n_p (sum n_j = N, DISJOINT).
Gamma = sum_j Gamma_j where Gamma_j = sum_{uv in M, uv in K_j} ell^2.

CONJECTURE (per-component): Gamma_j <= n_j^2  for each B-component K_j.
Then Gamma = sum Gamma_j <= sum n_j^2 <= (sum n_j)^2 = N^2.  (since n_j>=0, sum of squares <= square of sum)
This would be a CLEAN reduction: prove the bound on a graph whose B is CONNECTED.

Test: does Gamma_j <= n_j^2 hold per B-component?
"""
import verify_D25_lemma16 as L
from collections import deque
import flag_engine as fe

def adjset(n,A): return [set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]

def maxcut(n,adj):
    best=-1; bs=None
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; bs=side
    return best,bs

def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def bdist(n,adjB,src):
    d=[-1]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if d[w]<0: d[w]=d[u]+1; q.append(w)
    return d

def check_cut(n,adj,side):
    E=[(u,v) for u in range(n) for v in adj[u] if v>u]
    M=[(u,v) for (u,v) in E if side[u]==side[v]]
    adjB=[set() for _ in range(n)]
    for (u,v) in E:
        if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
    # B-components
    comp=[-1]*n; nc=0
    for s in range(n):
        if comp[s]<0:
            comp[s]=nc; q=deque([s])
            while q:
                u=q.popleft()
                for w in adjB[u]:
                    if comp[w]<0: comp[w]=nc; q.append(w)
            nc+=1
    csize=[0]*nc
    for x in range(n): csize[comp[x]]+=1
    GammaC=[0]*nc
    ok=True
    for (u,v) in M:
        d=bdist(n,adjB,u)[v]
        if d<4 or d%2: return None  # structural fail for this cut
        GammaC[comp[u]] += (d+1)**2
    # check per-component
    worst=0.0; viol=False
    for j in range(nc):
        if csize[j]>0:
            r=GammaC[j]/(csize[j]**2)
            worst=max(worst,r)
            if GammaC[j]>csize[j]**2+1e-9: viol=True
    return worst, viol, sum(GammaC), sum(s*s for s in csize)

def sweep(N):
    states=fe.enumerate_graphs(N, triangle_free=True)
    worst=0.0; viol=0; tested=0; sumsq_viol=0
    for (n,A) in states:
        adj=adjset(n,A)
        E=[(u,v) for u in range(n) for v in adj[u] if v>u]
        if not E: continue
        mc,cuts=all_maxcuts(n,adj)
        # pick the cut that MINIMIZES worst per-comp ratio (some max cut)
        best=None
        for side in cuts:
            r=check_cut(n,adj,side)
            if r is None: continue
            if best is None or r[0]<best[0]: best=r
        if best is None: continue
        tested+=1
        worst=max(worst,best[0])
        if best[1]: viol+=1
        if best[2]>best[3]+1e-9: sumsq_viol+=1
    print(f"N={N}: tested={tested} worst per-comp Gamma_j/n_j^2={worst:.4f} per-comp VIOL={viol} Gamma>sum n_j^2 VIOL={sumsq_viol}",flush=True)

if __name__=="__main__":
    # named
    for name,(N,A) in [("C5",L.c5()),("C5[2]",L.c5n(2)),("C5[3]",L.c5n(3)),("Petersen",L.petersen()),("K23-N13",L.gpt_k23())]:
        adj=adjset(N,A); mc,cuts=all_maxcuts(N,adj)
        best=None
        for side in cuts:
            r=check_cut(N,adj,side)
            if r and (best is None or r[0]<best[0]): best=r
        print(f"{name:10s} N={N} worst Gamma_j/n_j^2={best[0]:.4f} viol={best[1]} Gamma={best[2]} sum n_j^2={best[3]}")
    for N in [5,6,7,8,9]:
        sweep(N)
    print("DONE")
