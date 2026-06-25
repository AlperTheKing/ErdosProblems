import itertools
from itertools import combinations
from collections import deque

# Test the AUTHOR'S OWN claims about the obstruction:
# (1) The 3x3 grid B with M={(0,8),(2,6)} is triangle-free, all-d4, CD-valid, satisfies bound,
#     admits NO C5-homomorphism.
# (2) The coarea inequality only delivers factor 4 (4|M| <= |B|), not factor 25.
# We verify these and probe whether there's an incompatible configuration where the
# *naive per-level CD* (e_M(S_t) <= e_B(S_t)) integrated gives the WRONG constant.

# Build 3x3 grid graph: vertices 0..8 in a 3x3 grid, edges between grid-neighbors.
def grid3():
    n=9
    adj=[[0]*n for _ in range(n)]
    def idx(r,c): return r*3+c
    for r in range(3):
        for c in range(3):
            if c<2:
                a,b=idx(r,c),idx(r,c+1); adj[a][b]=adj[b][a]=1
            if r<2:
                a,b=idx(r,c),idx(r+1,c); adj[a][b]=adj[b][a]=1
    return adj,n

Badj,n = grid3()

def bfs(Badj,n,src):
    dist=[-1]*n; dist[src]=0; q=deque([src])
    while q:
        x=q.popleft()
        for y in range(n):
            if Badj[x][y] and dist[y]<0:
                dist[y]=dist[x]+1; q.append(y)
    return dist

# bipartition of grid (2-coloring)
color=[ (r+c)%2 for r in range(3) for c in range(3)]
print("grid is bipartite, colors:", color)
# M = same-color corner diagonals: corners are 0,2,6,8 all color 0; (0,8) and (2,6)
M=[(0,8),(2,6)]
# combined graph G = B + M
adjG=[row[:] for row in Badj]
for (u,v) in M:
    adjG[u][v]=adjG[v][u]=1

def is_triangle_free(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]:
                        return False
    return True
print("G triangle-free:", is_triangle_free(adjG,n))
for (u,v) in M:
    d=bfs(Badj,n,u)
    print(f"  d_B({u},{v}) =", d[v])

# CD check: for every subset S, e_M(S,V-S) <= e_B(S,V-S)
def edges_across(adj,S,n):
    cnt=0
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v] and ((u in S)!=(v in S)):
                cnt+=1
    return cnt
cdviol=0; worst=None
for mask in range(1<<n):
    S=set(i for i in range(n) if mask&(1<<i))
    eM=0
    for (u,v) in M:
        if (u in S)!=(v in S): eM+=1
    eB=edges_across(Badj,S,n)
    if eM>eB:
        cdviol+=1
        worst=(S,eM,eB)
print("CD violations over all 2^9 subsets:", cdviol)
if worst: print("  worst:", worst)

# Bound check
print("25|M|=",25*len(M)," vs N^2=",n*n, " -> bound holds:", 25*len(M)<=n*n)

# C5-homomorphism existence: proper 5-coloring of G mapping to C5 (color i ~ i+1 mod5)
def has_C5_hom(adj,n):
    # edges of G
    E=[(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v]]
    for assign in itertools.product(range(5),repeat=n):
        ok=True
        for (u,v) in E:
            if (assign[u]-assign[v])%5 not in (1,4):
                ok=False; break
        if ok: return True
    return False
print("G admits C5-homomorphism:", has_C5_hom(adjG,n))
