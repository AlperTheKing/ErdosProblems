#!/usr/bin/env python3
"""(iii)-direct attack: cluster many bad-edge geodesics through a shared core path C so that peeling C
removes a large L = sum of removed masses, while keeping remaining bad edges B-connected via alternate
routes (so (ii) holds and only (iii) can fail). We build inside larger C5[q] blow-ups where alternate
routes exist, and we ALSO scan ALL bad edges (the harness already does). Key new lever: make the core
part SMALL but the lobe parts that hang bad edges LARGE, so peeling the core removes many bad edges.
We also try forcing specific max cuts to maximize Gamma."""
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of, bdistB, shortest_path_B)
from adv_broom import mk, add, c5_blowup
from adv_broom4 import peel_margins

results=[]
def full(name,n,adj,side=None,margins=False):
    r=check_instance(n,adj,side=side)
    g=r.get('gamma'); n2=r.get('n2')
    ratio=(g/n2) if (g and n2) else 0
    obstruction=(r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                 and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel") is False)
    flag="*** OBSTRUCTION ***" if obstruction else ("<<SP False>>" if r.get('has_safe_peel') is False else "")
    print(f"[{name}] N={r.get('N')} tf={r.get('triangle_free')} Bconn={r.get('B_connected')} "
          f"m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} tight={r.get('tight')} "
          f"sp={r.get('has_safe_peel')} {flag}")
    if r.get('detail') and (not r.get('ok') or not r.get('B_connected')):
        print(f"      {r.get('detail')}")
    if margins and (obstruction or r.get('has_safe_peel') is False):
        peel_margins(name,n,adj)
    results.append((name,r,obstruction))
    return r

# Asymmetric C5 blow-up: ONE part big (call it the 'fan hub'), opposite parts also big so bad edges
# concentrate. In C5[q] the gamma-min cut places bad edges within parts. Make some parts size 1 (the
# 'spokes') and adjacent parts large (the 'fans'). Sweep size profiles, scan which beat ratio 0.62
# while staying safe_peel False.
print("=== asymmetric C5[a,b,c,d,e] profiles: find safe_peel=False with HIGH ratio ===")
import itertools
best=[]
for prof in itertools.product([1,2,3],repeat=5):
    if sum(prof)>20: continue
    if sum(prof)<7: continue
    n,adj,parts=c5_blowup(list(prof))
    r=check_instance(n,adj)
    if not (r.get('ok') and r.get('B_connected')): continue
    if (r.get('m') or 0)<2: continue
    g=r.get('gamma'); n2=r.get('n2'); ratio=g/n2 if (g and n2) else 0
    sp=r.get('has_safe_peel')
    if sp is False:
        best.append((ratio,prof,r.get('N'),r.get('m'),g,n2))
    if r.get('ge_n2') and sp is False:
        print(f"!!! OBSTRUCTION prof={prof}")
        peel_margins(f"C5{prof}",n,adj)
best.sort(reverse=True)
print(f"  asymmetric profiles with safe_peel=False: {len(best)}; top by ratio:")
for ratio,prof,N,m,g,n2 in best[:10]:
    print(f"   prof={prof} N={N} m={m} gamma={g} n2={n2} ratio={ratio:.4f}")

# Now: combine blow-up with a thin-neck bridge between two thick C5 lobes, varying neck=1 but lobes thick
print("\n=== thick lobes + thin neck (best of both: high mass per lobe, fragile neck) ===")
def thick_lobes_thin_neck(qlobe):
    # neck size 1 (part0). Lobe A: parts 1,2,3,4 size qlobe. Lobe B: parts 5,6,7,8 size qlobe.
    sizes=[1]+[qlobe]*8
    parts=[]; nxt=0
    for s in sizes: parts.append(list(range(nxt,nxt+s))); nxt+=s
    n=nxt; adj=mk(n)
    for cyc in ([0,1,2,3,4],[0,5,6,7,8]):
        for i in range(5):
            for u in parts[cyc[i]]:
                for v in parts[cyc[(i+1)%5]]:
                    add(adj,u,v)
    return n,adj,parts
for ql in (1,2):
    n,adj,parts=thick_lobes_thin_neck(ql)
    if n<=22: full(f"thicklobe-thinneck(q={ql})",n,adj,margins=True)

print(f"\n{len(results)} explicit tested; {sum(1 for _,_,o in results if o)} OBSTRUCTIONS.")
