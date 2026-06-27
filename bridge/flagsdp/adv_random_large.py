#!/usr/bin/env python3
"""Random near-tight search for N=13..18. Generate many triangle-free graphs (random edge
addition rejecting triangles + density-biased toward C5-blowup-like structure), compute
max-cut-min-Gamma, log high-ratio and no-peel instances. Flushes per-N."""
import sys, random, time
from peel_check import check_instance, is_triangle_free

random.seed(424242)

def random_triangle_free(n, p):
    adj=[set() for _ in range(n)]
    pairs=[(u,v) for u in range(n) for v in range(u+1,n)]
    random.shuffle(pairs)
    for (u,v) in pairs:
        if random.random()>p: continue
        if adj[u]&adj[v]: continue
        adj[u].add(v); adj[v].add(u)
    return adj

def random_bipartite_plus(n):
    """Random near-bipartite: random 2-coloring, dense cross edges, then a few same-side edges."""
    side=[random.randint(0,1) for _ in range(n)]
    adj=[set() for _ in range(n)]
    pairs=[(u,v) for u in range(n) for v in range(u+1,n)]
    random.shuffle(pairs)
    for (u,v) in pairs:
        # prefer cross edges; allow occasional same-side (bad) edge
        cross = side[u]!=side[v]
        pr = 0.8 if cross else 0.12
        if random.random()>pr: continue
        if adj[u]&adj[v]: continue
        adj[u].add(v); adj[v].add(u)
    return adj

def main():
    best_overall=(0.0,None)
    for n in range(13,19):
        t0=time.time(); cnt=0; maxr=0.0; near=0; nopeel=0; tight_nopeel=0
        nopeel_examples=[]
        trials=4000
        # keep<=22 means shortest geodesic length s>= n-22; for n<=18 always fine (s>=1)
        for it in range(trials):
            mode=it%3
            if mode==0: adj=random_triangle_free(n, random.choice([0.5,0.7,0.9,1.0]))
            else:       adj=random_bipartite_plus(n)
            if not is_triangle_free(n,adj): continue
            r=check_instance(n,adj)
            if not (r.get("ok") and r.get("B_connected") and r.get("m",0)>=2 and r.get("gamma") is not None):
                continue
            cnt+=1; ratio=r["gamma"]/r["n2"]
            if ratio>maxr: maxr=ratio
            if ratio>best_overall[0]: best_overall=(ratio,(n,r["m"],r["gamma"]))
            if ratio>=0.9: near+=1
            if r["has_safe_peel"] is False:
                nopeel+=1
                if r["tight"]: tight_nopeel+=1
                if ratio>=0.85 and len(nopeel_examples)<5:
                    edges=[(u,v) for u in range(n) for v in sorted(adj[u]) if v>u]
                    nopeel_examples.append((r["m"],r["gamma"],r["n2"],ratio,r["tight"],edges))
        print(f"[N={n}] trials={trials} valid={cnt} max_ratio={maxr:.5f} ratio>=0.9:{near} "
              f"nopeel:{nopeel} TIGHT_nopeel:{tight_nopeel} t={time.time()-t0:.1f}s", flush=True)
        for (m,g,n2,ratio,tight,edges) in nopeel_examples:
            print(f"   NOPEEL-HI N={n} m={m} gamma={g} n2={n2} ratio={ratio:.5f} tight={tight} edges={edges}", flush=True)
    print(f"\nbest_overall ratio={best_overall[0]:.5f} at {best_overall[1]}", flush=True)

if __name__=="__main__":
    main()
