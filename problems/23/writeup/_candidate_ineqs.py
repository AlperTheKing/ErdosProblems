#!/usr/bin/env python3
"""Test candidate per-vertex inequalities EXACTLY across census N<=10 + C5[q]."""
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

def rows_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    out=[]
    for w in range(n):
        R=F(0);T=F(0);ellmax=0
        bdeg=sum(1 for u in adj[w] if side[u]!=side[w])
        for f in M:
            Ps=geo[f];nf=len(Ps)
            cnt=sum(1 for P in Ps if w in P)
            if cnt:
                pf=F(cnt,nf);R+=pf;T+=ell[f]*pf
                if ell[f]>ellmax: ellmax=ell[f]
        out.append((w,R,T,ellmax,bdeg))
    return n,G,K,out

def C5blow(q):
    n=5*q; E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(q):
            for b in range(q):
                E.append((i*q+a,j*q+b))
    return n,E

worst={}
def feed(n,G,K,rows):
    for (w,R,T,ellmax,bdeg) in rows:
        if ellmax==0: continue
        tests={
          'C2 ellmax*R<=K': K-ellmax*R,
          'C1 T<=K': K-T,
          'D1 R<=bdeg': bdeg-R,
          'D2 ellmax*R<=N+bdeg*(N-ellmax)': (n+bdeg*(n-ellmax))-ellmax*R,
          'D3 T<=N+(bdeg-1)*(N-ellmax)': (n+(bdeg-1)*(n-ellmax))-T,
          'D5 R<=1+(N-ellmax)*bdeg/ellmax': (1+F((n-ellmax)*bdeg,ellmax))-R,
        }
        for k,slack in tests.items():
            if k not in worst or slack<worst[k][0]:
                worst[k]=(slack,n,G,K,w,R,T,ellmax,bdeg)

for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out:
        r=rows_of(*dec(g6))
        if r: feed(*r)
for q in (2,3,4):
    r=rows_of(*C5blow(q))
    if r: feed(*r)

for k in sorted(worst):
    slack,n,G,K,w,R,T,ellmax,bdeg=worst[k]
    status="HOLDS" if slack>=0 else "*** VIOLATED ***"
    print(f"{k}: min slack={float(slack):.4f} {status}  @ N={n} G={G} K={K} R={R} T={float(T):.3f} ellmax={ellmax} bdeg={bdeg}")
