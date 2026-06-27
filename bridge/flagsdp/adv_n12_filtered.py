#!/usr/bin/env python3
"""N=12 exhaustive but FILTERED: only run the (expensive) safe-peel check on instances whose
max-cut-min-Gamma ratio is high (>=0.80). Cheap pre-pass computes gamma via a lighter path.
Reports any tight/near-tight no-peel. The lemma only needs peels when gamma>=N^2, so high-ratio
is the only lemma-relevant regime."""
import time
import flag_engine
from peel_check import (is_triangle_free, maxcut_all, Bconnected, gamma_of, has_safe_peel)

N=12; N2=N*N

def bitmask_to_sets(n, A):
    adj=[set() for _ in range(n)]
    for u in range(n):
        m=A[u]; v=0
        while m:
            if m&1 and v!=u: adj[u].add(v)
            m>>=1; v+=1
    return adj

def best_cut_min_gamma(n, adj):
    mc,cuts=maxcut_all(n,adj)
    best=None
    for sd in cuts:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    return best

def main():
    gs=flag_engine.enumerate_graphs(N, triangle_free=True)
    t0=time.time()
    valid=0; maxr=0.0; near=0; checked_peel=0
    tight_list=[]; nopeel_hi=[]
    THRESH=0.80
    for (nn,A) in gs:
        adj=bitmask_to_sets(nn,A)
        # cheap: triangle-free is guaranteed by geng -t; skip redundant check
        best=best_cut_min_gamma(nn,adj)
        if best is None: continue
        G,M,sd=best
        if len(M)<2: continue
        valid+=1
        ratio=G/N2
        if ratio>maxr: maxr=ratio
        if ratio>=0.9: near+=1
        if ratio>=THRESH:
            sp,info=has_safe_peel(nn,adj,sd,M,G,nn)
            checked_peel+=1
            if G>=N2:
                tight_list.append((len(M),G,sp))
            if sp is False:
                edges=[(u,v) for u in range(nn) for v in sorted(adj[u]) if v>u]
                nopeel_hi.append((len(M),G,ratio,G>=N2,edges))
    print(f"[N=12] graphs={len(gs)} valid_m>=2_conn={valid} max_ratio={maxr:.5f} "
          f"ratio>=0.9:{near} peel_checked(ratio>={THRESH}):{checked_peel} t={time.time()-t0:.1f}s", flush=True)
    print(f"TIGHT (gamma>=144) m>=2 instances: {len(tight_list)}", flush=True)
    for (m,g,sp) in tight_list:
        print(f"   tight m={m} gamma={g} safe_peel={sp}", flush=True)
    print(f"high-ratio NO-PEEL instances (ratio>={THRESH}): {len(nopeel_hi)}", flush=True)
    obstr=0
    for (m,g,ratio,is_t,edges) in sorted(nopeel_hi,key=lambda x:-x[2]):
        mark='  <-- OBSTRUCTION' if is_t else ''
        if is_t: obstr+=1
        print(f"   m={m} gamma={g} ratio={ratio:.5f} tight={is_t}{mark}", flush=True)
        if is_t: print(f"      edges={edges}", flush=True)
    print(f"\nN=12 TOTAL OBSTRUCTIONS: {obstr}", flush=True)

if __name__=="__main__":
    main()
