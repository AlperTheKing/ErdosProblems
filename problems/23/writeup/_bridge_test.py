#!/usr/bin/env python3
"""Test the BRIDGE inequalities that would let D2/D5 imply ell_max*R<=K.
D2: ellmax*R <= N + bdeg*(N-ellmax).  To get <=K=N+(N^2-Gamma) we need
    BRIDGE-A:  bdeg(w)*(N-ellmax(w)) <= N^2 - Gamma   for the relevant w.
Also test the GLOBAL form and the per-vertex local CD geodesic bound D5:
    D5:  ellmax*R <= ellmax + (N-ellmax)*bdeg   (i.e. R <= 1 + (N-ellmax)*bdeg/ellmax)
Check BRIDGE-A exactly; if it fails find g6.  Also test a STRONGER local bound that
doesn't need the bridge: per-vertex  T(w) <= N + (N^2-Gamma) directly via a geodesic/CD count.
"""
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

worstA=None  # bridge-A: bdeg*(N-ellmax) <= N^2-Gamma  (only for vertices with bad-cycle through them)
worstAall=None
def proc(n,E):
    global worstA, worstAall
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    defGamma=n*n-G
    for w in range(n):
        ellmax=0;has=False
        bdeg=sum(1 for u in adj[w] if side[u]!=side[w])
        for f in M:
            if any(w in P for P in geo[f]):
                has=True
                if ell[f]>ellmax: ellmax=ell[f]
        if not has: continue
        lhs=bdeg*(n-ellmax)
        slack=defGamma-lhs
        if worstA is None or slack<worstA[0]:
            worstA=(slack,n,G,w,bdeg,ellmax,defGamma)

for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out: proc(*dec(g6))
for q in (2,3,4): proc(*C5blow(q))

slack,n,G,w,bdeg,ellmax,defGamma=worstA
status="HOLDS" if slack>=0 else "*** VIOLATED ***"
print(f"BRIDGE-A bdeg*(N-ellmax)<=N^2-Gamma: min slack={slack} {status} @ N={n} Gamma={G} N^2-G={defGamma} w={w} bdeg={bdeg} ellmax={ellmax} lhs={bdeg*(n-ellmax)}")
