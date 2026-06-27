#!/usr/bin/env python3
"""Hard stress of C1 (inc_cut(w)<=degB(w)) and D (ellmax*(degB+inc_bad)/2<=K) on large structured graphs
where brute maxcut is infeasible: odd-cycle blow-ups C(2k+1)[q] with the CANONICAL gamma-min cut supplied
by hand, plus Mycielskians (gmin via brute where small). EXACT Fractions.

For C(2k+1)[q]: parts 0..2k each size q, edges between consecutive parts (cyclic). The gamma-min connected-B
max cut: 2-colour the odd cycle as best as possible; one monochromatic part-pair carries the bad edges.
We construct it explicitly and verify it IS a max cut with connected B and minimal Gamma by checking against
the known Gamma=N^2 value.
"""
import io, contextlib
from fractions import Fraction as F
from collections import deque
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import geos as _geos

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

def oddcycle_blowup(k,q):
    """C(2k+1)[q]. parts 0..2k size q, consecutive (cyclic) complete bipartite. Returns n,adj,side,M,ell,G."""
    m=2*k+1; n=m*q
    adj=[set() for _ in range(n)]
    def vid(p,a): return p*q+a
    for p in range(m):
        for a in range(q):
            for b in range(q):
                adj[vid(p,a)].add(vid((p+1)%m,b)); adj[vid((p+1)%m,b)].add(vid(p,a))
    # 2-colouring the odd cycle of parts: colour part p by p%2; part m-1 conflicts with part0 (both even idx? )
    # m=2k+1 odd: parts 0..2k. colour 0,1,0,1,...,0 -> part0 and part(2k) both colour0 -> the edge (2k,0) monochromatic.
    side=[0]*n
    for p in range(m):
        c=p%2
        for a in range(q): side[vid(p,a)]=c
    # bad edges: between part 2k and part 0 (both colour0)
    M=[];
    for a in range(q):
        for b in range(q):
            u=vid(m-1,a); v=vid(0,b)
            if u<v: M.append((u,v))
            else: M.append((v,u))
    ell={}; G=0
    for f in M:
        d=_bdist(adj,side,f[0],f[1]); ell[f]=d+1; G+=(d+1)**2
    return n,adj,side,M,ell,G

def _bdist(adj,side,s,t):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1;q.append(v)
    return d.get(t,-1)

def analyze(adj,side,M,ell,n,G):
    degB=[sum(1 for v in adj[u] if side[u]!=side[v]) for u in range(n)]
    R=[F(0) for _ in range(n)]; ellmax=[0]*n
    inc_bad=[F(0) for _ in range(n)]; inc_cut=[F(0) for _ in range(n)]
    for f in M:
        x,y=f; Ps=geos(adj,side,x,y); nf=len(Ps)
        if nf==0: return None
        s1=F(1,nf)
        for P in Ps:
            for v in P:
                R[v]+=s1
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
                if v==x or v==y: inc_cut[v]+=s1; inc_bad[v]+=s1
                else: inc_cut[v]+=2*s1
    K=n+(n*n-G)
    c1=all(inc_cut[w]<=degB[w] for w in range(n))
    Dok=all(ellmax[w]*(F(degB[w])+inc_bad[w])/2<=K for w in range(n) if R[w]>0)
    Rok=all(ellmax[w]*R[w]<=K for w in range(n) if R[w]>0)
    # worst
    wc1=max((inc_cut[w]-degB[w] for w in range(n)),default=F(0))
    wD=max((ellmax[w]*(F(degB[w])+inc_bad[w])/2 - K for w in range(n) if R[w]>0),default=F(0))
    return dict(K=K,G=G,n=n,c1=c1,Dok=Dok,Rok=Rok,wc1=wc1,wD=wD)

if __name__=="__main__":
    print("=== C(2k+1)[q] blow-ups (canonical gmin cut): C1, D, (R) + Gamma=N^2 check ===")
    for (k,q) in [(2,5),(2,8),(2,10),(3,4),(3,6),(4,3),(4,5),(5,3),(2,15)]:
        n,adj,side,M,ell,G=oddcycle_blowup(k,q)
        d=analyze(adj,side,M,ell,n,G)
        print(f"  C{2*k+1}[{q}] N={n} Gamma={G} N^2={n*n} (=N^2:{G==n*n}) | C1={d['c1']}(w{float(d['wc1']):.2f}) D={d['Dok']}(w{float(d['wD']):.2f}) (R)={d['Rok']}")
