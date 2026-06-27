#!/usr/bin/env python3
"""DECISIVE exhaustive test of GPT's R2 master inequality for delta=0 (Erdos #23):
    Gamma(G) + D*(G) <= N^2     [D*(G) = min over shortest bad-geodesic peels C of D(C)]
and the stronger LOCAL version  D(C) <= N^2 - Gamma(G)  for EVERY shortest bad geodesic C.
A single connected-B triangle-free max-cut config violating the master inequality KILLS R2.
Sweep ALL triangle-free graphs N<=Nmax, take the max cut MINIMIZING Gamma (per the lemma 'for some max cut')."""
import sys
from collections import deque
import flag_engine as fe

def maxcut_all(n, adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best,cuts

def bdistB(n,adj,side,src,banned):
    d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d: d[v]=d[u]+1; q.append(v)
    return d

def Bconnected(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def gamma_min_cut(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconnected(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        G=0; ok=True
        for (u,v) in M:
            d=bdistB(n,adj,side,u,set()).get(v,-1)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    return best

def shortest_geodesics(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist:
                        dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    paths=[]
    def rec(v,acc):
        if v==s: paths.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return paths

def D_of(n,adj,side,M,C):
    Cset=set(C); K=[v for v in range(n) if v not in Cset]; idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    if m>20: return None
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    best=0
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM-dB>best: best=dM-dB
    return best

def Dstar_and_local(n,adj,side,M,Gamma,NN):
    """Return (Dstar, local_ok, worst_local). Dstar = min over shortest geodesics of D(C).
    local_ok = (D(C) <= N^2-Gamma for ALL shortest geodesics). worst_local = max(Gamma+D(C)-N^2)."""
    Dstar=None; worst_local=-10**9
    for (u,v) in M:
        for C in shortest_geodesics(n,adj,side,u,v):
            d=D_of(n,adj,side,M,C)
            if d is None: continue
            if Dstar is None or d<Dstar: Dstar=d
            worst_local=max(worst_local, Gamma+d-NN*NN)
    return Dstar, (worst_local<=0), worst_local

def run(Nmax, Nmin=5):
    for N in range(Nmin,Nmax+1):
        gs=fe.enumerate_graphs(N,triangle_free=True)
        nconf=0; master_viol=[]; local_viol=0; min_master_slack=10**9; min_local_slack=10**9
        for (n,A) in gs:
            adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
            mc,cuts=maxcut_all(n,adj)
            res=gamma_min_cut(n,adj,cuts)
            if res is None: continue
            side,G,M=res
            if len(M)<1: continue
            nconf+=1
            Dstar,local_ok,worst_local=Dstar_and_local(n,adj,side,M,G,n)
            if Dstar is None: continue
            master_slack=n*n-G-Dstar
            min_master_slack=min(min_master_slack,master_slack)
            min_local_slack=min(min_local_slack,-worst_local)
            if master_slack<0: master_viol.append((n,A,G,len(M),Dstar))
            if not local_ok: local_viol+=1
        print(f"N={N}: tri-free={len(gs)} connected-B configs={nconf} | MASTER viol(Gamma+D*>N^2)={len(master_viol)} (min slack={min_master_slack}) | LOCAL viol(some C: Gamma+D(C)>N^2)={local_viol} (min slack={min_local_slack})",flush=True)
        for (n,A,G,m,Ds) in master_viol[:5]:
            print(f"   !!! MASTER VIOLATION N={n} Gamma={G} m={m} D*={Ds} N^2={n*n} A={A}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__":
    a=[int(x) for x in sys.argv[1:]] or [10]
    run(a[0], a[1] if len(a)>1 else 5)
