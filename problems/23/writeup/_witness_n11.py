"""Find the N=11 G=75 vertex with T(w)=15>N=11 and dump its full structure:
which bad edges contribute, their ell, p_f, the geodesic overlap. This is the witness
that breaks T(w)<=N; understand WHY T can exceed N and how N^2-Gamma=46 absorbs it."""
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
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
found=None
for g6 in out:
    n,E=dec(g6); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj)
    if r is None: continue
    side,G,M,ell=r
    if G!=75: continue
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    for w in range(n):
        T=F(0)
        for f in M:
            Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
            if cnt: T+=ell[f]*F(cnt,nf)
        if T>=15:
            found=(g6,n,G,side,M,ell,geo,w,T); break
    if found: break
g6,n,G,side,M,ell,geo,w,T=found
print(f"g6={g6} N={n} Gamma={G} N^2-G={n*n-G} K={n+(n*n-G)} w={w} T(w)={T} (>N={n})")
print(f"side={side}")
print(f"#bad edges |M|={len(M)}, ells={sorted(ell.values())}")
print(f"contributing at w:")
for f in M:
    Ps=geo[f];nf=len(Ps);cnt=sum(1 for P in Ps if w in P)
    if cnt: print(f"  f={f} ell={ell[f]} n_f={nf} thru_w={cnt} p_f={F(cnt,nf)} ell*p_f={ell[f]*F(cnt,nf)}")
print(f"sum T(w) over all v = Gamma = {G} (identity)")
