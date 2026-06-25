import collections
# C5[2]: blow-up of C5, each part size 2. N=10. Parts 0..4 cycle.
# Standard max cut frustrates one antipodal pair. Compute |M|,|B|, coarea sum.
n=2
parts=[[2*i,2*i+1] for i in range(5)]
N=10
edges=[]
for i in range(5):
    j=(i+1)%5
    for u in parts[i]:
        for v in parts[j]:
            edges.append((u,v))
adj=[set() for _ in range(N)]
for u,v in edges: adj[u].add(v); adj[v].add(u)
def cut(side): return sum(1 for u,v in edges if side[u]!=side[v])
best=-1; bestside=None
for mask in range(1<<N):
    side=[(mask>>i)&1 for i in range(N)]
    c=cut(side)
    if c>best: best=c; bestside=side[:]
side=bestside
B=[(u,v) for u,v in edges if side[u]!=side[v]]
M=[(u,v) for u,v in edges if side[u]==side[v]]
print("N=10 C5[2]: |E|=",len(edges)," MaxCut=",best," |B|=",len(B)," beta=|M|=",len(M))
print("25|M| =",25*len(M),"  N^2=",N*N,"  ratio",25*len(M)/(N*N))
adjB=[set() for _ in range(N)]
for u,v in B: adjB[u].add(v); adjB[v].add(u)
def bfs(src):
    d=[-1]*N; d[src]=0; q=collections.deque([src])
    while q:
        x=q.popleft()
        for y in adjB[x]:
            if d[y]<0: d[y]=d[x]+1; q.append(y)
    return d
distB=[bfs(s) for s in range(N)]
# check all bad edges d_B=4
print("bad-edge B-distances:", sorted(set(distB[u][v] for u,v in M)))
best_co=max(sum(abs(distB[r][u]-distB[r][v]) for u,v in M) for r in range(N))
print("best coarea sum over roots =",best_co,"  vs |B| =",len(B),
      " -> coarea reads", best_co,"<=",len(B))
print("So coarea gives |M|<=|B| i.e. ",len(M),"<=",len(B),"  (factor-25 NOT recovered)")
