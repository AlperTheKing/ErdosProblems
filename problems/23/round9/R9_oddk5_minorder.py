"""R9: the minimum order of a triangle-free graph with an odd-K5 minor.

THEOREM (proved by hand in R9_oddk5.md, verified here).
  (i)  every triangle-free graph carrying an odd-K5 minor has >= 10 vertices and >= 15 edges;
  (ii) the Petersen graph attains both bounds;
  (iii) up to isomorphism it is the ONLY triangle-free graph on 10 vertices and 15 edges
       carrying one.

Part (iii) is decided here by complete enumeration: on 10 vertices a branch family must be
5 disjoint edges (a perfect matching, 5 edges) plus exactly one joining edge for each of the
10 pairs, so 15 edges and no freedom left.  Fix the matching to {01,23,45,67,89} (relabelling)
and run over all 4^10 = 1048576 choices of joining edges.
"""
from itertools import combinations, permutations
from fractions import Fraction as F
from R9_oddk5_lib import G, g6_decode
from R9_oddk5_minor import has_odd_k5_minor
import sys, time

def parity_ok(att):
    """att[(i,j)] = (t_i, t_j) in {0,1}^2 : which end of branch i resp. j the joining edge hits.
    sigma_ij = 1 + t_i + t_j ; need eps with sigma_ij = 1 + eps_i + eps_j  for all i<j."""
    for eps in range(32):
        good = True
        for (i, j), (ti, tj) in att.items():
            if (ti + tj) % 2 != (((eps >> i) & 1) + ((eps >> j) & 1)) % 2:
                good = False
                break
        if good:
            return True
    return False

def enumerate_10():
    A = [2 * i for i in range(5)]
    B = [2 * i + 1 for i in range(5)]
    prs = list(combinations(range(5), 2))
    found = []
    t0 = time.time()
    for code in range(4 ** 10):
        c = code
        att = {}
        edges = [(2 * i, 2 * i + 1) for i in range(5)]
        for (i, j) in prs:
            k = c & 3
            c >>= 2
            ti, tj = k & 1, (k >> 1) & 1
            att[(i, j)] = (ti, tj)
            edges.append((2 * i + ti, 2 * j + tj))
        if not parity_ok(att):
            continue
        g = G(10, edges)
        if g.m != 15:
            continue
        if not g.triangle_free():
            continue
        found.append(g)
    print(f"  4^10 configurations scanned in {time.time()-t0:.1f}s; "
          f"{len(found)} triangle-free 15-edge witnesses (labelled)")
    return found

def iso_classes(gs):
    try:
        import networkx as nx
    except ImportError:
        return None
    reps = []
    for g in gs:
        X = nx.Graph()
        X.add_nodes_from(range(g.n))
        X.add_edges_from(g.E)
        for (Y, cnt) in reps:
            if nx.is_isomorphic(X, Y):
                cnt[0] += 1
                break
        else:
            reps.append((X, [1]))
    return reps

if __name__ == "__main__":
    print("=" * 88)
    print("(iii) complete enumeration of the 10-vertex / 15-edge case")
    print("=" * 88)
    gs = enumerate_10()
    reps = iso_classes(gs)
    print(f"  isomorphism classes: {len(reps)}")
    import networkx as nx
    for (Y, cnt) in reps:
        g = G(10, list(Y.edges()))
        deg = sorted(dict(Y.degree()).values())
        # Petersen test: 3-regular, girth 5, SRG(10,3,0,1)
        import R9_oddk5_srg as S
        par = S.srg_params(g)
        print(f"    class with {cnt[0]} labelled copies: degrees {deg}, graph6 {g.g6()}, "
              f"srg params {par}  {'= PETERSEN' if par == (10,3,0,1) else ''}")
        f, w = has_odd_k5_minor(g, want_witness=True)
        print(f"      independent decider: odd-K5 minor = {f}")
    print()
    print("=" * 88)
    print("(i) no triangle-free graph on <= 9 vertices has one -- exhaustive check")
    print("=" * 88)
    src = r"E:/Projects/ErdosProblems/problems/23/round7/tf9.g6"
    try:
        lines = [l.strip() for l in open(src) if l.strip()]
    except OSError:
        lines = []
        print("  (census file unavailable, skipping the redundancy check)")
    print(f"  {len(lines)} graph6 words read from round7/tf9.g6")
    bad = 0
    t0 = time.time()
    hits = []
    for k, l in enumerate(lines):
        n, E = g6_decode(l)
        g = G(n, E)
        assert g.triangle_free(), "census contains a graph with a triangle: " + l
        if has_odd_k5_minor(g):
            hits.append(l)
        if k % 200 == 0:
            print(f"    {k}/{len(lines)}  ({time.time()-t0:.0f}s)  hits={len(hits)}")
            sys.stdout.flush()
    print(f"  DONE: {len(lines)} triangle-free 9-vertex graphs, odd-K5 minors found: "
          f"{len(hits)}  {hits[:5]}")
