#!/usr/bin/env python3
"""Wave2 test #2: refined center bound with two-tail sums.

For each cyclic connected graph, enumerate ALL shortest cycles (length = girth).
For each shortest cycle C let d(v,C) = min dist to C.  Define
  S1(C)  = max_v d(v,C)
  S2(C)  = max_{u != v} d(u,C) + d(v,C)   (top two values)
  S2*    = max over shortest cycles C of S2(C)
  S1*    = max over shortest cycles C of S1(C)

Candidate bounds tested (cyclic, e >= 1 only; g>=4 is the open regime but test all):
  B3': e <= max(diam - g//2, S2*)
  B4': e <= max(diam - g//2, S1* + something)?  (recorded raw for analysis)
Also matched buildability side (n <= 15):
  A2': t >= g - 1 + S2*(compat crude)  -- NOT expected to hold in general
       (branching stems!), recorded to measure the gap.
Records worst cases for inspection.
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
    rng = random.Random(999)
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


def shortest_cycles(A, g, cap=4000):
    out = []
    for cyc in nx.simple_cycles(A, length_bound=g):
        if len(cyc) == g:
            out.append(cyc)
            if len(out) >= cap:
                break
    return out


def main():
    tested = 0
    nB3 = 0
    minB3 = 10 ** 9
    violB3 = []
    gapA2 = {}  # histogram of t - (g-1+S2*) on graphs where S2* determines B3'
    nA2 = 0
    violA2 = []
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
        if e == 0:
            continue
        tested += 1
        nodes = sorted(A.nodes()); idx = {u: i for i, u in enumerate(nodes)}
        best_S2 = -1; best_S1 = -1
        for cyc in shortest_cycles(A, g):
            cset = [idx[u] for u in cyc]
            dC = [min(dist[v][c] for c in cset) for v in range(n)]
            s = sorted(dC, reverse=True)
            S1 = s[0]; S2 = s[0] + s[1]
            if S2 > best_S2: best_S2 = S2
            if S1 > best_S1: best_S1 = S1
        slackB3 = max(diam - g // 2, best_S2) - e
        minB3 = min(minB3, slackB3)
        if slackB3 < 0:
            nB3 += 1
            if len(violB3) < 40:
                violB3.append({"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                               "n": n, "girth": g, "diam": diam, "rad": rad, "e": e,
                               "S2": best_S2, "S1": best_S1, "slack": slackB3})
        if n <= TREE_N_CAP and best_S2 > diam - g // 2:
            t, _ = largest_induced_tree(n, adj)
            gap = t - (g - 1 + best_S2)
            gapA2[gap] = gapA2.get(gap, 0) + 1
            if gap < 0:
                nA2 += 1
                if len(violA2) < 40:
                    violA2.append({"name": name, "g6": nx.to_graph6_bytes(A, header=False).decode().strip(),
                                   "n": n, "girth": g, "t": t, "S2": best_S2, "gap": gap})
    out = {"tested": tested, "violB3": nB3, "min_slackB3": minB3,
           "violA2crude": nA2, "gapA2_hist": {str(k): v for k, v in sorted(gapA2.items())},
           "examplesB3": violB3, "examplesA2": violA2}
    with open(r"E:\Projects\ErdosProblems\problems_external\wowii_144\wave2\test_S2_results.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("tested", "violB3", "min_slackB3", "violA2crude", "gapA2_hist")}, indent=1))
    for r in violB3[:12]:
        print("B3", r)
    for r in violA2[:12]:
        print("A2", r)


if __name__ == "__main__":
    main()
