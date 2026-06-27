#!/usr/bin/env python3
"""Extend the independent master-inequality gate to the high-beta/e BAND witnesses
M(Petersen) [n=21] and M(Grotzsch) [n=23] -- beyond the N<=16 workflow reach.
Master: Gamma(G)+D*(G) <= N^2 over the Gamma-min connected-B max cut; LOCAL: Gamma+D(C)<=N^2 all shortest C.
Numpy-vectorized max cut + optimal-cut set; D(C) vectorized over 2^|K| recolorings."""
import numpy as np
from collections import deque

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    E2=[(min(a,b),max(a,b)) for a,b in E]; ap=2*n
    for u in range(n):
        for v in adj[u]: E2.append((min(u,n+v),max(u,n+v)))
    for u in range(n): E2.append((min(n+u,ap),max(n+u,ap)))
    return 2*n+1, sorted(set(E2))
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]
def grotzsch():
    E=[(i,(i+1)%5) for i in range(5)]
    for i in range(5): E+=[(5+i,(i-1)%5),(5+i,(i+1)%5)]
    for i in range(5): E.append((10,5+i))
    return 11,E

def maxcut_optimal_sides(n,edges):
    eu=np.array([u for u,v in edges]); ev=np.array([v for u,v in edges])
    masks=np.arange(1<<(n-1),dtype=np.int64)
    bits=((masks[:,None]>>np.arange(n)[None,:])&1).astype(np.int8)  # 2^(n-1) x n
    cut=np.zeros(len(masks),dtype=np.int32)
    for k in range(len(eu)):
        cut+=(bits[:,eu[k]]^bits[:,ev[k]])
    mx=int(cut.max())
    opt_idx=np.nonzero(cut==mx)[0]
    return mx, bits[opt_idx]   # array of optimal side-vectors (vertex0 side 0)

def Bconn(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n
def bdist(n,adj,side,s,t):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)
def shortest_geos(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    paths=[]
    def rec(v,acc):
        if v==s: paths.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return paths
def D_of(n,adj,side,M,C):
    Cset=set(C); K=[v for v in range(n) if v not in Cset]
    if len(K)>22: return None
    kset=set(K); idx={v:i for i,v in enumerate(K)}; m=len(K)
    Be=[(idx[u],idx[v]) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(idx[a],idx[b]) for (a,b) in M if a in kset and b in kset]
    masks=np.arange(1<<m,dtype=np.int64)
    bits=((masks[:,None]>>np.arange(m)[None,:])&1).astype(np.int8)
    dM=np.zeros(len(masks),dtype=np.int32); dB=np.zeros(len(masks),dtype=np.int32)
    for (a,b) in Mp: dM+=(bits[:,a]^bits[:,b])
    for (a,b) in Be: dB+=(bits[:,a]^bits[:,b])
    return int(max(0,int((dM-dB).max())))

def check(name,n,edges):
    edges=sorted(set((min(a,b),max(a,b)) for a,b in edges))
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    mx,opts=maxcut_optimal_sides(n,edges)
    beta=len(edges)-mx
    print(f"{name}: n={n} e={len(edges)} maxcut={mx} beta={beta} #opt-cuts(half)={len(opts)}",flush=True)
    best=None
    for side in opts:
        side=list(side)
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist(n,adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    if best is None:
        print(f"  no connected-B max cut with bad edges"); return
    side,G,M=best
    # D* and local
    Dstar=None; worst_local=-10**9
    for (u,v) in M:
        for C in shortest_geos(n,adj,side,u,v):
            d=D_of(n,adj,side,M,C)
            if d is None: continue
            if Dstar is None or d<Dstar: Dstar=d
            worst_local=max(worst_local,G+d-n*n)
    NN=n*n
    print(f"  Gamma-min connected-B cut: Gamma={G}, |M|={len(M)}, D*={Dstar}, N^2={NN}")
    print(f"  MASTER Gamma+D*={G+(Dstar or 0)} <= N^2={NN}? {G+(Dstar or 0)<=NN}  (slack {NN-G-(Dstar or 0)})")
    print(f"  LOCAL  max(Gamma+D(C))-N^2 = {worst_local} <= 0? {worst_local<=0}")
    print(f"  mass bound check: Gamma={G} <= N^2={NN}? {G<=NN}  (Gamma deficit {NN-G})",flush=True)

pn,pe=petersen(); check("M(Petersen)",*mycielski(pn,pe))
gn,ge=grotzsch(); check("M(Grotzsch)",*mycielski(gn,ge))
print("DONE",flush=True)
