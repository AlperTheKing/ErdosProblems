"""AUDIT 4.  W'_{L,b} = C_L[b, b+1, 1,...,1, b+1, b], alternating colouring.
Independent verification of THEOREM 4.2, from the explicit graph (families) and by
exhaustive profile scan (small-set threshold).  Also computes bip(W') exactly-by-construction
to show how far the exhibited cut is from a maximum cut.
"""
import os
import sys
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import (blowup, sigma_set, sigma_by_recut, adj_of, is_triangle_free,
                      named_families, sharp_stars)


def pattern(L, b):
    sizes = [b] + [b + 1] + [1] * (L - 4) + [b + 1, b]
    assert len(sizes) == L
    col = [i % 2 for i in range(L)]
    edges = [(i, i + 1) for i in range(L - 1)] + [(0, L - 1)]
    return sizes, col, edges


def build(L, b):
    sizes, col, edges = pattern(L, b)
    N, E, part, start = blowup(edges, sizes)
    side = [col[part[v]] for v in range(N)]
    return N, E, part, side, sizes, col, edges


def sigma_profile(s, sizes, col, edges):
    tot = 0
    for (i, j) in edges:
        eps = 1 if col[i] != col[j] else -1
        tot += eps * (s[i] * (sizes[j] - s[j]) + s[j] * (sizes[i] - s[i]))
    return tot


def min_neg_by_size(sizes, col, edges, cap=None):
    """Exhaustive DFS over profiles: smallest sum(s) with sigma<0 (exact)."""
    h = len(sizes)
    best = [None]

    def rec(i, s):
        if best[0] is not None and sum(s) >= best[0][0]:
            # cannot prune blindly (sigma not monotone) - only prune on size
            pass
        if i == h:
            v = sigma_profile(s, sizes, col, edges)
            if v < 0:
                t = sum(s)
                if best[0] is None or t < best[0][0]:
                    best[0] = (t, tuple(s), v)
            return
        for t in range(sizes[i] + 1):
            s[i] = t
            rec(i + 1, s)
        s[i] = 0
    rec(0, [0] * h)
    return best[0]


def odd_girth(N, E):
    """BFS-based odd girth (small graphs)."""
    adj = adj_of(N, E)
    best = None
    for s in range(N):
        dist = {s: 0}
        q = [s]
        while q:
            nq = []
            for u in q:
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        nq.append(w)
                    elif dist[w] == dist[u]:
                        c = dist[u] + dist[w] + 1
                        if best is None or c < best:
                            best = c
            q = nq
    return best


def main():
    print("=== W'_{L,b}: basic data, triangle-freeness, odd girth, families, threshold ===")
    for (L, b) in [(9, 8), (9, 12), (11, 10), (11, 14), (9, 15)]:
        N, E, part, side, sizes, col, edges = build(L, b)
        M = [e for e in E if side[e[0]] == side[e[1]]]
        tf = is_triangle_free(N, E)
        og = odd_girth(N, E) if N <= 60 else None
        print(f"\n  L={L} b={b}: sizes={sizes}  N={N} |E|={len(E)} |M|={len(M)} (b^2={b*b})")
        print(f"    triangle-free={tf}  odd girth={og}  25|M|={25*len(M)} vs N^2={N*N} -> "
              f"{'BEATS N^2/25' if 25*len(M) > N*N else 'no'}")
        # families computed on the explicit graph
        worst = {}
        for name, S in named_families(N, E, side):
            v = sigma_set(S, E, side)
            if name not in worst or v < worst[name][0]:
                worst[name] = (v, tuple(sorted(part[u] for u in S)))
        for name, S in sharp_stars(N, E, side, cap=None):
            v = sigma_set(S, E, side)
            if name not in worst or v < worst[name][0]:
                worst[name] = (v, None)
        # independent sets: supports = independent sets of C_L
        mn = None
        h = len(sizes)
        adjH = [set() for _ in range(h)]
        for (i, j) in edges:
            adjH[i].add(j); adjH[j].add(i)
        for r in range(1, h + 1):
            for T in combinations(range(h), r):
                if any(a in adjH[bb] for a in T for bb in T):
                    continue
                for t in product(*[range(sizes[i] + 1) for i in T]):
                    s = [0] * h
                    for k, i in enumerate(T):
                        s[i] = t[k]
                    val = sigma_profile(s, sizes, col, edges)
                    if mn is None or val < mn[0]:
                        mn = (val, tuple(s))
        worst["independent set"] = mn
        wp = None
        for i in range(h):
            s = [0] * h
            s[i] = sizes[i]
            val = sigma_profile(s, sizes, col, edges)
            if wp is None or val < wp[0]:
                wp = (val, tuple(s))
        worst["one whole part"] = wp
        for k in sorted(worst):
            flag = "  <== VIOLATED" if worst[k][0] < 0 else ""
            print(f"      min sigma over {k:22s} = {worst[k][0]}{flag}")
        neg = min_neg_by_size(sizes, col, edges)
        print(f"    smallest improving switch set: |S| = {neg[0]} (profile {neg[1]}, sigma={neg[2]})"
              f"   -> all |S| <= {neg[0]-1} = {(neg[0]-1)/N:.4f}N have sigma>=0")
        # bip(W') upper bound: alternate colours, make the monochromatic pair the cheapest edge
        prods = []
        for (i, j) in edges:
            prods.append(sizes[i] * sizes[j])
        print(f"    bip(W') <= min over pattern edges of n_i n_j = {min(prods)}   "
              f"(exhibited cut has |M| = {len(M)}; ratio = {len(M)/min(prods):.1f}x)")

    print("\n=== cross-check profile formula against the explicit graph (L=9,b=2 small) ===")
    N, E, part, side, sizes, col, edges = build(9, 2)
    bad = 0
    import random
    rng = random.Random(1)
    for _ in range(20000):
        S = {v for v in range(N) if rng.random() < 0.5}
        s = [0] * len(sizes)
        for v in S:
            s[part[v]] += 1
        if not (sigma_set(S, E, side) == sigma_profile(s, sizes, col, edges)
                == sigma_by_recut(S, E, side)):
            bad += 1
    print(f"  N={N}: random-subset mismatches = {bad} / 20000")


if __name__ == "__main__":
    main()
