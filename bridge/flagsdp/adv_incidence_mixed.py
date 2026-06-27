#!/usr/bin/env python3
"""Incidence-bipartite-plus, MIXED family.

Probe whether splicing the TIGHT gadget (a C5-blowup C5[q], Gamma=N^2 locally) onto
a high-girth bipartite Levi-type structure can produce a connected-B, triangle-free,
Gamma=N^2 (or near) instance with NO safe peel. Two mixed constructions:

(A) C5[q] with one part replaced/augmented by a short bipartite path gadget (raises
    some d_B without adding bad edges) -- keeps tightness pressure while making
    geodesics longer (so peeling a geodesic removes more vertices -> harder (iii)).

(B) Two C5 cycles sharing structure via a bipartite bridge (Levi-flavored), giving
    mixed bad-edge distances ell in {5, longer}.

We rely entirely on check_instance for the verdict.
"""
import itertools
from peel_check import check_instance, is_triangle_free, Bconnected, gamma_of, maxcut_all

def C5q_adj(q):
    n = 5 * q
    vid = lambda i, j: i * q + j
    adj = [set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u = vid(i, a); v = vid((i + 1) % 5, b)
                adj[u].add(v); adj[v].add(u)
    return n, adj, vid

def fresh(adj, k):
    """append k new isolated vertices, return new adj and the first new index."""
    base = len(adj)
    for _ in range(k):
        adj.append(set())
    return base

def link_bipartite(adj, A, B):
    """complete bipartite link between disjoint vertex lists A and B (all triangle-safe if A,B independent)."""
    for a in A:
        for b in B:
            adj[a].add(b); adj[b].add(a)

def constructionA(q, pathlen):
    """C5[q]; then take ONE bad edge's pair and lengthen the B-geodesic between two
    bad-edge endpoints by routing through a fresh bipartite path (raises d_B, Gamma)."""
    n, adj, vid = C5q_adj(q)
    # bad edges in C5[q] under the natural max cut are within-part NONE; actually
    # C5[q] bad edges arise because cut is the 5-cycle 2-coloring which is imperfect
    # (odd cycle). The harness finds them. We simply add a fresh bipartite path
    # connecting part 0 vertex 0 to part 2 vertex 0 to create extra long B-route.
    A = list(range(len(adj), len(adj)))  # placeholder
    # add a path of even length between vid(0,0) and vid(2,0) alternating sides
    prev = vid(0, 0)
    new0 = len(adj)
    for t in range(pathlen):
        w = len(adj); adj.append(set())
        adj[prev].add(w); adj[w].add(prev); prev = w
    # close to vid(2,0)
    adj[prev].add(vid(2, 0)); adj[vid(2, 0)].add(prev)
    return len(adj), adj

def constructionB(q):
    """Two disjoint C5[q] blowups joined by a single bipartite bridge edge set."""
    n1, adj1, vid1 = C5q_adj(q)
    n2, adj2, vid2 = C5q_adj(q)
    n = n1 + n2
    adj = [set(s) for s in adj1] + [set(x + n1 for x in s) for s in adj2]
    # bridge: connect part-0 of block1 to part-0 of block2 via two fresh vertices
    # to keep bipartite/triangle-free; just add complete-bipartite small link
    u = vid1(0, 0); v = n1 + vid2(0, 0)
    w = len(adj); adj.append(set())
    # u-w and w-v ... but u,v same "color" potentially; w bridges
    adj[u].add(w); adj[w].add(u)
    adj[w].add(v); adj[v].add(w)
    return len(adj), adj

if __name__ == "__main__":
    results = []
    print("=== Construction A: C5[q] + lengthened bipartite route ===")
    for q in (2, 3):
        for pathlen in (2, 4):
            n, adj = constructionA(q, pathlen)
            if n - 0 > 26:
                print(f"  q={q} pathlen={pathlen}: N={n} too big, skip auto"); continue
            r = check_instance(n, adj)
            results.append(("A", q, pathlen, r))
            print(f"  q={q} pathlen={pathlen}: N={r['N']} ok={r['ok']} tf={r.get('triangle_free')} "
                  f"Bconn={r.get('B_connected')} m={r.get('m')} gamma={r.get('gamma')} "
                  f"n2={r.get('n2')} tight={r.get('tight')} safe_peel={r.get('has_safe_peel')} | {r.get('detail')}")
    print("=== Construction B: two C5[q] + bridge ===")
    for q in (2, 3):
        n, adj = constructionB(q)
        if n > 26:
            print(f"  q={q}: N={n} too big, skip"); continue
        r = check_instance(n, adj)
        results.append(("B", q, None, r))
        print(f"  q={q}: N={r['N']} ok={r['ok']} tf={r.get('triangle_free')} "
              f"Bconn={r.get('B_connected')} m={r.get('m')} gamma={r.get('gamma')} "
              f"n2={r.get('n2')} tight={r.get('tight')} safe_peel={r.get('has_safe_peel')} | {r.get('detail')}")

    obstr = [t for t in results if t[3].get('ok') and t[3].get('triangle_free')
             and t[3].get('B_connected') and t[3].get('ge_n2')
             and t[3].get('m', 0) >= 2 and t[3].get('has_safe_peel') is False]
    print(f"\nOBSTRUCTIONS in mixed family: {len(obstr)}")
    for t in obstr:
        print("  ", t[:3], t[3]['detail'])
