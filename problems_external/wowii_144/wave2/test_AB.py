#!/usr/bin/env python3
"""Wave2 falsifier tests for the C144 proof scheme.

Scheme:  C144 (g - 1 + e <= t, cyclic case, e >= 1) follows from
  A : t >= g - 1 + (diam - g//2)          [two-tail via diametral pair]
  B : e <= diam - min(g//2, g - 2)        [pure metric center bound]
  plus known  t >= diam + 1  and  t >= g - 1.

This script hunts counterexamples to A and B (and rechecks C144) on:
 * networkx atlas connected graphs (n<=7)
 * random G(n,p) connected graphs
 * cycleLegs(g, spec) families (the Q1/Q2 falsifier shapes)
 * theta graphs
 * random trees + extra random edges (sparse large-girth-ish)
"""
import sys, json, random, itertools

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems_external\wowii_141\oracle")
from invariants import (nx_to_bitadj, graph_connected, all_pairs_dist, girth,
                        largest_induced_tree, eccentricities, ecc_of_set)

import networkx as nx

TREE_N_CAP = 16  # exact largest_induced_tree only up to this n


def cycle_legs(g, spec):
    G = nx.cycle_graph(g)
    nxt = g
    for pos, length in spec:
        prev = pos
        for _ in range(length):
            G.add_edge(prev, nxt)
            prev = nxt
            nxt += 1
    return G


def theta(a, b, c):
    # two hubs joined by three internally disjoint paths with a,b,c internal vertices
    G = nx.Graph()
    G.add_node(0); G.add_node(1)
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
    rng = random.Random(20260718)
    for n in range(8, 15):
        for p in (0.12, 0.18, 0.25, 0.4):
            for i in range(220):
                A = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
                if nx.is_connected(A):
                    yield (f"rand({n},{p},{i})", A)
    # trees + extra edges
    for n in range(8, 15):
        for extra in (1, 2, 3):
            for i in range(150):
                T = nx.random_labeled_tree(n, seed=rng.randrange(1 << 30))
                A = nx.Graph(T)
                tries = 0
                while A.number_of_edges() < n - 1 + extra and tries < 60:
                    u, v = rng.randrange(n), rng.randrange(n)
                    if u != v and not A.has_edge(u, v):
                        A.add_edge(u, v)
                    tries += 1
                yield (f"tree+{extra}({n},{i})", A)
    # cycleLegs: systematic small
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
                if a + b + 2 >= 3 and (a + b + 2 <= b + c + 2):
                    yield (f"theta({a},{b},{c})", theta(a, b, c))


def main():
    nA = nB = nC = 0
    violA, violB, violC = [], [], []
    tested = 0
    minA = minB = minC = 10 ** 9
    for name, A in graphs():
        n, adj = nx_to_bitadj(A)
        if n < 2 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0:
            continue  # acyclic case done
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        diam = max(ecc); rad = min(ecc)
        center = 0
        for v in range(n):
            if ecc[v] == rad:
                center |= 1 << v
        e = ecc_of_set(n, dist, center)
        tested += 1
        # B
        slackB = (diam - min(g // 2, g - 2)) - e
        minB = min(minB, slackB)
        if slackB < 0:
            nB += 1
            if len(violB) < 40:
                violB.append({"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                              "n": n, "girth": g, "diam": diam, "rad": rad, "e": e, "slackB": slackB})
        if n <= TREE_N_CAP:
            t, _ = largest_induced_tree(n, adj)
            slackA = t - (g - 1 + (diam - g // 2))
            minA = min(minA, slackA)
            if slackA < 0:
                nA += 1
                if len(violA) < 40:
                    violA.append({"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                                  "n": n, "girth": g, "diam": diam, "t": t, "slackA": slackA})
            slackC = t - (g - 1 + e)
            minC = min(minC, slackC)
            if slackC < 0:
                nC += 1
                violC.append({"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                              "n": n, "girth": g, "diam": diam, "e": e, "t": t})
    out = {"tested_cyclic": tested, "violA": nA, "violB": nB, "violC144": nC,
           "min_slackA": minA, "min_slackB": minB, "min_slackC144": minC,
           "examplesA": violA, "examplesB": violB, "examplesC": violC}
    with open(r"E:\Projects\ErdosProblems\problems_external\wowii_144\wave2\test_AB_results.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("tested_cyclic", "violA", "violB", "violC144",
                                          "min_slackA", "min_slackB", "min_slackC144")}, indent=1))
    for tag, lst in (("A", violA[:12]), ("B", violB[:12])):
        for r in lst:
            print(tag, r)


if __name__ == "__main__":
    main()
