#!/usr/bin/env python3
"""Spectral / energy probe. Established identity: sum_w T_uniform(w)=Gamma, so avg T = Gamma/N.
Target U: max_w T(w) <= K = N + (N^2-Gamma).  Equivalently  max_w T(w) - Gamma/N <= N + (N^2-Gamma) - Gamma/N.
At C5[q]: T const = N = Gamma/N (since Gamma=N^2), so max-avg=0, deficit RHS = N+(N^2-Gamma)-Gamma/N = N+0-N=0. tight.

So U <=> (DEV):  max_w T(w) - Gamma/N  <=  (N^2-Gamma)(1 + 1/N).
LHS is the DEVIATION of the congestion from its mean; RHS is the Gamma-deficit (times ~1).
This is a spectral-flavored statement: deviation of a flow-congestion from uniform is controlled by N^2-Gamma.

We test (DEV) and several spectral proxies:
 - lambda2(B) (algebraic connectivity), lambda_max(L_B)
 - max effective resistance in B
 - relation of (max T - meanT) to N^2-Gamma
EXACT for T (Fractions); float for spectra.
"""
import io, contextlib, subprocess
from fractions import Fraction as F
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def analyze(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    Bed=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v]]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        for P in Ps:
            for v in P: T[v]+=F(ell[f],nf)
    K=n+(n*n-G)
    maxT=max(T)
    dev=maxT-F(G,n)              # max T - Gamma/N
    rhs_dev=F((n*n-G)*(n+1),n)   # (N^2-Gamma)(1+1/N)
    # spectra of B Laplacian
    L=np.zeros((n,n))
    for u,v in Bed:
        L[u,u]+=1;L[v,v]+=1;L[u,v]-=1;L[v,u]-=1
    ev=np.sort(np.linalg.eigvalsh(L))
    lam2=ev[1]; lammax=ev[-1]
    return dict(n=n,G=G,K=K,maxT=maxT,dev=dev,rhs_dev=rhs_dev,lam2=lam2,lammax=lammax,
                devok=(dev<=rhs_dev))

if __name__=="__main__":
    acc=dict(devfail=0,worst=F(-10**9),arg=None,cnt=0)
    rows=[]
    G=[(f"C5[{q}]",blow(q)) for q in (2,3,4)]+[("n8",dec("G?\x60F\x60w"))]
    for nn in range(5,8):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        G+=[(g6,dec(g6)) for g6 in out]
    for nm,(n,E) in G:
        d=analyze(n,E)
        if d is None: continue
        acc['cnt']+=1
        if not d['devok']: acc['devfail']+=1
        slack=d['rhs_dev']-d['dev']
        if d['dev']-d['rhs_dev']>acc['worst']:
            acc['worst']=d['dev']-d['rhs_dev']; acc['arg']=(nm,float(d['dev']),float(d['rhs_dev']),d['G'],d['n'])
        # record correlation of dev with lam2 at near-extremal (small slack)
        rows.append((nm,float(d['dev']),float(d['rhs_dev']),float(slack),d['lam2'],d['lammax'],d['G'],d['n'],float(d['maxT']),d['K']))
    print("(DEV): maxT-Gamma/N <= (N^2-Gamma)(1+1/N)  -- fails=%d/%d  worst(dev-rhs)=%.4f at %s"
          %(acc['devfail'],acc['cnt'],float(acc['worst']),acc['arg']))
    # tight rows
    rows.sort(key=lambda r:r[3])
    print("tightest (DEV) rows [nm dev rhs slack lam2 lammax Gamma N maxT K]:")
    for r in rows[:8]:
        print("  %-10s dev=%.3f rhs=%.3f slack=%.4f lam2=%.3f lammax=%.3f G=%d N=%d maxT=%.2f K=%d"%r)
