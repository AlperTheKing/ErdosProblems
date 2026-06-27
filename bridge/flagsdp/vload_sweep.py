#!/usr/bin/env python3
"""Exhaustive check of the VERTEX-LOAD theorem over all connected-B m>=2 tri-free configs N<=Nmax:
does the GREEDY-BALANCED routing achieve max_v T(v) <= N+(N^2-Gamma)? (greedy success => theorem holds, since
greedy is a valid choice; greedy failure would need the optimal flow, flagged for LP follow-up.)"""
import sys
from collections import deque
import flag_engine as fe

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
def maxcut_all(n,E):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
        if c>best: best=c; cuts=[mask]
        elif c==best: cuts.append(mask)
    return best,cuts
def gamma_min_cut(n,adj,E):
    mc,cuts=maxcut_all(n,E); best=None
    for mask in cuts:
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        M=[(u,v) for (u,v) in E if side[u]==side[v]]
        G=0; ok=True
        for (u,v) in M:
            d=bdistB(n,adj,side,u,set()).get(v,-1)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    return best
def all_geos(n,adj,side,s,t):
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
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def greedy_maxload(n,adj,side,M):
    cyc={}; h={}
    for (u,v) in M:
        geos=all_geos(n,adj,side,u,v)
        if not geos: return None
        cyc[(u,v)]=geos; h[(u,v)]=len(geos[0])
    T=[0]*n
    for e in sorted(cyc,key=lambda e:-h[e]):
        best=None
        for C in cyc[e]:
            mx=max(T[w]+h[e] for w in C)
            if best is None or mx<best[0]: best=(mx,C)
        for w in best[1]: T[w]+=h[e]
    return max(T), sum(T)

def run(Nmax,Nmin=8):
    for N in range(Nmin,Nmax+1):
        gs=fe.enumerate_graphs(N,triangle_free=True); nconf=0; viol=0; worst=-10**9
        for (n,A0) in gs:
            adj=[set(v for v in range(n) if (A0[u]>>v)&1) for u in range(n)]
            E=[(u,v) for u in range(n) for v in adj[u] if v>u]
            res=gamma_min_cut(n,adj,E)
            if res is None: continue
            side,G,M=res
            if len(M)<2: continue
            r=greedy_maxload(n,adj,side,M)
            if r is None: continue
            mx,sT=r; nconf+=1; bound=n+(n*n-G)
            if sT!=G: print(f"   IDENTITY-FAIL N={n} sumT={sT}!=Gamma={G} A0={A0}",flush=True)
            if mx-bound>worst: worst=mx-bound
            if mx>bound:
                viol+=1
                print(f"   VLOAD-GREEDY-FAIL N={n} Gamma={G} deficit={n*n-G} maxT={mx} > bound={bound} A0={A0}",flush=True)
        print(f"N={N}: connected-B m>=2 configs={nconf} | greedy vertex-load max_v T(v) > N+(N^2-Gamma): {viol} (worst maxT-bound={worst})",flush=True)
    print("DONE",flush=True)

if __name__=="__main__":
    a=[int(x) for x in sys.argv[1:]] or [11]
    run(a[0], a[1] if len(a)>1 else 8)
