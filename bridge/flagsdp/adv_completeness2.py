#!/usr/bin/env python3
"""COMPLETENESS-CRITIC v2 (N<=20 so harness is fast).

DANGEROUS FEATURE TARGETED: a TIGHT or NEAR-TIGHT config where the unique min-Gamma max cut
forces every bad edge's shortest geodesic to be LONG, AND peeling that geodesic either
(i) breaks CD on the remainder (cut-tight pocket exposed) or (iii) overshoots L>2|C|N-|C|^2.

Families:
 (E) C7[q],C9[q] balanced and slightly-unbalanced blow-ups (long geodesics ell=7,9): does the
     LONG geodesic ever fail (iii)? Bound 2|C|N-|C|^2 with |C|=7 or 9 is tight only at balance.
 (F) 'Pentagon prism / antiprism' triangle-free dense graphs (C5 x K2 -> Petersen is GP(5,2),
     and the pentagonal antiprism) at N<=20.
 (G) Blown-up odd cycle where ONE part is split so two adjacent bad edges share their geodesic
     -> peeling one leaves the other's geodesic re-routed LONGER (Gamma' drops less => L small,
     but maybe (i) CD fails because the shared part's CD slack is consumed).
 (H) C5[q] with an extra 'diameter' bad edge added inside a part-pair to make a SECOND ell-class
     while staying tight-ratio: forces the min-ell bad edge into a cut-tight pocket.
 (I) Mobius-Kantor / generalized Petersen near the densest triangle-free vertex-transitive at
     N<=20 with chords, scanning chord sets for high ratio.
"""
import sys
from peel_check import check_instance

def add(adj,u,v):
    adj[u].add(v); adj[v].add(u)

def report(tag, n, adj, side=None):
    r = check_instance(n, adj, side=side)
    g = r.get('gamma'); n2 = r.get('n2')
    ratio = (g/n2) if (g and n2) else None
    flag = ""
    if r.get('ok') and r.get('triangle_free') and r.get('B_connected') and r.get('ge_n2') \
       and r.get('m',0)>=2 and r.get('has_safe_peel') is False:
        flag = "  <<<<< OBSTRUCTION"
    rs = f"{ratio:.4f}" if ratio is not None else "None"
    print(f"{tag}: N={r.get('N')} m={r.get('m')} g={g} n2={n2} ratio={rs} "
          f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} Bconn={r.get('B_connected')} "
          f"tf={r.get('triangle_free')} sp={r.get('has_safe_peel')}{flag}", flush=True)
    if not r.get('triangle_free'):
        print(f"    detail: {r.get('detail')}", flush=True)
    return r

# ---- generic odd-cycle blow-up with arbitrary part sizes ----
def oddcycle_blowup(sizes):
    """sizes = list of part sizes around an odd cycle of length len(sizes)."""
    k=len(sizes); assert k%2==1 and k>=5
    starts=[0];
    for s in sizes: starts.append(starts[-1]+s)
    n=starts[-1]; adj=[set() for _ in range(n)]
    def part(i): return range(starts[i], starts[i+1])
    for i in range(k):
        j=(i+1)%k
        for u in part(i):
            for v in part(j):
                add(adj,u,v)
    return n,adj

# ---- pentagonal antiprism (C5 x K2 antiprism): 10 vertices, triangle-free? antiprism has triangles. skip ----
# Petersen GP(5,2): N=10, triangle-free, vertex-transitive, girth5.
def petersen():
    n=10; adj=[set() for _ in range(n)]
    for i in range(5):
        add(adj,i,(i+1)%5)          # outer C5
        add(adj,i,5+i)              # spoke
        add(adj,5+i,5+(i+2)%5)     # inner pentagram
    return n,adj

# ---- C5[q] base for family H/I ----
def C5q(q):
    n=5*q; adj=[set() for _ in range(n)]
    def V(i,a): return i*q+a
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add(adj,V(i,a),V((i+1)%5,b))
    return n,adj

if __name__=="__main__":
    print("=== (E) odd-cycle blow-ups: balanced + slightly unbalanced (long geodesics) ===")
    fams = [
        [2,2,2,2,2,2,2],         # C7[2] N=14 tight
        [2,2,2,2,2,2,2,2,2],     # C9[2] N=18 tight
        [3,2,2,2,2,2,2],         # C7 unbalanced one big part N=15
        [2,3,2,3,2,3,2],         # C7 alternating-ish N=17
        [3,3,2,2,2,2,2],         # N=16
        [2,2,2,2,2,2,3],         # N=15
        [1,2,2,2,2,2,2],         # C7 one thin part N=13 (thin -> geodesic forced through it)
        [1,3,1,3,1,3,1],         # C7 alternating thin/thick N=13
        [1,2,1,2,1,2,1],         # C7 N=10 thin alt
        [2,1,2,1,2,1,2,1,2],     # C9 thin alt N=14
    ]
    for s in fams:
        n,adj=oddcycle_blowup(s)
        report(f"oddblow{tuple(s)}", n, adj)

    print("=== (F) Petersen ===")
    n,adj=petersen(); report("Petersen", n, adj)
