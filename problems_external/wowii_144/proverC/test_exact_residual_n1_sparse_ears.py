#!/usr/bin/env python3
"""Exact N1 search on sparse girth-preserving ear/tree graphs.

Each graph starts from a labelled chordless cycle of length g.  Random trees
and clean ears are added, and the final graph is retained only when its exact
girth is still g.  The base cycle therefore is a shortest cycle.  If it does
not witness N1, *all* shortest cycles are enumerated before a violation is
reported.  Thus there is no cycle cap in a reported result.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import networkx as nx


SEED = 20260718
TRIALS = 30_000
NMAX = 60
OUT = Path(__file__).with_name("exact_residual_n1_sparse_ears.json")


def build(rng: random.Random):
    g = rng.randint(5, 15)
    G = nx.cycle_graph(g)
    next_v = g

    # Add a random rooted forest attached to the current graph.
    for _ in range(rng.randint(0, 22)):
        parent = rng.randrange(next_v)
        G.add_edge(parent, next_v)
        next_v += 1

    # Add one to four long ears.  The length is chosen so the new ear plus a
    # pre-existing geodesic has length at least g.  Interactions among ears
    # are handled by the exact final-girth check below.
    for _ in range(rng.randint(0, 4)):
        if next_v + g > NMAX:
            break
        a, b = rng.sample(list(G.nodes), 2)
        d = nx.shortest_path_length(G, a, b)
        length = max(2, g - d) + rng.randint(0, 4)
        if next_v + length - 1 > NMAX:
            continue
        prev = a
        for _j in range(length - 1):
            G.add_edge(prev, next_v)
            prev = next_v
            next_v += 1
        G.add_edge(prev, b)

    # A second forest gives ears internal offshoots as well.
    room = NMAX - next_v
    for _ in range(rng.randint(0, min(12, room))):
        parent = rng.randrange(next_v)
        G.add_edge(parent, next_v)
        next_v += 1
    return G, g


def invariants(G: nx.Graph):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {v: max(dist[v].values()) for v in G}
    radius = min(ecc.values())
    diameter = max(ecc.values())
    centers = [v for v in G if ecc[v] == radius]
    dc = {v: min(dist[v][c] for c in centers) for v in G}
    e = max(dc.values())
    realizers = [v for v in G if dc[v] == e]
    return dist, radius, diameter, centers, e, realizers


def h_for_cycle(dist, realizers, K) -> int:
    return max(min(dist[x][a] for a in K) for x in realizers)


def all_shortest_cycle_sets(G: nx.Graph, g: int):
    found = set()
    shortest_seen = None
    for cyc in nx.simple_cycles(G, length_bound=g):
        q = len(cyc)
        if shortest_seen is None or q < shortest_seen:
            shortest_seen = q
        if q == g:
            found.add(frozenset(cyc))
    assert found and shortest_seen == g
    return found


def main() -> None:
    rng = random.Random(SEED)
    retained = residual = nontrivial = base_fail = 0
    min_slack = None
    min_record = None
    violation = None

    for trial in range(TRIALS):
        G, intended_g = build(rng)
        g = nx.girth(G)
        if g != intended_g:
            continue
        retained += 1
        dist, radius, D, centers, e, realizers = invariants(G)
        k = g // 2
        if D >= e + k:
            continue
        residual += 1
        if e <= k:
            continue
        nontrivial += 1
        threshold = e - k
        base = frozenset(range(g))
        h0 = h_for_cycle(dist, realizers, base)
        if h0 >= threshold:
            slack = h0 - threshold
            best_h = h0
            cycle_count = 1
        else:
            base_fail += 1
            cycles = all_shortest_cycle_sets(G, g)
            best_h = max(h_for_cycle(dist, realizers, K) for K in cycles)
            slack = best_h - threshold
            cycle_count = len(cycles)

        if min_slack is None or slack < min_slack:
            min_slack = slack
            min_record = {
                "trial": trial, "graph6": nx.to_graph6_bytes(
                    G, header=False).decode().strip(),
                "n": len(G), "m": G.number_of_edges(), "g": g, "k": k,
                "radius": radius, "diameter": D, "e": e,
                "threshold": threshold, "best_h": best_h,
                "cycle_count_checked": cycle_count,
                "centers": centers, "realizers": realizers,
            }
        if slack < 0:
            violation = min_record
            break

    result = {
        "test": "exact_residual_N1_sparse_ears",
        "seed": SEED, "planned_trials": TRIALS,
        "trials_completed": trial + 1,
        "retained_exact_girth": retained, "residual": residual,
        "nontrivial_e_gt_k": nontrivial,
        "base_cycle_failures_requiring_all_cycles": base_fail,
        "minimum_slack": min_slack, "minimum_record": min_record,
        "violation": violation,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
