#!/usr/bin/env python3
"""Apply CD to metric balls around w and relate to T(w),R(w).
For radius r, S_r = {v: d_B(w,v) <= r}. CD: delta_M(S_r) <= delta_B(S_r).
Idea: a bad cycle through w (length ell) has its two 'far' endpoints x,y at distances
d_x,d_y from w with d_x+d_y=ell-1. If we cut at radius r=floor((ell-1)/2), the cycle
crosses the cut delta(S_r) at least twice. Sum over cycles -> congestion bound.
Numerically test several couplings to find one tight at C5[q]:
  (B1) sum over contributing f of [crossings of f-geodesics over delta(S_r)] related to delta_B.
Simplest: T(w) = sum_f ell*p_f. We want T(w)<=N+(N^2-Gamma).
Test the 'antipode mass' identity: for the cut at mid-radius, how much B-boundary is needed.
Just collect data: per w, and per radius r, (a_r=#layer r, cumB_r=|S_r|, deltaB(S_r), deltaM(S_r))."""
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
def bdist_all(adj,side,s):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:d[v]=d[u]+1;q.append(v)
    return d
def bdist(adj,side,s,t): return bdist_all(adj,side,s).get(t,-1)
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

def deltaB(adj,side,Sset):
    c=0
    for u in Sset:
        for v in adj[u]:
            if side[u]!=side[v] and v not in Sset: c+=1
    return c

# KEY TEST: at C5[q], pick w. layers: a_0=1, a_1=2q (the two neighbor parts), a_2=2q (two more parts),
# the 5th part is at distance? Let's just print the layer profile + ball cuts at C5[2],C5[3], and a couple census tight.
def profile(n,E,tag):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    # pick the max-T vertex
    Tv=[F(0)]*n
    for f in M:
        Ps=geo[f];nf=len(Ps);h=ell[f]
        cnt=[0]*n
        for P in Ps:
            for v in set(P): cnt[v]+=1
        Tv=[Tv[v]+F(h,nf)*cnt[v] for v in range(n)]
    w=max(range(n),key=lambda v:Tv[v])
    dd=bdist_all(adj,side,w)
    maxd=max(dd.values())
    layers={d:[v for v in dd if dd[v]==d] for d in range(maxd+1)}
    a={d:len(layers[d]) for d in layers}
    print(f"[{tag}] N={n} G={G} K={K} w={w} T(w)={Tv[w]}({float(Tv[w]):.3f})")
    print(f"   layer sizes a_d: {a}")
    for rad in range(maxd):
        S=set(v for v in dd if dd[v]<=rad)
        print(f"   r={rad}: |S|={len(S)} deltaB(S)={deltaB(adj,side,S)}  (N-|S|={n-len(S)})")

for q in (2,3): profile(*C5blow(q),f"C5[{q}]")
profile(*dec("I?rFf_{N?"),"I?rFf_{N? (C5[2]-iso)")
# a couple high-defect census N=10 worst-T
out=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
# find max T(w)-... just take a few with smallest slack
def slack_of(g6):
    n,E=dec(g6); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r; K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    Tmax=F(0)
    for f in M:
        Ps=geos(adj,side,f[0],f[1]);nf=len(Ps);h=ell[f]
    Tv=[F(0)]*n
    for f in M:
        Ps=geo[f];nf=len(Ps);h=ell[f];cnt=[0]*n
        for P in Ps:
            for v in set(P): cnt[v]+=1
        Tv=[Tv[v]+F(h,nf)*cnt[v] for v in range(n)]
    return (K-max(Tv), g6)
cand=[slack_of(g) for g in out]; cand=[c for c in cand if c]
cand.sort(key=lambda x:x[0])
for s,g6 in cand[:2]:
    profile(*dec(g6),f"{g6} slack={float(s):.2f}")
