#!/usr/bin/env python3
"""Analytical decomposition of T_uniform at the worst vertex, for the proof attempt.
For each graph, gmin cut; at argmax vertex v* record:
  - bdeg(v*) = B-degree (cross edges at v*)
  - contributing bad edges f with p_f(v*)>0: (ell, p_f, ell*p_f, dist x->v, v->y)
  - K, Gamma, N, maxT, slack
Goal: find what bounds sum_f ell(f) p_f(v) <= K.  EXACT Fractions.
"""
import sys, subprocess
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

def analyze(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    K=n+(n*n-G)
    # per-edge geodesics
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    T=[F(0) for _ in range(n)]
    contribs=[[] for _ in range(n)]  # per v: list of (f, ell, p_f)
    for f in M:
        Ps=geo[f]; nf=len(Ps)
        if nf==0: return None
        share=F(ell[f],nf)
        cnt=[0]*n
        for P in Ps:
            for v in set(P): cnt[v]+=1
        for v in range(n):
            if cnt[v]:
                pf=F(cnt[v],nf)
                T[v]+=ell[f]*pf
                contribs[v].append((f,ell[f],pf))
    maxT=max(T); vstar=max(range(n),key=lambda v:T[v])
    bdeg=[sum(1 for w in adj[v] if side[v]!=side[w]) for v in range(n)]
    return dict(n=n,G=G,K=K,maxT=maxT,vstar=vstar,T=T,bdeg=bdeg,
                contribs=contribs[vstar],side=side,M=M,ell=ell,g6=g6)

if __name__=='__main__':
    # quick targeted look at named near-tight witnesses from census
    targets = ['L?`DAboU`w@{hS']  # worst-slack N=13 dense
    # also pull a few low-slack from census N<=10
    for nn in [9,10]:
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        best=None
        for g6 in out:
            a=analyze(g6)
            if a is None: continue
            slack=a['K']-a['maxT']
            if best is None or slack<best[0]: best=(slack,g6)
        if best: targets.append(best[1])
    for g6 in targets:
        a=analyze(g6)
        if a is None: print(g6,"skip"); continue
        print(f"\n=== g6={a['g6']} N={a['n']} Gamma={a['G']} K={a['K']} maxT={a['maxT']}({float(a['maxT']):.3f}) slack={a['K']-a['maxT']}({float(a['K']-a['maxT']):.3f}) ===")
        v=a['vstar']
        print(f"  v*={v} bdeg(v*)={a['bdeg'][v]} #bad-edges-total={len(a['M'])} #contributing={len(a['contribs'])}")
        s=F(0)
        for (f,l,pf) in sorted(a['contribs'],key=lambda x:-x[1]*x[2]):
            print(f"    f={f} ell={l} p_f={pf}({float(pf):.3f}) ell*p_f={l*pf}({float(l*pf):.3f})")
            s+=l*pf
        print(f"  sum = {s} = maxT={a['maxT']}  (check {s==a['maxT']})")
        print(f"  bdeg distribution: {sorted(a['bdeg'],reverse=True)}")
