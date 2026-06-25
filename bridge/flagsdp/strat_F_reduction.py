#!/usr/bin/env python3
"""STRATEGY F core test: does a series-parallel / 2-cut reduction tracking (t,n) carry the constant 25?

Two structural questions:
 (Q1) Are the binding (near-tight) triangle-free critical atoms SERIES-PARALLEL? If C5[q] or the obstructions
      contain a K4-subdivision / are 3-connected, a 2-terminal S-P reduction CANNOT decompose them.
 (Q2) Does D25 behave SUBADDITIVELY under the 2-cut (2-sum) operation in the way an induction would need?
      For a 2-sum of atoms K1, K2 along a vertex 2-cut {x,y}, how do (t, n, nu*) combine? Is there a clean
      square-gluing  25 t^2/n^2  that is preserved?

We test:
 A. 3-connectivity / SP-ness of C5[q] (q=2,3) and Petersen and K23-N13.
 B. The "necklace" of theta gadgets sharing endpoints in series (a chain of bad edges) -- does the per-atom
    25 t^2/n^2 add up correctly, or does sharing vertices break additivity (the GPT square-gluing handles
    EDGE-disjoint blocks via cut vertices, but 2-cuts share an EDGE/2 vertices)?
 C. The C5[q] tightness: how does t=q^2, n=5q force 25 t^2/n^2 = q^2 = nu* exactly, and can an SP reduction
    ever REACH q^2 parallel 5-cycles from theta steps?
"""
import itertools
import numpy as np
from collections import deque
from scipy.optimize import linprog
import verify_D25_lemma16 as L
import strat_F_theta as T


def is_k_connected(N, adj, k):
    """vertex connectivity >= k? brute: no separator of size < k. (small N only)"""
    if N <= k:
        return False
    verts = list(range(N))
    for r in range(0, k):
        for S in itertools.combinations(verts, r):
            # remove S, check connectivity of rest
            rest = [v for v in verts if v not in S]
            if len(rest) <= 1:
                continue
            seen = {rest[0]}
            st = [rest[0]]
            Sset = set(S)
            while st:
                u = st.pop()
                for w in adj[u]:
                    if w not in Sset and w not in seen:
                        seen.add(w)
                        st.append(w)
            if len(seen) < len(rest):
                return False  # separator of size r < k found
    return True


def has_k4_subdivision(N, adj):
    """crude: a graph is series-parallel IFF it has no K4 minor IFF treewidth<=2. Test via: SP graphs have
    a vertex of degree <=2 reducible by series/parallel moves down to a single edge / nothing. We do the
    reduction: repeatedly (parallel) merge multi-edges, (series) suppress degree-2 vertices. If we collapse
    to <=2 vertices it's SP; if a min-degree>=3 simple graph remains, NOT SP."""
    # adjacency as multiset
    from collections import Counter
    adjm = {u: Counter() for u in range(N)}
    for u in range(N):
        for v in adj[u]:
            adjm[u][v] += 1
    nodes = set(range(N))
    changed = True
    while changed and len(nodes) > 2:
        changed = False
        # parallel: nothing (simple) -- but series moves create multi-edges, fine
        # series: suppress a degree-2 vertex (sum of multiplicities == 2, two distinct nbrs or a loop)
        for u in list(nodes):
            deg = sum(adjm[u].values())
            if deg <= 1:
                # pendant or isolated: remove
                for w in list(adjm[u]):
                    adjm[w][u] -= adjm[u][w]
                    if adjm[w][u] <= 0:
                        del adjm[w][u]
                del adjm[u]
                nodes.discard(u)
                changed = True
                break
            if deg == 2:
                nbrs = list(adjm[u].elements())
                a, b = nbrs[0], nbrs[1]
                # suppress u, add edge a-b (avoid self-loop a==b)
                for w in list(adjm[u]):
                    adjm[w][u] -= adjm[u][w]
                    if adjm[w][u] <= 0:
                        del adjm[w][u]
                del adjm[u]
                nodes.discard(u)
                if a != b:
                    adjm[a][b] += 1
                    adjm[b][a] += 1
                changed = True
                break
        # parallel reduction: collapse multiedges to single (doesn't change SP-ness; keep simple-ish)
        for u in list(nodes):
            for w in list(adjm[u]):
                if adjm[u][w] > 1:
                    adjm[u][w] = 1
    # if reduced to <=2 nodes => SP (no K4 minor). else there's an irreducible min-deg>=3 core => K4 minor
    return len(nodes) > 2  # True = has K4 subdivision/minor = NOT series-parallel


def analyze(N, A, label):
    adj = L.adjset(N, A)
    c3 = is_k_connected(N, adj, 3)
    k4 = has_k4_subdivision(N, adj)
    sp = not k4
    print(f"{label:18s} n={N:3d}  3-connected={c3}   series-parallel={sp}  (hasK4minor={k4})", flush=True)


if __name__ == "__main__":
    print("=== STRATEGY F (Q1): are the binding atoms series-parallel? ===\n", flush=True)
    analyze(*L.c5(), "C5")
    analyze(*L.c5n(2), "C5[2]")
    analyze(*L.c5n(3), "C5[3]")
    analyze(*L.petersen(), "Petersen")
    analyze(*L.gpt_k23(), "K23-N13")
    analyze(*T.theta_atom(4, 6), "theta(4,6)")
    print("\nIf C5[q] (the TIGHT extremizer) is 3-connected / NOT series-parallel,")
    print("then a 2-terminal series-parallel reduction cannot reach it, and Strategy F")
    print("cannot have C5[q] as a reachable 'irreducible base case' of the SP reduction.")
    print("DONE", flush=True)
