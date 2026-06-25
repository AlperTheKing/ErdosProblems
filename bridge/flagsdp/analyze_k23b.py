import numpy as np
from collections import deque, Counter
import verify_D25_lemma16 as L

N, A = L.gpt_k23()
adj = L.adjset(N, A)
edges = [frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
mc, side = L.maxcut(N, adj)
tau = len(edges)-mc
sigs = L.min_signatures(N, adj, edges, tau)

# For Gamma: for EACH min signature S, compute B=K-S, d_B(e) for e in S, Gamma_S = sum (d_B+1)^2
def dB_pair(u,v,Bset,adjlist):
    dist=[-1]*N; dist[u]=0; q=deque([u])
    while q:
        x=q.popleft()
        for y in adjlist[x]:
            if dist[y]<0: dist[y]=dist[x]+1; q.append(y)
    return dist[v]

gammas=[]
for S in sigs:
    Bset=set(edges)-set(S)
    adjB=[[] for _ in range(N)]
    for e in Bset:
        a,b=tuple(e); adjB[a].append(b); adjB[b].append(a)
    g=0; ds=[]
    ok=True
    for e in S:
        u,v=tuple(e); d=dB_pair(u,v,Bset,adjB)
        if d<0: ok=False; break
        ds.append(d); g+=(d+1)**2
    if ok: gammas.append((g,tuple(sorted(ds))))
gammas.sort()
print(f"N^2={N*N}, 25*tau={25*tau}")
print(f"min Gamma over sigs = {gammas[0][0]} with dB profile {gammas[0][1]}")
print(f"max Gamma over sigs = {gammas[-1][0]} with dB profile {gammas[-1][1]}")
gc=Counter(g for g,_ in gammas)
print("Gamma distribution:", dict(sorted(gc.items())))
# So is Gamma<=N^2 for the MIN-gamma signature? all of them?
print(f"all sigs Gamma <= N^2={N*N}: {all(g<=N*N for g,_ in gammas)}")
