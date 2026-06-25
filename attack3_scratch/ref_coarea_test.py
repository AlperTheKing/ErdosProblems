import random, collections
random.seed(1)

def bfs_dist(adj, n, src):
    d=[-1]*n; d[src]=0; q=collections.deque([src])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if d[y]<0:
                d[y]=d[x]+1; q.append(y)
    return d

def is_triangle_free(adj,n):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]):
                return False
    return True

def cut_value(edges, side):
    return sum(1 for (u,v) in edges if side[u]!=side[v])

def max_cut(edges,n):
    best=-1
    for mask in range(1<<n):
        side={i:(mask>>i)&1 for i in range(n)}
        c=cut_value(edges,side)
        if c>best: best=c
    return best

def run_trials(N, trials=30000):
    viol_coarea=0; viol_lemma=0; max_ratio=0.0; found=0
    coarea_examples=[]
    for _ in range(trials):
        x=random.randint(2,N-2)
        X=list(range(x)); Y=list(range(x,N))
        Bedges=[]
        for u in X:
            for v in Y:
                if random.random()<0.45:
                    Bedges.append((u,v))
        adjB=[set() for _ in range(N)]
        for (u,v) in Bedges:
            adjB[u].add(v); adjB[v].add(u)
        distB=[bfs_dist(adjB,N,s) for s in range(N)]
        Medges=[]
        for grp in (X,Y):
            for i in range(len(grp)):
                for j in range(i+1,len(grp)):
                    u,v=grp[i],grp[j]
                    if distB[u][v]==4:
                        Medges.append((u,v))
        if not Medges: continue
        Medges=[e for e in Medges if random.random()<0.7]
        if not Medges: continue
        alledges=Bedges+Medges
        adj=[set() for _ in range(N)]
        for (u,v) in alledges:
            adj[u].add(v); adj[v].add(u)
        if not is_triangle_free(adj,N): continue
        side={i:(0 if i<x else 1) for i in range(N)}
        cutval=cut_value(alledges,side)
        if cutval!=max_cut(alledges,N): continue
        found+=1
        Mn=len(Medges); Bn=len(Bedges)
        ratio=25*Mn/(N*N)
        if ratio>max_ratio: max_ratio=ratio
        if 25*Mn> N*N: viol_lemma+=1
        for r in range(N):
            s=0; ok=True
            for (u,v) in Medges:
                du=distB[r][u]; dv=distB[r][v]
                if du<0 or dv<0: ok=False; break
                s+=abs(du-dv)
            if ok and s> Bn:
                viol_coarea+=1
                if len(coarea_examples)<3:
                    coarea_examples.append((N,r,s,Bn,list(Medges),list(Bedges)))
                break
    return found, viol_coarea, viol_lemma, max_ratio, coarea_examples

for N in range(6,12):
    f,vc,vl,mr,ex=run_trials(N, trials=40000)
    print(f"N={N}: found={f} coarea_violations={vc} lemma_violations={vl} max_ratio={mr:.3f}")
    for e in ex:
        print("   COAREA VIOL:", e)
