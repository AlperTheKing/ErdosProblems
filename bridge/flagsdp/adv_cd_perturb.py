#!/usr/bin/env python3
"""Targeted high-ratio probe: start from balanced/unbalanced C5[q] and apply small random EDITS
(add/remove a few edges, subdivide a link, merge parts) staying triangle-free, searching for any
config that (a) stays ge_n2/near-tight AND (b) has no safe peel AND ideally (c) fails via (i)CD.
This concentrates samples in the only region that ever gets near tight."""
import random, sys
from peel_check import (gamma_of, Bconnected, maxcut_all, bdistB,
                        shortest_path_B, cut_dom, is_triangle_free, check_instance)

def C5q(q):
    n=5*q; adj=[set() for _ in range(n)]
    def V(i,a): return i*q+a
    for i in range(5):
        for a in range(q):
            for b in range(q):
                adj[V(i,a)].add(V((i+1)%5,b)); adj[V((i+1)%5,b)].add(V(i,a))
    return n,adj

def oddblow(sizes):
    k=len(sizes); st=[0]
    for s in sizes: st.append(st[-1]+s)
    n=st[-1]; adj=[set() for _ in range(n)]
    def part(i): return range(st[i],st[i+1])
    for i in range(k):
        j=(i+1)%k
        for u in part(i):
            for v in part(j):
                adj[u].add(v); adj[v].add(u)
    return n,adj

def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def full_modes(n,adj):
    r=check_instance(n,adj)
    return r

def edit_and_test(base_fn, base_args, n_edits, iters, seed):
    random.seed(seed)
    n,adj0=base_fn(*base_args)
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    best=(-1.0,None)   # highest-ratio no-safe-peel
    obstr=[]
    for it in range(iters):
        adj=[set(a) for a in adj0]
        ne=random.randint(1,n_edits)
        for _ in range(ne):
            i,j=random.choice(pairs)
            if j in adj[i]:
                adj[i].discard(j); adj[j].discard(i)
            else:
                if not (adj[i]&adj[j]):   # keep triangle-free
                    adj[i].add(j); adj[j].add(i)
        if not tri_free(n,adj): continue
        r=check_instance(n,adj)
        if not (r.get("ok") and r.get("B_connected")): continue
        if r.get("m",0)<2: continue
        g=r.get("gamma"); n2=r.get("n2"); ratio=g/n2
        if r.get("has_safe_peel") is False:
            if ratio>best[0]:
                edges=[(i,j) for i in range(n) for j in adj[i] if j>i]
                best=(ratio,(r.get("m"),g,n2,edges,r.get("side")))
            if r.get("ge_n2"):
                edges=[(i,j) for i in range(n) for j in adj[i] if j>i]
                obstr.append((r.get("m"),g,n2,edges,r.get("side")))
    return best,obstr

if __name__=="__main__":
    q=int(sys.argv[1]) if len(sys.argv)>1 else 3
    iters=int(sys.argv[2]) if len(sys.argv)>2 else 30000
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 0
    print(f"perturbing C5[{q}] (N={5*q}) with up to 4 edits, {iters} samples...")
    best,obstr=edit_and_test(C5q,(q,),4,iters,seed)
    print(f"  best no-safe-peel ratio={best[0]:.4f}  info={best[1]}")
    print(f"  obstructions(ge_n2,no-peel)={len(obstr)}")
    for o in obstr[:5]: print("   OBSTRUCTION", o)
