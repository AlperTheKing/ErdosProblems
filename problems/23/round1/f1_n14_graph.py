"""Identify the unique extremal graph at N=14 (bip = 7 = floor(14^2/25))."""
import networkx as nx
from f1_bip import g6_decode, bip_bruteforce
from f1_c5_gap import c5_colourable

G6 = "M?AE@bH{AYN_LgBs?"
n, E = g6_decode(G6)
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
print("N =", n, "e =", G.number_of_edges(), "bip =", bip_bruteforce(n, E))
print("degrees:", sorted(dict(G.degree()).items()))
adj = {v: frozenset(G[v]) for v in G}
# twin classes
cls = {}
for v in G:
    cls.setdefault(adj[v], []).append(v)
print("twin classes:", [c for c in cls.values() if len(c) > 1])
# quotient graph
reps = [c[0] for c in cls.values()]
Q = G.subgraph(reps).copy()
print("quotient: n =", Q.number_of_nodes(), "e =", Q.number_of_edges())
qn, qE = Q.number_of_nodes(), [(u, v) for u, v in Q.edges()]
idx = {v: i for i, v in enumerate(Q.nodes())}
qE = [(idx[u], idx[v]) for u, v in qE]
print("quotient bip:", bip_bruteforce(qn, qE), " quotient degrees:",
      sorted(d for _, d in Q.degree()))
print("weights:", [len(c) for c in cls.values()])
print("C5-colourable:", c5_colourable(n, E))
print("chromatic number 3?", nx.algorithms.coloring.greedy_color(G) is not None)
# named comparisons
C13 = nx.circulant_graph(13, [1, 5])
print("C13(1,5): e =", C13.number_of_edges(), " bip =",
      bip_bruteforce(13, list(C13.edges())), " triangle-free:",
      all(not (set(C13[u]) & set(C13[v])) for u, v in C13.edges()))
print("quotient iso C13(1,5)?", nx.is_isomorphic(Q, C13))
# is G a subgraph of a blow-up of C13(1,5)?
print("aut group size:", len(list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())))
# independence number and neighbourhood structure
comp = nx.complement(G)
alpha = len(max(nx.find_cliques(comp), key=len))
print("alpha =", alpha)
# Mycielski / Kneser tests
print("is bipartite:", nx.is_bipartite(G))
# list all 5-cycles count
c5 = sum(1 for c in nx.simple_cycles(G, length_bound=5) if len(c) == 5)
c4 = sum(1 for c in nx.simple_cycles(G, length_bound=4) if len(c) == 4)
print("#C4 =", c4, " #C5 =", c5)
print("edges:", sorted(G.edges()))
