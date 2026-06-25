import numpy as np
from collections import deque, Counter
import flag_engine as fe
import verify_D25_lemma16 as L
from exp_lemma16_atoms import is_2connected, tau_of, is_edge_critical

def dB_pair(N,u,v,adjB):
    dist=[-1]*N; dist[u]=0; q=deque([u])
    while q:
        x=q.popleft()
        for y in adjB[x]:
            if dist[y]<0: dist[y]=dist[x]+1; q.append(y)
    return dist[v]

def min_gamma(N,A):
    adj=L.adjset(N,A); edges=[frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
    mc,side=L.maxcut(N,adj); tau=len(edges)-mc
    if tau==0: return None
    sigs=L.min_signatures(N,adj,edges,tau)
    best=None
    for S in sigs:
        Bset=set(edges)-set(S)
        adjB=[[] for _ in range(N)]
        for e in Bset:
            a,b=tuple(e); adjB[a].append(b); adjB[b].append(a)
        g=0; ok=True
        for e in S:
            u,v=tuple(e); d=dB_pair(N,u,v,adjB)
            if d<0: ok=False; break
            g+=(d+1)**2
        if ok and (best is None or g<best): best=g
    return (best,tau,N)

worst_ratio=0; worst=None; total=0; viol=0
nearest=[]
for N in [5,6,7,8,9]:
    states=fe.enumerate_graphs(N,triangle_free=True)
    for (n,A) in states:
        adj=L.adjset(n,A)
        if not is_2connected(n,adj): continue
        tau=tau_of(n,adj)
        if tau==0: continue
        if not is_edge_critical(n,A,adj,tau): continue
        r=min_gamma(n,A)
        if r is None: continue
        g,t,nn=r; total+=1
        ratio=g/(nn*nn)
        if g>nn*nn+1e-9: viol+=1
        nearest.append((ratio,g,nn,t))
        if ratio>worst_ratio: worst_ratio=ratio; worst=(g,nn,t)
nearest.sort(reverse=True)
print(f"total atoms={total}, Gamma>N^2 violations={viol}, worst Gamma/N^2={worst_ratio:.4f} at {worst}")
print("top 8 nearest-tight (ratio,Gamma,N,tau):")
for x in nearest[:8]: print("  ",x)
