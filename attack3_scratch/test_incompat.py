import itertools, random
from itertools import combinations
from collections import deque

# Stress test: can a CD-valid, all-d4, triangle-free instance WITHOUT C5-homomorphism
# approach the tight ratio 25|M|/N^2 = 1, or does incompatibility force slack?
# This tests whether the LEMMA's CONCLUSION (not just the proof) is safe.
# If we find ratio>1 -> lemma FALSE. If ratio stays <1 except for C5-hom instances ->
#   suggests the factor 25 genuinely needs the extra structure the proof can't supply,
#   but lemma still true (just hard).

def is_triangle_free(adj,n):
    for u in range(n):
        for v in range(u+1,n):
            if adj[u][v]:
                for w in range(n):
                    if adj[u][w] and adj[v][w]:
                        return False
    return True

def bfs(Badj,n,src):
    dist=[-1]*n; dist[src]=0; q=deque([src])
    while q:
        x=q.popleft()
        for y in range(n):
            if Badj[x][y] and dist[y]<0:
                dist[y]=dist[x]+1; q.append(y)
    return dist

def maxcut(adj,n):
    best=-1;bx=None
    for mask in range(1<<n):
        Xs=set(i for i in range(n) if mask&(1<<i))
        c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;bx=Xs
    return best,bx

def cd_valid(adj,n):
    # Is the all-vertices-as-given bipartition (we'll pass the actual cut) a maxcut?
    # Use: a cut X,Y is CD-valid iff it's a *maximum* cut. We just check max via flips?
    # Easiest: it's CD iff no single-subset flip improves. But CD is over ALL subsets =
    # exactly local-opt under arbitrary flips = global max cut. So check maxcut value.
    pass

# Random triangle-free graphs n=8..11, take max cut, restrict all-d4, record ratio.
def trial(n, tries):
    edges_all=list(combinations(range(n),2))
    best_ratio=0.0; best=None
    for _ in range(tries):
        adj=[[0]*n for _ in range(n)]
        # build a random triangle-free graph greedily
        order=edges_all[:]; random.shuffle(order)
        for (u,v) in order:
            adj[u][v]=adj[v][u]=1
            # check no triangle created
            tri=False
            for w in range(n):
                if adj[u][w] and adj[v][w]:
                    tri=True;break
            if tri:
                adj[u][v]=adj[v][u]=0
        mc,Xs=maxcut(adj,n)
        Badj=[[0]*n for _ in range(n)]; Mlist=[]
        for (u,v) in edges_all:
            if adj[u][v]:
                if (u in Xs)!=(v in Xs): Badj[u][v]=Badj[v][u]=1
                else: Mlist.append((u,v))
        if not Mlist: continue
        ok=True
        for (u,v) in Mlist:
            d=bfs(Badj,n,u)
            if d[v]!=4: ok=False;break
        if not ok: continue
        r=25.0*len(Mlist)/(n*n)
        if r>best_ratio:
            best_ratio=r; best=(len(Mlist),Xs)
    return best_ratio,best

random.seed(1)
for n in range(8,13):
    r,b=trial(n, 60000)
    print(f"n={n}: best ratio 25|M|/N^2 over random all-d4 maxcut instances = {r:.4f}  (|M|,X)={b}")
