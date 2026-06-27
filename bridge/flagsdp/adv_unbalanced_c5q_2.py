#!/usr/bin/env python3
"""Adversarial angle 2: unbalanced C5 blow-ups with PERTURBATIONS.
- internal non-edges removed differently per part (parts are independent sets normally;
  here we keep them independent but vary which cross-links exist -> sub-complete bipartite links)
- C7 / odd-cycle blow-ups (mixed odd-cycle) for cross-family signal
- near-tight extreme: balanced C5[q] with ONE link made sub-complete (delete edges)
We look for: tight (gamma=n2) m>=2 connected-B WITHOUT safe peel, and near-tight margins.
"""
import itertools, random
from peel_check import check_instance

def Ck_blowup(k, sizes, link_filter=None):
    """k-cycle blow-up. sizes len k. link_filter(i,a,b)->bool decides if part-i vertex a links part-(i+1) vertex b.
    Default: complete bipartite (all True)."""
    assert len(sizes)==k
    n=sum(sizes); off=[0]*k
    for i in range(1,k): off[i]=off[i-1]+sizes[i-1]
    adj=[set() for _ in range(n)]
    def pv(i): return range(off[i],off[i]+sizes[i])
    for i in range(k):
        j=(i+1)%k
        for ia,u in enumerate(pv(i)):
            for jb,v in enumerate(pv(j)):
                if link_filter is None or link_filter(i,ia,jb):
                    adj[u].add(v); adj[v].add(u)
    return n,adj

def fmt(tag,r):
    return (f"{tag} N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
            f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} Bconn={r.get('B_connected')} "
            f"safe={r.get('has_safe_peel')} | {r['detail']}")

obstructions=[]; near=[]; tested=0

print("=== C7 blow-ups (mixed odd cycle), balanced and unbalanced ===")
# C7[q]: gamma should = 49 q^2? Actually tight family is C5[q] (gamma=N^2) + odd cycles base.
for sizes in [(1,)*7,(2,)*7,(3,)*7,(2,2,2,2,2,2,1),(2,2,1,2,2,1,2),(3,2,2,2,2,2,2),(1,2,1,2,1,2,1)]:
    n=sum(sizes)
    if n>24: print(f"C7 {sizes} SKIP N={n}"); continue
    n,adj=Ck_blowup(7,sizes); r=check_instance(n,adj); tested+=1
    print(fmt(f"C7{sizes}",r))
    if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
        obstructions.append((f"C7{sizes}",r))
    if r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('B_connected'):
        near.append((r['n2']-r['gamma'],f"C7{sizes}",r))

print("\n=== C5[q] with ONE link edge-deleted (sub-complete) -> perturb tight family ===")
# Start from balanced C5[q], delete d edges from the link between part 0 and part 1.
for q in (3,4):
    n_full=5*q
    if n_full>22: continue
    for d in range(0, q*q):
        def lf(i,a,b,q=q,d=d):
            if i==0:  # link part0->part1
                # delete first d (a,b) pairs in row-major
                idx=a*q+b
                return idx>=d
            return True
        n,adj=Ck_blowup(5,(q,)*5,link_filter=lf); r=check_instance(n,adj); tested+=1
        if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
            obstructions.append((f"C5[{q}]-del{d}",r))
            print(fmt(f"C5[{q}]-del{d}",r)+" <<< OBSTRUCTION")
        if r.get('ok') and r.get('B_connected') and (r.get('m') or 0)>=2:
            near.append((r['n2']-r['gamma'],f"C5[{q}]-del{d}",r))
        if d<=4 or r.get('tight'):
            print(fmt(f"C5[{q}]-del{d}",r))

print("\n=== Random unbalanced C5 blow-ups with random sub-complete links (sizes 1..4) ===")
random.seed(23)
for trial in range(400):
    sizes=tuple(random.randint(1,4) for _ in range(5))
    n=sum(sizes)
    if n>22: continue
    # random link density per edge
    dens=random.choice([1.0,0.8,0.6])
    def lf(i,a,b,dens=dens):
        return random.random()<dens if dens<1.0 else True
    # need deterministic filter; precompute
    keep={}
    for i in range(5):
        for a in range(sizes[i]):
            for b in range(sizes[(i+1)%5]):
                keep[(i,a,b)]= (random.random()<dens)
    n,adj=Ck_blowup(5,sizes,link_filter=lambda i,a,b: keep[(i,a,b)]); r=check_instance(n,adj); tested+=1
    if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
        obstructions.append((f"rand{sizes}d{dens}",r))
        print(fmt(f"rand{sizes}d{dens}",r)+" <<< OBSTRUCTION")
    if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2:
        near.append((r['n2']-r['gamma'],f"rand{sizes}d{dens}",r))

print(f"\n=== SUMMARY === tested={tested} obstructions={len(obstructions)}")
near.sort()
print("Top near-tight m>=2 Bconn (smallest n2-gamma):")
seen=set(); cnt=0
for gap,tag,r in near:
    key=(gap,r.get('N'),r.get('m'))
    if key in seen: continue
    seen.add(key)
    print(f"  gap={gap} {fmt(tag,r)}")
    cnt+=1
    if cnt>=15: break
for tag,r in obstructions:
    print("OBSTRUCTION:", fmt(tag,r))
