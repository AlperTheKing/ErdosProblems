from itertools import combinations
from collections import deque

# Test the author's coarea/discharging claims directly on the grid counterexample
# and on C5[2], to see WHICH constant the per-level CD foliation actually yields.
#
# Author claims:
#  - sum_t e_M(S_t) >= 4|M| (each d4 edge crosses 4 boundaries) -- "TRUE and easy"
#  - per level: e_M(S_t) <= e_B(S_t) (CD)
#  - => 4|M| <= sum_t e_B(S_t). With |phi-drop|<=1 this is 4|M| <= |B|  (FACTOR 4)
#  - factor 25 NOT delivered.
# We verify on concrete instances that the foliation bound is indeed only factor 4,
# and check whether |B| can be as small as ~25|M|/... i.e. whether 4|M|<=|B| is loose.

def bfs(Badj,n,src):
    dist=[-1]*n; dist[src]=0; q=deque([src])
    while q:
        x=q.popleft()
        for y in range(n):
            if Badj[x][y] and dist[y]<0:
                dist[y]=dist[x]+1;q.append(y)
    return dist

def analyze(name, Badj, M, n):
    nB=sum(1 for u in range(n) for v in range(u+1,n) if Badj[u][v])
    print(f"--- {name}: N={n}, |M|={len(M)}, |B|={nB}")
    print(f"    factor-4 coarea bound: 4|M|={4*len(M)} <= |B|={nB} ? {4*len(M)<=nB}")
    print(f"    if it were factor-25: 25|M|={25*len(M)} <= ??? ; N^2={n*n}")
    # foliation from a base vertex: phi = d_B(base, .)
    # pick base = an endpoint of first bad edge
    base=M[0][0]
    phi=bfs(Badj,n,base)
    maxd=max(d for d in phi if d>=0)
    # sub-level sets S_t = {v: phi[v] <= t}
    total_eM=0; total_eB=0
    for t in range(maxd+1):
        S=set(v for v in range(n) if 0<=phi[v]<=t)
        eM=sum(1 for (u,v) in M if (u in S)!=(v in S))
        eB=sum(1 for u in range(n) for v in range(u+1,n) if Badj[u][v] and ((u in S)!=(v in S)))
        # CD must hold per level
        flag="" if eM<=eB else "  <-- CD VIOLATED!"
        total_eM+=eM; total_eB+=eB
    print(f"    sum_t e_M(S_t)={total_eM}, sum_t e_B(S_t)={total_eB}; CD-per-level sum holds: {total_eM<=total_eB}")

# grid3 + M={(0,8),(2,6)}
def grid3():
    n=9; adj=[[0]*n for _ in range(n)]
    def idx(r,c): return r*3+c
    for r in range(3):
        for c in range(3):
            if c<2: a,b=idx(r,c),idx(r,c+1); adj[a][b]=adj[b][a]=1
            if r<2: a,b=idx(r,c),idx(r+1,c); adj[a][b]=adj[b][a]=1
    return adj,n
Bg,ng=grid3()
analyze("3x3 grid", Bg, [(0,8),(2,6)], ng)

# C5[2]: blow-up of C5 with parts of size 2. Vertices: 5 groups x2 = 10.
# C5 cycle 0-1-2-3-4-0. Blow-up: complete bipartite between adjacent groups.
def c5blow(k):
    n=5*k
    adj=[[0]*n for _ in range(n)]
    def grp(g,i): return g*k+i
    for g in range(5):
        h=(g+1)%5
        for i in range(k):
            for j in range(k):
                a,b=grp(g,i),grp(h,j); adj[a][b]=adj[b][a]=1
    return adj,n
# max cut of C5[k]: it's the bad edges that are monochromatic. Known beta=k^2.
# We need the MAX CUT bipartition. For C5[2] take X = groups {0,2} sides...
# Actually known: cut puts the structure so that bad edges are inside. Let's just
# brute the maxcut.
def maxcut(adj,n):
    best=-1;bx=None
    for mask in range(1<<n):
        Xs=set(i for i in range(n) if mask&(1<<i)); c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;bx=Xs
    return best,bx
Ac,nc=c5blow(2)
mc,Xs=maxcut(Ac,nc)
Bc=[[0]*nc for _ in range(nc)]; Mc=[]
for u in range(nc):
    for v in range(u+1,nc):
        if Ac[u][v]:
            if (u in Xs)!=(v in Xs): Bc[u][v]=Bc[v][u]=1
            else: Mc.append((u,v))
print("C5[2] maxcut value", mc, "X", Xs, "beta=|M|=", len(Mc))
analyze("C5[2]", Bc, Mc, nc)
