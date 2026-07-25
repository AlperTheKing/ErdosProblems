"""audit_P4_gh — attack P4.md section (g)/(h): the C7 value 4/225 and the Grotzsch equality 1/25.

Exact facts established here:
  * for an ODD cycle C_{2k+1}, psi(C,x) = min_i x_i x_{i+1}  exactly, hence
        max_x psi(C_{2k+1}) = 1/(2k+1)^2   (AM-GM, attained ONLY at the uniform weighting).
    So max_x psi(C7) = 1/49 = 0.020408..., NOT 4/225 = 0.017778...
  * the C5 case of the same identity is why 1/25 is the extremal value at all.
  * for the Grotzsch graph only the LOWER bound max_x psi >= 1/25 is provable here
    (induced C5 + support monotonicity);  "= 1/25" is Erdos 23 for that graph.
"""
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import psi_graph, triangle_free, adj_matrix


def cycle(n):
    return [[(abs(i - j) % n in (1, n - 1)) for j in range(n)] for i in range(n)]


def grotzsch():
    # Mycielskian of C5: u0..u4 (the C5), v0..v4 (v_i ~ neighbours of u_i), w ~ all v_i
    n = 11
    adj = [[False] * n for _ in range(n)]

    def add(a, b):
        adj[a][b] = adj[b][a] = True
    for i in range(5):
        add(i, (i + 1) % 5)
    for i in range(5):
        for j in ((i + 1) % 5, (i - 1) % 5):
            add(5 + i, j)
        add(5 + i, 10)
    return adj


def min_edge_product(x, adj):
    n = len(x)
    return min(x[u] * x[v] for u, v in combinations(range(n), 2) if adj[u][v])


def check_odd_cycle(n):
    C = cycle(n)
    unif = [F(1, n)] * n
    ps = psi_graph(C, unif)
    print(f"  C{n}: psi(uniform) = {ps} = {float(ps):.8f}   min-edge-product = "
          f"{min_edge_product(unif, C)}   equal={ps == min_edge_product(unif, C)}")
    # verify psi = min edge product on random rational weightings
    import random
    rng = random.Random(3)
    bad = 0
    for _ in range(200):
        w = [rng.randint(0, 6) for _ in range(n)]
        if sum(w) == 0:
            continue
        x = [F(wi, sum(w)) for wi in w]
        if psi_graph(C, x) != min_edge_product(x, C):
            bad += 1
    print(f"       psi == min_i x_i x_(i+1) on 200 random weightings: {bad} failures")
    return ps


if __name__ == "__main__":
    print("(g)/(h) ODD CYCLES — exact maxima")
    for n in (5, 7, 9):
        check_odd_cycle(n)
    print()
    print("  AM-GM: min_i x_i x_{i+1} <= (prod_i x_i x_{i+1})^{1/n} = (prod x_i)^{2/n} <= 1/n^2 ,")
    print("  with equality iff x is uniform.  Hence max_x psi(C7) = 1/49 = "
          f"{float(F(1,49)):.8f}  >  4/225 = {float(F(4,225)):.8f}  <-- P4.md's value is REFUTED")
    print(f"  the falsifier is the uniform weighting on C7: psi = 1/49 > 4/225 "
          f"(difference {F(1,49)-F(4,225)} = {float(F(1,49)-F(4,225)):.8f})")
    print(f"  Gamma_7 IS C7 (connection set {{3,4}} = a 7-cycle): "
          f"psi(uniform Gamma_7) = {psi_graph(adj_matrix(7), [F(1,7)]*7)}")
    print(f"  min weighted degree at the true maximiser (uniform) = 2/7 = {float(F(2,7)):.4f}"
          f"  (P4.md says 4/15 = {float(F(4,15)):.4f}) -- also wrong, though still <= 1/3,")
    print("  so P4's qualitative point ('C7's maximiser has delta <= 1/3') survives its wrong number.")
    print()
    print("(g) GROTZSCH")
    G = grotzsch()
    n = 11
    E = sum(1 for u, v in combinations(range(n), 2) if G[u][v])
    print(f"  11 vertices, {E} edges, triangle-free={triangle_free(G)}")
    x = [F(1, 5)] * 5 + [F(0)] * 6
    ps = psi_graph(G, x)
    print(f"  psi at the induced-C5 weighting = {ps}  (= 1/25? {ps == F(1,25)})")
    print("  => max_x psi(Grotzsch) >= 1/25 is PROVED (support monotonicity: the graph induced on")
    print("     the support is exactly C5, so psi(G,x) = psi(C5,x|C5)).")
    print("  => 'max_x psi(Grotzsch) = 1/25' needs the UPPER bound, which is precisely Erdos 23")
    print("     for the Grotzsch blow-ups.  P4_gh_scope.py obtains it from a random/greedy search")
    print("     ('best psi found'), i.e. a lower bound only.  Equality is UNSUPPORTED.")
