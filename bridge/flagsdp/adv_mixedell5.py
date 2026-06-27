#!/usr/bin/env python3
"""Mixed-ell PART 5 (FAST): random TF graphs n<=16 only, flush output, hunt near-tight no-peel.
Plus a focused 'C5[q] with one elongated geodesic' family computing exact deficit."""
import sys, random
from peel_check import check_instance, gamma_of

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%5,b))
    return n,adj,vid

best=[]
def consider(name,n,adj):
    r=check_instance(n,adj)
    if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")): return r
    if r.get("m",0)<2: return r
    G=r.get("gamma"); n2=r.get("n2")
    if G is None: return r
    defc=n2-G
    if r.get("has_safe_peel")==False:
        print(f"  NO-PEEL {name}: N={n} m={r['m']} gamma={G} n2={n2} deficit={defc} tight={r['tight']}")
        sys.stdout.flush()
        if r.get("tight"): print(f"  *** OBSTRUCTION *** {name}")
    if defc<=0.12*n2:
        best.append((defc/n2,defc,name,r))
    return r

def random_tf(n,p,seed):
    rng=random.Random(seed)
    adj=[set() for _ in range(n)]
    edges=[(u,v) for u in range(n) for v in range(u+1,n)]
    rng.shuffle(edges)
    for (u,v) in edges:
        if rng.random()<p and not (adj[u]&adj[v]):
            add_edge(adj,u,v)
    return n,adj

if __name__=="__main__":
    print("=== random TF n<=16 (fast) ===", flush=True)
    for n in [11,12,13,14,15,16]:
        for p in [0.45,0.55,0.65,0.75]:
            for seed in range(60):
                nn,adj=random_tf(n,p,seed*131+n*7)
                consider(f"rand n={n} p={p} s={seed}",nn,adj)
        print(f"  done n={n}",flush=True)
    print("\n=== near-tight (deficit<=12%) ===",flush=True)
    best.sort()
    for frac,defc,name,r in best[:30]:
        print(f"  {100*frac:.1f}% def={defc} {name}: N={r['N']} m={r['m']} gamma={r['gamma']} "
              f"n2={r['n2']} tight={r['tight']} safe_peel={r['has_safe_peel']}",flush=True)
    print(f"total near-tight={len(best)}",flush=True)
