"""
G1: graph constructors for the delta > n/3 structure theory (Erdos bipartition conjecture, round 2).

Graphs built here, following the definitions in
  S. Brandt, S. Thomasse, "Dense triangle-free graphs are four-colorable:
  a solution to the Erdos-Simonovits problem" (preprint, J. Combin. Theory Ser. B),
  Section 1, and
  C.C. Chen, G.P. Jin, K.M. Koh, "Triangle-free graphs with large degree",
  Combin. Probab. Comput. 6 (1997) 381-396.

Gamma_i  (= Andrasfai graph And_i):
  vertex set {1,...,3i-1}; vertex j has neighbours j+i, ..., j+2i-1 (mod 3i-1).
  (Brandt-Thomasse, p.3.)  Equivalently, Heinig's definition: vertices v_0..v_{3i-2},
  v_a ~ v_b iff |a-b| = 1 mod 3.  The two are isomorphic (multiply indices by i mod 3i-1).

Vega graph Upsilon_i, i >= 2 (Brandt-Thomasse, p.4):
  start with Gamma_i on {1,...,3i-1}; add an edge xy and an induced 6-cycle
  (a,v,c,u,b,w); x joined to a,b,c; y joined to u,v,w;
  N(a) cap Gamma_i = N(u) cap Gamma_i = {1,...,i}
  N(b) cap Gamma_i = N(v) cap Gamma_i = {i+1,...,2i}
  N(c) cap Gamma_i = N(w) cap Gamma_i = {2i+1,...,3i-1}
  |Upsilon_i| = 3i+7.
  The other Vega graphs are Upsilon_i - {y}, Upsilon_i - {2i}, Upsilon_i - {y,2i}.
  Upsilon_2 - {y,4} is the Grotzsch graph.
"""

import itertools
import networkx as nx


def gamma(i):
    """Gamma_i = Andrasfai graph And_i, on 3i-1 vertices, i-regular."""
    p = 3 * i - 1
    G = nx.Graph()
    G.add_nodes_from(range(1, p + 1))
    for j in range(1, p + 1):
        for d in range(i, 2 * i):
            k = (j + d - 1) % p + 1
            G.add_edge(j, k)
    return G


def andrasfai_heinig(k):
    """Heinig's form: v_0..v_{3k-2}, v_a~v_b iff |a-b| = 1 mod 3."""
    p = 3 * k - 1
    G = nx.Graph()
    G.add_nodes_from(range(p))
    for a in range(p):
        for b in range(a + 1, p):
            if abs(a - b) % 3 == 1:
                G.add_edge(a, b)
    return G


def grotzsch():
    """Grotzsch graph = Mycielskian of C5, 11 vertices, triangle-free, 4-chromatic."""
    G = nx.Graph()
    # C5 on u0..u4, shadows w0..w4, apex z
    for i in range(5):
        G.add_edge(('u', i), ('u', (i + 1) % 5))
    for i in range(5):
        for j in [(i + 1) % 5, (i - 1) % 5]:
            G.add_edge(('w', i), ('u', j))
        G.add_edge(('w', i), ('z', 0))
    return nx.convert_node_labels_to_integers(G, ordering='sorted')


def vega(i, delete=()):
    """Upsilon_i (Vega graph on 3i+7 vertices), optionally minus a set of vertices.

    Vertex labels: integers 1..3i-1 for the Gamma_i part, and strings
    'x','y','a','b','c','u','v','w'.
    delete: iterable of labels to remove, e.g. ('y',) or ('y', 2*i).
    """
    assert i >= 2
    G = gamma(i)
    p = 3 * i - 1
    G.add_nodes_from(['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w'])
    G.add_edge('x', 'y')
    # induced 6-cycle (a,v,c,u,b,w)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']
    for t in range(6):
        G.add_edge(cyc[t], cyc[(t + 1) % 6])
    for t in ['a', 'b', 'c']:
        G.add_edge('x', t)
    for t in ['u', 'v', 'w']:
        G.add_edge('y', t)
    A = list(range(1, i + 1))
    B = list(range(i + 1, 2 * i + 1))
    C = list(range(2 * i + 1, p + 1))
    for t in ['a', 'u']:
        for j in A:
            G.add_edge(t, j)
    for t in ['b', 'v']:
        for j in B:
            G.add_edge(t, j)
    for t in ['c', 'w']:
        for j in C:
            G.add_edge(t, j)
    G.remove_nodes_from(list(delete))
    return G


def petersen_contract_edge():
    """Petersen graph with one edge contracted (9 vertices, triangle-free)."""
    P = nx.petersen_graph()
    e = list(P.edges())[0]
    return nx.contracted_edge(P, e, self_loops=False)


# ------------------------------------------------------------------ checks

def is_triangle_free(G):
    return max((len(c) for c in nx.find_cliques(G)), default=0) <= 2


def is_maximal_triangle_free(G):
    if not is_triangle_free(G):
        return False
    return nx.diameter(G) <= 2 if nx.is_connected(G) else False


def twin_free(G):
    nb = {v: frozenset(G[v]) for v in G}
    return len(set(nb.values())) == G.number_of_nodes()


def chromatic_number(G):
    n = G.number_of_nodes()
    for k in range(1, n + 1):
        if _kcolorable(G, k):
            return k
    return n


def _kcolorable(G, k):
    nodes = list(G.nodes())
    col = {}

    def bt(idx):
        if idx == len(nodes):
            return True
        v = nodes[idx]
        used = {col[u] for u in G[v] if u in col}
        cap = min(k, max(col.values(), default=-1) + 2)
        for c in range(cap):
            if c not in used:
                col[v] = c
                if bt(idx + 1):
                    return True
                del col[v]
        return False

    return bt(0)


def report(name, G):
    degs = [d for _, d in G.degree()]
    print(f"{name:22s} n={G.number_of_nodes():3d} m={G.number_of_edges():4d} "
          f"delta={min(degs)} Delta={max(degs)} delta/n={min(degs)/G.number_of_nodes():.5f} "
          f"trifree={is_triangle_free(G)} twinfree={twin_free(G)} "
          f"maxtf={is_maximal_triangle_free(G)} chi={chromatic_number(G)}")


if __name__ == '__main__':
    for i in range(1, 10):
        report(f"Gamma_{i}", gamma(i))
    print()
    report("Grotzsch", grotzsch())
    report("Petersen/e", petersen_contract_edge())
    print()
    for i in [2, 3, 4]:
        report(f"Upsilon_{i}", vega(i))
        report(f"Upsilon_{i}-y", vega(i, ('y',)))
        report(f"Upsilon_{i}-{2*i}", vega(i, (2 * i,)))
        report(f"Upsilon_{i}-y,{2*i}", vega(i, ('y', 2 * i)))
    print()
    # verify Upsilon_2 - {y,4} == Grotzsch
    H = vega(2, ('y', 4))
    print("Upsilon_2 - {y,4} isomorphic to Grotzsch:",
          nx.is_isomorphic(H, grotzsch()))
    # verify Gamma_3 == Wagner graph (Moebius ladder M8)
    W = nx.circulant_graph(8, [1, 4])
    print("Gamma_3 isomorphic to Wagner graph M8:", nx.is_isomorphic(gamma(3), W))
    print("Gamma_2 isomorphic to C5:", nx.is_isomorphic(gamma(2), nx.cycle_graph(5)))
    for k in range(2, 7):
        print(f"Gamma_{k} iso Heinig And_{k}:",
              nx.is_isomorphic(gamma(k), andrasfai_heinig(k)))
