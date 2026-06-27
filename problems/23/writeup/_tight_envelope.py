#!/usr/bin/env python3
"""Gather EXACT per-vertex (R, T, ellmax, bdeg, #contrib bad edges, geodesic-layer profile)
at ALL vertices where T(w)=K (tight) OR ellmax*R close to K, across census + C5[q],
to identify the TRUE tight structure and the right per-vertex invariant.
Also compute, per contributing bad edge f at w: (dx,dy)=B-dists from endpoints to w,
and n_f, and the number of f's geodesics through w (= p_f * n_f)."""
import subprocess
from collections import deque
from fractions import Fraction as F
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
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
def maxcut_all(n,adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]; best=-1;cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best:best=c;cuts=[side[:]]
        elif c==best:cuts.append(side[:])
    return cuts
def Bconn(n,adj,side):
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen:seen.add(v);q.append(v)
    return len(seen)==n
def bdist(adj,side,s,t):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:d[v]=d[u]+1;q.append(v)
    return d.get(t,-1)
def geos(adj,side,s,t):
    dist={s:0};pred={s:[]};layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist:dist[v]=dist[u]+1;pred[v]=[u];nxt.append(v)
                    elif dist[v]==dist[u]+1:pred[v].append(u)
        layer=nxt
    if t not in dist:return []
    P=[]
    def rec(v,acc):
        if v==s:P.append([s]+acc[::-1]);return
        for p in pred[v]:rec(p,acc+[v])
    rec(t,[]);return P
def gmin(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconn(n,adj,side):continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M:continue
        G=0;ok=True;ell={}
        for (u,v) in M:
            d=bdist(adj,side,u,v)
            if d<0:ok=False;break
            ell[(u,v)]=d+1;G+=(d+1)**2
        if ok and (best is None or G<best[1]):best=(side,G,M,ell)
    return best
def C5blow(q):
    n=5*q; E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(q):
            for b in range(q):
                E.append((i*q+a,j*q+b))
    return n,E

def report(n,E,label):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    for w in range(n):
        R=F(0);T=F(0);ellmax=0;nc=0
        bdeg=sum(1 for u in adj[w] if side[u]!=side[w])
        for f in M:
            Ps=geo[f];nf=len(Ps)
            cnt=sum(1 for P in Ps if w in P)
            if cnt:
                pf=F(cnt,nf);R+=pf;T+=ell[f]*pf;nc+=1
                if ell[f]>ellmax:ellmax=ell[f]
        if T==K:  # tight vertex
            print(f"[{label}] N={n} G={G} K={K} w={w}: R={R} T={T} ellmax={ellmax} bdeg={bdeg} #contrib={nc} ||  R*ellmax={R*ellmax}")

# C5[q] full profile (all vertices identical by symmetry, print one)
for q in (1,2,3):
    n,E=C5blow(q)
    print(f"--- C5[{q}] (N={n}) ---")
    report(n,E,f"C5[{q}]")
# census tight vertices N=9,10
for nn in [9,10]:
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    cnt=0
    for g6 in out:
        report(*dec(g6),g6)
        cnt+=1
