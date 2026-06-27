#!/usr/bin/env python3
"""
Adversarial finder #5 for Erdos #23 Step-2 R2 MASTER INEQUALITY.

FAMILY: RANDOM TRIANGLE-FREE connected graphs.
  For each n in {12,13,14,15,16}, generate >= 400 random *connected*
  *triangle-free* graphs by adding random edges one at a time, rejecting any
  edge that would create a triangle, growing density toward an "in-band-ish"
  target. Then test the R2 master inequality on each.

The master-inequality logic is delegated to the cross-validated clean-room
reference checker problems/23/writeup/r2_check_ref.py (exposes master_check).
The family GENERATOR below is original to this finder. We do NOT touch the
Step-2 bridge/flagsdp/*.py code.

A SINGLE master violation (Gamma + D* > n^2) on a connected-B config REFUTES R2.
We also track local violations (Gamma + D(C) > n^2 for some shortest C).
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import r2_check_ref as R  # master_check(n, edges) -> dict or None


def random_triangle_free_connected(n, rng, target_density):
    """Build a random connected triangle-free graph on n vertices.

    Strategy:
      1. Build a random spanning tree (guarantees connectivity) by attaching
         each new vertex to a random earlier vertex. A tree is triangle-free.
      2. Repeatedly try random non-edges; add one iff it keeps the graph
         triangle-free, until either the edge count reaches the target density
         or we exhaust a budget of failed attempts.
    Returns sorted edge list (each (a,b) with a<b).
    """
    adj = [set() for _ in range(n)]
    edges = set()

    def add_edge(a, b):
        if a > b:
            a, b = b, a
        adj[a].add(b)
        adj[b].add(a)
        edges.add((a, b))

    # 1. random spanning tree (random recursive attachment, shuffled order)
    order = list(range(n))
    rng.shuffle(order)
    for k in range(1, n):
        v = order[k]
        u = order[rng.randrange(k)]
        add_edge(u, v)

    # 2. grow with triangle-free random edges
    max_edges = int(round(target_density * n * (n - 1) / 2))
    # cap below the triangle-free maximum (Turan: <= n^2/4) defensively
    max_edges = min(max_edges, (n * n) // 4)
    fails = 0
    fail_budget = 20 * n * n
    while len(edges) < max_edges and fails < fail_budget:
        a = rng.randrange(n)
        b = rng.randrange(n)
        if a == b:
            fails += 1
            continue
        if a > b:
            a, b = b, a
        if (a, b) in edges:
            fails += 1
            continue
        # triangle test: a-b is safe iff a and b share no common neighbor
        if adj[a] & adj[b]:
            fails += 1
            continue
        add_edge(a, b)
        fails = 0  # reset on success so we keep trying to reach density

    return sorted(edges)


def run(seed=12345):
    rng = random.Random(seed)
    ns = [12, 13, 14, 15, 16]
    per_n = 450  # >= 400 as required
    # "in-band-ish" density: bad-edge band graphs sit near d_edge ~ 0.3-0.45 of
    # the Turan max; sample a spread of target densities to probe both sparse
    # (more bad edges, large Gamma) and dense (near max-cut tightness) regimes.
    density_choices = [0.18, 0.22, 0.26, 0.30, 0.34, 0.38, 0.42]

    grand = {
        "graphs_tested": 0,
        "configs": 0,
        "master_viol": 0,
        "local_viol": 0,
        "min_master_slack": None,
        "min_local_slack": None,
        "tight_master": [],   # edge lists with master slack 0
        "first_violation": None,
        "n_values": ns,
    }

    for n in ns:
        n_master_min = None
        n_configs = 0
        n_tight = 0
        for t in range(per_n):
            dens = rng.choice(density_choices)
            edges = random_triangle_free_connected(n, rng, dens)
            grand["graphs_tested"] += 1
            res = R.master_check(n, edges)
            if res is None:
                continue  # not a connected-B config (no valid cut / no bad edge)
            grand["configs"] += 1
            n_configs += 1
            ms = res["master_slack"]
            ls = res["worst_local_slack"]
            if grand["min_master_slack"] is None or ms < grand["min_master_slack"]:
                grand["min_master_slack"] = ms
            if n_master_min is None or ms < n_master_min:
                n_master_min = ms
            if grand["min_local_slack"] is None or ls < grand["min_local_slack"]:
                grand["min_local_slack"] = ls
            if ms == 0:
                n_tight += 1
                if len(grand["tight_master"]) < 25:
                    grand["tight_master"].append((n, edges, res))
            if ms < 0:
                grand["master_viol"] += 1
                if grand["first_violation"] is None:
                    grand["first_violation"] = (n, edges, res, "MASTER")
            if ls < 0:
                grand["local_viol"] += 1
                if grand["first_violation"] is None:
                    grand["first_violation"] = (n, edges, res, "LOCAL")
        print(f"n={n:2d}: graphs/n={per_n} configs={n_configs:4d} "
              f"tight(master=0)={n_tight} min_master_slack={n_master_min}")
        sys.stdout.flush()

    print("=" * 70)
    print("TOTAL graphs tested :", grand["graphs_tested"])
    print("connected-B configs :", grand["configs"])
    print("master violations   :", grand["master_viol"])
    print("local  violations   :", grand["local_viol"])
    print("global min master slack:", grand["min_master_slack"])
    print("global min local  slack:", grand["min_local_slack"])
    print("tight (master slack 0) examples found:", len(grand["tight_master"]))
    if grand["first_violation"]:
        print("FIRST VIOLATION:", grand["first_violation"])
    else:
        print("NO VIOLATIONS.")
    return grand


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
    run(seed)
