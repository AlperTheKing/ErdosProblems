#!/usr/bin/env python3
"""Adversarial angle: UNBALANCED C5 blow-ups.
5 parts of sizes (q0..q4) in the 5-cycle of complete bipartite links.
Vary the size vector; report Gamma vs N^2 and whether shortest-geodesic peel stays safe.
"""
import itertools
from peel_check import check_instance

def C5_blowup(sizes):
    """sizes = (q0,q1,q2,q3,q4); part i links completely to part (i+1)%5."""
    n = sum(sizes)
    # offsets
    off = [0]*5
    for i in range(1,5):
        off[i] = off[i-1] + sizes[i-1]
    adj = [set() for _ in range(n)]
    def part_vertices(i):
        return range(off[i], off[i]+sizes[i])
    for i in range(5):
        j = (i+1)%5
        for u in part_vertices(i):
            for v in part_vertices(j):
                adj[u].add(v); adj[v].add(u)
    return n, adj

def fmt(sizes, r):
    return (f"sizes={sizes} N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} "
            f"n2={r.get('n2')} tight={r.get('tight')} ge_n2={r.get('ge_n2')} "
            f"Bconn={r.get('B_connected')} safe={r.get('has_safe_peel')} | {r['detail']}")

if __name__=="__main__":
    obstructions = []
    near_tight = []
    tested = 0

    # 1. All balanced (sanity, tight family): q=1..4
    print("=== BALANCED (tight family C5[q]) ===")
    for q in range(1,5):
        sizes=(q,q,q,q,q)
        n,adj=C5_blowup(sizes)
        if n>26:
            print(f"sizes={sizes} SKIP N={n}>26"); continue
        r=check_instance(n,adj); tested+=1
        print(fmt(sizes,r))
        if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
            obstructions.append((sizes,r))

    # 2. Specific unbalanced examples from the prompt
    print("\n=== SPECIFIC UNBALANCED ===")
    specifics = [(3,1,1,1,1),(4,2,1,2,1),(5,1,4,1,3),(2,2,1,1,1),(3,2,2,1,1),
                 (1,1,1,1,2),(2,1,1,1,1),(3,3,3,3,2),(4,4,4,4,3),(2,2,2,2,1),
                 (3,3,3,2,2),(2,2,2,1,1),(4,4,3,3,2)]
    for sizes in specifics:
        n,adj=C5_blowup(sizes)
        if n>26:
            print(f"sizes={sizes} SKIP N={n}>26"); continue
        r=check_instance(n,adj); tested+=1
        print(fmt(sizes,r))
        if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
            obstructions.append((sizes,r))
        if r.get('ok') and r.get('B_connected') and r.get('gamma') is not None and r.get('n2'):
            gap=r['n2']-r['gamma']
            near_tight.append((gap,sizes,r))

    # 3. Exhaustive small unbalanced: all size vectors with entries 1..4, N<=24, not all equal
    print("\n=== EXHAUSTIVE entries 1..4, N<=24, non-uniform ===")
    for sizes in itertools.product(range(1,5),repeat=5):
        if len(set(sizes))==1: continue   # skip balanced (done above)
        n=sum(sizes)
        if n>24 or n<5: continue
        # canonical: avoid rotational/reflection duplicates by taking lexicographically smallest rotation+reflection
        rots = [tuple(sizes[i:]+sizes[:i]) for i in range(5)]
        rev = tuple(reversed(sizes))
        rots += [tuple(rev[i:]+rev[:i]) for i in range(5)]
        if sizes != min(rots): continue
        n,adj=C5_blowup(sizes)
        r=check_instance(n,adj); tested+=1
        flag=""
        if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
            obstructions.append((sizes,r)); flag=" <<< OBSTRUCTION"
        if r.get('ok') and r.get('B_connected') and r.get('gamma') is not None and r.get('n2'):
            gap=r['n2']-r['gamma']
            near_tight.append((gap,sizes,r))
        # only print obstructions and ge_n2 cases to keep output short
        if flag or r.get('ge_n2'):
            print(fmt(sizes,r)+flag)

    print(f"\n=== SUMMARY ===")
    print(f"tested={tested}")
    print(f"obstructions={len(obstructions)}")
    near_tight.sort()
    print("Closest-to-tight (smallest n2-gamma), top 12 with m>=2 and Bconn:")
    cnt=0
    for gap,sizes,r in near_tight:
        if (r.get('m') or 0)>=2 and r.get('B_connected'):
            print(f"  gap={gap} {fmt(sizes,r)}")
            cnt+=1
            if cnt>=12: break
    for sizes,r in obstructions:
        print("OBSTRUCTION:", fmt(sizes,r))
