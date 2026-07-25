"""Structure of the exact extremal graphs for a(N), N <= 14."""
import networkx as nx
from f1_bip import g6_decode, bip_bruteforce
from f1_c5_gap import c5_colourable

CAND = {
    11: ["J?BEFo}}@{?", "J?BD@g]Qvo?", "J?bFF`wN?{?", "J?`cn@w]?y?"],
    12: ["K?ABBBwerwBw", "K?BD@g]Qvo^?"],
    13: ["L??FFB_~?~^_Fw", "L?`DAboU`w@{hS", "L?`DE`gl@YJODg"],
}


def mycielskian(G):
    H = nx.Graph()
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    for u, v in G.edges():
        H.add_edge(idx[u], idx[v])
        H.add_edge(idx[u], n + idx[v])
        H.add_edge(idx[v], n + idx[u])
    for i in range(n):
        H.add_edge(n + i, 2 * n)
    return H


GROT = mycielskian(nx.cycle_graph(5))


def chrom(G):
    for k in range(2, 6):
        if nx.algorithms.coloring.greedy_color(G):
            pass
        # exact via brute force for small graphs
        n = G.number_of_nodes()
        nodes = list(G.nodes())
        col = {}
        def rec(i):
            if i == n:
                return True
            v = nodes[i]
            used = {col[w] for w in G[v] if w in col}
            for c in range(min(k, i + 1)):
                if c not in used:
                    col[v] = c
                    if rec(i + 1):
                        return True
                    del col[v]
            return False
        if rec(0):
            return k
    return None


def girth(G):
    g = None
    for cyc in nx.simple_cycles(G, length_bound=6):
        if g is None or len(cyc) < g:
            g = len(cyc)
    return g


print(f"Grotzsch graph: n={GROT.number_of_nodes()} e={GROT.number_of_edges()} "
      f"bip={bip_bruteforce(11, list(GROT.edges()))} chi={chrom(GROT)}")
print()
for N in sorted(CAND):
    for g6 in CAND[N]:
        n, E = g6_decode(g6)
        G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
        b = bip_bruteforce(n, E)
        degs = sorted(d for _, d in G.degree())
        iso_g = nx.is_isomorphic(G, GROT)
        subg = False
        if n >= 11:
            # does G contain the Grotzsch graph as a subgraph on 11 vertices?
            gm = nx.algorithms.isomorphism.GraphMatcher(G, GROT)
            subg = gm.subgraph_is_monomorphic()
        print(f"N={N} {g6:16s} e={G.number_of_edges():3d} bip={b} chi={chrom(G)} "
              f"girth={girth(G)} alpha={len(max(nx.find_cliques(nx.complement(G)), key=len))} "
              f"deg={degs} C5col={c5_colourable(n, E)} isGrotzsch={iso_g} "
              f"containsGrotzsch={subg}")
