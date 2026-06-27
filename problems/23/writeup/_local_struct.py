#!/usr/bin/env python3
"""For each near-tight witness vertex w, decompose R(w) and ell_max(w) by BFS-layer
structure. For each contributing bad edge f=(x,y) with a shortest cycle through w:
  d_x = d_B(x,w), d_y = d_B(y,w), d_x+d_y = ell(f)-1.
We want to understand the COUPLING that gives ell_max(w)*R(w) <= K = N+(N^2-Gamma).
Record: bdeg(w) (= # cut neighbors of w), the layer-by-layer geodesic counts,
and test candidate per-vertex inequalities.
"""
import subprocess
from collections import deque
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def Bdist(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def analyze_vertex(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    K=n+(n*n-G)
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    # per vertex w: R(w), ellmax(w), bdeg(w)
    rows=[]
    for w in range(n):
        R=F(0); ellmax=0; bdeg=sum(1 for u in adj[w] if side[u]!=side[w])
        contrib=[]
        for f in M:
            Ps=geo[f]; nf=len(Ps)
            cnt=sum(1 for P in Ps if w in P)
            if cnt:
                pf=F(cnt,nf); R+=pf
                if ell[f]>ellmax: ellmax=ell[f]
                # the layer split: among cycles through w, where does w sit?
                dx=Bdist(adj,side,f[0]).get(w,-1); dy=Bdist(adj,side,f[1]).get(w,-1)
                contrib.append((f,ell[f],pf,dx,dy))
        rows.append((w,R,ellmax,bdeg,contrib))
    return dict(n=n,G=G,K=K,side=side,M=M,ell=ell,rows=rows,g6=g6)

# find tightest per-vertex (max of ellmax*R) over census, check <= K
print("=== per-vertex ellmax(w)*R(w) vs K ; find worst ratio ===")
for nn in [8,9,10]:
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    worst=None
    for g6 in out:
        a=analyze_vertex(g6)
        if a is None: continue
        K=a['K']
        for (w,R,ellmax,bdeg,contrib) in a['rows']:
            val=ellmax*R
            slack=K-val
            if worst is None or slack<worst[0]:
                worst=(slack,g6,w,R,ellmax,bdeg,K,a['G'],a['n'],contrib)
    if worst:
        slack,g6,w,R,ellmax,bdeg,K,G,n,contrib=worst
        print(f"N={nn}: worst ellmax*R={ellmax}*{R}={ellmax*R}({float(ellmax*R):.3f}) K={K} slack={float(slack):.3f} bdeg(w)={bdeg} Gamma={G} g6={g6} w={w}")
        for (f,l,pf,dx,dy) in sorted(contrib,key=lambda x:-x[1]*x[2]):
            print(f"    f={f} ell={l} p_f={pf}({float(pf):.3f}) d_x(w)={dx} d_y(w)={dy} dx+dy={dx+dy}")
