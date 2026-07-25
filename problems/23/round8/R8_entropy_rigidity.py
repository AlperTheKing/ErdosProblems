"""Support rigidity for cut certificates, and its exact combinatorial test.

THEOREM R8-2 (aggregator rigidity).  Let H be triangle-free, let nu be a
probability distribution on the cuts of H and let Phi be ANY aggregator with

    (i)  min_j t_j  <=  Phi(t)          for all t >= 0,
    (ii) Phi(c,c,...,c) = c,
    (iii) Phi is strictly increasing in every coordinate.

If the certificate  Phi( (m_S(x))_{S in supp nu} ) <= 1/25 holds at a weighting
x with psi(H,x) = 1/25, then m_S(x) = 1/25 for EVERY S in supp(nu).

Proof.  psi(H,x) = 1/25 means m_S(x) >= 1/25 for every cut S, with equality for
at least one.  If some S_0 in supp(nu) had m_{S_0}(x) > 1/25 then by (iii) and
(ii), Phi((m_S(x))) > Phi(1/25,...,1/25) = 1/25, contradiction.  []

The arithmetic mean, every weighted geometric mean, every power mean, and the
Gibbs / free-energy aggregator  Phi_beta(t) = -(1/beta) log E_nu[exp(-beta t)]
(beta > 0) all satisfy (i)-(iii); Phi_beta -> arithmetic mean as beta -> 0 and
-> min as beta -> infinity.  So the whole exponential-moment family, which is
the sharpest form the entropy method takes, is subject to the same rigidity as
the plain first moment.

COROLLARY (rainbow test).  Let K be an induced C5 of H and x_K the uniform
weighting on V(K).  Then psi(H,x_K) = 1/25 and m_S(x_K) = |mono(S) cap E(K)|/25.
So every cut in the support of a working fixed certificate must have EXACTLY ONE
monochromatic edge inside EVERY induced C5 of H.  Call such a cut *rainbow-1*.
If H has no rainbow-1 cut, no fixed distribution over cuts -- under any
aggregator whatsoever -- can certify max_x psi(H,x) <= 1/25.

This file computes the rainbow-1 cuts exactly.
"""

from itertools import combinations
from R8_entropy_core import (cycle, blowup, petersen, grotzsch, wagner,
                             andrasfai, complete_bipartite, bip_weighted,
                             is_triangle_free, kneser_clebsch)


def adjacency(g):
    n, edges = g
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    return adj


def induced_c5s(g):
    """All vertex sets of size 5 inducing exactly a 5-cycle."""
    n, edges = g
    adj = adjacency(g)
    out = []
    for S in combinations(range(n), 5):
        deg = {v: sum(1 for u in S if adj[v][u]) for v in S}
        if all(d == 2 for d in deg.values()):
            # 2-regular on 5 vertices and connected  => C5
            start = S[0]
            seen, stack = {start}, [start]
            while stack:
                v = stack.pop()
                for u in S:
                    if adj[v][u] and u not in seen:
                        seen.add(u)
                        stack.append(u)
            if len(seen) == 5:
                out.append(S)
    return out


def c5_edges(g, S):
    n, edges = g
    adj = adjacency(g)
    return [(u, v) for (u, v) in edges if u in S and v in S and adj[u][v]]


def rainbow1_cuts(g, verbose=False):
    """Cuts whose monochromatic edge set meets every induced C5 exactly once."""
    n, edges = g
    pents = induced_c5s(g)
    pedges = [set(c5_edges(g, S)) for S in pents]
    hits = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        mono = set((u, v) for (u, v) in edges if side[u] == side[v])
        if all(len(mono & pe) == 1 for pe in pedges):
            hits.append((mask, frozenset(mono)))
    return pents, hits


if __name__ == "__main__":
    C5 = cycle(5)
    tests = [
        ("C5", C5),
        ("C7", cycle(7)),
        ("K33", complete_bipartite(3, 3)),
        ("C5[2]", blowup(C5, [2] * 5)),
        ("C5[3,1,2,2,1]", blowup(C5, [3, 1, 2, 2, 1])),
        ("Wagner=And(3)", wagner()),
        ("Petersen", petersen()),
        ("Grotzsch", grotzsch()),
        ("And(4)", andrasfai(4)),
    ]
    print(f"{'graph':16s} {'n':>3s} {'|E|':>4s} {'bip':>4s} {'#indC5':>7s} "
          f"{'#rainbow-1 cuts':>16s}   status")
    for name, g in tests:
        n, edges = g
        assert is_triangle_free(g)
        b = bip_weighted(g, [1] * n)[0]
        pents, hits = rainbow1_cuts(g)
        sizes = sorted(set(len(m) for _, m in hits))
        status = "fixed certificate possible" if hits else \
                 "NO fixed certificate (any aggregator)"
        if not pents:
            status = "no induced C5 -- rigidity test empty"
        print(f"{name:16s} {n:3d} {len(edges):4d} {b:4d} {len(pents):7d} "
              f"{len(hits):16d}   {status}  mono-sizes={sizes}")
        if hits and len(hits) <= 12:
            for mask, mono in hits[:12]:
                print(f"      mono set: {sorted(mono)}")
