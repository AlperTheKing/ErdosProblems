#!/usr/bin/env python3
"""Dissect the 9 P3-failure graphs: print window/tent/tail structure and an
actually-working compatible family (exact search over ALL truncated tails,
<=1 per attachment optional), to extract the general repair mechanism.
Exact arithmetic.  Run: python analyze_failures.py
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    graph_connected,
    nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402

FAILS = [
    "JAd?c?`?gI?",
    "RhCGGC@?K?_C?@??_?G?@_?C_????G",
    "QhCGGC@?G?_@?@_?_@?_@?@???G",
    "NhCGGC@?G?o@?OO?a??",
    "ZhCGGC@?G?_@?@??_?G?@??C??G??K??C??_???G???_??@A??@??_?????G",
    "ZhCGGC@?G?_@?@??_?G?@??E??G?C???C??@???G???a??@??G?????c????",
    "XhCGGC@?G?_@?@??o?G?_??C??G??G??C??@C??G_?????@???@",
    "ZhCGGC@?G?_@?@??_?G?@??C??K??GA????@???G??O_??_???@????_???G",
    "N?@?`o?H?CG@_K_@?K_",
]


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
    for g6 in FAILS:
        G = nx.from_graph6_bytes(g6.encode())
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        g = girth(n, adj)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r0, D = min(ecc), max(ecc)
        cm = 0
        for v in range(n):
            if ecc[v] == r0:
                cm |= 1 << v
        e = ecc_of_set(n, dist, cm)
        s = g // 2
        print("=" * 78)
        print(f"[{g6}] n={n} g={g} s={s} r={r0} D={D} e={e} "
              f"centers={[v for v in range(n) if cm >> v & 1]}")
        realizers = [v for v in range(n) if dist_to_set(dist, v, cm) == e]
        for K in shortest_cycles(G, g):
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
                print(f"  K={korder}  R0 (hmax={hmax} >= e)")
                continue
            xs = max(realizers, key=lambda v: (tails.get(v, (0,))[0],))
            hx = tails[xs][0] if xs in tails else 0
            mm = tails[xs][2][0] if xs in tails else None
            print(f"  K={korder}")
            print(f"  realizers={realizers} x*={xs} h={hx} att(x*)={mm} "
                  f"delta*={e - hx}")
            # noncentral window around m
            if mm is not None:
                W = [k for k in kverts if dk(k, mm) <= e - hx - 1]
                print(f"  window={sorted(W, key=lambda k: pos[k])} "
                      f"ecc={[ecc[k] for k in sorted(W, key=lambda kk: pos[kk])]}")
            # all tails
            for v, (h, m, att, seq) in sorted(tails.items()):
                extra = " X*" if v == xs else ""
                print(f"    tail v={v:3d} h={h} att={att} seq={seq}{extra}")
            # exact search: all tails (= all truncations), compatibility,
            # <= 1 per attachment NOT enforced; z loop; find max total,
            # record ONE optimal family reaching >= e if any
            items = sorted(tails.values(), reverse=True)
            best_fam = None
            for z in kverts:
                cands = []
                for (h, m, att, seq) in items:
                    if len(att) == 1 and att[0] == z:
                        continue
                    if len(att) == 2 and z not in att:
                        continue
                    am = m
                    m2 = m
                    while m2:
                        b = m2 & -m2
                        m2 ^= b
                        am |= adj[b.bit_length() - 1]
                    cands.append((h, m, att, seq, am))
                found = None

                def rec(i, used_adj, tot, chosen):
                    nonlocal found
                    if found:
                        return
                    if tot >= e:
                        found = list(chosen)
                        return
                    if i >= len(cands):
                        return
                    rem = sum(c[0] for c in cands[i:])
                    if tot + rem < e:
                        return
                    h, m, att, seq, am = cands[i]
                    if not (m & used_adj):
                        chosen.append((h, att, seq))
                        rec(i + 1, used_adj | am, tot + h, chosen)
                        chosen.pop()
                        if found:
                            return
                    rec(i + 1, used_adj, tot, chosen)

                rec(0, 0, 0, [])
                if found:
                    best_fam = (z, found)
                    break
            if best_fam:
                z, fam = best_fam
                tot = sum(f[0] for f in fam)
                print(f"  WORKING family z={z} total={tot} >= e={e}:")
                for h, att, seq in fam:
                    print(f"      h={h} att={att} seq={seq}")
                xin = any(seq and seq[0] == xs for _, _, seq in fam)
                print(f"      (x*-tail included: {xin})")
            else:
                print("  !! NO tail-only family reaches e (needs non-tail F)")


if __name__ == "__main__":
    main()
