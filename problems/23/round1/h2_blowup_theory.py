"""H2 core identity + exact check.

CLAIM (exact).  Let H be triangle-free on h vertices, n = (n_1..n_h) nonneg integers,
G = H[n] the blow-up (parts independent, base edges -> complete bipartite).  Then

    maxcut(G) = max_{S subset V(H)} sum_{ij in E(H), |{i,j} cap S| = 1} n_i n_j
    bip(G)    = min_{S subset V(H)} sum_{ij in E(H), i,j both in S or both outside} n_i n_j

Reason: writing x_i = #(part i on side A), the cut value
  sum_{ij in E(H)} [ x_i (n_j - x_j) + (n_i - x_i) x_j ]
is affine in each x_i separately, so its max over the box prod [0, n_i] is attained at a
vertex x_i in {0, n_i}, i.e. at a partition constant on parts.

This script verifies the identity by brute force on random small blow-ups.
"""
import random, itertools
from h2_lib import *


def bip_blowup(bn, bedges, parts):
    """Exact bip of the blow-up, via the identity (only 2^(bn-1) cuts)."""
    best = None
    for half in range(1 << (bn - 1)):       # vertex 0 fixed outside S
        S = half << 1
        tot = 0
        for (u, v) in bedges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += parts[u] * parts[v]
        if best is None or tot < best:
            best = tot
    return best


def bip_blowup_full(bn, bedges, parts):
    """Same but over all 2^bn cuts (identical by symmetry; sanity)."""
    best = None
    for S in range(1 << bn):
        tot = 0
        for (u, v) in bedges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += parts[u] * parts[v]
        if best is None or tot < best:
            best = tot
    return best


if __name__ == "__main__":
    random.seed(12345)
    bases = [
        ("C5", 5, C5_EDGES),
        ("C7", 7, C7_EDGES),
        ("Petersen", 10, PETERSEN_EDGES),
        ("K33", 6, [(i, 3 + j) for i in range(3) for j in range(3)]),
        ("C5+chordless path", 6, C5_EDGES + [(0, 5), (2, 5)]),
    ]
    ok = True
    for name, bn, be in bases:
        for trial in range(40):
            parts = [random.randint(1, 3) for _ in range(bn)]
            N = sum(parts)
            if N > 20:
                continue
            Nn, adj, offs = blowup(bn, be, parts)
            assert is_triangle_free(Nn, adj), name
            b1 = bip_exhaustive(Nn, adj)
            b2 = bip_blowup(bn, be, parts)
            b3 = bip_blowup_full(bn, be, parts)
            if not (b1 == b2 == b3):
                print("MISMATCH", name, parts, b1, b2, b3)
                ok = False
    print("identity verified on random blow-ups:", ok)
