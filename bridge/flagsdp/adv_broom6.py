#!/usr/bin/env python3
"""Print full ratios for the broom families so we can see how near-tight we can get and where (iii)
margin is smallest. Also the 'two C5 glued at a part' is the canonical broom: verify it and probe
its peel margins in detail (this is where a peel might disconnect remaining bad edges)."""
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of, bdistB, shortest_path_B)
from adv_broom import mk, add, c5_blowup
from adv_broom4 import peel_margins
from adv_broom5 import two_c5_shared, c5_plus_hub, c5_blowup_drop

def full(name,n,adj):
    r=check_instance(n,adj)
    g=r.get('gamma'); n2=r.get('n2')
    ratio=(g/n2) if (g and n2) else 0
    print(f"[{name}] N={r.get('N')} tf={r.get('triangle_free')} Bconn={r.get('B_connected')} "
          f"m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} tight={r.get('tight')} "
          f"safe_peel={r.get('has_safe_peel')}")
    return r

print("=== two-C5-shared ratios ===")
for q in (1,2):
    n,adj,parts=two_c5_shared(q)
    if n<=22: full(f"2xC5-shared(q={q})",n,adj)

print("\n=== C5[q]+hub ratios ===")
for q in (2,3):
    for h in (1,2,3):
        n,adj,parts=c5_plus_hub(q,h)
        if n<=22: full(f"C5[{q}]+{h}hub",n,adj)

print("\n=== C5[3]-drop ratios + margins (does a peel disconnect a remaining bad edge?) ===")
for ndrop in range(1,5):
    drops=[(0,k%3,1,(k)%3) for k in range(ndrop)]
    n,adj,parts=c5_blowup_drop([3]*5,drops)
    full(f"C5[3]-drop{ndrop}",n,adj)
