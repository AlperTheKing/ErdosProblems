#!/usr/bin/env python3
"""Fast capped randomized broom search (n<=16, flushed output). Glue odd-cycle blow-up lobes at a
shared neck part; vary lobe count, cycle lengths (5,7), part sizes, neck size. Looking for ANY
tight (ge_n2) safe_peel=False (= obstruction). Also report the max Gamma/N^2 among safe_peel=False."""
import random, sys
from peel_check import check_instance
from adv_broom import mk, add

def odd_cycle_blowup_lobes(lobe_specs):
    neck_size=lobe_specs[0][1][0]
    parts=[list(range(neck_size))]; nxt=neck_size
    lobe_part_idx=[]
    for (clen,sizes) in lobe_specs:
        idxs=[0]
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

random.seed(12345)
obstr=0; best_false=0.0; best_false_spec=None; tested=0
for trial in range(20000):
    nlobe=random.randint(2,4)
    neck=random.choice([1,1,1,2])
    specs=[]
    for _ in range(nlobe):
        clen=random.choice([5,5,7])
        psizes=[neck]+[random.randint(1,2) for _ in range(clen-1)]
        specs.append((clen,psizes))
    n,adj,parts=odd_cycle_blowup_lobes(specs)
    if n>16 or n<7: continue
    r=check_instance(n,adj)
    if not (r.get('ok') and r.get('B_connected')): continue
    if (r.get('m') or 0)<2: continue
    tested+=1
    g=r.get('gamma'); n2=r.get('n2'); ratio=g/n2 if (g and n2) else 0
    sp=r.get('has_safe_peel')
    if r.get('ge_n2') and sp is False:
        obstr+=1
        print(f"!!! OBSTRUCTION specs={specs} N={n} m={r.get('m')} gamma={g} n2={n2}", flush=True)
    if sp is False and ratio>best_false:
        best_false=ratio; best_false_spec=(n,r.get('m'),g,n2,specs)
print(f"# tested={tested} obstructions={obstr} max_ratio_safe_peel_False={best_false:.4f} "
      f"spec={best_false_spec}", flush=True)
