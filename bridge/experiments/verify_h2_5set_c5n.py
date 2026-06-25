#!/usr/bin/env python3
"""
Resolve synthesis-vs-critic contradiction on H2 (the 5-set peeling lemma) at the
extremal family C5[n].

H2 (the goal's peeling lemma): for triangle-free G on 5n vertices,
    EXISTS S, |S|=5, with  beta(G) <= beta(G-S) + (2n-1).
Equivalently: min over 5-sets S of  [beta(G) - beta(G-S)]  <=  2n-1.

Synthesis (Attack 6): the DIAGONAL 5-set of C5[n] gives drop = 2n-1 exactly
  (n=1->1, n=2->3) -> H2 holds with EQUALITY at C5[n].
Completeness critic: "all 220 5-sets of C5[2] give drop 4 > 3=2n-1" -> H2 FAILS
  at C5[2].  (The critic admitted a MaxCut bug in its own harness this round.)

These contradict. This script computes, over ALL C(5n,5) 5-sets:
    min drop, mean drop, max drop, and whether min drop == 2n-1.
beta is computed by EXACT brute-force MaxCut (2^V), no heuristics.
"""
import itertools


def build_c5n(n):
    """C5[n]: parts 0..4 each an independent set of size n; complete bipartite
    between consecutive parts (mod 5). Vertex index = part*n + j."""
    V = 5 * n
    edges = []
    for p in range(5):
        q = (p + 1) % 5
        for j in range(n):
            u = p * n + j
            for k in range(n):
                v = q * n + k
                edges.append((u, v))
    return V, edges


def maxcut(verts, edges):
    """Exact MaxCut over the induced subgraph on `verts` (a list of original
    vertex ids). Brute force 2^|verts|, fixing the first vertex to one side."""
    idx = {v: i for i, v in enumerate(verts)}
    m = len(verts)
    # adjacency as bitmasks over compact indices
    adj = [0] * m
    E = 0
    for (a, b) in edges:
        if a in idx and b in idx:
            ia, ib = idx[a], idx[b]
            adj[ia] |= (1 << ib)
            adj[ib] |= (1 << ia)
            E += 1
    if m == 0:
        return 0, 0
    best = 0
    # fix vertex 0 on side 0 -> iterate 2^(m-1) over the rest
    for half in range(1 << (m - 1)):
        side1 = half << 1  # bit i set => vertex i on side 1; vertex 0 = side 0
        cut = 0
        x = side1
        while x:
            low = x & (-x)
            v = low.bit_length() - 1
            cut += bin(adj[v] & ~side1).count('1')
            x ^= low
        if cut > best:
            best = cut
    return best, E


def beta(verts, edges):
    mc, E = maxcut(verts, edges)
    return E - mc


def main():
    for n in (1, 2, 3, 4):
        V, edges = build_c5n(n)
        allv = list(range(V))
        bG = beta(allv, edges)
        target = 2 * n - 1
        drops = []
        # iterate all 5-subsets
        for S in itertools.combinations(allv, 5):
            Sset = set(S)
            rem = [v for v in allv if v not in Sset]
            bRem = beta(rem, edges)
            drops.append(bG - bRem)
        mn, mx = min(drops), max(drops)
        mean = sum(drops) / len(drops)
        n_at_target = sum(1 for d in drops if d == target)
        n_below = sum(1 for d in drops if d <= target)
        print(f"n={n}  V={V}  beta(C5[n])={bG}  (n^2={n*n})  target 2n-1={target}")
        print(f"   #5-sets={len(drops)}  min_drop={mn}  mean_drop={mean:.4f}  max_drop={mx}")
        print(f"   #sets with drop==2n-1: {n_at_target}   #sets with drop<=2n-1: {n_below}")
        verdict = "H2 HOLDS (min<=2n-1)" if mn <= target else "H2 FAILS (min>2n-1)"
        tight = "TIGHT (min==2n-1)" if mn == target else f"min={mn} != 2n-1"
        print(f"   => {verdict}; {tight}")
        print()


if __name__ == "__main__":
    main()
