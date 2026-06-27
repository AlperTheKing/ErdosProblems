#!/usr/bin/env python3
"""Honest detail on the Mycielskians: max(L-bound) over ALL geodesics was the WRONG statistic (the safe-peel
lemma needs the BEST geodesic, not all). Report: (1) does a SAFE peel exist (has_safe_peel)? (2) min(L-bound)
over ALL shortest geodesics (is there ANY geodesic with L<=bound?) (3) per-bad-edge: does EVERY bad edge have a
safe geodesic, or only SOME (the right-choice question)? (4) max(L-bound) for context."""
import sys
from mycielskian_check import (mycielskian, edges_of, gamma_min_cut, all_shortest_geos, bdistB, D_of)

def detail(name, N, adj):
    E=edges_of(adj); e=len(E)
    res,mc=gamma_min_cut(N,adj,E)
    side,G,M=res; beta=len(M)
    print(f"\n=== {name}: N={N} e={e} beta={beta} Gamma={G} N^2={N*N} deficit={N*N-G} ===",flush=True)
    # per bad edge: does it have a SAFE geodesic (D=0, connected, L<=bound)?  + min/max (L-bound)
    glob_min=None; glob_max=None; safe_geos=0; total_geos=0
    bad_with_safe=0; bad_total=0
    for (u,v) in M:
        bad_total+=1; has_safe=False
        for C in all_shortest_geos(N,adj,side,u,v):
            total_geos+=1
            Cset=set(C); keep=set(x for x in range(N) if x not in Cset)
            Mp=[(a,b) for (a,b) in M if a in keep and b in keep]; Gp=0; conn=True
            for (a,b) in Mp:
                dd=bdistB(N,adj,side,a,banned=Cset).get(b,-1)
                if dd<0: conn=False; break
                Gp+=(dd+1)**2
            if not conn: continue
            L=G-Gp; bound=2*len(C)*N-len(C)**2; diff=L-bound
            glob_min=diff if glob_min is None else min(glob_min,diff)
            glob_max=diff if glob_max is None else max(glob_max,diff)
            d=D_of(N,adj,side,M,C)
            if d==0 and L<=bound:
                has_safe=True; safe_geos+=1
        if has_safe: bad_with_safe+=1
    print(f"    SAFE peel exists (some bad edge, D=0+conn+L<=bound)? {bad_with_safe>0}  "
          f"(bad edges with a safe geodesic: {bad_with_safe}/{bad_total}; safe geodesics: {safe_geos}/{total_geos})",flush=True)
    print(f"    L-bound over connected geodesics: min={glob_min}  max={glob_max}  "
          f"=> mass bound holds for the BEST geodesic? {glob_min is not None and glob_min<=0}; "
          f"FAILS on some geodesic? {glob_max is not None and glob_max>0}",flush=True)

if __name__=="__main__":
    C5=[(i,(i+1)%5) for i in range(5)]
    grot_N, grot_adj = mycielskian(5, C5); grot_edges=edges_of(grot_adj)
    pet_adj=[set() for _ in range(10)]
    for i in range(5):
        for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet_adj[a].add(b); pet_adj[b].add(a)
    pet_edges=edges_of(pet_adj)
    w=sys.argv[1] if len(sys.argv)>1 else "both"
    if w in ("pet","both"):
        N,adj=mycielskian(10,pet_edges); detail("M(Petersen)",N,adj)
    if w in ("grot","both"):
        N,adj=mycielskian(11,grot_edges); detail("M(Grotzsch)",N,adj)
    print("\nDONE",flush=True)
