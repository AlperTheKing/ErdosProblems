#!/usr/bin/env python3
"""COMPLETENESS-CRITIC adversarial angle for the safe-peel lemma (Erdos #23).

Most-dangerous-untested families:
 (A) Iterated / recursive C5 blow-up (C5 wreath C5[C5], C5[C5[q]]): the part-internal
     structure is itself C5-like, so a bad edge can be 'trapped' in a sub-pentagon whose
     ONLY B-geodesic between its endpoints exits and re-enters through a thin neck.
 (B) C5[q] with deleted cross-edges chosen to keep Gamma maximal while making the cut
     'fragile' (many alternative near-max cuts) -> (i) CD may fail on the peel remainder.
 (C) Generalized Mycielski / Kneser-type triangle-free graphs that are tight-ratio but NOT
     simple blow-ups (high odd-girth, every bad-edge geodesic forced LONG).
 (D) C5[q] 'pinched': two balanced blow-ups sharing a thick part, forcing every geodesic of
     a bad edge in one copy to be the local 5-cycle, but the SHARED part couples the two
     CD constraints so peeling breaks (i) for the other copy.
"""
from peel_check import check_instance, gamma_of, Bconnected, maxcut_all

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
          f"tf={r.get('triangle_free')} sp={r.get('has_safe_peel')}{flag}")
    if not r.get('triangle_free'):
        print(f"    detail: {r.get('detail')}")
    return r

def add(adj,u,v):
    adj[u].add(v); adj[v].add(u)

# ---------- (A) Iterated C5 blow-up: replace each of the 5 parts by an inner gadget ----------
def C5_of_gadget(inner_n, inner_adj_edges, inner_bipartite_side):
    """C5 wreath: 5 copies of an inner graph; between consecutive copies put the COMPLETE
    bipartite link respecting an inner 2-coloring so the whole thing stays triangle-free and
    the natural max cut alternates. inner_bipartite_side: 2-coloring of inner gadget (0/1).
    Cross link between copy i and copy i+1: connect inner-vertex a in copy i to inner-vertex b
    in copy i+1 iff inner_side[a]!=inner_side[b]? No -- to stay triangle-free with C5 parity we
    connect a(copy i) to b(copy i+1) for ALL a,b (complete bipartite between parts) only if that
    stays triangle-free. Complete link makes triangles if inner has edges. Instead: link only
    across matching color classes to avoid triangles."""
    pass  # superseded by explicit constructions below

# (A1) C5[C5]: 25 vertices, part i = an inner C5 (vertices i*5..i*5+4).
# Inner C5 edges are BAD candidates only if monochromatic under the global max cut.
# Cross link copy i -> copy i+1: complete bipartite would create triangles with inner C5 edges,
# so instead use a perfect-matching-free 'C5 product' link: connect a in copy i to b in copy i+1
# iff a==b (a clean matching) OR a,b adjacent-in-pentagon. We test a few link rules.
def C5_wreath(link_rule):
    n=25; adj=[set() for _ in range(n)]
    def V(i,a): return i*5+a
    # inner pentagons
    for i in range(5):
        for a in range(5):
            add(adj, V(i,a), V(i,(a+1)%5))
    for i in range(5):
        j=(i+1)%5
        for a in range(5):
            for b in range(5):
                if link_rule(a,b):
                    add(adj, V(i,a), V(j,b))
    return n,adj

# (D) Two C5[q] blow-ups sharing one thick part
def two_C5q_shared_part(q):
    """Copy1 parts P0..P4, Copy2 parts Q0..Q4, identify P0==Q0 (shared thick part, size q).
    Pentagon links P0-P1-P2-P3-P4-P0 and P0(=Q0)-Q1-Q2-Q3-Q4-Q0. Stays triangle-free (two C5s
    sharing one vertex-class -> the shared class has neighbors in P1,P4,Q1,Q4 which are mutually
    non-adjacent)."""
    # parts: shared S (q), then P1..P4 (q each), Q1..Q4 (q each) => total 9q
    n=9*q; adj=[set() for _ in range(n)]
    # index: S=0, P1=1,...,P4=4, Q1=5,...,Q4=8 (part index), vertex = part*q + a
    def V(p,a): return p*q+a
    def link(p1,p2):
        for a in range(q):
            for b in range(q):
                add(adj, V(p1,a), V(p2,b))
    # copy1 pentagon: S-P1-P2-P3-P4-S  (parts 0-1-2-3-4-0)
    link(0,1); link(1,2); link(2,3); link(3,4); link(4,0)
    # copy2 pentagon: S-Q1-Q2-Q3-Q4-S  (parts 0-5-6-7-8-0)
    link(0,5); link(5,6); link(6,7); link(7,8); link(8,0)
    return n,adj

# (B) Balanced C5[q] with k cross-edges deleted at chosen spots (try to keep ratio high, break CD)
def C5q(q):
    n=5*q; adj=[set() for _ in range(n)]
    def V(i,a): return i*q+a
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add(adj, V(i,a), V((i+1)%5,b))
    return n,adj

if __name__=="__main__":
    print("=== (D) two C5[q] sharing one thick part ===")
    for q in (1,2):
        n,adj=two_C5q_shared_part(q)
        report(f"twoC5q-shared q={q}", n, adj)

    print("=== (A) C5 wreath link rules ===")
    rules = {
        "match": lambda a,b: a==b,
        "shift1": lambda a,b: b==(a+1)%5,
        "shift2": lambda a,b: b==(a+2)%5,
        "match+shift2": lambda a,b: a==b or b==(a+2)%5,
    }
    for name,rule in rules.items():
        n,adj=C5_wreath(rule)
        report(f"C5wreath[{name}]", n, adj)
