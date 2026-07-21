#!/usr/bin/env python3
"""Mechanical verification of the P2 proof construction (WOWII 144, Angle B).

P2:  tree(G) >= diam(G) + ceil(g/2) - 1   for every connected cyclic G.

Proof shape being verified (g >= 5; g in {3,4} is the trivial t >= D+1 since
ceil(g/2)-1 = 1; D <= floor(g/2) is covered by T2 t >= g-1):

  Fix ANY shortest cycle K (chordless + isometric) and ANY diametral geodesic
  P = p_0..p_D.  s := floor(g/2).  I := { i : d(p_i, K) <= 1 }.

  Facts (g >= 5):
    (N')  every vertex outside K has at most ONE neighbour on K;
    (N)   every vertex not on a geodesic P has at most ONE neighbour on P;
    (T3)  K is isometric, arcs are geodesics; K minus a vertex is induced P_{g-1}.

  Case A (I empty):  let R = r_0..r_delta be a shortest P-K path
      (p* = r_0 on P, k* = r_delta on K, delta = d(P,K) >= 2).
      F := P u {r_1..r_{delta-1}}  -- one component, pendant chain at p*,
      exactly one edge into K (r_{delta-1} -> k*).  z := any K-vertex != k*.
      |F| = D + delta >= D + 2.

  Case B (I nonempty): l := min I, r := max I, dl := d(p_l,K), dr := d(p_r,K).
      (dl = 0 forces l = 0; dr = 0 forces r = D -- else contradiction with
       minimality/maximality since a neighbour of a K-vertex is in I.)
      B1 (r - l >= 2):
          C1 := p_0..p_l        if dl = 1   (unique K-nbr k_a of p_l),
                p_0..p_{l-1}    if dl = 0   (empty when l = 0; k_a := p_l = p_0)
          C2 := p_r..p_D        if dr = 1   (unique K-nbr k_b),
                p_{r+1}..p_D    if dr = 0   (empty when r = D; k_b := p_r = p_D)
          F := C1 u C2, z := any K-vertex not in {k_a, k_b}.
          |F| = D - (r-l) + [dl=1] + [dr=1] >= D - s
          because r - l = d(p_l,p_r) <= dl + d_K(k_a,k_b) + dr <= dl + s + dr.
      B2 (r = l): then dl = 1 (dl = 0 gives l=0=r=D i.e. D=0, absurd);
          F := whole P (one component, exactly one K-edge at p_l -> k(l)),
          z := any K-vertex != k(l).   |F| = D + 1.
      B3 (r = l+1):
          (1,1): k(l) != k(r) (else triangle), F := whole P, z := k(l);
                 exactly one edge into K - z (at k(r)); edges into z are free.
                 |F| = D + 1.
          (0,1): l = 0; F := p_1..p_D, one K-edge (p_1 -> p_0 = its unique
                 K-nbr); z != p_0.  |F| = D.
          (1,0): mirror.  (0,0): l=0, r=D=1: impossible for g >= 5.

  Then Lemma M: T := (K - z) u F is an induced tree with (g-1) + |F| vertices,
  so tree >= (g-1) + (D - s) = D + ceil(g/2) - 1.

This script re-runs the construction for EVERY shortest cycle K (cap CYC_CAP)
and EVERY diametral pair (cap PAIR_CAP, canonical BFS geodesic each) on every
corpus graph with g >= 5, and checks with exact integer arithmetic:
  (V1) claimed case analysis is exhaustive + internal assertions (N), (N'),
       dl=0 => l=0, k(l) != k(r) in B3(1,1), etc.;
  (V2) F is disjoint from K; components of G[F] are exactly the claimed ones;
  (V3) every component sends EXACTLY one edge into K - {z} (mult. counted);
  (V4) |F| >= D - s;
  (V5) T = (K-z) u F induces a tree (connected, |E| = |T|-1) of size (g-1)+|F|
       >= D + ceil(g/2) - 1;
  (V6) for n <= TREE_CAP, cross-check tree(G) >= D + ceil(g/2) - 1 against the
       exhaustive largest_induced_tree.
Also verifies the g in {3,4} arithmetic (target == D + 1 <= tree via geodesic:
geodesics always induce paths) and the D <= s arithmetic (target <= g - 1).

Run:  python verify_P2_construction.py        (seed 20260721)
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
WAVE2 = ROOT.parent / "wave2"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))
sys.path.insert(0, str(WAVE2))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    eccentricities,
    edges_in_mask,
    girth,
    graph_connected,
    is_connected_mask,
    largest_induced_tree,
    nx_to_bitadj,
)
from bridge_tests import adversarial_graphs, shortest_cycles  # noqa: E402
from sweep_families import build_family_graphs, random_graphs  # noqa: E402
from route_b_tests import (  # noqa: E402
    chorded_cycle,
    cycle_random_legs,
    cycle_random_trees,
    forced_girth_random,
    gen_theta,
    graph6,
    trap_family,
)

SEED = 20260721
CYC_CAP = 12       # max shortest cycles tested per graph
PAIR_CAP = 24      # max diametral pairs tested per (graph, K)
TREE_CAP = 15      # exhaustive tree cross-check only for n <= TREE_CAP


def cycle_order(adj, kset: frozenset) -> list[int]:
    """Cyclic order of a chordless cycle given as a vertex set."""
    ks = sorted(kset)
    start = ks[0]
    order = [start]
    prev = None
    cur = start
    while True:
        nbrs = [v for v in ks if adj[cur] >> v & 1 and v != prev]
        assert nbrs, "cycle order reconstruction failed"
        nxt = min(nbrs) if prev is None else nbrs[0]
        if nxt == start:
            break
        order.append(nxt)
        prev, cur = cur, nxt
    assert len(order) == len(ks)
    return order


def bfs_geodesic(n, adj, dist, u, v) -> list[int]:
    """Canonical geodesic u -> v (min-index parent choice)."""
    path = [u]
    cur = u
    while cur != v:
        nxt = None
        m = adj[cur]
        while m:
            b = m & -m
            m ^= b
            w = b.bit_length() - 1
            if dist[w][v] == dist[cur][v] - 1:
                nxt = w
                break
        assert nxt is not None
        path.append(nxt)
        cur = nxt
    return path


def components_of(adj, mask: int) -> list[int]:
    comps = []
    rem = mask
    while rem:
        start = rem & -rem
        reached = start
        frontier = start
        while frontier:
            new = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                new |= adj[b.bit_length() - 1]
            new &= mask & ~reached
            reached |= new
            frontier = new
        comps.append(reached)
        rem &= ~reached
    return comps


def mask_of(vs) -> int:
    m = 0
    for v in vs:
        m |= 1 << v
    return m


def k_neighbors(adj, v, k_mask) -> list[int]:
    out = []
    m = adj[v] & k_mask
    while m:
        b = m & -m
        m ^= b
        out.append(b.bit_length() - 1)
    return out


def build_F(n, adj, dist, korder, P):
    """Return (components, z, case_tag) exactly following the proof."""
    g = len(korder)
    k_mask = mask_of(korder)
    D = len(P) - 1
    dK = [dist_to_set(dist, p, k_mask) for p in P]
    I = [i for i, d in enumerate(dK) if d <= 1]

    # fact (N'): <= 1 K-neighbour for outside vertices
    for v in range(n):
        if not (k_mask >> v & 1):
            assert len(k_neighbors(adj, v, k_mask)) <= 1, "N' violated"

    if not I:
        # Case A
        delta = min(dK)
        assert delta >= 2
        i_star = dK.index(delta)
        p_star = P[i_star]
        # shortest p*-K path with d(p*,K)=delta = d(P,K)
        # (argmin over P of dist-to-K IS d(P,K))
        # geodesic from p_star to its nearest K-vertex
        tgt = None
        for k in korder:
            if dist[p_star][k] == delta:
                tgt = k
                break
        R = bfs_geodesic(n, adj, dist, p_star, tgt)
        assert len(R) == delta + 1
        # fact (N): r_1 has exactly one neighbour on P (= p_star)
        r1 = R[1]
        nbrs_on_P = [p for p in P if adj[r1] >> p & 1]
        assert nbrs_on_P == [p_star] or nbrs_on_P == sorted([p_star]), \
            f"(N) violated: {nbrs_on_P}"
        comp = list(P) + R[1:delta]          # P plus r_1..r_{delta-1}
        kstar = R[delta]
        z = next(k for k in korder if k != kstar)
        return [comp], z, "A"

    l, r = I[0], I[-1]
    dl, dr = dK[l], dK[r]
    if dl == 0:
        assert l == 0, "dl=0 must force l=0"
    if dr == 0:
        assert r == D, "dr=0 must force r=D"

    if r - l >= 2:
        if dl == 1:
            C1 = P[: l + 1]
            ka = k_neighbors(adj, P[l], k_mask)
            assert len(ka) == 1
            ka = ka[0]
        else:
            C1 = P[:l]                      # empty (l = 0)
            ka = P[l]
        if dr == 1:
            C2 = P[r:]
            kb = k_neighbors(adj, P[r], k_mask)
            assert len(kb) == 1
            kb = kb[0]
        else:
            C2 = P[r + 1:]                  # empty (r = D)
            kb = P[r]
        z = next(k for k in korder if k not in (ka, kb))
        comps = [c for c in (C1, C2) if c]
        return comps, z, "B1"

    if r == l:
        assert dl == 1, "r=l with dl=0 impossible (D=0)"
        kl = k_neighbors(adj, P[l], k_mask)[0]
        z = next(k for k in korder if k != kl)
        return [list(P)], z, "B2"

    assert r == l + 1
    if (dl, dr) == (1, 1):
        kl = k_neighbors(adj, P[l], k_mask)[0]
        kr = k_neighbors(adj, P[r], k_mask)[0]
        assert kl != kr, "triangle => g=3 contradiction"
        return [list(P)], kl, "B3-11"
    if (dl, dr) == (0, 1):
        assert l == 0
        kb = k_neighbors(adj, P[1], k_mask)
        assert kb == [P[0]]
        z = next(k for k in korder if k != P[0])
        return [P[1:]], z, "B3-01"
    if (dl, dr) == (1, 0):
        assert r == D
        ka = k_neighbors(adj, P[D - 1], k_mask)
        assert ka == [P[D]]
        z = next(k for k in korder if k != P[D])
        return [P[:D]], z, "B3-10"
    raise AssertionError("B3-00 reached: impossible for g >= 5")


def verify_instance(n, adj, dist, korder, P, fails, tag):
    g = len(korder)
    s = g // 2
    D = len(P) - 1
    k_mask = mask_of(korder)
    comps, z, case = build_F(n, adj, dist, korder, P)

    fmask = 0
    total = 0
    for c in comps:
        cm = mask_of(c)
        assert cm & fmask == 0, "components overlap"
        fmask |= cm
        total += len(c)
    # V2: F disjoint from K, components exactly as claimed
    if fmask & k_mask:
        fails.append((tag, case, "F meets K")); return case
    real_comps = components_of(adj, fmask)
    if sorted(real_comps) != sorted(mask_of(c) for c in comps):
        fails.append((tag, case, "component structure differs")); return case
    # G[F] forest
    if edges_in_mask(adj, fmask) != total - len(real_comps):
        fails.append((tag, case, "F not a forest")); return case
    # V3: exactly one edge into K - z per component
    kz = k_mask & ~(1 << z)
    for cm in real_comps:
        cnt = 0
        m = cm
        while m:
            b = m & -m
            m ^= b
            cnt += (adj[b.bit_length() - 1] & kz).bit_count()
        if cnt != 1:
            fails.append((tag, case, f"component sends {cnt} edges into K-z"))
            return case
    # V4
    if total < D - s:
        fails.append((tag, case, f"|F|={total} < D-s={D - s}")); return case
    # V5: induced tree
    tmask = (k_mask & ~(1 << z)) | fmask
    size = tmask.bit_count()
    if size != g - 1 + total:
        fails.append((tag, case, "size mismatch")); return case
    if not is_connected_mask(adj, tmask) or \
            edges_in_mask(adj, tmask) != size - 1:
        fails.append((tag, case, "T not an induced tree")); return case
    if size < D + (g + 1) // 2 - 1:
        fails.append((tag, case, "tree smaller than P2 target")); return case
    return case


def main() -> None:
    rng = random.Random(SEED)
    corpora: list[tuple[str, nx.Graph]] = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 2 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(1500):
        corpora.append(cycle_random_legs(rng))
    for _ in range(1000):
        corpora.append(cycle_random_trees(rng))
    for _ in range(800):
        corpora.append(chorded_cycle(rng))
    for _ in range(500):
        corpora.append(gen_theta(rng))
    got = tries = 0
    while got < 900 and tries < 20000:
        tries += 1
        res = forced_girth_random(rng, gmin=5)
        if res is not None:
            corpora.append(res)
            got += 1
    # sharp instances: C_g + path L <= s ; cycleLegs g=10,11 three legs len 2
    for g in range(5, 26):
        for L in range(0, g // 2 + 1):
            G = nx.cycle_graph(g)
            prev = 0
            for i in range(L):
                G.add_edge(prev, f"t{i}")
                prev = f"t{i}"
            corpora.append((f"CgPlusPath(g={g},L={L})", G))
    for g in (10, 11):
        for spread in ((0, 3, 7), (0, 4, 8), (0, 3, 6)):
            G = nx.cycle_graph(g)
            for j, pos in enumerate(spread):
                G.add_edge(pos, f"a{j}")
                G.add_edge(f"a{j}", f"b{j}")
            corpora.append((f"cycleLegs(g={g},{spread})", G))

    seen = set()
    fails: list = []
    case_hist = Counter()
    checked = graphs5 = trivia34 = trivialD = crosschecked = 0
    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 2 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        D = max(ecc)
        s = g // 2
        target = D + (g + 1) // 2 - 1
        if g in (3, 4):
            assert target == D + 1     # trivial: geodesic
            trivia34 += 1
            continue
        if D <= s:
            assert target <= g - 1     # trivial: T2
            trivialD += 1
            continue
        graphs5 += 1
        if n <= TREE_CAP:
            t, _ = largest_induced_tree(n, adj)
            assert t >= target, f"P2 ITSELF FALSE on {name} [{g6}]"
            crosschecked += 1
        cycles = shortest_cycles(G, g)[:CYC_CAP]
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if dist[u][v] == D][:PAIR_CAP]
        for K in cycles:
            korder = cycle_order(adj, K)
            for (u, v) in pairs:
                P = bfs_geodesic(n, adj, dist, u, v)
                tag = f"{name} [{g6}] u={u} v={v}"
                case = verify_instance(n, adj, dist, korder, P, fails, tag)
                case_hist[case] += 1
                checked += 1

    print(f"graphs distinct           : {len(seen)}")
    print(f"  g in {{3,4}} (trivial)    : {trivia34}")
    print(f"  g>=5, D<=s (T2 trivial) : {trivialD}")
    print(f"  g>=5, D>s  (construct)  : {graphs5}")
    print(f"instances (K x pair)      : {checked}")
    print(f"exhaustive cross-checks   : {crosschecked}")
    print(f"case histogram            : {dict(case_hist)}")
    print(f"FAILURES                  : {len(fails)}")
    for f in fails[:25]:
        print("  ", f)


if __name__ == "__main__":
    main()
