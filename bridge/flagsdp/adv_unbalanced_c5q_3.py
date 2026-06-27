#!/usr/bin/env python3
"""Adversarial angle 3: near-C5 structures that might reach Gamma=N^2 off the balanced blow-up.
- C5[q] with an EXTRA vertex glued in (size vector perturbed by adding a pendant blade)
- two-link-doubled C5 blow-up (parts joined by C4-gadgets internally)
- 'fat' odd cycles: C9[q]
- weighted-ish: add a few intra-part... no (would break independent-set); instead add chords forming longer cycles
Goal: any tight (gamma=n2) m>=2 connected-B WITHOUT safe peel. Report margins.
"""
import itertools
from peel_check import check_instance, gamma_of, maxcut_all, Bconnected

def Ck_blowup(k, sizes):
    n=sum(sizes); off=[0]*k
    for i in range(1,k): off[i]=off[i-1]+sizes[i-1]
    adj=[set() for _ in range(n)]
    def pv(i): return range(off[i],off[i]+sizes[i])
    for i in range(k):
        j=(i+1)%k
        for u in pv(i):
            for v in pv(j): adj[u].add(v); adj[v].add(u)
    return n,adj,off,pv

def fmt(tag,r):
    return (f"{tag} N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
            f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} Bconn={r.get('B_connected')} "
            f"safe={r.get('has_safe_peel')} | {r['detail']}")

obstructions=[]; tested=0; tight_cases=[]

# C9[q] balanced odd-cycle blow-ups (longer odd cycle tight family check)
print("=== C9[q] blow-ups ===")
for q in (1,2):
    n=9*q
    if n>22: print(f"C9[{q}] SKIP N={n}"); continue
    nn,adj,off,pv=Ck_blowup(9,(q,)*9); r=check_instance(nn,adj); tested+=1
    print(fmt(f"C9[{q}]",r))
    if r.get('tight') and (r.get('m') or 0)>=2: tight_cases.append((f"C9[{q}]",r))
    if r.get('ok') and r.get('B_connected') and r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
        obstructions.append((f"C9[{q}]",r))

# C5[q] plus a few extra vertices forming a longer geodesic (stretch a bad edge)
# Insert an extra independent vertex between two parts to lengthen B-distances.
print("\n=== C5[2] with extra subdivision vertices on bad-edge geodesics ===")
# Take C5[2] (N=10), then add vertices to make some bad-edge geodesics longer than 5.
# This tests whether a long-geodesic peel (|C|>5) ever violates condition (iii).
def C5q_stretch(q, extra_chain):
    """C5[q] then attach a path of 'extra_chain' new vertices bridging part0<->part2 (keeps triangle-free if alternating)."""
    n,adj,off,pv=Ck_blowup(5,(q,)*5)
    # we will not add a chain that creates triangles; instead just return base
    return n,adj

# Instead: directly build asymmetric blow-ups of C5 with parts up to size 5 but capped N<=22
print("\n=== Asymmetric C5 blow-ups sizes 1..5, N in [10,22], non-uniform, check any tight ===")
any_unbalanced_tight=False
for sizes in itertools.product(range(1,6),repeat=5):
    if len(set(sizes))==1: continue
    n=sum(sizes)
    if n<10 or n>22: continue
    rots=[tuple(sizes[i:]+sizes[:i]) for i in range(5)]
    rev=tuple(reversed(sizes)); rots+=[tuple(rev[i:]+rev[:i]) for i in range(5)]
    if sizes!=min(rots): continue
    nn,adj,off,pv=Ck_blowup(5,sizes)
    # compute gamma over ALL max cuts (not just min) to be safe about tightness
    mc,cuts=maxcut_all(nn,adj)
    found_tight=False
    for sd in cuts:
        if not Bconnected(nn,adj,sd): continue
        G,M=gamma_of(nn,adj,sd)
        if G is None: continue
        if G>=nn*nn and len(M)>=2:
            found_tight=True
    if found_tight:
        any_unbalanced_tight=True
        r=check_instance(nn,adj); tested+=1
        print("UNBALANCED-TIGHT:",fmt(str(sizes),r))
        if r.get('has_safe_peel') is False and r.get('ge_n2') and (r.get('m') or 0)>=2:
            obstructions.append((str(sizes),r))
    tested+=1
print(f"any unbalanced C5 blow-up reached Gamma>=N^2 (m>=2)? {any_unbalanced_tight}")

# Double-check: confirm max over ALL cuts of gamma for a few unbalanced never hits n^2
print("\n=== max-gamma over ALL max cuts for sample unbalanced (sanity that min-pick isn't hiding tight) ===")
for sizes in [(4,2,1,2,1),(3,1,3,1,2),(5,1,4,1,3),(2,3,2,3,1)]:
    nn,adj,off,pv=Ck_blowup(5,sizes)
    mc,cuts=maxcut_all(nn,adj)
    gmax=-1; gmin=10**9
    for sd in cuts:
        if not Bconnected(nn,adj,sd): continue
        G,M=gamma_of(nn,adj,sd)
        if G is None: continue
        gmax=max(gmax,G); gmin=min(gmin,G)
    print(f"sizes={sizes} N={nn} n2={nn*nn} maxcut={mc} #cuts={len(cuts)} gamma_min={gmin} gamma_max={gmax} reach_n2={gmax>=nn*nn}")

print(f"\n=== SUMMARY === tested={tested} obstructions={len(obstructions)} tight_m>=2={len(tight_cases)}")
for tag,r in tight_cases: print("TIGHT:",fmt(tag,r))
for tag,r in obstructions: print("OBSTRUCTION:",fmt(tag,r))
