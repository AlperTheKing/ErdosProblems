"""(g)/(h): what the Brandt-Thomasse reduction actually delivers, and what the chain silently
assumes.

Checked against the source (Brandt & Thomasse, "Dense triangle-free graphs are four-colorable",
perso.ens-lyon.fr/stephan.thomasse/liste/vega11.pdf):

  Thm 1  A weighted maximal triangle-free, twin-free graph with minimum degree delta > 1/3 is
         either isomorphic to a graph Gamma_i (vertex set {1..3i-1}, j ~ j+i,...,j+2i-1 mod 3i-1),
         hence 3-colourable, or contains the Grotzsch graph as an induced subgraph (chi >= 4).
  Cor 4.1 The twin-free, maximal triangle-free, weighted graphs with delta > 1/3 are the
         3-colourable graphs Gamma_i, i >= 1, and the 4-chromatic VEGA graphs.

so the reduction class is  {Andrasfai/circle graphs} U {Vega graphs},  and the hypothesis is on
the MINIMUM WEIGHTED DEGREE of the weighting one is actually using.

This script measures the two things the brief does not address:
  (1) the Vega branch is nonempty and TIGHT: the smallest Vega graph is the Grotzsch graph, whose
      max_x psi is exactly 1/25 (it has an induced C5), so it is not a case that can be waved away;
      it is not a circle graph (it is 4-chromatic), so items 3-7 say nothing about it.
  (2) psi-maximisers do NOT generally have min weighted degree > 1/3, so "WLOG delta > 1/3" is an
      extra hypothesis, not a normalisation.
"""
import random
from fractions import Fraction as F
from itertools import combinations
from P4_core import psi_graph, has_triangle, gamma_graph

random.seed(5)


def grotzsch():
    """Mycielskian of C5: 11 vertices 0..4 (C5), 5..9 (shadows), 10 (apex)"""
    n = 11
    adj = [[False] * n for _ in range(n)]

    def add(u, v):
        adj[u][v] = adj[v][u] = True
    for i in range(5):
        add(i, (i + 1) % 5)
    for i in range(5):
        add(5 + i, (i + 1) % 5)
        add(5 + i, (i - 1) % 5)
        add(5 + i, 10)
    return adj


def chrom(adj):
    n = len(adj)
    for k in (2, 3, 4, 5):
        col = [-1] * n

        def bt(i):
            if i == n:
                return True
            for c in range(k):
                if all(not adj[i][j] or col[j] != c for j in range(i)):
                    col[i] = c
                    if bt(i + 1):
                        return True
                    col[i] = -1
            return False
        if bt(0):
            return k
    return None


def diameter_le2(adj):
    n = len(adj)
    for u, v in combinations(range(n), 2):
        if not adj[u][v] and not any(adj[u][w] and adj[w][v] for w in range(n)):
            return False
    return True


def twin_free(adj):
    n = len(adj)
    for u, v in combinations(range(n), 2):
        if adj[u] == adj[v]:
            return False
    return True


def psi_float(adj, w, cuts):
    """min over precomputed cut masks of the monochromatic weight (floats, for the search only)"""
    q = float(sum(w))
    x = [t / q for t in w]
    n = len(w)
    E = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u][v]]
    best = None
    for side in cuts:
        c = sum(x[u] * x[v] for u, v in E if side[u] == side[v])
        if best is None or c < best:
            best = c
    return best


def induced_c5s(adj):
    n = len(adj)
    out = []
    for S in combinations(range(n), 5):
        sub = [[adj[u][v] for v in S] for u in S]
        deg = [sum(r) for r in sub]
        if deg != [2] * 5:
            continue
        # connected 2-regular on 5 vertices = C5
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in range(5):
                if sub[u][v] and v not in seen:
                    seen.add(v)
                    stack.append(v)
        if len(seen) == 5:
            out.append(S)
    return out


def max_psi(adj, q=40, tries=250):
    """hill climb over integer weights in float, exact Fraction check at the end.
    Seeded with every induced C5 (weight q/5 each), which is the known 1/25 configuration."""
    n = len(adj)
    cuts = []
    for msk in range(1 << (n - 1)):
        cuts.append([(msk >> i) & 1 for i in range(n - 1)] + [0])
    best = (F(0), None)
    starts = []
    for S in induced_c5s(adj)[:6]:
        w = [0] * n
        for i in S:
            w[i] = q // 5
        starts.append(w)
    for t in range(tries + len(starts)):
        if t < len(starts):
            w = list(starts[t])
        else:
            w = [0] * n
            for _ in range(q):
                w[random.randrange(n)] += 1
        cur = psi_float(adj, w, cuts)
        improved = True
        while improved:
            improved = False
            for i in range(n):
                for j in range(n):
                    if i == j or w[i] == 0:
                        continue
                    w[i] -= 1
                    w[j] += 1
                    v = psi_float(adj, w, cuts)
                    if v > cur + 1e-15:
                        cur, improved = v, True
                    else:
                        w[i] += 1
                        w[j] -= 1
        ex = psi_graph(adj, [F(t, q) for t in w])
        if ex > best[0]:
            best = (ex, list(w))
    return best


