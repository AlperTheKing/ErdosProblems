import itertools
from itertools import combinations
from collections import deque

def is_triangle_free(adj, n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]:
                        return False
    return True

def maxcut(adj, n):
    best = -1; bestX = None
    for mask in range(1<<n):
        Xs = set(i for i in range(n) if mask&(1<<i))
        cut = 0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs) != (v in Xs)):
                    cut+=1
        if cut>best:
            best=cut; bestX=Xs
    return best, bestX

def bfs(Badj, n, src):
    dist=[-1]*n; dist[src]=0; q=deque([src])
    while q:
        x=q.popleft()
        for y in range(n):
            if Badj[x][y] and dist[y]<0:
                dist[y]=dist[x]+1; q.append(y)
    return dist

def enumerate_all(n):
    edges_all = list(combinations(range(n),2))
    m=len(edges_all)
    violations=[]; checked=0; tightcount=0; maxratio=0.0
    for bits in range(1<<m):
        adj=[[0]*n for _ in range(n)]
        for i,(u,v) in enumerate(edges_all):
            if bits&(1<<i):
                adj[u][v]=adj[v][u]=1
        if not is_triangle_free(adj,n): continue
        mc, Xs = maxcut(adj,n)
        Badj=[[0]*n for _ in range(n)]
        Mlist=[]
        for (u,v) in edges_all:
            if adj[u][v]:
                if (u in Xs)!=(v in Xs):
                    Badj[u][v]=Badj[v][u]=1
                else:
                    Mlist.append((u,v))
        if not Mlist: continue
        ok=True
        for (u,v) in Mlist:
            dist=bfs(Badj,n,u)
            if dist[v]!=4:
                ok=False; break
        if not ok: continue
        checked+=1
        r = 25.0*len(Mlist)/(n*n)
        if r>maxratio: maxratio=r
        if 25*len(Mlist) > n*n:
            violations.append((bits, len(Mlist)))
        if 25*len(Mlist)==n*n:
            tightcount+=1
    return checked, violations, tightcount, maxratio

for n in range(5,8):
    checked, violations, tight, mr = enumerate_all(n)
    print(f"n={n}: all-d4 instances checked={checked}, violations={len(violations)}, tight={tight}, max(25|M|/n^2)={mr:.4f}")
    if violations:
        print("  VIOLATIONS:", violations[:5])
