#!/usr/bin/env python3
"""STRESS-TEST the new candidate lemma  (T(w)-N)_+ <= N^2 - Gamma  for every vertex w,
over the Gamma-minimizing connected-B max cut. Beyond census: C5[q] big, odd-cycle blow-ups
C_{2k+1}[t], Mycielskians, hub-funnel gadget, random triangle-free dense graphs.
EXACT Fractions. Any violation -> print g6/structure. Also report min slack & where tight."""
import subprocess, random
from collections import deque
from fractions import Fraction as F
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
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
def gmin_full(n,adj):
    cuts=maxcut_all(n,adj); best=None
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
def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    return adj
def test(n,E,tag,allgmin=False):
    adj=adj_of(n,E)
    # use ALL connected-B max cuts (worst over gamma-min ties) when allgmin
    cuts=maxcut_all(n,adj)
    results=[]
    Gmin=None
    cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0;ok=True;ell={}
        for (u,v) in M:
            d=bdist(adj,side,u,v)
            if d<0: ok=False;break
            ell[(u,v)]=d+1;G+=(d+1)**2
        if ok: cand.append((G,side,M,ell))
    if not cand: return None
    Gmin=min(c[0] for c in cand)
    use=[c for c in cand if c[0]==Gmin] if allgmin else [min(cand,key=lambda c:c[0])]
    worst=None
    for (G,side,M,ell) in use:
        geo={f:geos(adj,side,f[0],f[1]) for f in M}
        defG=n*n-G
        for w in range(n):
            T=F(0)
            for f in M:
                Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
                if cnt: T+=ell[f]*F(cnt,nf)
            excess=max(F(0),T-n)
            slack=defG-excess
            if worst is None or slack<worst[0]: worst=(slack,n,G,defG,w,float(T))
    return worst

def C_blow(k,t):  # C_{2k+1}[t]
    m=2*k+1; n=m*t; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(t):
            for b in range(t): E.append((i*t+a,j*t+b))
    return n,E
def mycielski(n0,E0):
    # standard Mycielskian
    n=2*n0+1; E=list(E0)
    for (a,b) in E0:
        E.append((a,n0+b)); E.append((n0+a,b))
    for i in range(n0): E.append((n0+i,2*n0))
    return n,E

results=[]
# census
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    w=None
    for g6 in out:
        b=[ord(c)-63 for c in g6]; nn2=b[0]; bits=[]
        for x in b[1:]:
            for k in range(5,-1,-1): bits.append((x>>k)&1)
        E=[];i=0
        for jj in range(1,nn2):
            for ii in range(jj):
                if i<len(bits) and bits[i]: E.append((ii,jj))
                i+=1
        r=test(nn2,E,g6,allgmin=True)
        if r and (w is None or r[0]<w[0]): w=r
    if w: results.append((f"census N={nn} (all gmin)",w))
# blow-ups
for k in (2,3):       # C5, C7
    for t in (2,3,4,5):
        r=test(*C_blow(k,t),f"C{2*k+1}[{t}]")
        if r: results.append((f"C{2*k+1}[{t}]",r))
# Mycielski of C5
n5,E5=(5,[(i,(i+1)%5) for i in range(5)])
nm,Em=mycielski(n5,E5)
r=test(nm,Em,"Myciel(C5)")
if r: results.append(("Myciel(C5)=Grotzsch",r))
# random triangle-free dense
random.seed(1)
def rand_trifree(n,p):
    E=[]; adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    random.shuffle(pairs)
    for (i,j) in pairs:
        if random.random()<p and not (adj[i]&adj[j]):
            E.append((i,j)); adj[i].add(j); adj[j].add(i)
    return n,E
for n in (10,11,12):
    worstr=None
    for _ in range(40):
        r=test(*rand_trifree(n,0.5),"rand")
        if r and (worstr is None or r[0]<worstr[0]): worstr=r
    if worstr: results.append((f"rand trifree N={n} x40",worstr))

print("=== STRESS  (T(w)-N)_+ <= N^2-Gamma ===")
anyviol=False
for tag,w in results:
    slack,n,G,defG,wi,T=w
    st="OK" if slack>=0 else "*** VIOLATION ***"
    if slack<0: anyviol=True
    print(f"  {tag:28} minslack={float(slack):+.4f} {st}  (worst: N={n} G={G} N^2-G={defG} w={wi} T={T:.3f})")
print("VIOLATION FOUND" if anyviol else "NO VIOLATIONS")
