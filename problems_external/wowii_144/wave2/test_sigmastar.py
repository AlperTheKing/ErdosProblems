#!/usr/bin/env python3
"""Wave2 test #5: exact-provable-form alignment.

sigma*(C) = sum h_i                          if k <= g-1   (k = #branches)
          = sum h_i - (sum of (k-g+1) smallest h_i)   if k >= g
  (this is exactly what the multi-tail construction proves for g>=5:
   one stem per branch, stems use <= g-1 distinct attachment points)

 E*  (g>=5): e <= max(diam - g//2, max over shortest cycles of sigma*)
 A*  (g>=5, n<=15): t >= g - 1 + sigma*(C) for every shortest cycle
 T3+ (g=4): t = diam+1 ==> e <= diam-2, on a girth-4-heavy corpus
"""
import sys, json, random, itertools

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems_external\wowii_141\oracle")
from invariants import (nx_to_bitadj, graph_connected, all_pairs_dist, girth,
                        largest_induced_tree, eccentricities, ecc_of_set)

import networkx as nx

TREE_N_CAP = 15


def cycle_legs(g, spec):
    G = nx.cycle_graph(g)
    nxt = g
    for pos, length in spec:
        prev = pos
        for _ in range(length):
            G.add_edge(prev, nxt); prev = nxt; nxt += 1
    return G


def graphs():
    for A in nx.graph_atlas_g()[2:]:
        if A.number_of_nodes() >= 2 and nx.is_connected(A):
            yield ("atlas", A)
    rng = random.Random(424242)
    for n in range(8, 15):
        for p in (0.12, 0.18, 0.25, 0.4):
            for i in range(160):
                A = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
                if nx.is_connected(A):
                    yield (f"rand({n},{p},{i})", A)
    for n in range(8, 15):
        for extra in (1, 2, 3, 4):
            for i in range(120):
                T = nx.random_labeled_tree(n, seed=rng.randrange(1 << 30))
                A = nx.Graph(T); tries = 0
                while A.number_of_edges() < n - 1 + extra and tries < 60:
                    u, v = rng.randrange(n), rng.randrange(n)
                    if u != v and not A.has_edge(u, v):
                        A.add_edge(u, v)
                    tries += 1
                yield (f"tree+{extra}({n},{i})", A)
    for g in range(4, 13):
        specs = []
        for a in range(0, g):
            for b in range(a + 1, g):
                for l1 in (1, 2, 3, 5):
                    for l2 in (1, 2, 3, 5):
                        specs.append(((a, l1), (b, l2)))
        for a, b, c in itertools.combinations(range(g), 3):
            for l in (1, 2, 3, 5):
                specs.append(((a, l), (b, l), (c, l)))
        # many-pendant specs (stress k >= g)
        for l in (1, 2):
            specs.append(tuple((i, l) for i in range(g)))
            specs.append(tuple((i, l) for i in range(0, g, 2)))
        for spec in specs:
            yield (f"cycleLegs({g},{spec})", cycle_legs(g, spec))
    # girth-4 heavy: random bipartite + C4-with-legs + hubbed even cycles
    for n1 in range(3, 8):
        for n2 in range(3, 8):
            for i in range(120):
                A = nx.Graph(nx.bipartite.random_graph(n1, n2, 0.45, seed=rng.randrange(1 << 30)))
                if A.number_of_nodes() >= 2 and nx.is_connected(A):
                    yield (f"bip({n1},{n2},{i})", A)
    for m in range(3, 8):
        for step in (2,):
            G = nx.cycle_graph(2 * m); hub = 2 * m
            for i in range(0, 2 * m, step):
                G.add_edge(hub, i)
            yield (f"hub({m})", G)
            for legpos in range(2 * m):
                G2 = nx.Graph(G); G2.add_edge(legpos, 2 * m + 1); G2.add_edge(2 * m + 1, 2 * m + 2)
                yield (f"hubleg({m},{legpos})", G2)


def shortest_cycles(A, g, cap=3000):
    out = []
    for cyc in nx.simple_cycles(A, length_bound=g):
        if len(cyc) == g:
            out.append(cyc)
            if len(out) >= cap:
                break
    return out


def main():
    stats = {k: {"viol": 0, "min": 10 ** 9, "ex": [], "app": 0} for k in ("Estar", "Astar", "T3plus")}

    def rec(key, slack, info):
        s = stats[key]
        s["app"] += 1
        s["min"] = min(s["min"], slack)
        if slack < 0:
            s["viol"] += 1
            if len(s["ex"]) < 30:
                s["ex"].append(info)

    for name, A in graphs():
        n, adj = nx_to_bitadj(A)
        if n < 2 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0:
            continue
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        diam = max(ecc); rad = min(ecc)
        center = 0
        for v in range(n):
            if ecc[v] == rad:
                center |= 1 << v
        e = ecc_of_set(n, dist, center)
        nodes = sorted(A.nodes()); idx = {u: i for i, u in enumerate(nodes)}
        t = None
        if n <= TREE_N_CAP:
            t, _ = largest_induced_tree(n, adj)
        if g >= 5:
            bestSS = -1
            for cyc in shortest_cycles(A, g):
                cset = set(idx[u] for u in cyc)
                dC = [min(dist[v][idx[u]] for u in cyc) for v in range(n)]
                H = A.subgraph([u for u in A.nodes() if idx[u] not in cset])
                hs = sorted(max(dC[idx[u]] for u in comp) for comp in nx.connected_components(H))
                k = len(hs)
                sigma_star = sum(hs) - (sum(hs[:k - g + 1]) if k >= g else 0)
                bestSS = max(bestSS, sigma_star)
                if t is not None:
                    rec("Astar", t - (g - 1 + sigma_star),
                        {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                         "n": n, "girth": g, "t": t, "sigma_star": sigma_star})
            if e >= 1:
                rec("Estar", max(diam - g // 2, bestSS) - e,
                    {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                     "n": n, "girth": g, "diam": diam, "e": e, "bestSS": bestSS})
        if g == 4 and e >= 1 and t is not None and t == diam + 1:
            rec("T3plus", (diam - 2) - e,
                {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                 "n": n, "diam": diam, "rad": rad, "e": e, "t": t})
    out = {}
    for k, s in stats.items():
        out[k] = {"applicable": s["app"], "viol": s["viol"],
                  "min_slack": (s["min"] if s["app"] else None), "examples": s["ex"]}
    with open(r"E:\Projects\ErdosProblems\problems_external\wowii_144\wave2\test_sigmastar_results.json", "w") as f:
        json.dump(out, f, indent=1)
    for k in ("Estar", "Astar", "T3plus"):
        print(k, {kk: out[k][kk] for kk in ("applicable", "viol", "min_slack")})
        for r in out[k]["examples"][:8]:
            print("  ", r)


if __name__ == "__main__":
    main()
