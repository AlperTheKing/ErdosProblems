#!/usr/bin/env python3
"""INDEPENDENT recompute (separate code) of maxcut, Gamma, K, and T_uniform for key graphs,
to cross-check hub_adv.Tuniform. No reuse of census_GPI internals except dec for graph6 input parsing.
Uses its own brute maxcut, BFS distance, BFS geodesic enumeration, exact Fractions."""
from fractions import Fraction as Fr
from collections import deque
from itertools import product

def dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[];i=0
    for jj in range(1,n):
        for ii in range(jj):
            if i<len(bits) and bits[i]: E.append((ii,jj))
            i+=1
    return n,E

def solve(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    # all max cuts
    best=-1; cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    # B-connectivity (bipartite cut subgraph connected on all n vertices)
    def bconn(side):
        seen={0}; q=deque([0])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
        return len(seen)==n
    # restricted-B distance + geodesics
    def geos(side,s,t):
        dist={s:0}; pred={s:[]}; layer=[s]
        while layer:
            nxt=[]
            for u in layer:
                for v in adj[u]:
                    if side[u]!=side[v]:
                        if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                        elif dist[v]==dist[u]+1: pred[v].append(u)
            layer=nxt
        if t not in dist: return None, []
        P=[]
        def rec(v,acc):
            if v==s: P.append([s]+acc[::-1]); return
            for p in pred[v]: rec(p,acc+[v])
        rec(t,[])
        return dist[t], P
    bestcfg=None
    for side in cuts:
        if not bconn(side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ell={}; ok=True; geomap={}
        for (u,v) in M:
            d,P=geos(side,u,v)
            if d is None or not P: ok=False; break
            ell[(u,v)]=d+1; G+=(d+1)**2; geomap[(u,v)]=P
        if not ok: continue
        if bestcfg is None or G<bestcfg[0]:
            bestcfg=(G,side,M,ell,geomap)
    if bestcfg is None: return None
    G,side,M,ell,geomap=bestcfg
    T=[Fr(0)]*n
    for f in M:
        P=geomap[f]; nf=len(P); share=Fr(ell[f],nf)
        for path in P:
            for w in path: T[w]+=share
    K=n+(n*n-G)
    return dict(n=n,G=G,K=K,M=M,ell=ell,T=T,maxT=max(T),side=side)

cases=["G?`F`w","DUW","FCp`_","H?AAF_}","I?ABCc]}?","J???E?pNu\\?"]
for g6 in cases:
    n,E=dec(g6); r=solve(n,E)
    if r is None: print(g6,"-> no config"); continue
    viol = r['maxT']>r['K']
    print(f"{g6}: N={r['n']} Gamma={r['G']} K={r['K']} maxT={r['maxT']}={float(r['maxT']):.4f} ratio={float(r['maxT'])/r['K']:.4f} slack={r['K']-r['maxT']} viol={viol}")
