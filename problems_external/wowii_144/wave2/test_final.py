#!/usr/bin/env python3
"""Wave2 test #4: final lemma battery.

 T1 (g>=5): e <= sigma-minus  (pure branch-height sum, no diam branch at all)
 T2 (g>=5): e <= max(diam - g//2, sigma-minus)   [= E-, re-verified]
 T3 (g=4):  t = diam+1  ==>  e <= diam - 2       [girth-4 endgame]
 T4 (g=4):  e <= max(diam - 2, sigma)            [does the g>=5 scheme fail how often at 4?]
 T5 (g>=5): sanity C144
Also for T3 record the joint-condition frequency.
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


def theta(a, b, c):
    G = nx.Graph(); G.add_node(0); G.add_node(1)
    nxt = 2
    for k in (a, b, c):
        prev = 0
        for _ in range(k):
            G.add_edge(prev, nxt); prev = nxt; nxt += 1
        G.add_edge(prev, 1)
    return G


def hub_wheel(m, step):
    # C_{2m} plus hub adjacent to every 'step'-th vertex
    G = nx.cycle_graph(2 * m)
    hub = 2 * m
    for i in range(0, 2 * m, step):
        G.add_edge(hub, i)
    return G


def graphs():
    for A in nx.graph_atlas_g()[2:]:
        if A.number_of_nodes() >= 2 and nx.is_connected(A):
            yield ("atlas", A)
    rng = random.Random(31337)
    for n in range(8, 15):
        for p in (0.12, 0.18, 0.25, 0.4):
            for i in range(200):
                A = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
                if nx.is_connected(A):
                    yield (f"rand({n},{p},{i})", A)
    for n in range(8, 15):
        for extra in (1, 2, 3, 4):
            for i in range(150):
                T = nx.random_labeled_tree(n, seed=rng.randrange(1 << 30))
                A = nx.Graph(T); tries = 0
                while A.number_of_edges() < n - 1 + extra and tries < 60:
                    u, v = rng.randrange(n), rng.randrange(n)
                    if u != v and not A.has_edge(u, v):
                        A.add_edge(u, v)
                    tries += 1
                yield (f"tree+{extra}({n},{i})", A)
    for g in range(3, 13):
        specs = []
        for a in range(0, g):
            for b in range(a + 1, g):
                for l1 in (1, 2, 3, 5):
                    for l2 in (1, 2, 3, 5):
                        specs.append(((a, l1), (b, l2)))
        for a, b, c in itertools.combinations(range(g), 3):
            for l in (1, 2, 3, 5):
                specs.append(((a, l), (b, l), (c, l)))
        for spec in specs:
            yield (f"cycleLegs({g},{spec})", cycle_legs(g, spec))
    for a in range(0, 7):
        for b in range(max(a, 1), 8):
            for c in range(b, 9):
                yield (f"theta({a},{b},{c})", theta(a, b, c))
    for m in range(2, 8):
        for step in (1, 2):
            yield (f"hub({m},{step})", hub_wheel(m, step))
    # bipartite-ish girth-4 stress: random bipartite
    for n1 in range(3, 7):
        for n2 in range(3, 7):
            for i in range(60):
                A = nx.bipartite.random_graph(n1, n2, 0.5, seed=rng.randrange(1 << 30))
                A = nx.Graph(A)
                if A.number_of_nodes() >= 2 and nx.is_connected(A):
                    yield (f"bip({n1},{n2},{i})", A)


def shortest_cycles(A, g, cap=3000):
    out = []
    for cyc in nx.simple_cycles(A, length_bound=g):
        if len(cyc) == g:
            out.append(cyc)
            if len(out) >= cap:
                break
    return out


def main():
    stats = {k: {"viol": 0, "min": 10 ** 9, "ex": [], "n_applicable": 0}
             for k in ("T1", "T2", "T3", "T4", "T5")}

    def rec(key, slack, info):
        s = stats[key]
        s["n_applicable"] += 1
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
        diam = max(ecc)
        center = 0
        rad = min(ecc)
        for v in range(n):
            if ecc[v] == rad:
                center |= 1 << v
        e = ecc_of_set(n, dist, center)
        if e == 0:
            continue
        nodes = sorted(A.nodes()); idx = {u: i for i, u in enumerate(nodes)}
        bestSumM = -1
        for cyc in shortest_cycles(A, g):
            cset = set(idx[u] for u in cyc)
            dC = [min(dist[v][idx[u]] for u in cyc) for v in range(n)]
            H = A.subgraph([u for u in A.nodes() if idx[u] not in cset])
            sumh = 0; minh = 10 ** 9; attach_all = set(); nb = 0
            for comp in nx.connected_components(H):
                h = max(dC[idx[u]] for u in comp)
                sumh += h; minh = min(minh, h); nb += 1
                for u in comp:
                    for w in A[u]:
                        if idx[w] in cset:
                            attach_all.add(idx[w])
            covered = (len(attach_all) == g and nb > 0)
            bestSumM = max(bestSumM, sumh - (minh if covered else 0))
        info = {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                "n": n, "girth": g, "diam": diam, "rad": rad, "e": e, "sumM": bestSumM}
        if g >= 5:
            rec("T1", bestSumM - e, dict(info, slack=bestSumM - e))
            rec("T2", max(diam - g // 2, bestSumM) - e, info)
            if n <= TREE_N_CAP:
                t, _ = largest_induced_tree(n, adj)
                rec("T5", t - (g - 1 + e), dict(info, t=t))
        if g == 4:
            rec("T4", max(diam - 2, bestSumM) - e, dict(info, slack=max(diam - 2, bestSumM) - e))
            if n <= TREE_N_CAP:
                t, _ = largest_induced_tree(n, adj)
                if t == diam + 1:
                    rec("T3", (diam - 2) - e, dict(info, t=t, slack=(diam - 2) - e))
    out = {}
    for k, s in stats.items():
        out[k] = {"applicable": s["n_applicable"], "viol": s["viol"],
                  "min_slack": (s["min"] if s["n_applicable"] else None), "examples": s["ex"]}
    with open(r"E:\Projects\ErdosProblems\problems_external\wowii_144\wave2\test_final_results.json", "w") as f:
        json.dump(out, f, indent=1)
    for k in ("T1", "T2", "T3", "T4", "T5"):
        print(k, {kk: out[k][kk] for kk in ("applicable", "viol", "min_slack")})
    for k in ("T1", "T3", "T4"):
        for r in out[k]["examples"][:10]:
            print(k, r)


if __name__ == "__main__":
    main()
