"""Final exact gates for R8.

GATE 1  Grotzsch witness, recomputed in the independent representation of
        R8_transport_verify (adjacency sets, DFS 5-cycles, tuple cuts):
        every C5-perfect cut S of the Grotzsch graph satisfies nu_S(x) = 1/20
        at  x = 1/2 on the Mycielski apex, 1/10 on each of the five shadows.

GATE 2  double subdivision identity  maxcut(G'') = maxcut(G) + 2|E(G)|
        (G'' = every edge subdivided twice), which raises the girth by a factor 3
        and hence carries NP-hardness of MaxCut into the triangle-free class.

GATE 3  Conjecture T (the Motzkin-Straus support transport LP) refuted exactly.
"""
import sys
from fractions import Fraction as F
from itertools import product

sys.path.insert(0, ".")
from R8_transport_lib import *              # noqa
import R8_transport_verify as IV            # independent implementation


# ---------------------------------------------------------------- GATE 1
def gate1():
    n = 11
    pairs = [(i, (i + 1) % 5) for i in range(5)]                 # C5 0..4
    for u, v in [(i, (i + 1) % 5) for i in range(5)]:            # Mycielski
        pairs += [(u, 5 + v), (v, 5 + u)]
    pairs += [(5 + i, 10) for i in range(5)]
    G = IV.mk(n, pairs)
    nn, A = G
    assert IV.is_triangle_free(nn, A)
    cyc = IV.five_cycles_induced(nn, A)
    perfect = [c for c in IV.all_cuts(nn) if all(IV.k_of(c, es) == 1 for vs, es in cyc)]
    x = [F(0)] * 5 + [F(1, 10)] * 5 + [F(1, 2)]
    print("GATE1 Grotzsch: n=%d |indC5|=%d  #C5-perfect cuts=%d" % (nn, len(cyc), len(perfect)))
    vals = []
    for c in perfect:
        nu = sum(x[u] * x[v] for u in range(nn) for v in A[u] if u < v and c[u] == c[v])
        vals.append(nu)
    print("      nu at x=(0^5,(1/10)^5,1/2) over the C5-perfect cuts:", [str(v) for v in vals])
    print("      min = %s ;  1/25 = %s ;  min > 1/25 ? %s"
          % (min(vals), F(1, 25), min(vals) > F(1, 25)))
    # true psi at the same x, by brute force over all cuts
    best = None
    for c in IV.all_cuts(nn):
        s = sum(x[u] * x[v] for u in range(nn) for v in A[u] if u < v and c[u] == c[v])
        best = s if best is None else min(best, s)
    print("      true psi(Grotzsch,x) = %s" % best)


# ---------------------------------------------------------------- GATE 2
def gate2():
    def subdivide2(G):
        idx = G.n
        edges = []
        for u, v in G.edges:
            a, b = idx, idx + 1
            idx += 2
            edges += [(u, a), (a, b), (b, v)]
        return Graph(idx, edges, G.name + "''")

    for G in [Graph(3, [(0, 1), (1, 2), (0, 2)], "K3"),
              Graph(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], "K4"),
              cycle(5), petersen()]:
        if G.n > 5:
            continue
        H = subdivide2(G)
        mcG = G.m - G.bip()
        mcH = H.m - H.bip()
        print("GATE2 %-4s maxcut=%2d |E|=%2d  ->  G'' n=%2d maxcut=%2d   maxcut(G)+2|E| = %2d  %s"
              % (G.name, mcG, G.m, H.n, mcH, mcG + 2 * G.m,
                 "OK" if mcH == mcG + 2 * G.m else "MISMATCH"))


# ---------------------------------------------------------------- GATE 3
def gate3():
    print("GATE3  Conjecture T:  max_x min_S X(U_S) <= 2/5 ?   (x = uniform used as witness)")
    for G in testbed() + [andrasfai(4)]:
        best = None
        for S in G.all_cuts():
            U = 0
            for u, v in G.mono_edges(S):
                U |= (1 << u) | (1 << v)
            k = popcount(U)
            best = k if best is None else min(best, k)
        lhs = F(best, G.n)
        print("   %-16s min_S X(U_S) at uniform = %s = %.4f   vs 2/5   -> %s"
              % (G.name, lhs, float(lhs), "REFUTES T" if lhs > F(2, 5) else "consistent"))


if __name__ == "__main__":
    gate1()
    print()
    gate2()
    print()
    gate3()
