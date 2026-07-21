#!/usr/bin/env python3
"""Angle B step 1: reverse-engineer the C142 equality cases + decide the
proof shape for the cycle-base route R2.

Questions answered (exact arithmetic only):
  (A) Full structural description of the two girth-6 equality cases
      (FK_h_, FhEK?): adjacency, ecc table, B, f-realizers, shortest cycles,
      per-cycle M(K), optimal witness forests F.
  (B) For all 113 equality cases: verify max_K M(K) == f + 1 - floor(g/3)
      (R2 tightness) and record WHERE the max is attained (which K / F shape).
  (C) TAIL TEST (decides proof shape): on every corpus graph with g >= 4,
      is  max_K ecc_G(K)  >=  f + 1 - floor(g/3)  ?  (ecc_G(K) = max_v d(v,K),
      max over shortest cycles K).  If true, a single-geodesic-tail
      construction suffices for R2 and the rest is a metric lemma.
      Violations are dumped with full data for study.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent          # proverB
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
from lemma_e_tests import M_of_cycle, components_of_mask  # noqa: E402
from bridge_oracle import (  # noqa: E402
    M_collection_max, bits_list, build_corpus)

EQ_JSON = W142 / "oracle" / "equality_cases.json"
OUT = ROOT / "analyze_equality_results.json"


def dist_to_mask(n, adj, mask):
    """BFS distances from a vertex set (mask)."""
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


def basic(g6s):
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = ecc_set(n, dist, periph)
    g = girth(n, adj)
    return G, n, adj, dist, ecc, D, periph, f, g


def describe_g6_case(g6s):
    G, n, adj, dist, ecc, D, periph, f, g = basic(g6s)
    rec = {"g6": g6s, "n": n, "edges": sorted(map(list, G.edges())),
           "girth": g, "D": D, "ecc": ecc,
           "B": bits_list(periph), "f": f,
           "f_realizers": [v for v in range(n)
                           if min(dist[v][b] for b in bits_list(periph)) == f]}
    cyc_info = []
    for K in shortest_cycles(G, g):
        kv = sorted(K)
        km = 0
        for v in kv:
            km |= 1 << v
        mk = M_of_cycle(n, adj, kv)
        dK = dist_to_mask(n, adj, km)
        cyc_info.append({"K": kv, "M": mk, "eccK": max(dK), "d_to_K": dK})
    rec["cycles"] = cyc_info
    rec["maxMK"] = max(c["M"] for c in cyc_info)
    rec["target_q"] = f + 1 - g // 3
    return rec


def main():
    eq = json.loads(EQ_JSON.read_text())["equality_cases"]
    out = {}

    # ---- (A) the two girth-6 cases in full detail
    out["g6_cases"] = [describe_g6_case(c["g6"]) for c in eq
                       if c["girth"] == 6]

    # ---- (B) R2 tight structure on all 113
    bad = []
    tight_hist = Counter()
    for c in eq:
        G, n, adj, dist, ecc, D, periph, f, g = basic(c["g6"])
        entries = []
        for K in shortest_cycles(G, g):
            kv = sorted(K)
            km = 0
            for v in kv:
                km |= 1 << v
            entries.append((km, km, [1 << v for v in kv]))
        maxMK, capped = M_collection_max(n, adj, entries, 22)
        q = f + 1 - g // 3
        tight_hist[(g, maxMK - max(q, 0))] += 1
        if maxMK != max(q, 0):
            bad.append({"g6": c["g6"], "g": g, "f": f, "maxMK": maxMK,
                        "q": q})
    out["eq_R2_structure"] = {
        "hist_(g, maxMK-minus-max(q,0))": {str(k): v
                                           for k, v in
                                           sorted(tight_hist.items())},
        "nonminimal_cases": bad[:20], "n_nonminimal": len(bad)}

    # ---- (C) tail test on the full corpus, g >= 4
    tasks = build_corpus()
    n_eval = 0
    viol = []
    minslack = None
    minwit = None
    slack_hist = Counter()
    girth_min = {}
    for name, g6s in tasks:
        try:
            G = nx.from_graph6_bytes(g6s.encode("ascii"))
            n, adj = nx_to_bitadj(G)
            if n < 2 or not graph_connected(n, adj):
                continue
            g = girth(n, adj)
            if g == 0 or g < 4:
                continue
            dist = all_pairs_dist(n, adj)
            ecc = eccentricities(n, dist)
            D = max(ecc)
            periph = 0
            for v in range(n):
                if ecc[v] == D:
                    periph |= 1 << v
            f = ecc_set(n, dist, periph)
            q = f + 1 - g // 3
            best_ecc = 0
            for K in shortest_cycles(G, g):
                km = 0
                for v in K:
                    km |= 1 << v
                dK = dist_to_mask(n, adj, km)
                m = max(dK)
                if m > best_ecc:
                    best_ecc = m
            sl = best_ecc - q          # >= 0 wanted
            n_eval += 1
            slack_hist[sl] += 1
            if minslack is None or sl < minslack:
                minslack = sl
                minwit = f"{name} [{g6s}] n={n} g={g} D={D} f={f} " \
                         f"eccK={best_ecc} q={q}"
            if g not in girth_min or sl < girth_min[g][0]:
                girth_min[g] = (sl, f"{name} [{g6s}]")
            if sl < 0 and len(viol) < 60:
                viol.append({"name": name, "g6": g6s, "n": n, "g": g,
                             "D": D, "f": f, "best_eccK": best_ecc, "q": q,
                             "slack": sl})
        except Exception as exc:
            print("ERR", name, exc)
    out["tail_test"] = {
        "evaluated_g_ge_4": n_eval,
        "violations": len([1 for s, c in slack_hist.items()
                           if s < 0 for _ in range(c)]),
        "viol_examples": viol,
        "min_slack": minslack, "min_witness": minwit,
        "slack_hist": {str(k): v for k, v in sorted(slack_hist.items())},
        "per_girth_min": {str(k): list(v)
                          for k, v in sorted(girth_min.items())}}

    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["eq_R2_structure"], indent=2)[:1500])
    print("tail test: evaluated", n_eval, "min_slack", minslack)
    print("  witness:", minwit)
    print("  violations:", len(viol))
    for v in viol[:15]:
        print("   ", v)


if __name__ == "__main__":
    main()
