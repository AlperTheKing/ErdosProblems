#!/usr/bin/env python3
"""Probe the COUPLING that must tie high R(w) to Gamma-deficit. We test several candidate
electrical/combinatorial inequalities at the binding vertex, EXACT where possible, and report which
hold/fail across census + C5[q] + n8 + Mycielski. The decoupled bounds overshoot; we want a single
COUPLED Q(w) with ellmax(w)*R(w) <= K.

Candidate quantities at vertex w (over the gamma-min cut):
  Let F(w) = { bad edges f : some shortest cycle of f passes through w }  (the cycles touching w).
  For f in F(w): p_f(w) in (0,1], ell(f).
  R(w)=sum p_f(w),  T(w)=sum ell(f) p_f(w),  L=ellmax(w).

KEY STRUCTURAL FACTS to test:
 (A) Each shortest odd cycle through w uses exactly 2 B-edges at w (w has >=2 of its B-neighbors on the cycle).
     => "cycle-degree" at w <= deg_B(w). Count of cycle-incidences weighted by p.
 (B) sum_f p_f(w)*ell(f) = T(w); and the cycles through w partition into B-edge-pairs at w.
 (C) Candidate:  R(w) <= deg_B(w)  ? (each unit of R uses 2 half-edges at w, total half-edge load <= deg_B(w)??)
 (D) Candidate global: sum_w R(w) = sum_f ell(f) (each cycle has ell vertices) -- KNOWN identity.
 (E) Candidate: ellmax(w)*R(w) <= N + (deg_B(w)-correction)...
We just MEASURE these to find the true coupling.
"""
import io, contextlib
from fractions import Fraction as F
from collections import deque, defaultdict
import numpy as np, subprocess
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def info(n,E):
    adj=build_adj(n,E)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    n_=n
    degB=[0]*n
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v]: degB[u]+=1
    R=[F(0) for _ in range(n)]; T=[F(0) for _ in range(n)]; ellmax=[0]*n
    # cycle-degree at w: weighted count of (B-edge at w used by a cycle through w)
    halfedge=[F(0) for _ in range(n)]   # sum over cycles through w of p * (#cycle-B-edges at w)=2p
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        s1=F(1,nf)
        for P in Ps:
            cyc=P[:]            # path x..y; the cycle adds edge y-x
            # vertices on cycle = P (all distinct), edges = consecutive in P plus (P[-1],P[0])
            cl=set(cyc)
            for idx,v in enumerate(cyc):
                R[v]+=s1; T[v]+=s1*ell[f]
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
                # number of cycle-edges incident to v = 2 always (it's a cycle) -> halfedge += 2*s1
                halfedge[v]+=2*s1
    return dict(n=n,G=G,M=M,ell=ell,R=R,T=T,ellmax=ellmax,degB=degB,halfedge=halfedge,side=side,K=n+(n*n-G))

def check(name,n,E,acc):
    d=info(n,E)
    if d is None: return
    n=d['n']; K=d['K']
    for w in range(n):
        L=d['ellmax'][w]; Rw=d['R'][w]
        if Rw==0: continue
        lhs=L*Rw
        # candidate C: R(w) <= degB(w)?
        c_C = (Rw<=d['degB'][w])
        # halfedge(w)=2 R(w) always; so R(w)=halfedge/2. number of distinct B-edges at w used (weighted) <= degB
        acc['cnt']+=1
        if not c_C: acc['failC']+=1
        # record max of L*Rw / K
        ratio=float(lhs)/K
        if ratio>acc['maxratio']: acc['maxratio']=ratio; acc['arg']=(name,w,float(lhs),K,float(Rw),L,d['degB'][w])
        # is L*Rw <= K? must hold
        if lhs>K: acc['VIOL']+=1; acc['violarg']=(name,w,lhs,K)

if __name__=="__main__":
    acc=dict(cnt=0,failC=0,maxratio=0.0,arg=None,VIOL=0,violarg=None)
    for q in (2,3,4,5,6): check(f"C5[{q}]",*blow(q),acc=acc)
    check("n8",*dec("G?\x60F\x60w"),acc=acc)
    for nn in range(5,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); check(f"N{nn}",n,E,acc=acc)
    print("vertices checked:",acc['cnt'])
    print("R(w)<=degB(w) failures:",acc['failC'],"(if 0, candidate C holds)")
    print("L*R(w)>K violations:",acc['VIOL'], acc['violarg'])
    print("max ratio L*R/K =",acc['maxratio'],"at",acc['arg'])
