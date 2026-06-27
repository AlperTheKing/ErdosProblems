#!/usr/bin/env python3
"""End-to-end EXACT check of the logical chain on a sample, confirming:
  LEMMA (per-vertex): for all w, (T(w)-N)_+ <= N^2-Gamma
    == for all w, T(w) <= N + (N^2-Gamma) = K            [U / vertex-load bound]
  => max_w T(w) <= K
  => GPI: for all phi>=0, sum_f ell(f) m_phi(f) <= K sum_v phi(v)
     [since T(w) is the phi=indicator load; GPI <= U via min<=avg, already established]
  => phi=1: Gamma = sum_f ell(f)^2 <= ... actually GPI with phi=1 gives sum_f ell(f)*ell(f)=Gamma
     and RHS K*N. Hmm the cleanest: U at the max vertex + conservation gives Gamma<=N^2 ONLY via GPI.
  The ESTABLISHED reduction (given) is U => GPI => Gamma<=N^2 => beta<=N^2/25.
We just RE-CONFIRM: on each sample graph, (a) compute T(w) for all w, (b) verify max T<=K,
(c) verify Gamma<=N^2, (d) verify the per-vertex lemma form, all EXACTLY consistent."""
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
def C_blow(k,t):
    m=2*k+1; n=m*t; E=[]
    for i in range(m):
        for a in range(t):
            for b in range(t): E.append((i*t+a,((i+1)%m)*t+b))
    return n,E
samples=[("C5[2]",C_blow(2,2)),("C5[3]",C_blow(2,3)),("witness",dec("J???E?pNu\\")),
         ("n8 hubfunnel",dec("G?`F`w")),("C7",( (7,[(i,(i+1)%7) for i in range(7)]) ))]
print("chain: LEMMA(per-vertex) <=> U(maxT<=K) ; both => Gamma<=N^2 (via established GPI)")
for tag,(n,E) in samples:
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj)
    if r is None: print(f"{tag}: no gmin"); continue
    side,G,M,ell=r; K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    Tv=[F(0)]*n
    for f in M:
        Ps=geo[f];nf=len(Ps);cnt=[0]*n
        for P in Ps:
            for v in set(P): cnt[v]+=1
        Tv=[Tv[v]+F(ell[f],nf)*cnt[v] for v in range(n)]
    maxT=max(Tv); sumT=sum(Tv)
    lemma_ok=all((max(F(0),Tv[w]-n))<=(n*n-G) for w in range(n))
    print(f"{tag:14} N={n} G={G} K={K} maxT={float(maxT):.3f} sumT={sumT}(==Gamma:{sumT==G}) "
          f"maxT<=K:{maxT<=K} Gamma<=N^2:{G<=n*n} LEMMA:{lemma_ok}")
