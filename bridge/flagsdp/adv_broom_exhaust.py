#!/usr/bin/env python3
"""Deterministic EXHAUSTIVE enumeration of broom gluings (2 lobes), all part-size profiles up to a
budget, neck in {1,2,3}, cycle lengths in {3,5,7}. This systematically covers the broom design space.
Report obstructions (tight & safe_peel False) and the max ratio among safe_peel=False instances."""
import itertools, sys
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

tested=0; obstr=0; best_false=0.0; best_false_spec=None
best_overall=0.0; best_overall_spec=None
for neck in (1,2,3):
    for c1,c2 in itertools.combinations_with_replacement((3,5,7),2):
        # part sizes for non-neck parts in each lobe, sizes 1..3, but cap total
        for s1 in itertools.product((1,2,3),repeat=c1-1):
            for s2 in itertools.product((1,2,3),repeat=c2-1):
                spec=[(c1,[neck]+list(s1)),(c2,[neck]+list(s2))]
                n=neck+sum(s1)+sum(s2)
                if n>16: continue
                adjpack=odd_cycle_blowup_lobes(spec)
                n,adj,parts=adjpack
                r=check_instance(n,adj)
                if not (r.get('ok') and r.get('B_connected')): continue
                if (r.get('m') or 0)<2: continue
                tested+=1
                g=r.get('gamma'); n2=r.get('n2'); ratio=g/n2 if (g and n2) else 0
                sp=r.get('has_safe_peel')
                if ratio>best_overall:
                    best_overall=ratio; best_overall_spec=(n,r.get('m'),g,n2,r.get('tight'),sp,spec)
                if r.get('ge_n2') and sp is False:
                    obstr+=1
                    print(f"!!! OBSTRUCTION spec={spec} N={n} m={r.get('m')} gamma={g} n2={n2}", flush=True)
                if sp is False and ratio>best_false:
                    best_false=ratio; best_false_spec=(n,r.get('m'),g,n2,spec)
print(f"# EXHAUSTIVE 2-lobe brooms: tested={tested} obstructions={obstr}", flush=True)
print(f"# max ratio among safe_peel=False = {best_false:.4f} spec={best_false_spec}", flush=True)
print(f"# max ratio overall = {best_overall:.4f} spec={best_overall_spec}", flush=True)
