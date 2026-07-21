#!/usr/bin/env python3
"""Residual probe 3: pin the exact proof obligations.

Deterministic descent tails: desc(v) = min-index neighbour w with
h(w) = h(v) - 1;  T(v) = v > desc(v) > ... > (height 1);  att(v) = K-neighbour
set of the bottom (unique for g >= 5; 1 or 2 antipodal at g = 4; canonical
attachment = min).  Facts to exploit: tails sharing a vertex share their
bottom, hence their attachment; so distinct attachments => vertex-disjoint.

Measured per residual graph (cyclic, e >= 1, e > D - s), per shortest cycle K:

  (P0)  g=4 single-tail validity: for every v with h(v) = h_max, the canonical
        tail is a valid M-witness for a suitable z  (checked by direct
        induced-tree test on (K - z) u T(v)).
  (P1)  R0 frequency: h_max >= e.
  (P2)  in R1 (h_max < e): does some x* realizer have delta* = e - h(x*) <= s?
        does C meet K?  (case split R1a/R1b)
  (P3)  H-R1: exists z + compatible family of canonical tails with DISTINCT
        attachments, x*-tail INCLUDED (x* = min-index realizer with min h),
        sum >= e?  Exact search over distinct-attachment families.
  (P4)  interference stats: among pairs of canonical per-attachment best
        tails, count adjacent (interfering) pairs and check the girth bound
        H1 + H2 + d_K(rho1, rho2) >= g - 1.

Run: python residual_probe3.py    (seed 20260724)
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
    ecc_of_set,
    eccentricities,
    edges_in_mask,
    girth,
    graph_connected,
    is_connected_mask,
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

SEED = 20260724
CYC_CAP = 8
EXP_CAP = 17


def mask_of(vs):
    m = 0
    for v in vs:
        m |= 1 << v
    return m


def build_tails(n, adj, dist, kverts, k_mask):
    """Deterministic descent tail for every outside vertex.
    Returns dict v -> (height, mask, att_tuple, vertex_list)."""
    h = {v: dist_to_set(dist, v, k_mask) for v in range(n)
         if not (k_mask >> v & 1)}
    desc = {}
    for v in h:
        if h[v] <= 1:
            continue
        m = adj[v]
        best = None
        while m:
            b = m & -m
            m ^= b
            w = b.bit_length() - 1
            if not (k_mask >> w & 1) and h.get(w) == h[v] - 1:
                best = w
                break                       # min index first
        desc[v] = best
    tails = {}
    for v in h:
        if h[v] == 0:
            continue
        seq = [v]
        cur = v
        while h[cur] > 1:
            cur = desc[cur]
            seq.append(cur)
        att = tuple(sorted(k for k in kverts if adj[cur] >> k & 1))
        tails[v] = (h[v], mask_of(seq), att, seq)
    return tails


def dK(korder_pos, g, a, b):
    d0 = abs(korder_pos[a] - korder_pos[b]) % g
    return min(d0, g - d0)


def cycle_order(adj, kset):
    ks = sorted(kset)
    start = ks[0]
    order = [start]
    prev = None
    cur = start
    while True:
        nbrs = [v for v in ks if adj[cur] >> v & 1 and v != prev]
        nxt = min(nbrs) if prev is None else nbrs[0]
        if nxt == start:
            break
        order.append(nxt)
        prev, cur = cur, nxt
    return order


def valid_tree(n, adj, k_mask, z, fmask, expect_comps):
    tmask = (k_mask & ~(1 << z)) | fmask
    size = tmask.bit_count()
    return (is_connected_mask(adj, tmask)
            and edges_in_mask(adj, tmask) == size - 1)


def main() -> None:
    rng = random.Random(SEED)
    corpora = []
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
            corpora.append(res); got += 1
    got = tries = 0
    while got < 500 and tries < 20000:
        tries += 1
        res = forced_girth_random(rng, gmin=4)
        if res is not None:
            corpora.append(res); got += 1

    seen = set()
    stats = Counter()
    p0_fail = []
    p2_no_smalldelta = []
    p3_fail = []
    p4_viol = []
    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 2 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0 or n - g > EXP_CAP:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r0, D = min(ecc), max(ecc)
        cm = 0
        for v in range(n):
            if ecc[v] == r0:
                cm |= 1 << v
        e = ecc_of_set(n, dist, cm)
        s = g // 2
        if e == 0 or e <= D - s:
            continue
        stats["residual"] += 1
        c_on_k_any = False
        realizers = [v for v in range(n)
                     if dist_to_set(dist, v, cm) == e]
        for K in shortest_cycles(G, g)[:CYC_CAP]:
            kverts = sorted(K)
            k_mask = mask_of(kverts)
            korder = cycle_order(adj, K)
            pos = {v: i for i, v in enumerate(korder)}
            tails = build_tails(n, adj, dist, kverts, k_mask)
            hmax = max((t[0] for t in tails.values()), default=0)
            stats["K_instances"] += 1

            # P0: single-tail validity at any girth
            for v, (h, m, att, seq) in tails.items():
                if h != hmax:
                    continue
                ok_any = False
                for z in kverts:
                    if len(att) == 1 and att[0] == z:
                        continue
                    if len(att) == 2 and z not in att:
                        continue
                    if valid_tree(n, adj, k_mask, z, m, 1):
                        ok_any = True
                        break
                if not ok_any:
                    p0_fail.append((name, g6, g, v))
                break                        # one deepest vertex suffices

            if c_on_k_any is False and cm & k_mask:
                c_on_k_any = True

            if hmax >= e:
                stats["K_R0"] += 1
                continue
            stats["K_R1"] += 1
            # P2: delta* <= s for some realizer?
            deltas = [e - dist_to_set(dist, x, k_mask) for x in realizers]
            if min(deltas) > s:
                p2_no_smalldelta.append((name, g6, g, e, min(deltas), s,
                                         bool(cm & k_mask)))
            if cm & k_mask:
                stats["K_R1_conK"] += 1
            else:
                stats["K_R1_noconK"] += 1

            # P3: exact search, distinct attachments, x*-tail forced
            xstar = min(realizers,
                        key=lambda v: (dist_to_set(dist, v, k_mask), v))
            # best tail per canonical attachment (min att vertex), keep top
            by_att = {}
            for v, (h, m, att, seq) in tails.items():
                key = att[0]
                cur = by_att.get(key)
                if cur is None or h > cur[0]:
                    by_att[key] = (h, m, att, v)
            xt = tails.get(xstar)
            found = False
            # z loop
            for z in kverts:
                if xt is not None:
                    if len(xt[2]) == 1 and xt[2][0] == z:
                        continue
                    if len(xt[2]) == 2 and z not in xt[2]:
                        continue
                cands = []
                for key, (h, m, att, v) in sorted(by_att.items()):
                    if v == xstar:
                        continue
                    if len(att) == 1 and att[0] == z:
                        continue
                    if len(att) == 2 and z not in att:
                        continue
                    cands.append((h, m, att, v))
                # branch and bound for max total with compatibility
                base_mask = xt[1] if xt is not None else 0
                base_adj = base_mask
                mm = base_mask
                while mm:
                    b = mm & -mm
                    mm ^= b
                    base_adj |= adj[b.bit_length() - 1]
                base_tot = xt[0] if xt is not None else 0
                cands.sort(reverse=True)
                target = e

                def rec(i, used_adj, used_mask, tot):
                    if tot >= target:
                        return True
                    if i >= len(cands):
                        return False
                    rem = sum(c[0] for c in cands[i:])
                    if tot + rem < target:
                        return False
                    h, m, att, v = cands[i]
                    if not (m & used_adj):
                        am = m
                        mm2 = m
                        while mm2:
                            b = mm2 & -mm2
                            mm2 ^= b
                            am |= adj[b.bit_length() - 1]
                        if rec(i + 1, used_adj | am, used_mask | m, tot + h):
                            return True
                    return rec(i + 1, used_adj, used_mask, tot)

                if rec(0, base_adj, base_mask, base_tot):
                    found = True
                    break
            if found:
                stats["K_R1_P3ok"] += 1
            else:
                p3_fail.append((name, g6, n, g, r0, D, e, hmax))

            # P4: interference girth bound among per-attachment best tails
            items = sorted(by_att.items())
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    h1, m1, att1, v1 = items[i][1]
                    h2, m2, att2, v2 = items[j][1]
                    if m1 & m2:
                        p4_viol.append((name, g6, "SHARE", items[i][0],
                                        items[j][0]))
                        continue
                    a1 = 0
                    mm2 = m1
                    while mm2:
                        b = mm2 & -mm2
                        mm2 ^= b
                        a1 |= adj[b.bit_length() - 1]
                    if a1 & m2:
                        dd = dK(pos, g, items[i][0], items[j][0])
                        if h1 + h2 + dd < g - 1:
                            p4_viol.append((name, g6, "GIRTH", h1, h2, dd, g))
                        else:
                            stats["interf_pairs_ok"] += 1

    print(f"graphs seen        : {len(seen)}")
    for k in sorted(stats):
        print(f"  {k:18s}: {stats[k]}")
    print(f"P0 single-tail fail: {len(p0_fail)}")
    for rec in p0_fail[:10]:
        print("   ", rec)
    print(f"P2 delta*>s cases  : {len(p2_no_smalldelta)}")
    for rec in p2_no_smalldelta[:10]:
        print("   ", rec)
    print(f"P3 H-R1 failures   : {len(p3_fail)}")
    for rec in p3_fail[:20]:
        print("   ", rec)
    print(f"P4 violations      : {len(p4_viol)}")
    for rec in p4_viol[:10]:
        print("   ", rec)


if __name__ == "__main__":
    main()
