import random, collections, math
random.seed(7)

def bfs_dist(adj,n,src):
    d=[-1]*n; d[src]=0; q=collections.deque([src])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if d[y]<0: d[y]=d[x]+1; q.append(y)
    return d
def tri_free(adj,n):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True
def cut_value(edges,side): return sum(1 for(u,v)in edges if side[u]!=side[v])
def max_cut(edges,n):
    best=-1
    for mask in range(1<<n):
        side={i:(mask>>i)&1 for i in range(n)}
        c=cut_value(edges,side)
        if c>best: best=c
    return best

# Find an instance that is NOT a single complete-bipartite block (M not = U x V)
# i.e. the M-graph (monochromatic, sides) is not a complete bipartite block.
# Among CD all-d4 instances, report: how often is M a single complete block?
# And: how tight is coarea (best over r of sum|dphi|) vs |B| on NON-block instances?

def is_complete_block(Medges):
    # M edges all inside X (assume); check if endpoints form U x V complete bipartite
    # Build graph on M, check it's complete bipartite between its two color classes.
    nodes=set()
    for u,v in Medges: nodes.add(u); nodes.add(v)
    adjm={n:set() for n in nodes}
    for u,v in Medges: adjm[u].add(v); adjm[v].add(u)
    # 2-color
    color={}
    for s in nodes:
        if s in color: continue
        color[s]=0; q=[s]
        while q:
            x=q.pop()
            for y in adjm[x]:
                if y not in color: color[y]=1-color[x]; q.append(y)
                elif color[y]==color[x]: return False
    A=[n for n in nodes if color[n]==0]; Bc=[n for n in nodes if color[n]==1]
    for a in A:
        for b in Bc:
            if b not in adjm[a]: return False
    return True

N=10
block_cnt=0; nonblock_cnt=0; coarea_tight_nonblock=0; nonblock_examples=[]
for _ in range(200000):
    x=random.randint(2,N-2)
    X=list(range(x)); Y=list(range(x,N))
    Bedges=[]
    for u in X:
        for v in Y:
            if random.random()<0.45: Bedges.append((u,v))
    adjB=[set() for _ in range(N)]
    for u,v in Bedges: adjB[u].add(v); adjB[v].add(u)
    distB=[bfs_dist(adjB,N,s) for s in range(N)]
    Medges=[]
    for grp in (X,Y):
        for i in range(len(grp)):
            for j in range(i+1,len(grp)):
                u,v=grp[i],grp[j]
                if distB[u][v]==4: Medges.append((u,v))
    if len(Medges)<2: continue
    Medges=[e for e in Medges if random.random()<0.8]
    if len(Medges)<2: continue
    alledges=Bedges+Medges
    adj=[set() for _ in range(N)]
    for u,v in alledges: adj[u].add(v); adj[v].add(u)
    if not tri_free(adj,N): continue
    side={i:(0 if i<x else 1) for i in range(N)}
    if cut_value(alledges,side)!=max_cut(alledges,N): continue
    # only consider M entirely inside one side for block test
    allX=all(u<x and v<x for u,v in Medges)
    allY=all(u>=x and v>=x for u,v in Medges)
    if not (allX or allY):
        # mixed sides -> definitely not single block; treat as nonblock
        nonblock_cnt+=1
        continue
    if is_complete_block(Medges):
        block_cnt+=1
    else:
        nonblock_cnt+=1
        Mn=len(Medges); Bn=len(Bedges)
        best=max(sum(abs(distB[r][u]-distB[r][v]) for u,v in Medges) for r in range(N))
        if best==Bn:
            coarea_tight_nonblock+=1
        if len(nonblock_examples)<3:
            nonblock_examples.append((Mn,Bn,best,25*Mn/(N*N)))

print(f"N={N}: complete-block instances={block_cnt}  NON-block instances={nonblock_cnt}")
print(f"  among single-side non-block, coarea exactly tight (best==|B|): {coarea_tight_nonblock}")
print("  non-block examples (|M|,|B|,best_coarea,ratio):", nonblock_examples)
