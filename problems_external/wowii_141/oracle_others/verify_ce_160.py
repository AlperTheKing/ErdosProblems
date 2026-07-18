"""Self-contained verifier: counterexample to FC WrittenOnTheWallII conjecture160.

FC statement (GraphConjecture160.lean):
  For connected G:  maxL + maxT * cC4 <= Ls G, where
    maxL = max_v indepNum(G[N(v)])
    maxT = max_v #(3-cliques containing v)
    cC4  = countInducedC4 G  (number of INDUCED 4-cycles)
    Ls G = max #leaves over spanning trees of G.

Counterexample: graph6 "D]w" (5 vertices, 7 edges) = K_{2,3} plus one edge
inside the 3-side.  maxL=2, maxT=2, cC4=2, Ls=3:  2 + 2*2 = 6 > 3.

Root cause: the formalization multiplies the max triangle count by the induced-
C4 *count*; any graph with both triangles and >=1 induced C4 (and small max-
leaf number) violates it.  489 of the 995 connected graphs on 2..7 vertices
are counterexamples.
"""

import itertools
import networkx as nx

G = nx.from_graph6_bytes(b"D]w")
V = list(G.nodes())
assert nx.is_connected(G) and G.number_of_nodes() == 5


def alpha(H):
    nodes = list(H.nodes())
    for r in range(len(nodes), 0, -1):
        for S in itertools.combinations(nodes, r):
            if all(not H.has_edge(u, v) for u, v in itertools.combinations(S, 2)):
                return r
    return 0


maxL = max(alpha(G.subgraph(list(G.neighbors(v)))) for v in V)
maxT = max(sum(1 for a, b in itertools.combinations(list(G.neighbors(v)), 2)
               if G.has_edge(a, b)) for v in V)


def isInducedC4(a, b, c, d):
    """Exact Lean SimpleGraph.isInducedC4 (three pairings)."""
    A = G.has_edge

    def chk(p, q, r, s):
        return A(p, q) and A(q, r) and A(r, s) and A(s, p) \
            and not A(p, r) and not A(q, s)
    return chk(a, b, c, d) or chk(a, b, d, c) or chk(a, c, b, d)


ordered = sum(1 for t in itertools.product(V, repeat=4)
              if len(set(t)) == 4 and isInducedC4(*t))
cC4 = ordered // 24  # exact Lean countInducedC4

Ls = 0
for T in itertools.combinations(list(G.edges()), 4):
    H = nx.Graph()
    H.add_nodes_from(V)
    H.add_edges_from(T)
    if nx.is_connected(H):
        Ls = max(Ls, sum(1 for v in V if H.degree(v) == 1))

lhs = maxL + maxT * cC4
print(f"graph6=D]w  edges={sorted(G.edges())}")
print(f"maxL={maxL}  maxT={maxT}  countInducedC4={cC4}  Ls={Ls}")
print(f"conjecture160 asserts {lhs} <= {Ls}:  {lhs <= Ls}")
assert (maxL, maxT, cC4, Ls) == (2, 2, 2, 3)
assert lhs > Ls
print("COUNTEREXAMPLE CONFIRMED")
