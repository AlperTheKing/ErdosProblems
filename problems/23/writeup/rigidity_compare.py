#!/usr/bin/env python3
"""Clarify the relationship between:
  (a) tau* = LP optimum min over fractional cycle-splits x of max_v load_x(v)   [census_GPI.gpi_tau]
  (b) maxT_uniform = max_v T_uniform(v) with the UNIFORM split (each shortest cycle of f weight 1/nf)
and the bound K = N + (N^2 - Gamma).

U (the task's claim) is about (b): max_v T_uniform(v) <= K.
GPI needs (a): tau* <= K.  Since uniform split is ONE feasible x, tau* <= maxT_uniform.
So U (on uniform) is STRONGER than GPI.  We test when each is tight.
Report g6 where tau*=N but maxT_uniform>N (uniform NOT tight though LP is)."""
import subprocess
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG, gpi_tau

def adj_of(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def maxT_uniform(n,E):
    adj=adj_of(n,E)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0)]*n
    for (u,v) in M:
        Ps=geos(adj,side,u,v); nf=len(Ps); h=ell[(u,v)]; share=F(h,nf)
        cnt=[0]*n
        for P in Ps:
            for w in set(P): cnt[w]+=1
        T=[T[w]+share*cnt[w] for w in range(n)]
    return dict(n=n,G=G,K=n+(n*n-G),maxT=max(T),gammafull=(G==n*n))

import sys
for nn in range(5, (int(sys.argv[1]) if len(sys.argv)>1 else 11)+1):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    tot=0; u_viol=0; u_tight=0; u_tight_gfull=0; u_tight_other=[]
    lp_tight=0; lp_tight_not_u=[]
    worstU=F(-10**9)
    for g6 in out:
        n,E=dec(g6)
        d=maxT_uniform(n,E)
        if d is None: continue
        tot+=1
        # uniform check
        if d['maxT']>d['K']:
            u_viol+=1; print(f"  U-VIOLATION {g6} N={n} K={d['K']} maxT={d['maxT']}")
        if d['K']-d['maxT']>worstU: pass
        if d['maxT']==d['K']:
            u_tight+=1
            if d['gammafull']: u_tight_gfull+=1
            else: u_tight_other.append(g6)
        # LP check (float) for cross-ref
        rr=gpi_tau(n,E)
        if rr and not (isinstance(rr,tuple) and rr[0]=='LPfail'):
            G2,n2,tau,K2=rr
            if abs(tau-n2)<1e-6:
                lp_tight+=1
                # is uniform also tight (maxT==N)?  note K==N iff gammafull
                if not (d['gammafull'] and d['maxT']==n):
                    lp_tight_not_u.append((g6, str(d['maxT']), d['K'], d['gammafull']))
    print(f"N={nn}: tot={tot} | U:viol={u_viol} tight={u_tight}(gfull={u_tight_gfull},other={len(u_tight_other)}) | "
          f"LP:tau*=N count={lp_tight}, of which uniform-NOT-(tight&gfull)={len(lp_tight_not_u)}", flush=True)
    if u_tight_other: print(f"   U-tight but Gamma<N^2: {u_tight_other[:15]}")
    if lp_tight_not_u: print(f"   LP-tight(tau*=N) but uniform maxT>N [g6,maxT,K,gfull]: {lp_tight_not_u[:8]}")
