#!/usr/bin/env python3
"""Probe the geodesic-counting structure around w to bound R(w).
For vertex w let layers L_d = {v : d_B(w,v)=d}, a_d=|L_d|.
For each contributing bad edge f=xy, a shortest cycle through w splits at w:
  geodesic x->w (length d_x) and w->y (length d_y), d_x+d_y=ell(f)-1=ell-1.
p_f(w) = (#geos x->w thru-able)*(#geos w->y)/n_f, but really fraction of f's geos passing w.
Test candidate bounds on R(w):
  (G1) R(w) <= a_1 = bdeg(w)              [tried D1 -> false]
  (G2) R(w) <= sum_d (a_d choose ...)?
  (G3) the 'first-step' bound: every bad cycle thru w enters w from a cut-neighbor and
       leaves to a cut-neighbor on the OTHER side along the cycle; so #cycles thru w <=
       (pairs of cut-neighbors)? = bdeg choose 2 ? test.
  (G4) R(w) <= bdeg(w)*(bdeg(w)-1)/2 / something
Report per-vertex (R, bdeg, a_2, candidate values), find tight relation."""
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

# candidate bound: R(w) <= (# ordered pairs (a,b) of DISTINCT cut-neighbors of w with a,b on
#  same side as each other (=opposite to w)) /2 ... i.e. a bad cycle thru w uses TWO cut edges at w
# (entering and leaving), to two distinct neighbors n1,n2 on opposite side of w. So #cycles thru w
# at the LOCAL level <= C(bdeg,2). And R(w) (expected) <= C(bdeg,2)? Test.
worst={}
def feed(key,slack,info):
    if key not in worst or slack<worst[key][0]: worst[key]=(slack,info)
def proc(n,E,tag):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    for w in range(n):
        R=F(0);ellmax=0
        nbrs=[u for u in adj[w] if side[u]!=side[w]]
        bdeg=len(nbrs)
        # count actual bad cycles thru w and their entry/exit neighbors
        cyc_thru=0
        for f in M:
            Ps=geo[f];nf=len(Ps)
            cnt=sum(1 for P in Ps if w in P)
            if cnt:
                R+=F(cnt,nf)
                if ell[f]>ellmax:ellmax=ell[f]
                cyc_thru+=cnt
        if ellmax==0: continue
        Cbdeg2=F(bdeg*(bdeg-1),2)
        feed('R<=C(bdeg,2)', Cbdeg2-R, (n,G,w,bdeg,float(R),float(Cbdeg2)))
        feed('R<=bdeg*(N-ellmax)/(ellmax-2)?', None if ellmax<=2 else F(bdeg*(n-ellmax),ellmax-2)-R, (n,G,w,bdeg,ellmax,float(R)))

for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out: proc(*dec(g6),g6)
for q in (2,3,4): proc(*C5blow(q),f"C5[{q}]")

for k,(slack,info) in worst.items():
    if slack is None: continue
    st="HOLDS" if slack>=0 else "*** VIOLATED ***"
    print(f"{k}: min slack={float(slack):.4f} {st} @ {info}")
