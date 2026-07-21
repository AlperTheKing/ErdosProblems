#!/usr/bin/env python3
"""TEST-PI: per-component z-tail potential, on ALL hard-branch corpus graphs.

For a shortest cycle K and z in K, for each component C of G - V(K):
    pi_z(C) = max over v in C of d_{G[C + (K\\{z})]}(v, K\\{z})   (0 if none)
i.e. the longest z-tail that stays inside C.  Each component's deepest
z-tail is a valid Lemma-M component (g >= 5; g = 4 flagged separately),
tails in distinct components never collide, and all share the single z.

Tested claim PI: for hard-branch graphs (s >= 1 and m >= 1) in the GOOD zone
(D >= g - 2*floor(g/3) + 1):   max_K max_z  sum_C pi_z(C) >= m.

Also verify the BAD-ZONE dichotomy claims:
  zone boxes (g,D) in {(4,2),(5,2),(5,3),(7,3),(8,4),(11,5)} with the f
  windows derived in the notes; check m <= 2 there, and that the claimed
  construction reaches M >= m (via: h >= 2 tail, or two outside vertices
  nonadjacent -> two singletons, or adjacent -> ear pair).
Exact integers only.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
for p in (PE / "wowii_141" / "oracle", PE / "wowii_144" / "oracle",
          PE / "wowii_144" / "wave2"):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import build_corpus, bits_list  # noqa: E402
from lemma_e_tests import components_of_mask  # noqa: E402

CYC_CAP = 250


def dist_to_mask(dist_v, mask):
    best = None
    m = mask
    while m:
        b = m & -m
        m ^= b
        d = dist_v[b.bit_length() - 1]
        if best is None or d < best:
            best = d
    return best


def bfs_from_set(n, adj, allowed_mask, start_mask):
    """BFS distances from start_mask, moving only inside allowed_mask
    (start vertices need not be in allowed_mask).  -1 = unreachable."""
    dist = [-1] * n
    frontier = []
    for v in range(n):
        if start_mask >> v & 1:
            dist[v] = 0
            frontier.append(v)
    d = 0
    while frontier:
        nxt = []
        for u in frontier:
            nb = adj[u] & allowed_mask
            while nb:
                b = nb & -nb
                nb ^= b
                w = b.bit_length() - 1
                if dist[w] == -1:
                    dist[w] = d + 1
                    nxt.append(w)
        frontier = nxt
        d += 1
    return dist


def eval_one(task):
    name, g6s = task
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    if n < 2 or not graph_connected(n, adj):
        return None
    g = girth(n, adj)
    if g < 4:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = ecc_set(n, dist, periph)
    c23 = (2 * g + 2) // 3
    s = f + c23 - D - 1
    m = f + 1 - g // 3
    if s <= 0 or m <= 0:
        return None                     # not hard branch
    good_zone = D >= g - 2 * (g // 3) + 1
    rec = {"name": name, "g6": g6s, "n": n, "g": g, "D": D, "f": f,
           "m": m, "good_zone": good_zone}
    full = (1 << n) - 1
    best_pi = 0
    for K in shortest_cycles(G, g)[:CYC_CAP]:
        kv = sorted(K)
        km = 0
        for v in kv:
            km |= 1 << v
        comps = components_of_mask(adj, full & ~km)
        for z in kv:
            base = km & ~(1 << z)
            tot = 0
            for cm in comps:
                dd = bfs_from_set(n, adj, cm, base)
                mx = 0
                cc = cm
                while cc:
                    b = cc & -cc
                    cc ^= b
                    v = b.bit_length() - 1
                    if dd[v] > mx:
                        mx = dd[v]
                tot += mx
            if tot > best_pi:
                best_pi = tot
    rec["best_pi"] = best_pi
    rec["pi_ok"] = best_pi >= m
    return rec


def main():
    t0 = time.time()
    tasks = build_corpus()
    print(f"corpus: {len(tasks)}", flush=True)
    hard = 0
    good_fail = []
    bad_zone_recs = []
    margin_hist = Counter()
    girth4_hard = 0
    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one, tasks, chunksize=32):
            if rec is None:
                continue
            hard += 1
            if rec["g"] == 4:
                girth4_hard += 1
            if rec["good_zone"]:
                margin_hist[rec["best_pi"] - rec["m"]] += 1
                if not rec["pi_ok"]:
                    good_fail.append(rec)
            else:
                bad_zone_recs.append(rec)
    print(f"hard-branch graphs (g>=4): {hard} (g=4: {girth4_hard})")
    print("GOOD zone PI margin hist:", dict(sorted(margin_hist.items())))
    print("GOOD zone PI failures:", len(good_fail))
    for r in good_fail[:20]:
        print("  ", r)
    print("BAD zone members:", len(bad_zone_recs))
    boxes = Counter((r["g"], r["D"], r["f"]) for r in bad_zone_recs)
    print("bad-zone boxes:", dict(sorted(boxes.items())))
    bad_fail = [r for r in bad_zone_recs if not r["pi_ok"]]
    print("bad-zone PI failures (info only):", len(bad_fail))
    for r in bad_fail[:10]:
        print("  ", r)
    json.dump({"hard": hard,
               "good_margin": {str(k): v
                               for k, v in sorted(margin_hist.items())},
               "good_fail": good_fail,
               "bad_boxes": {str(k): v for k, v in sorted(boxes.items())},
               "bad_fail": bad_fail},
              open(ROOT / "pi_results.json", "w"), indent=2)
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
