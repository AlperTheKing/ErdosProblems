#!/usr/bin/env python3
"""FAST robustness check of  (T(w)-N)_+ <= N^2-Gamma  on key STRUCTURED families only
(no census), using ONE gmin per graph. Families: C_{2k+1}[t] for k=2,3,4 t up to 6;
Grotzsch (Mycielski C5); hub-funnel G?`F`w blow-ups; larger odd cycles.
EXACT Fractions. Print min slack per family and tightness."""
from collections import deque
from fractions import Fraction as F
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
def gmin_known(n,adj,side):
    # use a GIVEN cut (for large blow-ups where maxcut enumeration is infeasible)
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0;ell={}
    for (u,v) in M:
        d=bdist(adj,side,u,v)
        if d<0: return None
        ell[(u,v)]=d+1;G+=(d+1)**2
    return side,G,M,ell
def C_blow(k,t):
    m=2*k+1; n=m*t; E=[]
    for i in range(m):
        for a in range(t):
            for b in range(t): E.append((i*t+a,((i+1)%m)*t+b))
    return n,E
def check(n,E,tag,use=None,big=False):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    if big and use is not None:
        r=gmin_known(n,adj,use)
    else:
        r=gmin(n,adj)
    if r is None: return f"{tag}: gmin fail"
    side,G,M,ell=r
    defG=n*n-G
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    worst=None
    for w in range(n):
        T=F(0)
        for f in M:
            Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
            if cnt: T+=ell[f]*F(cnt,nf)
        slack=defG-max(F(0),T-n)
        if worst is None or slack<worst[0]: worst=(slack,w,float(T))
    sl,w,T=worst
    st="OK" if sl>=0 else "*** VIOLATION ***"
    return f"{tag:14} N={n} G={G} N^2-G={defG} | minslack={float(sl):+.3f} {st} (w={w} T={T:.3f})"
# canonical 2-coloring for odd-cycle blow-up: part i side = i<k? use proper balanced cut: parts alternate
def blowcut(k,t):
    m=2*k+1; side=[0]*(m*t)
    # the gamma-min cut: one part is the 'odd' part; assign sides by a near-bipartition of C_m
    col=[0]*m
    for i in range(m): col[i]=i%2
    # last vertex same as 0 (odd) -> the bad edges sit on the (m-1,0) seam region
    for i in range(m):
        for a in range(t): side[i*t+a]=col[i]
    return side
print("=== FAST structured-family robustness:  (T(w)-N)_+ <= N^2-Gamma ===")
for k in (2,3,4):
    for t in (2,3,4,5,6):
        n,E=C_blow(k,t)
        if n<=15: print(check(n,E,f"C{2*k+1}[{t}]"))
        else:
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b);adj[b].add(a)
            print(check(n,E,f"C{2*k+1}[{t}]",use=blowcut(k,t),big=True))
# Grotzsch / Mycielski C5
def mycielski(n0,E0):
    n=2*n0+1; E=list(E0)
    for (a,b) in E0:
        E.append((a,n0+b)); E.append((n0+a,b))
    for i in range(n0): E.append((n0+i,2*n0))
    return n,E
print(check(*mycielski(5,[(i,(i+1)%5) for i in range(5)]),"Grotzsch"))
