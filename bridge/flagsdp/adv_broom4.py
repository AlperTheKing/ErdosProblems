#!/usr/bin/env python3
"""Instrument the peel margins on C5[q] and blow-ups of odd cycles, to see how tight (iii) is and
whether a clustered/uneven blow-up can push some peel over the L<=bound line. Also build a
'clustered' blow-up: one part is large (the broom core) and bad edges concentrate there."""
import itertools
from collections import Counter
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        bdistB, shortest_path_B)
from adv_broom import mk, add, c5_blowup

def peel_margins(name,n,adj):
    """For the gamma-min connected-B max cut, list each bad edge's peel and L vs bound."""
    mc,cuts=maxcut_all(n,adj)
    best=None
    for sd in cuts:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    if best is None: print(f"[{name}] no cc max cut"); return
    G,M,sd=best
    print(f"[{name}] N={n} Gamma={G} N^2={n*n} m={len(M)} tight={G==n*n}")
    any_safe=False
    rows=[]
    for (u,v) in M:
        P=shortest_path_B(n,adj,sd,u,v)
        if P is None: continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep: continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; conn=True
        for (a,b) in Mp:
            d=bdistB(n,adj,sd,a,banned=C).get(b,-1)
            if d<0: conn=False; break
            Gp+=(d+1)**2
        bound=2*s*n-s*s
        L = (G-Gp) if conn else None
        rows.append((u,v,s,conn,L,bound, (L is not None and L<=bound)))
    rows.sort(key=lambda r:(r[3], (r[4] if r[4] is not None else 10**9)))
    for (u,v,s,conn,L,bound,iii) in rows[:8]:
        print(f"   bad({u},{v}) |C|={s} (ii)conn={conn} L={L} bound={bound} (iii)={iii}")
    return G,M,sd

if __name__=="__main__":
    print("=== C5[q] peel margins ===")
    for q in (2,3,4):
        n,adj,parts=c5_blowup([q]*5)
        peel_margins(f"C5[{q}]",n,adj)
    print("\n=== uneven blow-ups (one big core part) ===")
    for big in (3,4,5,6):
        qs=[big,1,1,1,1]
        if sum(qs)>22: continue
        n,adj,parts=c5_blowup(qs)
        peel_margins(f"C5{tuple(qs)}",n,adj)
    print("\n=== two big parts ===")
    for big in (2,3,4):
        qs=[big,big,1,1,1]
        if sum(qs)>22: continue
        n,adj,parts=c5_blowup(qs)
        peel_margins(f"C5{tuple(qs)}",n,adj)
