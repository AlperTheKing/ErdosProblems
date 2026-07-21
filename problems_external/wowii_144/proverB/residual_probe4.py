#!/usr/bin/env python3
"""Residual probe 4: end-to-end test of SCHEME v3 for the residual Lemma E.

Per residual R1 K-instance (h_max < e, some x* with delta* = e - h <= s):

  posts:   for each K-position rho, H(rho) = max height of an outside vertex
           whose deterministic-tail bottom is adjacent to rho.
  window:  W = ball_K(m, delta*-1), m = canonical attachment of the deepest
           e-realizer x*.  All noncentral (theorem).
  tents:   post (rho,H) covers sigma in W iff d_K(sigma,rho) >= r+1-H(rho).
  checks:
   (C1) every sigma in W is covered by some post  (tent existence theorem);
   (C2) S6-analog: does the M-POST (rho = m) cover some window position?
        (equivalently H(m) >= r+2-delta*)  -- count frequency;
   (C3) minimal cover R (greedy by descending H, then prune), |R| stats;
   (C4) family {m-post} u {R posts}, deepest deterministic tails; conflict
        pairs = pairs with a cross edge; realcap_ij = min over cross edges of
        (h(a)+h(b)) - 1; girth cap check realcap_ij >= g-2-d_K(rho_i,rho_j);
   (C5) TRUNCATION ASSEMBLY: maximize sum t_i (t_i <= H_i, and for conflict
        pairs t_i + t_j <= realcap_ij) via exact search; success iff >= e
        AND a z exists (z avoids all used attachments, g >= 5; g=4 handled
        with double-attachment absorption);
   (C6) z-availability: #used attachments vs g.

Failures dumped in full.  Run: python residual_probe4.py   (seed 20260725)
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
    girth,
    graph_connected,
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

SEED = 20260725
CYC_CAP = 8
EXP_CAP = 17


def mask_of(vs):
    m = 0
    for v in vs:
        m |= 1 << v
    return m


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


def build_tails(n, adj, dist, kverts, k_mask):
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
                break
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
    st = Counter()
    fails = []
    s6_viol = []
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
        realizers = [v for v in range(n) if dist_to_set(dist, v, cm) == e]
        for K in shortest_cycles(G, g)[:CYC_CAP]:
            kverts = sorted(K)
            k_mask = mask_of(kverts)
            korder = cycle_order(adj, K)
            pos = {v: i for i, v in enumerate(korder)}

            def dk(a, b):
                d0 = abs(pos[a] - pos[b]) % g
                return min(d0, g - d0)

            tails = build_tails(n, adj, dist, kverts, k_mask)
            hmax = max((t[0] for t in tails.values()), default=0)
            if hmax >= e:
                st["R0"] += 1
                continue
            st["R1"] += 1
            xs = max(realizers, key=lambda v: (tails[v][0] if v in tails
                                               else 0, -v))
            if xs in tails:
                hx = tails[xs][0]
                mm = tails[xs][2][0]
            else:                     # realizer on K
                hx = 0
                mm = xs
            delta = e - hx
            if delta > s:
                st["R1_delta_gt_s"] += 1
                continue
            W = [k for k in kverts if dk(k, mm) <= delta - 1]
            # posts: H(rho) and deepest tail per rho (canonical: max h, min v)
            post = {}
            for v, (h, m, att, seq) in sorted(tails.items()):
                for rho in att:
                    cur = post.get(rho)
                    if cur is None or h > cur[0]:
                        post[rho] = (h, m, att, seq)
            # C1 coverage + C2 m-post
            cover_ok = True
            m_covers = False
            for sig in W:
                got_t = False
                for rho, (H, _, _, _) in post.items():
                    if dk(sig, rho) >= r0 + 1 - H:
                        got_t = True
                        if rho == mm:
                            m_covers = True
                if not got_t:
                    cover_ok = False
            if not cover_ok:
                fails.append(("C1", name, g6, g, e))
                continue
            if m_covers:
                s6_viol.append((name, g6, g, r0, delta, post[mm][0]))
                st["C2_mpost_covers"] += 1
            # C3 minimal cover excluding m-post if possible
            cands = sorted(((H, rho) for rho, (H, _, _, _) in post.items()
                            if rho != mm), reverse=True)
            chosen = []
            uncovered = set(W)
            for H, rho in cands:
                if not uncovered:
                    break
                cov = {sig for sig in uncovered
                       if dk(sig, rho) >= r0 + 1 - H}
                if cov:
                    chosen.append(rho)
                    uncovered -= cov
            if uncovered:
                st["cover_needs_mpost"] += 1
                fails.append(("C3-mneed", name, g6, g, e))
                continue
            # prune to minimal
            changed = True
            while changed:
                changed = False
                for rho in list(chosen):
                    rest = [q for q in chosen if q != rho]
                    if all(any(dk(sig, q) >= r0 + 1 - post[q][0]
                               for q in rest) for sig in W):
                        chosen = rest
                        changed = True
                        break
            st[f"coversize_{len(chosen)}"] += 1
            fam = ([mm] if mm in post else []) + chosen
            # C4 conflicts (realcap + cross-edge count)
            confl = {}
            ncross = {}
            for i in range(len(fam)):
                for j in range(i + 1, len(fam)):
                    Hi, mi, _, seqi = post[fam[i]]
                    Hj, mj, _, seqj = post[fam[j]]
                    assert not (mi & mj), "distinct-attachment tails share!"
                    best = None
                    cnt = 0
                    for a in seqi:
                        ha = dist_to_set(dist, a, k_mask)
                        for b in seqj:
                            if adj[a] >> b & 1:
                                cnt += 1
                                hb = dist_to_set(dist, b, k_mask)
                                if best is None or ha + hb < best:
                                    best = ha + hb
                    if best is not None:
                        cap = best - 1
                        gcap = g - 2 - dk(fam[i], fam[j])
                        assert cap >= gcap, "girth cap violated!"
                        confl[(i, j)] = cap
                        ncross[(i, j)] = cnt
                        st["conflict_pairs"] += 1
                        if cnt == 1:
                            st["conflict_1edge"] += 1
                        # multi-cross girth law: h+H >= g
                        if cnt >= 2:
                            assert Hi + Hj >= g, "multi-cross without h+H>=g"
                            st["conflict_multiedge"] += 1
            # C5 assembly: truncation everywhere, plus optionally ONE
            # 1-cross-edge pair taken as a UNION component (full heights,
            # z := one of its two attachments, no other member there).
            H = [post[rho][0] for rho in fam]
            kf = len(fam)
            best_tot = 0

            def solve(union_pair):
                """max sum with pair constraints; union pair fixed at full."""
                btot = 0
                fixed = {}
                if union_pair is not None:
                    i, j = union_pair
                    fixed[i] = H[i]
                    fixed[j] = H[j]

                def rec(i, t, tot):
                    nonlocal btot
                    if tot + sum(H[i:]) <= btot:
                        return
                    if i == kf:
                        btot = max(btot, tot)
                        return
                    rng = ([fixed[i]] if i in fixed
                           else range(H[i], -1, -1))
                    for ti in rng:
                        ok = True
                        for j in range(i):
                            c = confl.get((j, i))
                            if c is not None and union_pair is not None \
                                    and (j, i) == union_pair:
                                continue   # union pair keeps its edge
                            if c is not None and t[j] + ti > c:
                                ok = False
                                break
                        if ok:
                            t.append(ti)
                            rec(i + 1, t, tot + ti)
                            t.pop()
                            if btot >= e:
                                return

                rec(0, [], 0)
                return btot

            used_atts = set(fam)
            zfree = [k for k in kverts if k not in used_atts]
            ok_inst = False
            if zfree:
                best_tot = solve(None)
                if best_tot >= e:
                    ok_inst = True
            if not ok_inst:
                for (i, j), cnt in ncross.items():
                    if cnt != 1:
                        continue
                    # union absorbs at z in {fam[i], fam[j]}; other
                    # components keep their attachments (all distinct)
                    for zc in (fam[i], fam[j]):
                        others = used_atts - {zc}
                        if zc in others:
                            continue
                        tot = solve((i, j))
                        if tot >= e:
                            ok_inst = True
                            st["C5_via_union"] += 1
                        break
                    if ok_inst:
                        break
            if ok_inst:
                st["C5_ok"] += 1
            else:
                st["C5_fail"] += 1
                fails.append(("C5", name, g6, n, g, r0, D, e, hx, delta,
                              [post[rho][0] for rho in fam],
                              dict(confl), dict(ncross), best_tot,
                              len(zfree)))

    print(f"graphs seen: {len(seen)}")
    for k in sorted(st):
        print(f"  {k:20s}: {st[k]}")
    print(f"S6-analog violations (m-post covers window): {len(s6_viol)}")
    for recd in s6_viol[:10]:
        print("   ", recd)
    print(f"FAILURES: {len(fails)}")
    for recd in fails[:25]:
        print("   ", recd)


if __name__ == "__main__":
    main()
