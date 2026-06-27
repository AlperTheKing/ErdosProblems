#!/usr/bin/env python3
"""Decisive numerical test of GPT's peel LEMMA: every connected-B triangle-free instance with Gamma>=N^2
has a SAFE geodesic odd-cycle peel C (CD preserved + every remaining bad edge in one B'-component +
L=Gamma-Gamma' <= 2|C|N-|C|^2). Since Gamma<=N^2 holds numerically, 'Gamma>=N^2' = the TIGHT instances.
Sweep ALL triangle-free graphs N<=Nmax, take a max cut MINIMIZING Gamma (GPT 'for some max cut'), keep the
connected-B tight ones, test the peel. ANY tight connected-B instance with NO safe peel = the obstruction."""
import sys
from collections import deque
from itertools import combinations
import flag_engine as fe

def all_maxcuts(n, adj):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def bdistB(n, adj, side, src, banned=None):
    banned=banned or set()
    d=[-1]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for v in range(n):
            if v!=u and adj[u][v] and side[u]!=side[v] and v not in banned and d[v]<0:
                d[v]=d[u]+1; q.append(v)
    return d

def Bconnected(n, adj, side):
    # B = cross edges; connected on all n vertices?
    seen=set([0]); q=deque([0])
    while q:
        u=q.popleft()
        for v in range(n):
            if adj[u][v] and side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def gamma_min_cut(n, adj):
    mc,cuts=all_maxcuts(n,adj); best=None
    for side in cuts:
        M=[(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v] and side[u]==side[v]]
        G=0; ok=True
        for (u,v) in M:
            d=bdistB(n,adj,side,u)[v]
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    return best   # (side,Gamma,M) or None

def shortest_path_B(n, adj, side, s, t):
    par={s:None}; q=deque([s])
    while q:
        u=q.popleft()
        if u==t: break
        for v in range(n):
            if adj[u][v] and side[u]!=side[v] and v not in par: par[v]=u; q.append(v)
    if t not in par: return None
    p=[]; x=t
    while x is not None: p.append(x); x=par[x]
    return p[::-1]

def cut_dom(keep, n, adj, side, M):
    K=sorted(keep); kset=set(K); idx={v:i for i,v in enumerate(K)}; m=len(K)
    if m>20: return None
    Be=[(u,v) for u in K for v in K if u<v and adj[u][v] and side[u]!=side[v]]
    Me=[(u,v) for (u,v) in M if u in kset and v in kset]
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Me if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM>dB: return False
    return True

def has_safe_peel(n, adj, side, M, Gamma, NN):
    for (u,v) in M:
        P=shortest_path_B(n,adj,side,u,v)
        if P is None: continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep: continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; ok=True
        for (a,b) in Mp:
            d=bdistB(n,adj,side,a,banned=C)[b]
            if d<0: ok=False; break
            Gp+=(d+1)**2
        if not ok: continue   # a bad edge disconnected in B' -> not safe
        L=Gamma-Gp; bound=2*s*NN-s*s
        if L>bound: continue
        cd=cut_dom(keep,n,adj,side,Mp)
        if cd is True: return True,(u,v,s,Gp,L,bound)
    return False,None

def run(Nmax):
    for N in range(5,Nmax+1):
        gs=fe.enumerate_graphs(N,triangle_free=True)
        tight=0; safe=0; obstr=[]
        for (n,A) in gs:
            adj=[[bool((A[u]>>v)&1) for v in range(n)] for u in range(n)]
            res=gamma_min_cut(n,adj)
            if res is None: continue
            side,G,M=res
            if G< n*n: continue              # not tight (Gamma<N^2)
            if not Bconnected(n,adj,side): continue
            tight+=1
            sp,info=has_safe_peel(n,adj,side,M,G,n)
            if sp: safe+=1
            else: obstr.append((n,A,G,len(M)))
        print(f"N={N}: tri-free={len(gs)}; TIGHT connected-B (Gamma=N^2)={tight}; with SAFE peel={safe}; OBSTRUCTIONS={len(obstr)}",flush=True)
        for (n,A,G,m) in obstr[:5]: print(f"   !!! OBSTRUCTION N={n} m={m} Gamma={G} A={A}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]) if len(sys.argv)>1 else 10)
