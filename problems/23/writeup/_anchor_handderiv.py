"""Exact HAND-DERIVATION check for C_{2k+1}[t] blow-ups, WITHOUT brute maxcut.
We KNOW the gamma-min cut analytically: in C_{2k+1}[t], vertices are classes 0..2k each size t,
edges only between consecutive classes (cyclically). The bipartite cut B: 2-color the cycle of
classes greedily 0,1,0,1,...,0 around the odd cycle => exactly ONE consecutive class-pair gets the
SAME color (the 'seam'), making all t*t edges between that pair BAD (monochromatic); all other
class-pair edges are cut. We verify this cut is connected-B, compute Gamma, M, the shortest cycles
of each bad edge (= the t*t edges of the seam), and R(w), T(w), ell_max(w) EXACTLY, and compare
ell_max*R to K.  This sidesteps maxcut_all so we can go to large t/k."""
from fractions import Fraction as F
from collections import deque

def build(k,t):
    m=2*k+1; n=m*t
    cls=lambda i: list(range(i*t,(i+1)*t))
    adj=[set() for _ in range(n)]
    for i in range(m):
        j=(i+1)%m
        for a in cls(i):
            for b in cls(j):
                adj[a].add(b); adj[b].add(a)
    # 2-color classes 0..2k around odd cycle: color[i]=i%2 ; then class 2k has color 0 == class 0 color 0
    # seam between class m-1 (=2k, color0) and class 0 (color0): SAME color => those edges monochromatic.
    color=[i%2 for i in range(m)]
    # vertex side = color of its class
    side=[color[v//t] for v in range(n)]
    return n,m,t,adj,side

def bdist_restr(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d

def geos(adj,side,s,tt):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if tt not in dist: return []
    P=[]
    def rec(v,acc):
        if v==s: P.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(tt,[]); return P

for (k,t) in [(2,1),(2,2),(2,3),(2,4),(3,1),(3,2),(3,3),(4,1),(4,2),(5,1)]:
    n,m,t,adj,side=build(k,t)
    # connected-B check
    d0=bdist_restr(adj,side,0)
    if len(d0)!=n:
        print(f"C{m}[{t}] N={n}: B NOT connected under this cut -> skip"); continue
    # bad edges = monochromatic
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    ell={}; G=0
    for (u,v) in M:
        dd=bdist_restr(adj,side,u); h=dd[v]+1; ell[(u,v)]=h; G+=h*h
    K=n+(n*n-G)
    R={w:F(0) for w in range(n)}; T={w:F(0) for w in range(n)}; emax={w:0 for w in range(n)}
    for (u,v) in M:
        Ps=geos(adj,side,u,v); nf=len(Ps); h=ell[(u,v)]
        cnt={}
        for P in Ps:
            for w in P: cnt[w]=cnt.get(w,0)+1
        for w,c in cnt.items():
            pf=F(c,nf); R[w]+=pf; T[w]+=h*pf
            if h>emax[w]: emax[w]=h
    maxprod=max(emax[w]*R[w] for w in range(n))
    maxT=max(T.values())
    ells=sorted(set(ell.values()))
    Rset=sorted(set(R.values()))
    print(f"C{m}[{t}] N={n} Gamma={G} (=N^2? {G==n*n}) K={K} |M|={len(M)} ell={ells} R-vals={Rset} maxT={maxT} max(ellmax*R)={maxprod} (=K? {maxprod==K})")
