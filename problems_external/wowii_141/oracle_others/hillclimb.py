"""Hill-climbing minimization of conjecture slack for conj 100 and 291.

slack291(G) = hh_zero_step + freqMinTriangles - gamma_t   (violation iff < 0)
slack100(G) = S - rhs^2 where rhs = 4(alpha-1)-2maxL      (violation iff <= 0
              and rhs >= 0; both G and Gc connected)
"""

import sys
import random
import itertools

import networkx as nx

from wowii_oracle import (nx_to_adj, graph_key, popcount, indep_num_mask,
                          hh_zero_step, num_triangles_at, total_dom_number,
                          connected_mask)

INF = 10 ** 9


def slack_291(G):
    if not nx.is_connected(G) or G.number_of_nodes() <= 3:
        return INF, ""
    n, adj = nx_to_adj(G)
    gt = total_dom_number(n, adj)
    if gt is None:
        return INF, ""
    deg = [popcount(adj[v]) for v in range(n)]
    k = hh_zero_step(deg)
    tri = [num_triangles_at(adj, v) for v in range(n)]
    mn = min(tri)
    freq = sum(1 for t in tri if t == mn)
    return k + freq - gt, f"gamma_t={gt}, k={k}, freqMinTri={freq}"


def slack_100(G):
    n = G.number_of_nodes()
    if n < 2 or not nx.is_connected(G):
        return INF, ""
    nn, adj = nx_to_adj(G)
    full = (1 << nn) - 1
    cadj = [full & ~adj[v] & ~(1 << v) for v in range(nn)]
    if not connected_mask(cadj, full):
        return INF, ""
    memo = {}
    alpha = indep_num_mask(adj, full, memo)
    maxL = max(indep_num_mask(adj, adj[v], memo) for v in range(nn))
    S = sum(popcount(cadj[v]) ** 2 for v in range(nn))
    rhs = 4 * (alpha - 1) - 2 * maxL
    if rhs < 0:
        return INF, ""
    return S - rhs * rhs, f"alpha={alpha}, maxL={maxL}, complL2sq={S}, rhs={rhs}"
    # violation iff slack <= 0  (ceil(x) <= alpha-1 iff x <= alpha-1
    #  iff sqrt(S) <= rhs iff S <= rhs^2)


def climb(slack_fn, seeds, rounds, rng, viol_pred, tag):
    best_overall = (INF, None, "")
    found = []
    pop = list(seeds)
    for r in range(rounds):
        # pick a graph, mutate
        G = rng.choice(pop).copy()
        n = G.number_of_nodes()
        op = rng.random()
        if op < 0.42:
            u, v = rng.sample(range(n), 2)
            if G.has_edge(u, v):
                G.remove_edge(u, v)
            else:
                G.add_edge(u, v)
        elif op < 0.6 and n < 13:
            u = rng.randrange(n)
            G.add_edge(n, u)  # add pendant
        elif op < 0.75 and n < 13:
            u, v = rng.sample(range(n), 2)
            G.add_edge(n, u)
            G.add_edge(n, v)
        else:
            u, v = rng.sample(range(n), 2)
            w, x = rng.sample(range(n), 2)
            if G.has_edge(u, v) and not G.has_edge(w, x) and (u, v) != (w, x):
                G.remove_edge(u, v)
                G.add_edge(w, x)
        G = nx.convert_node_labels_to_integers(G)
        s, det = slack_fn(G)
        if s >= INF:
            continue
        if viol_pred(s):
            g6 = graph_key(G)
            found.append((g6, det))
            print(f"VIOLATION[{tag}]: {g6} :: {det}", flush=True)
            if len(found) >= 5:
                break
        if s < best_overall[0]:
            best_overall = (s, graph_key(G), det)
        # population update: keep low-slack graphs
        if s <= best_overall[0] + 1 and len(pop) < 400:
            pop.append(G)
        elif s <= best_overall[0] + 1:
            pop[rng.randrange(len(pop))] = G
    return best_overall, found


def main():
    which = sys.argv[1]
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 99)
    if which == "291":
        seeds = []
        while len(seeds) < 30:
            nh = rng.randint(6, 10)
            H = nx.gnp_random_graph(nh, rng.choice([0.5, 0.65, 0.8]),
                                    seed=rng.randrange(1 << 30))
            if nx.is_connected(H):
                H.add_edge(nh, rng.randrange(nh))
                seeds.append(nx.convert_node_labels_to_integers(H))
        best, found = climb(slack_291, seeds, 12000, rng,
                            lambda s: s < 0, "291")
    else:
        seeds = []
        while len(seeds) < 30:
            n = rng.randint(6, 12)
            Gc = nx.gnp_random_graph(n, rng.choice([0.2, 0.3, 0.4]),
                                     seed=rng.randrange(1 << 30))
            s = rng.randint(3, 6)
            for a, b in itertools.combinations(range(min(s, n)), 2):
                Gc.add_edge(a, b)
            G = nx.complement(Gc)
            if G.number_of_nodes() >= 2 and nx.is_connected(G) \
               and nx.is_connected(Gc):
                seeds.append(G)
        best, found = climb(slack_100, seeds, 12000, rng,
                            lambda s: s <= 0, "100")
    print(f"[{which}] best slack: {best[0]} at {best[1]} :: {best[2]}")
    print(f"TOTAL VIOLATIONS: {len(found)}")
    if found:
        with open("violations_targeted.txt", "a") as f:
            for g6, det in found:
                f.write(f"{which}\t{g6}\t{det}\n")


if __name__ == "__main__":
    main()
