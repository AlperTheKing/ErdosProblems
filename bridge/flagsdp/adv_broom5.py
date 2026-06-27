#!/usr/bin/env python3
"""Targeted brooms INSIDE the C5[q] tight family. We perturb C5[q] in ways that cluster
bad-edge mass on shared geodesics or create B-bottlenecks (so peeling disconnects remaining
bad edges -> (ii) fails) while keeping Gamma as high as possible. Run through harness +
peel-margin instrument."""
import itertools
from collections import Counter
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        bdistB, shortest_path_B)
from adv_broom import mk, add, c5_blowup, summarize
from adv_broom4 import peel_margins

results=[]
def test(name,n,adj,show=True):
    r,obstruction,near=summarize(name,n,adj,verbose=False)
    results.append((name,r,obstruction,near))
    if obstruction:
        print(f"!!! OBSTRUCTION [{name}]")
        peel_margins(name,n,adj)
    elif show and (near or r.get('tight')):
        print(f"[{name}] N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
              f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} safe_peel={r.get('has_safe_peel')} "
              f"ratio={(r.get('gamma') or 0)/(r.get('n2') or 1):.4f}")
    return r,obstruction,near

# ---- Broom 1: C5[q] with a missing matching inside one bipartite link (create longer geodesics)
# Removing some cross-edges between two parts forces some bad-edge geodesics to detour -> longer ell,
# but lowers maxcut so the gamma-min cut may flip. Sweep how many edges removed.
def c5_blowup_drop(qs, drops):
    """drops = list of (partA, idxA, partB, idxB) cross edges to delete from C5[q]."""
    n,adj,parts=c5_blowup(qs)
    for (a,ia,b,ib) in drops:
        u=parts[a][ia]; v=parts[b][ib]
        adj[u].discard(v); adj[v].discard(u)
    return n,adj,parts

print("=== Broom 1: C5[3] with cross-edges dropped (forces detour geodesics) ===")
n0,adj0,parts0=c5_blowup([3]*5)
# drop edges between part0 and part1 to lengthen geodesics passing there
import random
random.seed(1)
for ndrop in range(1,7):
    # drop a matching of size ndrop between part0,part1
    drops=[(0,k%3,1,(k)%3) for k in range(ndrop)]
    n,adj,parts=c5_blowup_drop([3]*5,drops)
    test(f"C5[3]-drop{ndrop}",n,adj)

# ---- Broom 2: attach an extra C5 sharing ONE part (two C5[q] glued at a part) -> bad edges of
# both lobes have geodesics through the shared part = a broom core.
print("\n=== Broom 2: two C5 lobes glued at a shared part (broom core) ===")
def two_c5_shared(q):
    """Parts A0..A4 form one C5[q]; parts B1..B4 + shared A0 form another C5[q]. Shared core=A0."""
    # We'll build 9 parts: A0(shared), A1,A2,A3,A4, B1,B2,B3,B4
    sizes=[q]*9
    parts=[]; nxt=0
    for s in sizes:
        parts.append(list(range(nxt,nxt+s))); nxt+=s
    n=nxt; adj=mk(n)
    A=[0,1,2,3,4]; B=[0,5,6,7,8]  # both cycles share part index 0
    for cyc in (A,B):
        for i in range(5):
            for u in parts[cyc[i]]:
                for v in parts[cyc[(i+1)%5]]:
                    add(adj,u,v)
    return n,adj,parts
for q in (1,2):
    n,adj,parts=two_c5_shared(q)
    if n<=22:
        test(f"2xC5-shared(q={q})",n,adj)

# ---- Broom 3: C5[q] PLUS extra bad edges within a part via an added vertex bridging two parts
#   add a vertex w adjacent to all of part1 and part4 (the two non-neighbors of part0 thru cycle)
#   -> w sits like an extra 'part0' but only in B; creates many bad edges sharing geodesics.
print("\n=== Broom 3: C5[q] + extra hub vertices duplicating a part (clustered bad edges) ===")
def c5_plus_hub(q, num_hubs):
    n,adj,parts=c5_blowup([q]*5)
    base=n
    for h in range(num_hubs):
        adj.append(set()); w=len(adj)-1; n+=1
        # hub behaves like an extra vertex of part0: adjacent to part1 and part4
        for v in parts[1]+parts[4]:
            add(adj,w,v)
    return n,adj,parts
for q in (2,3):
    for h in range(1,4):
        n,adj,parts=c5_plus_hub(q,h)
        if n>22: continue
        test(f"C5[{q}]+{h}hub",n,adj)

print(f"\n{len(results)} tested; {sum(1 for _,_,o,_ in results if o)} obstructions; "
      f"{sum(1 for _,_,o,nr in results if nr and not o)} near-tight.")
