#!/usr/bin/env python3
"""Test whether A_M := sum_f ell(f) <= N + (N^2 - Gamma) holds (a clean global bound that would
imply T(w)<=A_M<=K since T(w)=sum ell p_f <= sum ell = A_M).
At the witness J???E?pNu\: A_M = 5+5+5 = 15, N+(N^2-G)=11+46=57, holds with slack 42.
At C5[q]: A_M = q^2 * 5 = 5q^2, K=N=5q. So A_M=5q^2 vs 5q: A_M >> K for q>=2! So A_M<=K is FALSE.
=> T(w)<=A_M is too lossy at C5[q] (where most p_f are SMALL). Confirm A_M<=K fails at C5[q],
and measure how often A_M<=K holds vs T(w)<=K. This tells us the bound must use p_f<1 crucially."""
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
def gmin(n,adj):
    best=None
    for side in maxcut_all(n,adj):
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
def C_blow(k,t):
    m=2*k+1; n=m*t; E=[]
    for i in range(m):
        for a in range(t):
            for b in range(t): E.append((i*t+a,((i+1)%m)*t+b))
    return n,E
def AM(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj)
    if r is None: return None
    side,G,M,ell=r
    return sum(ell.values()), n, G, n+(n*n-G)
for tag,(n,E) in [("C5[2]",C_blow(2,2)),("C5[3]",C_blow(2,3)),("C5[4]",C_blow(2,4)),
                  ("witness",dec("J???E?pNu\\"))]:
    r=AM(n,E)
    if r: a,n2,G,K=r; print(f"{tag}: A_M=sum ell={a} | K=N+(N^2-G)={K} | A_M<=K: {a<=K}")
print("=> A_M<=K is FALSE at C5[q] (q>=2); so T(w)<=A_M is too weak there. The p_f<1 'spreading' is essential.")
