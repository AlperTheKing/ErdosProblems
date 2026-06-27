#!/usr/bin/env python3
"""Adversarial near-tight search for the safe-peel lemma (Erdos #23 delta=0).
Angle: random-near-tight. Generate triangle-free graphs (exhaustive geng for N<=12,
random for N=13..18), compute max cut MINIMIZING Gamma, rank by Gamma/N^2 among
m>=2 connected-B instances, test the top ones for a safe peel.
Report top instances and any obstruction (m>=2, tight, has_safe_peel False)."""
import sys, random, time
from collections import deque
import flag_engine
from peel_check import check_instance, is_triangle_free, maxcut_all, Bconnected, gamma_of

random.seed(20230626)

def bitmask_to_sets(n, A):
    adj=[set() for _ in range(n)]
    for u in range(n):
        m=A[u]
        v=0
        while m:
            if m&1:
                if v!=u: adj[u].add(v)
            m>>=1; v+=1
    return adj

def random_triangle_free(n, tries_factor=4):
    """Random maximal-ish triangle-free graph: shuffle all pairs, add edge if no triangle."""
    adj=[set() for _ in range(n)]
    pairs=[(u,v) for u in range(n) for v in range(u+1,n)]
    random.shuffle(pairs)
    for (u,v) in pairs:
        # adding uv makes triangle iff common neighbor
        if adj[u]&adj[v]: continue
        # probabilistic thinning to vary density
        adj[u].add(v); adj[v].add(u)
    return adj

def random_triangle_free_p(n, p):
    """Random triangle-free with edge-acceptance prob p (sparser, more varied structure)."""
    adj=[set() for _ in range(n)]
    pairs=[(u,v) for u in range(n) for v in range(u+1,n)]
    random.shuffle(pairs)
    for (u,v) in pairs:
        if random.random()>p: continue
        if adj[u]&adj[v]: continue
        adj[u].add(v); adj[v].add(u)
    return adj

def evaluate(n, adj):
    """Return dict if it's a valid m>=2 connected-B instance, else None. Fast pre-filter."""
    if not is_triangle_free(n,adj): return None
    r=check_instance(n,adj)
    if not r.get("ok"): return None
    if not r.get("B_connected"): return None
    if r.get("m",0)<2: return None
    if r.get("gamma") is None: return None
    return r

def main():
    results=[]  # (ratio, N, m, gamma, has_safe_peel, side, adj, source)
    # ---- Exhaustive geng for small N ----
    for n in range(5, 13):
        t0=time.time()
        gs=flag_engine.enumerate_graphs(n, triangle_free=True)
        cnt=0
        for (nn,A) in gs:
            adj=bitmask_to_sets(nn,A)
            r=evaluate(nn,adj)
            if r is None: continue
            ratio=r["gamma"]/r["n2"]
            results.append((ratio, nn, r["m"], r["gamma"], r["has_safe_peel"], r["side"], adj, f"geng{n}"))
            cnt+=1
        print(f"[geng N={n}] graphs={len(gs)} valid_m>=2_conn={cnt} t={time.time()-t0:.1f}s", flush=True)

    # ---- Random for larger N ----
    for n in range(13, 19):
        t0=time.time(); cnt=0; trials=3000
        for it in range(trials):
            if it%3==0:
                adj=random_triangle_free(n)
            else:
                adj=random_triangle_free_p(n, p=random.choice([0.4,0.55,0.7,0.85,1.0]))
            r=evaluate(n,adj)
            if r is None: continue
            ratio=r["gamma"]/r["n2"]
            results.append((ratio, n, r["m"], r["gamma"], r["has_safe_peel"], r["side"], adj, f"rand{n}"))
            cnt+=1
        print(f"[rand N={n}] trials={trials} valid_m>=2_conn={cnt} t={time.time()-t0:.1f}s", flush=True)

    # ---- Rank ----
    results.sort(key=lambda x:-x[0])
    print("\n=== TOP 25 by Gamma/N^2 (m>=2, B-connected) ===")
    obstructions=[]
    seen=set()
    for (ratio,n,m,gamma,sp,side,adj,src) in results[:60]:
        key=(n,m,gamma,sp)
        # dedup display a bit
        print(f"ratio={ratio:.5f} N={n} m={m} gamma={gamma} n2={n*n} tight={gamma==n*n} safe_peel={sp} src={src}")
        if sp is False and gamma>=n*n and m>=2:
            obstructions.append((n,m,gamma,side,adj,src))

    print("\n=== TIGHT (gamma==N^2) m>=2 instances and their peel status ===")
    tights=[r for r in results if r[3]==r[1]*r[1]]
    tight_nopeel=0
    for (ratio,n,m,gamma,sp,side,adj,src) in tights:
        if sp is False:
            tight_nopeel+=1
    print(f"total tight m>=2 conn instances: {len(tights)}; with NO safe peel: {tight_nopeel}")

    # near-tight no-peel (ratio high but maybe not exactly tight) -- any safe_peel False at all?
    nopeel=[r for r in results if r[4] is False]
    print(f"\n=== ANY instance with has_safe_peel False (any ratio): {len(nopeel)} ===")
    nopeel.sort(key=lambda x:-x[0])
    for (ratio,n,m,gamma,sp,side,adj,src) in nopeel[:20]:
        print(f"  NOPEEL ratio={ratio:.5f} N={n} m={m} gamma={gamma} tight={gamma==n*n} src={src}")

    print(f"\nOBSTRUCTIONS (tight, m>=2, no safe peel): {len(obstructions)}")
    for (n,m,gamma,side,adj,src) in obstructions[:5]:
        print(f"  N={n} m={m} gamma={gamma} side={side}")
        # print adjacency edges for reproduction
        edges=[(u,v) for u in range(n) for v in sorted(adj[u]) if v>u]
        print(f"    edges={edges}")

if __name__=="__main__":
    main()
