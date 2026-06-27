#!/usr/bin/env python3
"""Mixed-ell PART 4: (A) minimal perturbations of tight C5[q] that inject a longer bad edge
while staying NEAR-tight; (B) random triangle-free max-cut search filtered to near-tight,
looking for any tight/near-tight instance with NO safe peel.

The lemma's hypothesis is gamma>=N^2 (tight). We hunt the boundary: deficit small + mixed ell.
"""
import random
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        has_safe_peel)

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%5,b))
    return n,adj,vid

best_neartight=[]   # (deficit, name, r)
def consider(name,n,adj,side=None):
    r=check_instance(n,adj,side=side)
    if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")): return r
    if r.get("m",0)<2: return r
    G=r.get("gamma"); n2=r.get("n2")
    if G is None: return r
    defc=n2-G
    if r.get("has_safe_peel")==False:
        print(f"  NO-PEEL {name}: N={n} m={r['m']} gamma={G} n2={n2} deficit={defc} tight={r['tight']}")
        if r.get("tight"):
            print(f"  *** OBSTRUCTION *** {name}")
    if defc<=0.10*n2:   # within 10% of tight
        best_neartight.append((defc,name,r))
    return r

# ---- A. C5[q]: remove a few cross edges to create a longer detour (inject ell=7) ----
# In C5[q], every bad (mono) edge is between part i and part i (same color) -> wait, mono edges
# are within-part? No: parts are independent sets. After the natural maxcut (colors alternate
# around the 5-cycle, but 5 is odd so one adjacency is mono). Let's just take C5[q] and DELETE
# some cross edges to elongate one geodesic, then re-evaluate.
def C5q_delete_cross(q, dels):
    n,adj,vid=C5q(q)
    for (i,a,j,b) in dels:
        u=vid(i,a); v=vid(j,b)
        adj[u].discard(v); adj[v].discard(u)
    return n,adj

# ---- B. random triangle-free graph, near max density, check near-tight ----
def random_tf(n, p, seed):
    rng=random.Random(seed)
    adj=[set() for _ in range(n)]
    edges=[(u,v) for u in range(n) for v in range(u+1,n)]
    rng.shuffle(edges)
    for (u,v) in edges:
        if rng.random()<p:
            # add only if keeps triangle-free
            if not (adj[u] & adj[v]):
                add_edge(adj,u,v)
    return n,adj

# ---- C. C5[q] with ONE part split into two parts at distance 2 (creates ell variation) ----
def C5q_split_part(q):
    # take C5[q], pick one vertex w in part0, detach it and reattach via a length-3 detour
    n,adj,vid=C5q(q)
    if q<2: return None
    w=vid(0,0)
    # remove w's edges to part1, reroute through 2 new vertices x,y: w-x-y-(part1 vertices)
    nbrs1=[vid(1,b) for b in range(q)]
    for u in nbrs1: adj[w].discard(u); adj[u].discard(w)
    x,y=len(adj),len(adj)+1
    adj.append(set()); adj.append(set())
    add_edge(adj,w,x); add_edge(adj,x,y)
    for u in nbrs1: add_edge(adj,y,u)
    return len(adj),adj

if __name__=="__main__":
    print("=== A. C5[q] delete-cross perturbations (inject longer geodesics) ===")
    # delete a single cross edge between part0 and part1
    for q in [3,4]:
        n,adj=C5q_delete_cross(q,[(0,0,1,0)])
        consider(f"C5[{q}] del(0,0-1,0)",n,adj)
        n,adj=C5q_delete_cross(q,[(0,0,1,0),(0,0,1,1)] if q>=2 else [])
        consider(f"C5[{q}] del2",n,adj)
    # delete a 'matching' of cross edges to lengthen many geodesics
    for q in [3,4]:
        dels=[(0,a,1,a) for a in range(q)]
        n,adj=C5q_delete_cross(q,dels)
        consider(f"C5[{q}] del-matching01",n,adj)

    print("\n=== C. C5[q] split-part detour (mixed ell) ===")
    for q in [3,4,5]:
        res=C5q_split_part(q)
        if res is None: continue
        n,adj=res
        if n>24:
            print(f"  C5[{q}] split-part skipped N={n}>24"); continue
        consider(f"C5[{q}] split-part",n,adj)

    print("\n=== B. random triangle-free near-dense graphs (hunt near-tight) ===")
    found=0
    for n in [12,14,16,18,20]:
        for p in [0.5,0.6,0.7]:
            for seed in range(40):
                nn,adj=random_tf(n,p,seed*100+n)
                r=consider(f"rand n={n} p={p} s={seed}",nn,adj)
    print("\n=== NEAR-TIGHT (deficit<=10% of n2) collected ===")
    best_neartight.sort()
    for defc,name,r in best_neartight[:25]:
        print(f"  deficit={defc} ({100*defc/r['n2']:.1f}%) {name}: N={r['N']} m={r['m']} "
              f"gamma={r['gamma']} n2={r['n2']} tight={r['tight']} safe_peel={r['has_safe_peel']}")
    print(f"\ntotal near-tight collected={len(best_neartight)}")
