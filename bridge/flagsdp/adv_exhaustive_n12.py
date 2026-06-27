#!/usr/bin/env python3
"""Exhaustive geng scan N=8..12: for every triangle-free graph, compute max-cut-min-Gamma,
collect ALL m>=2 connected-B instances, report (a) max ratio seen, (b) every has_safe_peel False
instance with its ratio (esp. any tight one), (c) histogram of ratios near 1.
Writes results to stdout flushed per N. N=12 only if time permits (pass argv 'n12')."""
import sys, time
import flag_engine
from peel_check import check_instance, is_triangle_free

def bitmask_to_sets(n, A):
    adj=[set() for _ in range(n)]
    for u in range(n):
        m=A[u]; v=0
        while m:
            if m&1 and v!=u: adj[u].add(v)
            m>>=1; v+=1
    return adj

def scan(n, nopeel_log, top_log):
    gs=flag_engine.enumerate_graphs(n, triangle_free=True)
    t0=time.time(); cnt=0; max_ratio=0.0; near=0; nopeel=0; tight_nopeel=0
    for (nn,A) in gs:
        adj=bitmask_to_sets(nn,A)
        if not is_triangle_free(nn,adj): continue
        r=check_instance(nn,adj)
        if not (r.get("ok") and r.get("B_connected") and r.get("m",0)>=2 and r.get("gamma") is not None):
            continue
        cnt+=1
        ratio=r["gamma"]/r["n2"]
        if ratio>max_ratio: max_ratio=ratio
        if ratio>=0.9: near+=1
        if ratio>=0.999:
            top_log.append((nn,r["m"],r["gamma"],r["has_safe_peel"],ratio,A))
        if r["has_safe_peel"] is False:
            nopeel+=1
            edges=[(u,v) for u in range(nn) for v in sorted(adj[u]) if v>u]
            nopeel_log.append((nn,r["m"],r["gamma"],r["n2"],ratio,r["tight"],edges))
            if r["tight"]: tight_nopeel+=1
    print(f"[N={n}] graphs={len(gs)} valid_m>=2_conn={cnt} max_ratio={max_ratio:.5f} "
          f"ratio>=0.9:{near} nopeel:{nopeel} TIGHT_nopeel:{tight_nopeel} t={time.time()-t0:.1f}s", flush=True)

def main():
    nopeel_log=[]; top_log=[]
    ns=range(8,12)
    if len(sys.argv)>1 and sys.argv[1]=="n12":
        ns=range(8,13)
    for n in ns:
        scan(n, nopeel_log, top_log)

    print("\n=== TIGHT or ratio>=0.999 instances (the lemma-relevant ones) ===", flush=True)
    for (nn,m,gamma,sp,ratio,A) in top_log:
        print(f"  N={nn} m={m} gamma={gamma} ratio={ratio:.5f} safe_peel={sp}", flush=True)

    print(f"\n=== ALL has_safe_peel False instances (count={len(nopeel_log)}) ===", flush=True)
    nopeel_log.sort(key=lambda x:-x[4])
    obstr=0
    for (nn,m,gamma,n2,ratio,tight,edges) in nopeel_log[:40]:
        is_obstr = (gamma>=n2 and m>=2)
        if is_obstr: obstr+=1
        print(f"  N={nn} m={m} gamma={gamma} n2={n2} ratio={ratio:.5f} tight={tight}"
              f"{'  <-- OBSTRUCTION' if is_obstr else ''}", flush=True)
        if is_obstr:
            print(f"     edges={edges}", flush=True)
    print(f"\nTOTAL OBSTRUCTIONS (m>=2, tight gamma>=n2, no safe peel): {obstr}", flush=True)

if __name__=="__main__":
    main()
