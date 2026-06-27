#!/usr/bin/env python3
"""Push the broom toward tightness. Variants:
 (1) k-book of C5 lobes sharing ONE part (k ears -> many bad edges through a thin neck).
 (2) two C5[q] lobes sharing an EDGE (two consecutive parts) -> thicker but maybe higher ratio.
 (3) lobes sharing a part but with the OTHER parts blown up (q big) while neck stays size 1.
We want safe_peel False AND ratio as close to 1 as possible. Tight+False = obstruction.
"""
from peel_check import check_instance
from adv_broom import mk, add, c5_blowup
from adv_broom4 import peel_margins

results=[]
def full(name,n,adj,margins=False):
    r=check_instance(n,adj)
    g=r.get('gamma'); n2=r.get('n2')
    ratio=(g/n2) if (g and n2) else 0
    obstruction=(r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                 and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel") is False)
    flag="*** OBSTRUCTION ***" if obstruction else ("<<safe_peel False>>" if r.get('has_safe_peel') is False else "")
    print(f"[{name}] N={r.get('N')} tf={r.get('triangle_free')} Bconn={r.get('B_connected')} "
          f"m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} tight={r.get('tight')} "
          f"safe_peel={r.get('has_safe_peel')} {flag}")
    if obstruction or (margins and r.get('has_safe_peel') is False):
        peel_margins(name,n,adj)
    results.append((name,r,obstruction))
    return r

# (1) k-book of C5 lobes sharing one part (part 0 = neck). q controls lobe-part size.
def book_c5(k, q, neck=1):
    """neck part has 'neck' vertices; each lobe l contributes 4 fresh parts of size q forming a
    C5 with the shared neck part. Bad edges live in each lobe; geodesics pass through neck."""
    # parts: index 0 = neck (size neck). Then for each lobe 4 parts of size q.
    sizes=[neck]+[q]*(4*k)
    parts=[]; nxt=0
    for s in sizes:
        parts.append(list(range(nxt,nxt+s))); nxt+=s
    n=nxt; adj=mk(n)
    for l in range(k):
        cyc=[0, 1+4*l, 2+4*l, 3+4*l, 4+4*l]  # neck + 4 lobe parts -> C5
        for i in range(5):
            for u in parts[cyc[i]]:
                for v in parts[cyc[(i+1)%5]]:
                    add(adj,u,v)
    return n,adj,parts

print("=== (1) k-book of C5 lobes sharing one neck part (neck=1) ===")
for k in (2,3,4):
    for q in (1,2):
        n,adj,parts=book_c5(k,q,neck=1)
        if n>22: continue
        full(f"book(k={k},q={q},neck=1)",n,adj,margins=True)

print("\n=== (1b) neck size 2 (thicker neck) ===")
for k in (2,3):
    for q in (1,2):
        n,adj,parts=book_c5(k,q,neck=2)
        if n>22: continue
        full(f"book(k={k},q={q},neck=2)",n,adj)

# (2) two C5 lobes sharing an EDGE = two consecutive parts (parts 0,1 shared).
def two_c5_share_edge(q):
    # parts: 0,1 shared; lobe A uses 0,1,2,3,4 ; lobe B uses 0,1,5,6,7? No: a C5 needs the shared
    # edge 0-1 plus 3 more parts. cyc A: 0-1-2-3-4-0 ; cyc B: 0-1-5-6-7-0. Shared edge {0,1}.
    sizes=[q]*8
    parts=[]; nxt=0
    for s in sizes:
        parts.append(list(range(nxt,nxt+s))); nxt+=s
    n=nxt; adj=mk(n)
    for cyc in ([0,1,2,3,4],[0,1,5,6,7]):
        for i in range(5):
            for u in parts[cyc[i]]:
                for v in parts[cyc[(i+1)%5]]:
                    add(adj,u,v)
    return n,adj,parts

print("\n=== (2) two C5 lobes sharing an EDGE ===")
for q in (1,2):
    n,adj,parts=two_c5_share_edge(q)
    if n<=22: full(f"2xC5-shareEdge(q={q})",n,adj,margins=True)

# (3) shared single-vertex neck, lobes blown up large (neck stays 1)
print("\n=== (3) two lobes, neck part size 1, other lobe parts size q (max asymmetry) ===")
def two_lobe_thin_neck(q):
    # neck part 0 size 1; lobe A parts 1,2,3,4 size q; lobe B parts 5,6,7,8 size q
    sizes=[1]+[q]*8
    parts=[]; nxt=0
    for s in sizes:
        parts.append(list(range(nxt,nxt+s))); nxt+=s
    n=nxt; adj=mk(n)
    for cyc in ([0,1,2,3,4],[0,5,6,7,8]):
        for i in range(5):
            for u in parts[cyc[i]]:
                for v in parts[cyc[(i+1)%5]]:
                    add(adj,u,v)
    return n,adj,parts
for q in (1,2):
    n,adj,parts=two_lobe_thin_neck(q)
    if n<=22: full(f"2lobe-thinneck(q={q})",n,adj,margins=True)

print(f"\n{len(results)} tested; {sum(1 for _,_,o in results if o)} OBSTRUCTIONS.")
