#!/usr/bin/env python3
"""Wave2 test #3: the center-push lemma E and multi-tail buildability A'.

For each shortest cycle C:
  branches = components of G - C; h_i = max_{v in B_i} d(v, C)  (height)
  attach_i = set of cycle vertices adjacent to B_i
  SumH(C)   = sum_i h_i
  SumH-(C)  = SumH - min h_i  if union(attach_i) = C else SumH   (buildable form)
Tested:
  E : e <= max(diam - g//2, max_C SumH(C))
  E-: e <= max(diam - g//2, max_C SumH-(C))
  A': t >= g - 1 + SumH-(C) for every shortest cycle C   (g >= 5 only claim;
      recorded for all g to see where it breaks)
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


def graphs():
    for A in nx.graph_atlas_g()[2:]:
        if A.number_of_nodes() >= 2 and nx.is_connected(A):
            yield ("atlas", A)
    rng = random.Random(777)
    for n in range(8, 15):
        for p in (0.12, 0.18, 0.25, 0.4):
            for i in range(160):
                A = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
                if nx.is_connected(A):
                    yield (f"rand({n},{p},{i})", A)
    for n in range(8, 15):
        for extra in (1, 2, 3):
            for i in range(120):
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
            for l in (2, 3, 5):
                specs.append(((a, l), (b, l), (c, l)))
        for spec in specs:
            yield (f"cycleLegs({g},{spec})", cycle_legs(g, spec))
    for a in range(0, 7):
        for b in range(max(a, 1), 8):
            for c in range(b, 9):
                yield (f"theta({a},{b},{c})", theta(a, b, c))


def shortest_cycles(A, g, cap=3000):
    out = []
    for cyc in nx.simple_cycles(A, length_bound=g):
        if len(cyc) == g:
            out.append(cyc)
            if len(out) >= cap:
                break
    return out


def main():
    tested = 0
    stats = {k: {"viol": 0, "min": 10 ** 9, "ex": []} for k in ("E", "Eminus", "Aprime_g5", "Aprime_all")}

    def rec(key, slack, info):
        s = stats[key]
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
        bestSum = -1; bestSumM = -1
        cycles = shortest_cycles(A, g)
        for cyc in cycles:
            cset = set(idx[u] for u in cyc)
            dC = [min(dist[v][idx[u]] for u in cyc) for v in range(n)]
            H = A.subgraph([u for u in A.nodes() if idx[u] not in cset])
            sumh = 0; minh = 10 ** 9; attach_all = set()
            nbranch = 0
            for comp in nx.connected_components(H):
                h = max(dC[idx[u]] for u in comp)
                sumh += h; minh = min(minh, h); nbranch += 1
                for u in comp:
                    for w in A[u]:
                        if idx[w] in cset:
                            attach_all.add(idx[w])
            covered = (len(attach_all) == g)
            sumh_m = sumh - (minh if (covered and nbranch > 0) else 0)
            bestSum = max(bestSum, sumh)
            bestSumM = max(bestSumM, sumh_m)
            if t is not None:
                slack = t - (g - 1 + sumh_m)
                info = {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                        "n": n, "girth": g, "t": t, "sumh": sumh, "sumh_m": sumh_m,
                        "covered": covered, "slack": slack}
                rec("Aprime_all", slack, info)
                if g >= 5:
                    rec("Aprime_g5", slack, info)
        if e >= 1:
            tested += 1
            base = diam - g // 2
            infoE = {"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                     "n": n, "girth": g, "diam": diam, "rad": rad, "e": e,
                     "bestSum": bestSum, "bestSumM": bestSumM}
            rec("E", max(base, bestSum) - e, dict(infoE, slack=max(base, bestSum) - e))
            rec("Eminus", max(base, bestSumM) - e, dict(infoE, slack=max(base, bestSumM) - e))
    out = {"tested_e_ge_1": tested}
    for k, s in stats.items():
        out[k] = {"viol": s["viol"], "min_slack": s["min"], "examples": s["ex"]}
    with open(r"E:\Projects\ErdosProblems\problems_external\wowii_144\wave2\test_E_results.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: {"viol": out[k]["viol"], "min_slack": out[k]["min_slack"]}
                      for k in ("E", "Eminus", "Aprime_g5", "Aprime_all")}, indent=1))
    print("tested(e>=1):", tested)
    for k in ("E", "Eminus", "Aprime_g5"):
        for r in out[k]["examples"][:8]:
            print(k, r)


if __name__ == "__main__":
    main()
