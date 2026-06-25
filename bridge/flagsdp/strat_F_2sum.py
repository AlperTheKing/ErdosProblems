#!/usr/bin/env python3
"""STRATEGY F (Q2): 2-sum gluing behaviour of D25, and where the constant 25 concentrates.

A 2-sum glues two atoms K1, K2 along a vertex 2-cut {x,y} (identify x1=x2, y1=y2, optionally delete the
shared edge). Tutte: every 2-connected graph decomposes uniquely into 3-connected pieces, cycles, and bonds
via 2-sums. Strategy F = run this decomposition, hope D25 is subadditive across 2-sums with C5/theta bases.

We test the SUBADDITIVITY/GLUING numerically:
  - take K1 = C5[2] (3-connected, near-tight) and attach a long theta tail via a 2-cut.
  - measure (t,n,nu*) before/after; check the square-gluing 25 sum t_i^2 / (sum-ish n_i^2) relation.

KEY DIAGNOSTIC: D25's bound 25 t^2/n^2 with a single block is set by the 3-connected piece. When we 2-sum a
LONG path/theta tail, n grows but t and nu* barely move -> 25 t^2/n^2 DROPS (slack grows). So D25 is
'monotone safe' under attaching SP tails. The DANGER is the reverse: building up t by GLUING many
3-connected near-tight pieces. Test whether 2-summing two C5[2]'s preserves 25 t^2/n^2 ~ nu*.
"""
import itertools
import numpy as np
import verify_D25_lemma16 as L
import strat_F_theta as T


def graph_from_edges(N, edges):
    A = [0] * N
    for (u, v) in edges:
        A[u] |= 1 << v
        A[v] |= 1 << u
    return N, A


def edges_of(N, A):
    adj = L.adjset(N, A)
    return [(u, v) for u in range(N) for v in adj[u] if v > u]


def relabel(N, A, offset, identify=None):
    """return edge list with vertices shifted by offset, except vertices in identify (dict old->newglobal)."""
    identify = identify or {}
    es = []
    for (u, v) in edges_of(N, A):
        uu = identify.get(u, u + offset)
        vv = identify.get(v, v + offset)
        es.append((uu, vv))
    return es


def two_sum(N1, A1, c1, N2, A2, c2, delete_shared=True):
    """glue K1,K2 along 2-cut: identify c1=(x1,y1) of K1 with c2=(x2,y2) of K2. Returns merged graph.
    If both have edge (x,y) and delete_shared, drop one copy (the 'virtual' edge)."""
    x1, y1 = c1
    x2, y2 = c2
    off = N1
    # map K2 vertices: x2->x1, y2->y1, others-> off + (index skipping x2,y2)
    newid = {x2: x1, y2: y1}
    nxt = N1
    for v in range(N2):
        if v in (x2, y2):
            continue
        newid[v] = nxt
        nxt += 1
    es = set()
    for (u, v) in edges_of(N1, A1):
        es.add((min(u, v), max(u, v)))
    for (u, v) in edges_of(N2, A2):
        uu, vv = newid[u], newid[v]
        e = (min(uu, vv), max(uu, vv))
        if delete_shared and e == (min(x1, y1), max(x1, y1)):
            continue
        es.add(e)
    Nm = nxt
    return graph_from_edges(Nm, list(es))


if __name__ == "__main__":
    print("=== STRATEGY F (Q2): 2-sum gluing of D25 ===\n", flush=True)

    print("-- base atoms --")
    for builder, lab in [(L.c5, "C5"), (lambda: L.c5n(2), "C5[2]"), (lambda: T.theta_atom(4, 6), "theta46")]:
        N, A = builder()
        T.report(N, A, lab)

    print("\n-- 2-sum: C5[2] with a theta(4,6) tail glued on a 2-cut (a B-edge pair) --")
    N1, A1 = L.c5n(2)
    # pick a 2-cut in C5[2]: two adjacent vertices won't be a 2-cut (3-connected). Use a non-edge pair.
    # Just attach theta's terminals (0,1) to two C5[2] vertices 0,5 (in different classes).
    N2, A2 = T.theta_atom(4, 6)
    merged = two_sum(N1, A1, (0, 5), N2, A2, (0, 1), delete_shared=True)
    T.report(*merged, "C5[2]+theta tail")

    print("\n-- 2-sum: two C5[2] blocks glued along a 2-cut (DANGER: stacking near-tight pieces) --")
    Na, Aa = L.c5n(2)
    Nb, Ab = L.c5n(2)
    merged2 = two_sum(Na, Aa, (0, 5), Nb, Ab, (0, 5), delete_shared=False)
    T.report(*merged2, "C5[2] 2-sum C5[2]")

    print("\n-- disjoint union joined by ONE bridge edge (block-cut, the PROVED square-gluing case) --")
    Na, Aa = L.c5n(2)
    Nb, Ab = L.c5n(2)
    # bridge: vertex Na-? to Nb offset. block-cut: cut vertex. attach b-copy at a single shared vertex.
    es = [(min(u, v), max(u, v)) for (u, v) in edges_of(Na, Aa)]
    newid = {0: 0}  # identify b.vertex0 with a.vertex0 (cut vertex)
    nxt = Na
    for v in range(1, Nb):
        newid[v] = nxt
        nxt += 1
    for (u, v) in edges_of(Nb, Ab):
        uu, vv = newid[u], newid[v]
        es.append((min(uu, vv), max(uu, vv)))
    bc = graph_from_edges(nxt, list(set(es)))
    T.report(*bc, "C5[2]#C5[2] cutvtx")
    print("\nObservation: block-cut (cut-vertex) gluing ADDS t and nu* (proved square-gluing); the binding")
    print("25 t^2/n^2 lives inside each 3-CONNECTED block, NOT across the SP/2-cut interface.")
    print("DONE", flush=True)
