#!/usr/bin/env python3
"""Search for a TRUE coupled per-vertex inequality tight at BOTH C5[q] and odd cycles.
Collect per-vertex tuples (R,T,ellmax,bdeg,N,Gamma,Ksurplus=N^2-Gamma) over census N<=11 + C5[q] + Cn.
Then test parametric families of the form
    ellmax*R <= N + c1*(N^2-Gamma) + c2*<localdefect>
and look for the tightest valid (>=0) member tight at the extremals.
Key new local quantity: per-w 'cycle defect' -- measure how R fails to be 'pure'.
Also: maybe the right statement is in terms of T directly and the SUM constraint.
We FOCUS: print the full per-vertex scatter to see if ellmax*R - N correlates with (N^2-Gamma)/N
or with a local quantity. Output: for each vertex with ellmax*R > N (i.e. exceeds the C5 value),
print ellmax*R-N, N^2-Gamma, bdeg, and ratio."""
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
def Cn(n):
    return n,[(i,(i+1)%n) for i in range(n)]

data=[]  # (N,Gamma,R,T,ellmax,bdeg, w-tag)
def proc(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return
    side,G,M,ell=r
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    for w in range(n):
        R=F(0);T=F(0);ellmax=0
        bdeg=sum(1 for u in adj[w] if side[u]!=side[w])
        for f in M:
            Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
            if cnt:
                pf=F(cnt,nf);R+=pf;T+=ell[f]*pf
                if ell[f]>ellmax:ellmax=ell[f]
        if ellmax: data.append((n,G,R,T,ellmax,bdeg))

for nn in range(5,12):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out: proc(*dec(g6))
for q in (2,3,4): proc(*C5blow(q))
for nn in (5,7,9,11,13): proc(*Cn(nn))

# scatter where ellmax*R - N > 0
print("vertices with ellmax*R > N (excess vs C5-value), sorted by excess/(N^2-G):")
rows=[]
for (N,G,R,T,ellmax,bdeg) in data:
    excess=ellmax*R-N
    defect=N*N-G
    if excess>0:
        rows.append((excess,defect,N,G,R,ellmax,bdeg))
rows.sort(key=lambda x:-(F(x[0],x[1]) if x[1]>0 else F(10**9)))
for excess,defect,N,G,R,ellmax,bdeg in rows[:12]:
    ratio = float(excess/defect) if defect>0 else float('inf')
    print(f"  N={N} G={G} ellmax={ellmax} R={R} bdeg={bdeg} | excess(ellmaxR-N)={float(excess):.3f} N^2-G={defect} ratio={ratio:.4f}")
# also: is ellmax*R <= N + (N^2-G) i.e. excess<=defect ALWAYS? (this is C2=target)
maxratio=max((F(e,d) for e,d,_,_,_,_,_ in rows if d>0), default=0)
print("max excess/defect =", maxratio, float(maxratio), " (target C2 needs <=1)")
