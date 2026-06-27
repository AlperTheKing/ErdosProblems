import subprocess, random
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
# strengthened: c*(T(w)-N) <= N^2-Gamma  ; find max ratio (T-N)/(N^2-G) over defect>0
worst_ratio=F(0); wc=None
worst_strong=None  # min (N^2-G) - 7*(T-N)_+
def proc(n,E):
    global worst_ratio,wc,worst_strong
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj)
    if r is None: return
    side,G,M,ell=r; defG=n*n-G
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    for w in range(n):
        T=F(0)
        for f in M:
            Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
            if cnt: T+=ell[f]*F(cnt,nf)
        exc=T-n
        if exc>0 and defG>0:
            rr=F(exc,defG)
            if rr>worst_ratio: worst_ratio=rr; wc=(n,G,w,float(T),defG)
        s7=defG-7*max(F(0),exc)
        if worst_strong is None or s7<worst_strong[0]: worst_strong=(s7,n,G,w,float(T),defG)
for nn in range(5,10):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out: proc(*dec(g6))
for k in (2,3,4):
    for t in (2,3,4,5): proc(*C_blow(k,t))
print("max ratio (T-N)/(N^2-Gamma) =", worst_ratio, float(worst_ratio), "@", wc)
s7,n,G,w,T,defG=worst_strong
print(f"strengthened 7*(T-N)_+ <= N^2-Gamma : min slack={s7} {'HOLDS' if s7>=0 else 'FAILS'} @ N={n} G={G} w={w} T={T} N^2-G={defG}")
