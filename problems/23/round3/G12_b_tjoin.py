"""G12 task (b): the T-join / double-cover formulation of bip, made precise and
verified exactly on small cases.

STATEMENT 1 (coset / cographic T-join form).
  Let Cut(G) <= GF(2)^E be the cut (cocycle) space and 1 the all-ones vector.
  Then   bip(G) = min { |F| : F in 1 + Cut(G) }.
  Equivalently F is admissible iff |F cap Z| = |Z| (mod 2) for every element Z of
  the cycle space; i.e. F meets every ODD cycle an odd number of times and every
  EVEN cycle an even number of times.  This is exactly the T-join problem for the
  COGRAPHIC matroid M*(G) (for planar G, = a T-join in the dual with T = odd faces,
  which is Hadlock's theorem).

STATEMENT 2 (double cover form).
  Let Gt = G x K2 with V = {(v,0),(v,1)} and edges (u,0)(v,1), (u,1)(v,0) for uv in E;
  for F <= E let Ft be the set of BOTH lifts of every edge of F.  Then
      G - F is bipartite  <=>  in Gt - Ft, (v,0) and (v,1) lie in different components for every v.
  Hence bip(G) = minimum "paired multicut" in the bipartite double cover separating
  the N antipodal pairs.

Both are verified here by brute force.
"""
from fractions import Fraction as F
import itertools
import networkx as nx
import G12_core as C


def cut_space_vectors(n, E):
    """All 2^(n-1) cuts as edge-bitmasks."""
    out = []
    for S in range(1 << (n - 1)):
        mask = 0
        for i, (u, v) in enumerate(E):
            if ((S >> u) & 1) != ((S >> v) & 1):
                mask |= 1 << i
        out.append(mask)
    return out


def statement1(n, E):
    m = len(E)
    ones = (1 << m) - 1
    coset = {ones ^ c for c in cut_space_vectors(n, E)}
    best = min(bin(x).count("1") for x in coset)
    # parity characterisation check on the minimiser
    Fbest = next(x for x in coset if bin(x).count("1") == best)
    cyc = C.all_cycles(n, E)
    ok = True
    for path, es in cyc:
        inter = sum(1 for e in es if (Fbest >> e) & 1)
        if inter % 2 != len(es) % 2:
            ok = False
            break
    return best, ok, Fbest


def statement2(n, E, F_mask):
    """Check: G - F bipartite <=> in the double cover minus both lifts of F,
    (v,0) and (v,1) are separated for all v."""
    rem = [E[i] for i in range(len(E)) if not ((F_mask >> i) & 1)]
    bip_ok = (C.bip_bruteforce_fast(n, rem) == 0)
    D = nx.Graph()
    for v in range(n):
        D.add_node((v, 0))
        D.add_node((v, 1))
    for (u, v) in rem:
        D.add_edge((u, 0), (v, 1))
        D.add_edge((u, 1), (v, 0))
    sep = all(not nx.has_path(D, (v, 0), (v, 1)) for v in range(n))
    return bip_ok, sep


def random_subset_check(n, E, trials=200):
    """Verify statement 2 as an equivalence on random F, not only on the optimum."""
    import random
    m = len(E)
    bad = 0
    for _ in range(trials):
        mask = random.getrandbits(m)
        a, b = statement2(n, E, mask)
        if a != b:
            bad += 1
    return bad


def main():
    tests = []
    tests.append(("C5", ) + C.C5())
    N, E = C.blowup(5, C.C5()[1], [2] * 5)
    tests.append(("C5[2]", N, E))
    P = nx.petersen_graph()
    vs = sorted(P.nodes())
    idx = {v: i for i, v in enumerate(vs)}
    tests.append(("Petersen", 10, sorted(tuple(sorted((idx[u], idx[v]))) for u, v in P.edges())))
    n, E = C.graph6_to_edges("K?ABBBwerwBw")
    tests.append(("extremal N=12", n, E))
    # OK5 = 13-vertex integrality-gap witness
    e5 = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    idx = {ed: i for i, ed in enumerate(e5)}
    sub = {idx[(0, 1)], idx[(2, 3)], idx[(2, 4)], idx[(3, 4)]}
    EE = []
    nxt = 5
    for i, (u, v) in enumerate(e5):
        if i in sub:
            EE += [(u, nxt), (nxt, nxt + 1), (nxt + 1, v)]
            nxt += 2
        else:
            EE.append((u, v))
    tests.append(("OK5 (gap witness)", nxt, EE))

    print("=" * 78)
    print("(b) coset / cographic-T-join form and double-cover form: exact verification")
    print("=" * 78)
    for name, n, E in tests:
        if len(E) > 26:
            print(f"{name}: |E|={len(E)} too large for the 2^|E| coset check, skipped")
            continue
        best, parity_ok, Fm = statement1(n, E)
        bip = C.bip_bruteforce_fast(n, E)
        a, b = statement2(n, E, Fm)
        bad = random_subset_check(n, E, 200)
        Fedges = [E[i] for i in range(len(E)) if (Fm >> i) & 1]
        print(f"{name}: N={n} |E|={len(E)}")
        print(f"    STATEMENT 1: min weight of the coset 1 + Cut(G) = {best};  bip = {bip};  equal = {best==bip}")
        print(f"        parity characterisation holds on the minimiser (|F cap Z| = |Z| mod 2 for every cycle Z): {parity_ok}")
        print(f"        minimiser F = {Fedges}")
        print(f"    STATEMENT 2: G-F bipartite = {a}, double cover separates all antipodal pairs = {b}")
        print(f"        equivalence failures on 200 random F: {bad}")

    print()
    print("=" * 78)
    print("Consequence of the min-max question")
    print("=" * 78)
    print("  The T-join min-max analogue is: min odd-cycle edge cover = LP value tau*.")
    print("  Guenin (JCTB 83 (2001) 112-168): a signed graph is weakly bipartite (its")
    print("  odd-cycle covering polyhedron {x>=0 : x(C)>=1} is integral) IFF it has no")
    print("  odd-K5 minor.  For the all-negative signing of a graph this is exactly the")
    print("  condition under which bip = tau* = nu*.")
    print("  OK5 above is a triangle-free odd-K5 SUBDIVISION, hence has an odd-K5 minor,")
    print("  and indeed bip = 4 > 10/3 = nu*.  So NO min-max certificate exists in general.")


if __name__ == "__main__":
    main()
