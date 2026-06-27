#!/usr/bin/env python3
"""Inspect the bad-edge / geodesic structure of C5[q] and unbalanced blow-ups,
then build broom variants. Goal: high-ell bad edges clustered on few core vertices."""
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        bdistB, shortest_path_B)
from adv_broom import mk, add, summarize, c5_blowup

def inspect(name, n, adj):
    mc,cuts=maxcut_all(n,adj)
    # mimic check_instance's choice: connected-B max cut minimizing gamma
    best=None
    for sd in cuts:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    if best is None:
        print(f"[{name}] no connected-B max cut"); return
    G,M,sd=best
    print(f"[{name}] N={n} maxcut={mc} Gamma={G} N^2={n*n} m={len(M)}")
    # per-bad-edge ell distribution
    from collections import Counter
    ells=Counter()
    for (u,v) in M:
        d=bdistB(n,adj,sd,u).get(v,-1)
        ells[d+1]+=1
    print(f"        ell(=d_B+1) histogram: {dict(sorted(ells.items()))}")

if __name__=="__main__":
    for q in (2,3):
        n,adj,parts=c5_blowup([q]*5)
        inspect(f"C5[{q}]", n,adj)
