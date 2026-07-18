#!/usr/bin/env python3
"""Exact computational oracle for WOWII / Graffiti.pc Conjecture 142.

FC statement tested (formal-conjectures-w141c
FormalConjectures/WrittenOnTheWallII/GraphConjecture142.lean, defs in
FormalConjecturesForMathlib/Combinatorics/SimpleGraph/{VertexDistance,
Eccentricity}.lean, read 2026-07-18):

    G connected, |V| >= 2.
    B    := maxEccentricityVertices G = { v | eccent v = ediam }   (periphery)
    f    := eccSet G B = max_{v in V} min_{b in B} dist(v, b)
           (max over ALL v, members of B contribute 0)
    t    := largestInducedTreeSize G  (>= 1; singletons count, empty set not)
    girth:= length of shortest cycle, 0 if acyclic

    C142:  (2/3) * girth + f  <=  t        (exact Fractions here)

Questions answered on the corpus (atlas n=2..7 connected, wowii_141 sweep
families + same-seed random sweep, adversarial families, extremal candidates
up to n=20):

  Q3 (girth-cycle escape): for every connected CYCLIC G, does there exist a
     shortest cycle K (equivalently an induced cycle of length g = girth; every
     shortest cycle is induced) and a vertex x with

         d(x, V(K))  >=  f - floor(g/3) + 1        [exact integer inequality]

     Bridge arithmetic (exact): if additionally t >= (g-1) + d(x,V(K)) for that
     witness, then t >= g - 1 + f - floor(g/3) + 1 = f + (g - floor(g/3))
     = f + ceil(2g/3) >= f + (2/3) g, which is C142.  We therefore also test
       q3_bridge_all : t >= g - 1 + d(x,V(K)) for EVERY girth cycle K, every x
       q3_combined   : EXISTS (K, x) with d(x,V(K)) >= f - floor(g/3) + 1
                       AND t >= g - 1 + d(x,V(K)).

  Q4 (double tail): for EVERY diametral geodesic P (all geodesics of all
     diametral pairs are enumerated, dedup'd by vertex set, capped at
     PATH_CAP; a shortest path is determined by its vertex set) and every
     vertex x:   t >= |V(P)| + d(x, V(P)) = (diam+1) + d(x,V(P)) ?
     Violations reported.

  Q5: for x* an f-realizing vertex (dist(x*, B) = f): does there exist a
     diametral geodesic P with
         d(x*, V(P))  >=  (2/3) girth + f - diam - 1     (exact Fractions)?
     Both quantifications reported: forall x* (each realizer must have its own
     P) and exists x*.

  EQUALITY MINING: all exact equality cases (2/3)g + f = t with graph6, girth,
     f, t, B, center; extremal-family tightness table up to n = 20.

Everything exact: integers + Fraction; the invariant implementations are
imported unchanged from problems_external/wowii_141/oracle/invariants.py.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = (ROOT.parent.parent / "wowii_141" / "oracle").resolve()
sys.path.insert(0, str(W141))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_set,
    girth,
    is_connected_mask,
    largest_induced_tree,
    nx_to_bitadj,
)
import sweep_families as sf  # noqa: E402

MAXN = 20
PATH_CAP = 50000
TWO_THIRDS = Fraction(2, 3)
OUT_MAIN = ROOT / "oracle142_results.json"
OUT_EQ = ROOT / "equality_cases.json"
OUT_EXT = ROOT / "extremal_report.json"

ATLAS_EXPECTED = {2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853}


def graph6(G: nx.Graph) -> str:
    H = nx.convert_node_labels_to_integers(G, ordering="default")
    H = nx.convert_node_labels_to_integers(H, ordering="sorted")
    return nx.to_graph6_bytes(H, header=False).decode("ascii").strip()


def mask_bits(mask: int) -> list[int]:
    out = []
    while mask:
        b = mask & -mask
        mask ^= b
        out.append(b.bit_length() - 1)
    return out


# --------------------------------------------------------------------- Q3 core

def girth_cycles(n: int, adj: list[int], g: int) -> list[int]:
    """All vertex-set masks of induced cycles of length g = girth(G).
    Every shortest cycle is chordless, hence induced; every induced g-cycle is
    a shortest cycle.  Exhaustive over C(n, g) subsets."""
    cycles = []
    for comb in itertools.combinations(range(n), g):
        mask = 0
        for v in comb:
            mask |= 1 << v
        if all((adj[v] & mask).bit_count() == 2 for v in comb) and \
                is_connected_mask(adj, mask):
            cycles.append(mask)
    return cycles


def eval_q3(n: int, adj: list[int], dist, g: int, f: int, t: int):
    if g == 0:
        return None
    thr = f - g // 3 + 1
    cycles = girth_cycles(n, adj, g)
    assert cycles, "cyclic graph must contain an induced girth cycle"
    d_max = -1
    exists = False
    bridge_all = True
    combined = False
    for km in cycles:
        dvals = [dist_to_set(dist, x, km) for x in range(n)]
        mx = max(dvals)
        if mx > d_max:
            d_max = mx
        if t < g - 1 + mx:
            bridge_all = False
        if mx >= thr:
            exists = True
        if not combined:
            for d in dvals:
                if d >= thr and t >= g - 1 + d:
                    combined = True
                    break
    return {
        "num_girth_cycles": len(cycles),
        "d_max": d_max,
        "threshold": thr,
        "trivial": thr <= 0,
        "exists": exists,
        "bridge_all": bridge_all,
        "combined": combined,
    }


# ------------------------------------------------------------------ Q4/Q5 core

def diametral_geodesics(n: int, adj: list[int], dist, diam: int,
                        cap: int = PATH_CAP):
    """Vertex-set masks of ALL geodesics between ALL diametral pairs.
    A shortest path is determined by its vertex set (order = distance from u),
    so dedup by mask is lossless.  Returns (mask set, path count, truncated)."""
    masks: set[int] = set()
    total = 0
    for u in range(n):
        for v in range(u + 1, n):
            if dist[u][v] != diam:
                continue
            stack = [(v, 1 << v)]
            while stack:
                w, pm = stack.pop()
                if w == u:
                    total += 1
                    masks.add(pm)
                    if total >= cap:
                        return masks, total, True
                    continue
                dw = dist[u][w]
                m = adj[w]
                while m:
                    b = m & -m
                    m ^= b
                    p = b.bit_length() - 1
                    if dist[u][p] == dw - 1:
                        stack.append((p, pm | (1 << p)))
    return masks, total, False


def eval_q45(n: int, adj: list[int], dist, diam: int, g: int, f: int, t: int,
             periph_mask: int):
    masks, npaths, trunc = diametral_geodesics(n, adj, dist, diam)
    plen = diam + 1
    per_mask_maxd = {}
    q4_viol = []
    for pm in masks:
        mx = max(dist_to_set(dist, x, pm) for x in range(n))
        per_mask_maxd[pm] = mx
        if t < plen + mx:
            q4_viol.append((pm, mx))
    worst = None
    if q4_viol:
        pm, mx = max(q4_viol, key=lambda z: z[1])
        worst = {"P": mask_bits(pm), "maxd": mx, "lhs": plen + mx, "t": t}
    realizers = [v for v in range(n)
                 if dist_to_set(dist, v, periph_mask) == f]
    rhs5 = TWO_THIRDS * g + f - diam - 1
    fails5 = []
    for x in realizers:
        # masks is nonempty: a diametral pair always exists for n >= 2
        best = max(dist_to_set(dist, x, pm) for pm in masks)
        if Fraction(best) < rhs5:
            fails5.append({"x": x, "best_d": best})
    q4 = {
        "num_paths": npaths,
        "num_masks": len(masks),
        "truncated": trunc,
        "num_viol_masks": len(q4_viol),
        "worst": worst,
    }
    q5 = {
        "rhs": str(rhs5),
        "trivial": rhs5 <= 0,
        "num_realizers": len(realizers),
        "num_fail_realizers": len(fails5),
        "forall": not fails5,
        "exists": len(fails5) < len(realizers),
        "fails": fails5[:5],
        "truncated": trunc,
    }
    return q4, q5


# ------------------------------------------------------------------- pipeline

def process_graph(n: int, adj: list[int]) -> dict:
    dist = all_pairs_dist(n, adj)
    ecc = [max(r) for r in dist]
    diam = max(ecc)
    rad = min(ecc)
    periph_mask = 0
    center_mask = 0
    for v in range(n):
        if ecc[v] == diam:
            periph_mask |= 1 << v
        if ecc[v] == rad:
            center_mask |= 1 << v
    g = girth(n, adj)
    t, _w = largest_induced_tree(n, adj)
    f = ecc_set(n, dist, periph_mask)
    lhs = TWO_THIRDS * g + f
    slack = Fraction(t) - lhs
    q3 = eval_q3(n, adj, dist, g, f, t)
    q4, q5 = eval_q45(n, adj, dist, diam, g, f, t, periph_mask)
    return {
        "n": n,
        "m": sum(a.bit_count() for a in adj) // 2,
        "girth": g,
        "diam": diam,
        "radius": rad,
        "tree": t,
        "f": f,
        "slack": slack,
        "eq": slack == 0,
        "periph": mask_bits(periph_mask),
        "center": mask_bits(center_mask),
        "q3": q3,
        "q4": q4,
        "q5": q5,
    }


# --------------------------------------------------------- graph constructors

def double_broom(L: int, a: int, b: int) -> nx.Graph:
    G = nx.path_graph(L)
    for i in range(a):
        G.add_edge(0, f"a{i}")
    for i in range(b):
        G.add_edge(L - 1, f"b{i}")
    return G


def spider_at(G: nx.Graph, root, legs, tag: str) -> None:
    for j, ln in enumerate(legs):
        prev = root
        for i in range(ln):
            nd = f"{tag}{j}_{i}"
            G.add_edge(prev, nd)
            prev = nd


def cycle_two_spiders(g: int, legs) -> nx.Graph:
    G = nx.cycle_graph(g)
    spider_at(G, 0, legs, "s")
    spider_at(G, g // 2, legs, "t")
    return G


def triangle_chain(k: int) -> nx.Graph:
    G = nx.Graph()
    for i in range(k):
        c0, c1, m = f"c{i}", f"c{i+1}", f"m{i}"
        G.add_edge(c0, c1)
        G.add_edge(c0, m)
        G.add_edge(m, c1)
    return G


def clique_chain(m: int, k: int) -> nx.Graph:
    G = nx.Graph()
    for i in range(k):
        nodes = [f"c{i}", f"c{i+1}"] + [f"x{i}_{j}" for j in range(m - 2)]
        for aa, bb in itertools.combinations(nodes, 2):
            G.add_edge(aa, bb)
    return G


def friendship(k: int) -> nx.Graph:
    G = nx.Graph()
    for i in range(k):
        G.add_edge("h", f"u{i}")
        G.add_edge("h", f"v{i}")
        G.add_edge(f"u{i}", f"v{i}")
    return G


def clique_two_tails(m: int, k1: int, k2: int) -> nx.Graph:
    G = nx.complete_graph(m)
    prev = 0
    for i in range(k1):
        G.add_edge(prev, f"p{i}")
        prev = f"p{i}"
    prev = 1
    for i in range(k2):
        G.add_edge(prev, f"q{i}")
        prev = f"q{i}"
    return G


def build_adversarial() -> list[tuple[str, nx.Graph]]:
    out = []
    # barbells: two cliques + long path ("long paths with heavy ends")
    for m in (3, 4, 5, 6):
        for k in range(0, MAXN - 2 * m + 1):
            out.append((f"barbell({m},{k})", nx.barbell_graph(m, k)))
    # lollipops (periphery-concentrated: periphery = far clique + tail end)
    for m in range(3, 9):
        for k in range(0, min(13, MAXN - m + 1)):
            out.append((f"lollipop({m},{k})", nx.lollipop_graph(m, k)))
    # double brooms / brooms (long paths with heavy star ends)
    for L in range(3, 15):
        for (a, b) in [(2, 2), (3, 3), (4, 4), (1, 3), (2, 5), (3, 0),
                       (5, 0)]:
            if L + a + b <= MAXN:
                out.append((f"double_broom({L},{a},{b})",
                            double_broom(L, a, b)))
    # cycle + two deep spiders at (near-)antipodal roots
    for g in range(3, 10):
        for legs in [(2, 2), (3, 3), (4, 4), (2, 2, 2), (3, 3, 3)]:
            if g + 2 * sum(legs) <= MAXN:
                out.append((f"cycle_two_spiders({g},{legs})",
                            cycle_two_spiders(g, legs)))
    # clique with two tails (periphery concentrated on tail ends)
    for m in (4, 5, 6):
        for (k1, k2) in [(1, 1), (2, 2), (3, 3), (4, 2), (5, 5), (6, 6)]:
            if m + k1 + k2 <= MAXN:
                out.append((f"clique_two_tails({m},{k1},{k2})",
                            clique_two_tails(m, k1, k2)))
    return out


def build_extremal() -> list[tuple[str, nx.Graph]]:
    out = []
    for n in range(3, MAXN + 1):
        out.append((f"K({n})", nx.complete_graph(n)))
        out.append((f"C({n})", nx.cycle_graph(n)))
    for m in range(3, MAXN):
        out.append((f"lollipop({m},1)", nx.lollipop_graph(m, 1)))
    for m in range(3, 13):
        out.append((f"lollipop({m},2)", nx.lollipop_graph(m, 2)))
    for k in range(1, 10):
        out.append((f"friendship({k})", friendship(k)))
        out.append((f"triangle_chain({k})", triangle_chain(k)))
    for k in range(2, 7):
        if 3 * k + 1 <= MAXN:
            out.append((f"clique_chain(4,{k})", clique_chain(4, k)))
    for k in range(2, 5):
        if 4 * k + 1 <= MAXN:
            out.append((f"clique_chain(5,{k})", clique_chain(5, k)))
    for gg in (3, 6, 9, 12):
        for k in range(1, MAXN - gg + 1):
            out.append((f"tadpole({gg},{k})", sf.tadpole(gg, k)))
    for gg in range(3, MAXN):
        out.append((f"tadpole({gg},1)", sf.tadpole(gg, 1)))
    for a in range(1, 15):
        for b in range(max(a, 2), 15):
            for c in range(b, 15):
                if a + b + c - 1 <= 16:
                    out.append((f"theta({a},{b},{c})", sf.theta(a, b, c)))
    for k in range(1, 13):
        if 6 + k <= MAXN:
            out.append((f"cycle_star(6,{k})", sf.cycle_pendant_star(6, k)))
    return out


def build_corpus() -> list[tuple[str, str, nx.Graph]]:
    items: list[tuple[str, str, nx.Graph]] = []
    from networkx.generators.atlas import graph_atlas_g
    atlas_counts: dict[int, int] = {}
    for i, G in enumerate(graph_atlas_g()):
        n = G.number_of_nodes()
        if 2 <= n <= 7 and nx.is_connected(G):
            atlas_counts[n] = atlas_counts.get(n, 0) + 1
            items.append(("atlas", f"atlas_{i}", G))
    if atlas_counts != ATLAS_EXPECTED:
        print(f"WARNING: atlas connected counts {atlas_counts} != expected "
              f"{ATLAS_EXPECTED}", flush=True)
    for name, G in sf.build_family_graphs():
        items.append(("family", name, G))
    for name, G in sf.random_graphs(random.Random(sf.SEED)):
        items.append(("random", name, G))
    for name, G in build_adversarial():
        items.append(("adversarial", name, G))
    for name, G in build_extremal():
        items.append(("extremal", name, G))
    return items


# ------------------------------------------------------------------ main run

def main() -> None:
    t0 = time.time()
    items = build_corpus()
    print(f"corpus: {len(items)} items", flush=True)

    cache: dict[str, dict] = {}
    per_item: list[dict] = []
    seen_first: dict[str, str] = {}

    for idx, (source, name, G) in enumerate(items):
        n = G.number_of_nodes()
        if n < 2 or n > MAXN or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        g6 = graph6(G)
        if g6 in cache:
            res = cache[g6]
        else:
            nn, adj = nx_to_bitadj(G)
            res = process_graph(nn, adj)
            cache[g6] = res
            seen_first[g6] = f"{source}:{name}"
        per_item.append({"source": source, "name": name, "g6": g6, **{
            k: res[k] for k in ("n", "girth", "diam", "tree", "f")},
            "slack": str(res["slack"]), "eq": res["eq"]})
        if (idx + 1) % 250 == 0:
            print(f"  [{idx + 1}/{len(items)}] unique={len(cache)} "
                  f"t={time.time() - t0:.0f}s", flush=True)

    # ----------------------------------------------------------- aggregation
    uniq = list(cache.items())
    c142_viol = []
    by_girth: dict[int, dict] = {}
    eq_cases = []
    q3_tested = q3_trivial = 0
    q3_exist_fail, q3_bridge_fail, q3_combined_fail = [], [], []
    q4_graph_viol = []
    q5_forall_fail, q5_exists_fail = [], []
    q5_nontrivial = 0
    q45_truncated = []

    for g6, r in uniq:
        gg = r["girth"]
        sl = r["slack"]
        d = by_girth.setdefault(gg, {"count": 0, "min_slack": None,
                                     "num_at_min": 0, "witness": None,
                                     "equality_count": 0})
        d["count"] += 1
        if d["min_slack"] is None or sl < d["min_slack"]:
            d["min_slack"] = sl
            d["num_at_min"] = 1
            d["witness"] = f"{seen_first[g6]} [{g6}]"
        elif sl == d["min_slack"]:
            d["num_at_min"] += 1
        if sl < 0:
            c142_viol.append({"g6": g6, "name": seen_first[g6], **{
                k: r[k] for k in ("n", "girth", "f", "tree")},
                "slack": str(sl)})
        if r["eq"]:
            d["equality_count"] += 1
            eq_cases.append({
                "g6": g6, "first_seen_as": seen_first[g6], "n": r["n"],
                "m": r["m"], "girth": gg, "f": r["f"], "tree": r["tree"],
                "diam": r["diam"], "radius": r["radius"],
                "B": r["periph"], "center": r["center"]})
        if r["q3"] is not None:
            q3_tested += 1
            q3 = r["q3"]
            if q3["trivial"]:
                q3_trivial += 1
            info = {"g6": g6, "name": seen_first[g6], "n": r["n"],
                    "girth": gg, "f": r["f"], "tree": r["tree"],
                    "d_max": q3["d_max"], "threshold": q3["threshold"]}
            if not q3["exists"]:
                q3_exist_fail.append(info)
            if not q3["bridge_all"]:
                q3_bridge_fail.append(info)
            if not q3["combined"]:
                q3_combined_fail.append(info)
        q4 = r["q4"]
        if q4["truncated"]:
            q45_truncated.append(g6)
        if q4["num_viol_masks"] > 0:
            q4_graph_viol.append({
                "g6": g6, "name": seen_first[g6], "n": r["n"], "girth": gg,
                "diam": r["diam"], "tree": r["tree"], "f": r["f"],
                "num_viol_masks": q4["num_viol_masks"],
                "num_masks": q4["num_masks"], "worst": q4["worst"]})
        q5 = r["q5"]
        if not q5["trivial"]:
            q5_nontrivial += 1
        info5 = {"g6": g6, "name": seen_first[g6], "n": r["n"], "girth": gg,
                 "f": r["f"], "diam": r["diam"], "rhs": q5["rhs"],
                 "num_realizers": q5["num_realizers"],
                 "num_fail_realizers": q5["num_fail_realizers"],
                 "fails": q5["fails"]}
        if not q5["forall"]:
            q5_forall_fail.append(info5)
        if not q5["exists"]:
            q5_exists_fail.append(info5)

    eq_cases.sort(key=lambda e: (e["girth"], e["n"], e["g6"]))

    # extremal family tightness table
    ext_rows = []
    for it in per_item:
        if it["source"] != "extremal":
            continue
        ext_rows.append({"name": it["name"], "g6": it["g6"], "n": it["n"],
                         "girth": it["girth"], "f": it["f"],
                         "tree": it["tree"], "slack": it["slack"],
                         "tight": it["eq"]})

    by_girth_out = {str(k): {"count": v["count"],
                             "min_slack": str(v["min_slack"]),
                             "num_at_min": v["num_at_min"],
                             "witness": v["witness"],
                             "equality_count": v["equality_count"]}
                    for k, v in sorted(by_girth.items())}

    payload = {
        "test": "WOWII_C142_oracle_Q3_Q4_Q5_equality",
        "date": "2026-07-18",
        "definitions": {
            "B": "maxEccentricityVertices = periphery {v : eccent v = ediam}",
            "f": "eccSet(G,B) = max_v min_{b in B} dist(v,b)",
            "c142": "(2/3)*girth + f <= tree  (exact Fractions)",
            "q3_integer_form": "EXISTS induced girth-cycle K, EXISTS x: "
                               "d(x,V(K)) >= f - floor(girth/3) + 1",
            "q3_bridge": "t >= girth - 1 + d(x,V(K)); with q3 gives t >= f + "
                         "ceil(2*girth/3) >= f + (2/3)*girth",
            "q4": "for EVERY diametral geodesic P, every x: "
                  "t >= (diam+1) + d(x,V(P))",
            "q5": "for f-realizing x*: EXISTS diametral geodesic P with "
                  "d(x*,V(P)) >= (2/3)*girth + f - diam - 1",
        },
        "corpus_items": len(per_item),
        "unique_graphs": len(uniq),
        "sources": {s: sum(1 for it in per_item if it["source"] == s)
                    for s in ("atlas", "family", "random", "adversarial",
                              "extremal")},
        "c142_violations": c142_viol,
        "min_slack_by_girth": by_girth_out,
        "equality_count": len(eq_cases),
        "q3": {
            "tested_cyclic": q3_tested,
            "trivial_threshold_le0": q3_trivial,
            "exists_failures": q3_exist_fail,
            "bridge_all_failure_count": len(q3_bridge_fail),
            "bridge_all_failures_sample": q3_bridge_fail[:40],
            "combined_failures": q3_combined_fail,
        },
        "q4": {
            "tested": len(uniq),
            "graphs_with_violations": len(q4_graph_viol),
            "violations_sample": q4_graph_viol[:400],
            "violating_g6": [z["g6"] for z in q4_graph_viol][:4000],
        },
        "q5": {
            "tested": len(uniq),
            "nontrivial_rhs_count": q5_nontrivial,
            "forall_failure_count": len(q5_forall_fail),
            "forall_failures_sample": q5_forall_fail[:100],
            "exists_failure_count": len(q5_exists_fail),
            "exists_failures": q5_exists_fail[:200],
        },
        "geodesic_truncated_graphs": q45_truncated,
        "runtime_sec": round(time.time() - t0, 1),
    }
    OUT_MAIN.write_text(json.dumps(payload, indent=2) + "\n",
                        encoding="ascii")
    OUT_EQ.write_text(json.dumps({"equality_cases": eq_cases}, indent=2)
                      + "\n", encoding="ascii")
    OUT_EXT.write_text(json.dumps({"extremal_rows": ext_rows}, indent=2)
                       + "\n", encoding="ascii")

    print(json.dumps({
        "unique_graphs": len(uniq),
        "c142_violations": len(c142_viol),
        "equality_count": len(eq_cases),
        "min_slack_by_girth": {k: v["min_slack"]
                               for k, v in by_girth_out.items()},
        "q3_exists_failures": len(q3_exist_fail),
        "q3_bridge_all_failures": len(q3_bridge_fail),
        "q3_combined_failures": len(q3_combined_fail),
        "q4_graphs_with_violations": len(q4_graph_viol),
        "q5_forall_failures": len(q5_forall_fail),
        "q5_exists_failures": len(q5_exists_fail),
        "truncated": len(q45_truncated),
        "runtime_sec": payload["runtime_sec"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