def max_min_degree(adj):
    """max over weightings x of min_v (weighted degree of v) - an LP.
    For a vertex-transitive graph this equals d/n by symmetrisation (min of linear functions is
    concave, so averaging over the automorphism group cannot decrease it)."""
    from scipy.optimize import linprog
    n = len(adj)
    # variables (x_1..x_n, t); maximise t s.t. sum_j adj_ij x_j - t >= 0, sum x = 1, x >= 0
    A_ub = []
    for i in range(n):
        A_ub.append([-1.0 if adj[i][j] else 0.0 for j in range(n)] + [1.0])
    res = linprog(c=[0.0] * n + [-1.0], A_ub=A_ub, b_ub=[0.0] * n,
                  A_eq=[[1.0] * n + [0.0]], b_eq=[1.0],
                  bounds=[(0, None)] * n + [(None, None)], method='highs')
    return res.x[-1] if res.success else float('nan')


def min_supp_degree(adj, w):
    q = sum(w)
    x = [F(t, q) for t in w]
    ds = [sum(x[j] for j in range(len(w)) if adj[i][j]) for i in range(len(w)) if w[i] > 0]
    return min(ds)


if __name__ == '__main__':
    print("=" * 92)
    print("(g) THE VEGA BRANCH - smallest member = Grotzsch graph")
    print("=" * 92)
    G = grotzsch()
    print(f"  11 vertices, triangle-free: {not has_triangle(G)}, chromatic number: {chrom(G)}, "
          f"twin-free: {twin_free(G)}, maximal triangle-free (diam<=2): {diameter_le2(G)}")
    v, w = max_psi(G, q=40, tries=25)
    print(f"  max_x psi(Grotzsch) found = {v} = {float(v):.8f}   (= 1/25 ? {v == F(1,25)})")
    print(f"  attained at integer weights {w} / 40, support size {sum(1 for t in w if t)}")
    print(f"  min weighted degree over the support at that maximiser = {min_supp_degree(G, w)} "
          f"= {float(min_supp_degree(G,w)):.4f}  (> 1/3 ? {min_supp_degree(G,w) > F(1,3)})")
    print("  the Grotzsch graph is 4-chromatic, hence NOT isomorphic to any circle graph Gamma_i,")
    print("  so items 3-7 (measures on the circle) do not touch this branch at all.")

    print("\n" + "=" * 92)
    print("(h) IS 'delta > 1/3' A NORMALISATION?  min support degree at psi-maximisers")
    print("=" * 92)
    tests = [("C7 = Gamma_7", gamma_graph(7)), ("Gamma_10", gamma_graph(10)),
             ("Gamma_13", gamma_graph(13)), ("C5 = Gamma_5", gamma_graph(5)),
             ("Wagner = Gamma_8", gamma_graph(8)), ("Gamma_11", gamma_graph(11)),
             ("Petersen", None), ("Grotzsch", G)]
    pet = [[False] * 10 for _ in range(10)]
    for i in range(5):
        pet[i][(i + 1) % 5] = pet[(i + 1) % 5][i] = True
        pet[i][i + 5] = pet[i + 5][i] = True
        pet[5 + i][5 + (i + 2) % 5] = pet[5 + (i + 2) % 5][5 + i] = True
    tests = [(nm, (pet if a is None else a)) for nm, a in tests]
    print(f"  {'graph':16s} {'best psi found':>14s} {'25*psi':>8s} {'supp':>5s} "
          f"{'min deg at that x':>18s} {'max_x min deg':>14s} {'ind C5?':>8s}")
    for nm, adj in tests:
        v, w = max_psi(adj, q=30, tries=20)
        d = min_supp_degree(adj, w)
        md = max_min_degree(adj)
        c5 = len(induced_c5s(adj)) > 0
        print(f"  {nm:16s} {str(v):>14s} {float(25*v):8.4f} {sum(1 for t in w if t):5d} "
              f"{float(d):18.4f} {md:14.4f} {str(c5):>8s}"
              f"   {'' if md > 1/3 else '<- no FULL-support weighting has delta>1/3'}")
    print("""
  Reading of the table.  psi only depends on the subgraph induced on the support, so the honest
  question is whether the SUPPORT-induced graph can be given delta > 1/3.  For every graph here
  that contains an induced C5, the value 1/25 is attained by the C5-supported weighting, whose
  support-induced graph is C5 with delta = 2/5 > 1/3 - so the reduction hypothesis IS available,
  but only through the conjecture's own extremal configuration (circular; see (h)).
  C7 is the clean negative case: it has NO induced C5, its maximum 4/225 is attained at min support
  degree 4/15 <= 1/3, its full-support max-min-degree is 2/7 < 1/3, and every proper induced
  subgraph of C7 is a forest (psi = 0).  So inside the delta > 1/3 class C7 contributes only psi = 0,
  while its true maximum is 4/225 > 0: the delta > N/3 theorem cannot see it at all.""")
