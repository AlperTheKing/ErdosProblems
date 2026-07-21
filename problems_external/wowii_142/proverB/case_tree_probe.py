#!/usr/bin/env python3
"""Angle B step 2: simulate the draft case tree of the proof on the full
corpus; verify every proven branch's guarantee EXACTLY, and dump all graphs
landing in the unresolved holes:

  H1 = C5b: g = 4, D in {3,4}  (hard slice f = D-1)
  H2 = C9 : g >= 5, all-K ecc(K) <= q-1, f >= 2*floor(g/3)+1  (band-high)

Case tree (t = tree size target f + ceil(2g/3), q = f + 1 - floor(g/3)):
  C0: g = 3                                  -> T4+T1   (check f <= D-1)
  C1: f <= floor(g/3) - 1                    -> T2
  C2: f <= D + 1 - ceil(2g/3)                -> T1
  C3: g >= 5, D >= 2*ceil(2g/3) - 3          -> M-P + x-tail
      (check: min over diametral geodesics P of d(x,P) >= f - floor(D/2)
       for every f-realizer x; and closure arithmetic)
  C4: g = 4, D >= 5                          -> M-P + reroute x-tail
      (same metric check; delta >= 2 then t >= D + delta >= f + 3)
  C5a: g = 4, D = 2                          -> M(K) >= 1 = f
  C5b: g = 4, D in {3,4}                     -> HOLE H1 (dump)
  C6: g >= 5, h* = max_K ecc(K) >= q         -> single tail
  C7: g >= 5, h* <= q-1,
      g - 2*floor(g/3) <= f <= 2*floor(g/3)  -> three tails (verify S3 >= q
      for the WORST choice of K, x-realizer, diametral pair)
  C8: g >= 5, h* <= q-1, f <= g-2*floor(g/3)-1 -> q <= 2 leftover:
      q = 1: impossible here (h* >= 1 >= q handled by C6)
      q = 2: n = g+1 -> tadpole contradiction (verify f <= floor(g/3));
             n >= g+2 -> two depth-1 vertices (verify >= 2 exist at h*=1)
  C9: g >= 5, h* <= q-1, f >= 2*floor(g/3)+1 -> HOLE H2 (dump)
All arithmetic exact integers.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
sys.path.insert(0, str(PE / "wowii_141" / "oracle"))
sys.path.insert(0, str(PE / "wowii_144" / "oracle"))
sys.path.insert(0, str(PE / "wowii_144" / "wave2"))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import (  # noqa: E402
    bits_list, build_corpus, diametral_geodesic_sets)

OUT = ROOT / "case_tree_probe_results.json"


def dist_to_mask(n, adj, mask):
    INF = 10 ** 9
    dist = [INF] * n
    frontier = []
    for v in bits_list(mask):
        dist[v] = 0
        frontier.append(v)
    d = 0
    while frontier:
        d += 1
        nxt = []
        for u in frontier:
            nb = adj[u]
            while nb:
                b = nb & -nb
                nb ^= b
                w = b.bit_length() - 1
                if dist[w] > d:
                    dist[w] = d
                    nxt.append(w)
        frontier = nxt
    return dist


def classify(name, g6s):
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    if n < 2 or not graph_connected(n, adj):
        return None
    g = girth(n, adj)
    if g == 0:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    Bl = bits_list(periph)
    f = ecc_set(n, dist, periph)
    if f == 0:
        return ("F0", None)          # easy branch, not our task
    c23 = (2 * g + 2) // 3           # ceil(2g/3)
    fl3 = g // 3
    q = f + 1 - fl3
    base = {"name": name, "g6": g6s, "n": n, "g": g, "D": D, "f": f, "q": q}

    if g == 3:
        assert f <= D - 1, ("T4 fail!", base)
        return ("C0", None)
    if f <= fl3 - 1:
        return ("C1", None)
    if f <= D + 1 - c23:
        return ("C2", None)

    xs = [v for v in range(n) if min(dist[v][b] for b in Bl) == f]

    def worst_delta():
        """min over f-realizers x and ALL diametral geodesics P of d(x, P);
        also returns whether metric bound f - floor(D/2) holds for it."""
        gsets, capped = diametral_geodesic_sets(n, adj, dist, D, 20000)
        wd = None
        for pm in gsets:
            dP = dist_to_mask(n, adj, pm)
            for x in xs:
                if wd is None or dP[x] < wd:
                    wd = dP[x]
        return wd, capped

    if g >= 5 and D >= 2 * c23 - 3:
        wd, capped = worst_delta()
        ok_metric = capped or wd >= f - D // 2
        ok_close = (f <= D // 2) or (D + 1 + max(wd, 0) >= f + c23)
        return ("C3", None if (ok_metric and ok_close) else
                {**base, "why": "C3 guarantee failed", "worst_delta": wd})
    if g == 4 and D >= 5:
        wd, capped = worst_delta()
        ok_metric = capped or wd >= f - D // 2
        # f = D-1 here; reroute gives t >= D + delta, delta >= ceil(D/2)-1>=2
        ok_close = D + max(wd, 0) >= f + 3 or capped
        return ("C4", None if (ok_metric and ok_close) else
                {**base, "why": "C4 guarantee failed", "worst_delta": wd})
    if g == 4:
        if D == 2:
            return ("C5a", None if f == 1 else
                    {**base, "why": "C5a expected f=1"})
        info = dict(base)
        info["ecc_per_K"] = []
        for K in shortest_cycles(G, g):
            km = 0
            for v in K:
                km |= 1 << v
            info["ecc_per_K"].append(max(dist_to_mask(n, adj, km)))
        return ("C5b", info)

    # g >= 5 from here; compute h* = max over shortest cycles of ecc(K)
    Ks = shortest_cycles(G, g)
    hstar = 0
    percyc = []
    for K in Ks:
        km = 0
        for v in K:
            km |= 1 << v
        e = max(dist_to_mask(n, adj, km))
        percyc.append((sorted(K), e))
        if e > hstar:
            hstar = e
    if hstar >= q:
        return ("C6", None)
    if g - 2 * fl3 <= f <= 2 * fl3:
        # verify worst-case S3 >= q over every K, realizer, diametral pair
        worst = None
        for K, _e in percyc:
            km = 0
            for v in K:
                km |= 1 << v
            dK = dist_to_mask(n, adj, km)
            hx = min(dK[x] for x in xs)
            best_pair = None
            for i, b in enumerate(Bl):
                for w in Bl[i:]:
                    if dist[b][w] == D:
                        s = dK[b] + dK[w]
                        if best_pair is None or s < best_pair:
                            best_pair = s
            s3 = hx + best_pair
            if worst is None or s3 < worst:
                worst = s3
        return ("C7", None if worst >= q else
                {**base, "why": "C7 S3 < q", "worst_S3": worst,
                 "hstar": hstar})
    if f <= g - 2 * fl3 - 1:
        # q in {1, 2}; q=1 cannot reach here (C6 would fire since h*>=1)
        if q <= 1:
            return ("C8", {**base, "why": "q<=1 leaked past C6",
                           "hstar": hstar})
        if n == g + 1:
            return ("C8", {**base, "why": "tadpole with f=fl3+1?!",
                           "hstar": hstar})
        # n >= g+2 and h* = 1: need >= 2 depth-1 vertices (all non-K at d 1)
        if hstar == 1 and n - g >= 2:
            return ("C8", None)
        return ("C8", {**base, "why": "C8 unexpected shape",
                       "hstar": hstar})
    info = dict(base)
    info["hstar"] = hstar
    info["percyc_ecc"] = [e for _k, e in percyc]
    return ("C9", info)


def main():
    tasks = build_corpus()
    print(f"corpus: {len(tasks)}")
    counts = Counter()
    holes = {"C5b": [], "C9": []}
    fails = []
    done = 0
    for nameg6 in tasks:
        done += 1
        if done % 2000 == 0:
            print(f"  {done}/{len(tasks)}", flush=True)
        try:
            r = classify(*nameg6)
        except AssertionError as exc:
            fails.append(repr(exc))
            continue
        if r is None:
            continue
        tag, info = r
        counts[tag] += 1
        if tag in ("C5b", "C9") and info is not None:
            holes[tag].append(info)
        elif info is not None:
            fails.append(info)
    out = {"counts": dict(counts), "branch_guarantee_failures": fails,
           "H1_g4_members": holes["C5b"][:400],
           "H1_count": len(holes["C5b"]),
           "H2_band_members": holes["C9"][:400],
           "H2_count": len(holes["C9"])}
    OUT.write_text(json.dumps(out, indent=2))
    print("counts:", dict(counts))
    print("guarantee failures:", len(fails))
    for x in fails[:10]:
        print("  FAIL:", x)
    print("H1 (g4 D<=4) members:", len(holes["C5b"]))
    for x in holes["C5b"][:12]:
        print("  H1:", {k: x[k] for k in ("name", "g6", "n", "D", "f")})
    print("H2 (band) members:", len(holes["C9"]))
    for x in holes["C9"][:12]:
        print("  H2:", x)


if __name__ == "__main__":
    main()
