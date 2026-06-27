#!/usr/bin/env python3
"""Mixed-ell brooms (odd-cycle lobes of length 5 and 7 sharing a neck) + randomized gluings.
Mixed ell means bad edges with different d_B (so different (d_B+1)^2 contributions) clustered on a
shared neck. Also random: glue several odd-cycle blow-up lobes at shared parts, random sizes."""
import random, itertools
from peel_check import check_instance, maxcut_all, Bconnected, gamma_of
from adv_broom import mk, add
from adv_broom4 import peel_margins

results=[]
def full(name,n,adj,margins=False):
    if n>23: return None
    r=check_instance(n,adj)
    g=r.get('gamma'); n2=r.get('n2'); ratio=(g/n2) if (g and n2) else 0
    obstruction=(r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                 and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel") is False)
    sp=r.get('has_safe_peel')
    if obstruction:
        print(f"!!! OBSTRUCTION [{name}] N={r.get('N')} m={r.get('m')} gamma={g} n2={n2}")
        peel_margins(name,n,adj)
    elif sp is False and ratio>=0.5:
        print(f"[{name}] N={r.get('N')} m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} sp=False")
        if margins: peel_margins(name,n,adj)
    results.append((name,r,obstruction,ratio,sp))
    return r

def odd_cycle_blowup_lobes(lobe_specs):
    """lobe_specs: list of (cycle_len, [part_sizes]) where part_sizes[0] is the SHARED neck part
    (all lobes share part index 0). Builds odd-cycle blow-ups glued at part 0."""
    neck_size=lobe_specs[0][1][0]
    parts=[list(range(neck_size))]; nxt=neck_size
    lobe_part_idx=[]
    for (clen,sizes) in lobe_specs:
        idxs=[0]  # shared neck
        for s in sizes[1:]:
            parts.append(list(range(nxt,nxt+s))); idxs.append(len(parts)-1); nxt+=s
        lobe_part_idx.append(idxs)
    n=nxt; adj=mk(n)
    for (clen,sizes),idxs in zip(lobe_specs,lobe_part_idx):
        L=len(idxs)
        for i in range(L):
            for u in parts[idxs[i]]:
                for v in parts[idxs[(i+1)%L]]:
                    add(adj,u,v)
    return n,adj,parts

print("=== mixed-ell: C5 lobe + C7 lobe sharing neck=1 ===")
# C5 lobe: 5 parts (1 neck + 4). C7 lobe: 7 parts (1 neck + 6). Sizes small.
for nq in (1,):
    for q5 in (1,2):
        for q7 in (1,):
            spec=[(5,[nq]+[q5]*4),(7,[nq]+[q7]*6)]
            n,adj,parts=odd_cycle_blowup_lobes(spec)
            full(f"C5(q{q5})+C7(q{q7})neck{nq}",n,adj,margins=True)

print("\n=== two C7 lobes sharing neck=1 ===")
for q in (1,2):
    spec=[(7,[1]+[q]*6),(7,[1]+[q]*6)]
    n,adj,parts=odd_cycle_blowup_lobes(spec)
    full(f"2xC7-neck1(q={q})",n,adj,margins=True)

print("\n=== three C5 lobes sharing neck=1 (broom with 3 ears) ===")
spec=[(5,[1,1,1,1,1])]*3
n,adj,parts=odd_cycle_blowup_lobes(spec)
full("3xC5-neck1",n,adj,margins=True)

print("\n=== randomized gluings (many odd-cycle lobes, random sizes, neck 1 or 2) ===")
random.seed(7)
best_false=[]
for trial in range(4000):
    nlobe=random.randint(2,4)
    neck=random.choice([1,1,1,2])
    specs=[]
    for _ in range(nlobe):
        clen=random.choice([5,7])
        psizes=[neck]+[random.randint(1,2) for _ in range(clen-1)]
        specs.append((clen,psizes))
    # ensure neck consistent
    specs=[(c,[neck]+s[1:]) for (c,s) in specs]
    try:
        n,adj,parts=odd_cycle_blowup_lobes(specs)
    except Exception:
        continue
    if n>21 or n<7: continue
    r=check_instance(n,adj)
    if not (r.get('ok') and r.get('B_connected')): continue
    if (r.get('m') or 0)<2: continue
    g=r.get('gamma'); n2=r.get('n2'); ratio=g/n2 if (g and n2) else 0
    sp=r.get('has_safe_peel')
    if r.get('ge_n2') and sp is False:
        print(f"!!! OBSTRUCTION random specs={specs}")
        peel_margins("rand-obs",n,adj)
    if sp is False:
        best_false.append((ratio,n,r.get('m'),g,n2,tuple((c,tuple(s)) for c,s in specs)))
best_false.sort(reverse=True)
print(f"  random safe_peel=False count={len(best_false)}; top ratios:")
for ratio,n,m,g,n2,specs in best_false[:8]:
    print(f"   ratio={ratio:.4f} N={n} m={m} gamma={g} n2={n2} specs={specs}")

print(f"\n{len(results)} explicit; obstructions(explicit)={sum(1 for *_,o,__,___ in [(x,)+t[1:] for x,t in enumerate(results)] if False)}")
print(f"OBSTRUCTIONS total flagged above; explicit results: {sum(1 for _,_,o,_,_ in results if o)}")
