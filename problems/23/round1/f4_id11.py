import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import networkx as nx
from f1_bip import g6_decode, bip_bruteforce

for g6 in ["J?bFF`wN?{?", "I?rFf_{N?"]:
    n, E = g6_decode(g6)
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
    print(g6, "n", n, "m", G.number_of_edges(),
          "deg", sorted(dict(G.degree()).values()), "bip", bip_bruteforce(n, E))
    if n == 11:
        for S in [(1,2),(1,3),(1,4),(1,5),(2,3),(2,5),(3,4),(2,4),(3,5),(4,5)]:
            C = nx.Graph(); C.add_nodes_from(range(11))
            for i in range(11):
                for s in S:
                    C.add_edge(i, (i+s) % 11)
            if C.number_of_edges() == 22 and nx.is_isomorphic(C, G):
                print("   ISO to Cayley(Z_11, +-{%d,%d})" % S)
    print("   automorphisms:",
          sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter()))
    print("   odd girth:", min(len(c) for c in nx.minimum_cycle_basis(G)),
          " max independent set:",
          max(len(c) for c in nx.find_cliques(nx.complement(G))))
