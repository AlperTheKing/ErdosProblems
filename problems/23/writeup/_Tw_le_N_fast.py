#!/usr/bin/env python3
"""Test whether T(w) <= N alone holds (the C5[q] value is exactly N).
If T(w)<=N ALWAYS, then since K=N+(N^2-Gamma)>=N (as Gamma<=N^2 is the GOAL not assumption)...
careful: Gamma<=N^2 is what we're proving, can't assume. But T(w)<=N would give max T<=N<=K
whenever Gamma<=N^2, circular. Still: is T(w)<=N a theorem? Check census. If it FAILS, by how much,
and is the failure <= N^2-Gamma (giving T(w)<=N+(N^2-Gamma)=K directly)?
This is the cleanest possible split: T(w) <= N + max(0, T(w)-N) and we'd need (T(w)-N)_+ <= N^2-Gamma."""
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

worst_TleN=None       # min (N - T(w))  : if >=0 always, T<=N holds
worst_split=None      # min (N^2-Gamma) - (T(w)-N)_+
def proc(n,E):
    global worst_TleN, worst_split
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    defG=n*n-G
    for w in range(n):
        T=F(0)
        for f in M:
            Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
            if cnt: T+=ell[f]*F(cnt,nf)
        sl=n-T
        if worst_TleN is None or sl<worst_TleN[0]: worst_TleN=(sl,n,G,w,float(T))
        excess=max(F(0),T-n)
        s2=defG-excess
        if worst_split is None or s2<worst_split[0]: worst_split=(s2,n,G,w,float(T),defG,float(excess))

for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out: proc(*dec(g6))
for q in (2,3,4,5): proc(*C5blow(q))

sl,n,G,w,T=worst_TleN
print(f"[T(w)<=N] min slack(N-T)={float(sl):.4f} {'HOLDS' if sl>=0 else '*** FAILS ***'} @ N={n} G={G} w={w} T={T:.3f}")
s2,n,G,w,T,defG,exc=worst_split
print(f"[(T-N)_+ <= N^2-Gamma] min slack={float(s2):.4f} {'HOLDS' if s2>=0 else '*** FAILS ***'} @ N={n} G={G} w={w} T={T:.3f} N^2-G={defG} excess={exc:.3f}")
