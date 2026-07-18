"""Targeted search #2:
 F. conj100: G with sparse complement containing planted clique
    (violation iff sqrt(sum deg_Gc^2) <= 4(alpha-1) - 2*maxL, both sides connected)
 G. conj291: dense H + 1-2 pendant vertices (freqMinTriangles small)
 H. conj217: theta graphs / subdivisions (sparse, small Ls, residue check)
"""

import sys
import random
import itertools

import networkx as nx

from wowii_oracle import (nx_to_adj, graph_key, popcount, bits,
                          indep_num_mask, residue_of, hh_zero_step,
                          num_triangles_at, total_dom_number, connected_mask,
                          Ls_of, ham_ends)

VIOL = []


def report(name, g6, detail):
    VIOL.append((name, g6, detail))
    print(f"VIOLATION conj{name}: {g6} :: {detail}", flush=True)


def search_100(trials=20000, seed=1001):
    rng = random.Random(seed)
    best_margin = None
    for _ in range(trials):
        n = rng.randint(6, 15)
        s = rng.randint(3, min(8, n - 1))
        # complement Gc: clique K_s + outer vertices attached sparsely
        Gc = nx.Graph()
        Gc.add_nodes_from(range(n))
        clique = list(range(s))
        for a, c in itertools.combinations(clique, 2):
            Gc.add_edge(a, c)
        for w in range(s, n):
            k = rng.choice([1, 1, 2, 2, 3, 4])
            for t in rng.sample(range(n), min(k, n - 1)):
                if t != w:
                    Gc.add_edge(w, t)
        if not nx.is_connected(Gc):
            continue
        G = nx.complement(Gc)
        if G.number_of_edges() == 0 or not nx.is_connected(G):
            continue
        nn, adj = nx_to_adj(G)
        full = (1 << nn) - 1
        memo = {}
        alpha = indep_num_mask(adj, full, memo)
        maxL = max(indep_num_mask(adj, adj[v], memo) for v in range(nn))
        cadj = [full & ~adj[v] & ~(1 << v) for v in range(nn)]
        S = sum(popcount(cadj[v]) ** 2 for v in range(nn))
        rhs = 4 * (alpha - 1) - 2 * maxL
        margin = S - rhs * rhs if rhs >= 0 else None
        if rhs >= 0 and S <= rhs * rhs:
            report("100", graph_key(G),
                   f"alpha={alpha}, maxL={maxL}, complL2sq={S}")
        if rhs >= 0 and (best_margin is None or margin < best_margin):
            best_margin = margin
    print(f"[100-planted] {trials} trials, best S-rhs^2 margin={best_margin}",
          flush=True)


def search_291(trials=8000, seed=2911):
    rng = random.Random(seed)
    tested = 0
    best = None
    for _ in range(trials):
        nh = rng.randint(6, 11)
        p = rng.choice([0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        H = nx.gnp_random_graph(nh, p, seed=rng.randrange(1 << 30))
        if not nx.is_connected(H):
            continue
        G = H.copy()
        npend = rng.choice([1, 1, 1, 2])
        targets = rng.sample(range(nh), npend)
        for i, t in enumerate(targets):
            G.add_edge(nh + i, t)
        n, adj = nx_to_adj(G)
        if n <= 3:
            continue
        tested += 1
        gt = total_dom_number(n, adj)
        deg = [popcount(adj[v]) for v in range(n)]
        k = hh_zero_step(deg)
        tri = [num_triangles_at(adj, v) for v in range(n)]
        mn = min(tri)
        freq = sum(1 for t in tri if t == mn)
        slack = k + freq - gt
        if best is None or slack < best:
            best = slack
        if gt > k + freq:
            report("291", graph_key(G),
                   f"gamma_t={gt}, k={k}, freqMinTri={freq}")
    print(f"[291-pendant] tested={tested}, min slack (k+freq-gamma_t)={best}",
          flush=True)


def search_217(seed=2171):
    """Theta graphs, generalized theta, subdivided K4/K_{2,3}: sparse graphs
    with small Ls; check residue=2 branch of 217."""
    tested = 0
    cases = []
    # generalized theta: two hubs joined by k internally-disjoint paths
    for k in (3, 4):
        for lens in itertools.combinations_with_replacement(range(1, 6), k):
            if sum(l - 1 for l in lens) + 2 > 13:
                continue
            if lens.count(1) > 1:
                continue  # multigraph
            G = nx.Graph()
            u, v = 0, 1
            nid = 2
            for L in lens:
                prev = u
                for _ in range(L - 1):
                    G.add_edge(prev, nid)
                    prev = nid
                    nid += 1
                G.add_edge(prev, v)
            cases.append(G)
    # subdivisions of K4
    K4 = nx.complete_graph(4)
    rng = random.Random(seed)
    for _ in range(300):
        G = nx.Graph(K4)
        nid = 4
        for (a, b) in list(K4.edges()):
            subdiv = rng.randint(0, 2)
            if subdiv:
                G.remove_edge(a, b)
                prev = a
                for _ in range(subdiv):
                    G.add_edge(prev, nid)
                    prev = nid
                    nid += 1
                G.add_edge(prev, b)
        if G.number_of_nodes() <= 14:
            cases.append(nx.convert_node_labels_to_integers(G))
    seen = set()
    for G in cases:
        g6 = graph_key(nx.convert_node_labels_to_integers(G))
        if g6 in seen or not nx.is_connected(G):
            continue
        seen.add(g6)
        tested += 1
        n, adj = nx_to_adj(G)
        deg = [popcount(adj[v]) for v in range(n)]
        res = residue_of(deg)
        Ls = Ls_of(n, adj)
        ind = 1 if res == 2 else 0
        if Ls <= 4 * ind + 2:
            ends = ham_ends(n, adj)
            ham = ends[(1 << n) - 1] != 0
            if not ham:
                report("217", g6, f"Ls={Ls}, residue={res}, ham=False")
    print(f"[217-theta] tested={tested}", flush=True)


def main():
    which = sys.argv[1]
    if which == "100":
        search_100()
    elif which == "291":
        search_291()
    elif which == "217":
        search_217()
    if VIOL:
        with open("violations_targeted.txt", "a") as f:
            for name, g6, det in VIOL:
                f.write(f"{name}\t{g6}\t{det}\n")
    print(f"TOTAL VIOLATIONS: {len(VIOL)}")


if __name__ == "__main__":
    main()
