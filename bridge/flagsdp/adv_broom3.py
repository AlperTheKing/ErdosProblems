#!/usr/bin/env python3
"""Broom gadgets: a C5[q] core with extra 'ear' vertices that create many high-ell bad edges
clustered on shared geodesic vertices. We sweep part-size profiles and ear placements and run
EVERY candidate through the harness. Report near-tight and obstructions."""
import itertools
from peel_check import check_instance
from adv_broom import mk, add, summarize, c5_blowup

results=[]
def test(name,n,adj):
    r,obstruction,near=summarize(name,n,adj,verbose=False)
    if obstruction:
        print(f"!!! OBSTRUCTION [{name}] {r}")
    results.append((name,r,obstruction,near))
    return r,obstruction,near

# Strategy A: unbalanced C5 blow-up. Gamma/N^2 ratio drops off balance, but let's map it,
# and find where safe_peel could fail near the balanced point.
print("=== Strategy A: unbalanced C5[q1..q5] sweep ===")
for qs in itertools.product(range(1,5),repeat=5):
    if sum(qs)>22: continue
    if max(qs)-min(qs)>2: continue  # near balanced
    n,adj,parts=c5_blowup(list(qs))
    r,obstruction,near=test(f"C5{qs}",n,adj)
    if near or obstruction:
        print(f"   near/obs C5{qs}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} "
              f"n2={r.get('n2')} safe_peel={r.get('has_safe_peel')} tight={r.get('tight')}")

# Strategy B: C5 (5 single vertices) with a 'broom' = extra leaf paths attached to one part.
# A pendant odd ear: attach a path of even B-length between two vertices of the same side to
# create a long bad edge. We attach several ears all rooted at the same core vertex.
print("\n=== Strategy B: C5 core + clustered odd ears (brooms) ===")
def c5_core_with_ears(num_ears, ear_len):
    """C5 on vertices 0..4 (cycle). Add num_ears ears; each ear is a path of length 'ear_len'
    (in graph edges) starting at vertex 0 and ending with a bad edge back near vertex 0's part.
    We make each ear a path 0 - a1 - a2 - ... and then a final 'chord' bad edge.
    Keep it simple: build an odd cycle through 0 for each ear (shares vertex 0)."""
    # base C5
    n=5; adj=mk(n)
    for i in range(5): add(adj,i,(i+1)%5)
    # each ear: a path from 0 of length ear_len edges back to 0's neighbor creating odd cycle
    for e in range(num_ears):
        prev=0
        for k in range(ear_len-1):
            adj.append(set()); w=len(adj)-1; n+=1
            add(adj,prev,w); prev=w
        # close ear back to vertex 1 (neighbor of 0) -> creates odd/even cycle through 0,1
        add(adj,prev,1)
    return n,adj

for num_ears in range(1,6):
    for ear_len in (4,6,8):
        n,adj=c5_core_with_ears(num_ears,ear_len)
        if n>24: continue
        r,obstruction,near=test(f"C5+ear(k={num_ears},len={ear_len})",n,adj)
        print(f"   C5+ear k={num_ears} len={ear_len}: N={r.get('N')} tf={r.get('triangle_free')} "
              f"Bconn={r.get('B_connected')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
              f"safe_peel={r.get('has_safe_peel')} | {r.get('detail')}")

print(f"\n{len(results)} instances tested; "
      f"{sum(1 for _,_,o,_ in results if o)} obstructions; "
      f"{sum(1 for _,_,o,nr in results if nr and not o)} near-tight.")
