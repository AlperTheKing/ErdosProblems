import numpy as np
from collections import deque
import verify_D25_lemma16 as L

N, A = L.gpt_k23()
adj = L.adjset(N, A)
edges = [frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
mc, side = L.maxcut(N, adj)
tau = len(edges)-mc
print(f"N={N} tau={tau} #edges={len(edges)} maxcut={mc} side={side}")
# bad edges of this max cut
M0 = [e for e in edges if side[min(e)]==side[max(e)]]
print(f"M0 (bad edges this cut), |M0|={len(M0)}: {[tuple(sorted(e)) for e in M0]}")
B0 = [e for e in edges if side[min(e)]!=side[max(e)]]
# d_B between endpoints of each bad edge
def dB(u,v,Bset):
    adjB=[[] for _ in range(N)]
    for e in Bset:
        a,b=tuple(e); adjB[a].append(b); adjB[b].append(a)
    dist=[-1]*N; dist[u]=0; q=deque([u])
    while q:
        x=q.popleft()
        for y in adjB[x]:
            if dist[y]<0: dist[y]=dist[x]+1; q.append(y)
    return dist[v]
Bset=set(B0)
for e in M0:
    u,v=tuple(e); print(f"  bad {u}-{v}: d_B={dB(u,v,Bset)}")
# all minimum signatures
sigs = L.min_signatures(N, adj, edges, tau)
print(f"#min signatures = {len(sigs)}")
# how many distinct edges appear across signatures
allsigedges=set()
for s in sigs: allsigedges|=set(s)
print(f"distinct edges in some min sig = {len(allsigedges)} of {len(edges)}")
# odd cycles & their lengths
cyc = L.all_odd_cycles_v(N, adj)
from collections import Counter
print("odd cycle length dist:", Counter(len(c) for c in cyc))
