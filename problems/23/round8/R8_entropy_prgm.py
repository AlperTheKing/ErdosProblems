"""Exhaustive exact evaluation of the PRGM certificate (numpy, int64).

PRGM(H,a) = min over phi: V(H) -> Z5 of  prod_{r in Z5} m_r(phi,a),
with m_r the monochromatic weight of the r-th rotation cut of phi
(see R8_entropy_core.py for the derivation of m_r).

The certificate claim under test is

        25^5 * PRGM(H,a)  <=  (sum a)^10          (*)

which is equivalent to  (prod_r m_r)^{1/5} <= (sum a)^2 / 25, and implies
bip(H[a]) <= (sum a)^2 / 25 because min_r m_r <= geometric mean.

All arithmetic is int64; the driver asserts no overflow.
"""

import numpy as np
from R8_entropy_core import rotation_values, rotation_cut_check


def prgm_numpy(g, a, chunk=1 << 20, return_arg=True):
    """Exact min over all 5^(n-1) maps phi with phi[0]=0 of prod_r m_r."""
    n, edges = g
    a = np.asarray(a, dtype=np.int64)
    total = 5 ** (n - 1)
    pw = np.array([5 ** j for j in range(n)], dtype=np.int64)
    best = None
    bestidx = -1
    W = int(sum(int(a[u]) * int(a[v]) for u, v in edges))
    assert W ** 5 < 2 ** 62, "int64 overflow risk: reduce weights"
    for lo in range(0, total, chunk):
        hi = min(lo + chunk, total)
        idx = np.arange(lo, hi, dtype=np.int64)
        phi = np.empty((hi - lo, n), dtype=np.int64)
        phi[:, 0] = 0
        for j in range(1, n):
            phi[:, j] = (idx // pw[j - 1]) % 5
        E1 = np.zeros((hi - lo, 5), dtype=np.int64)
        E2 = np.zeros((hi - lo, 5), dtype=np.int64)
        Z = np.zeros(hi - lo, dtype=np.int64)
        for (u, v) in edges:
            w = int(a[u]) * int(a[v])
            if w == 0:
                continue
            d = (phi[:, u] - phi[:, v]) % 5
            Z += w * (d == 0)
            for p in range(5):
                E1[:, p] += w * (((d == 1) & (phi[:, v] == p)) |
                                 ((d == 4) & (phi[:, u] == p)))
                E2[:, p] += w * (((d == 2) & (phi[:, v] == p)) |
                                 ((d == 3) & (phi[:, u] == p)))
        prod = np.ones(hi - lo, dtype=np.int64)
        for r in range(5):
            m = (E1[:, (r - 1) % 5] + Z + E2[:, r % 5]
                 + E2[:, (r + 1) % 5] + E2[:, (r + 2) % 5])
            prod *= m
        j = int(np.argmin(prod))
        if best is None or int(prod[j]) < best:
            best = int(prod[j])
            bestidx = lo + j
    if not return_arg:
        return best
    phi = [0] * n
    t = bestidx
    for j in range(1, n):
        phi[j] = (t // 5 ** (j - 1)) % 5
    return best, tuple(phi)


def verify_phi(g, a, phi):
    """Re-derive the five m_r two independent ways; return them."""
    m1 = rotation_values(g, a, phi)
    m2 = [rotation_cut_check(g, a, phi, r) for r in range(5)]
    assert m1 == m2, (m1, m2)
    return m1


if __name__ == "__main__":
    import sys
    from itertools import product as iproduct
    from R8_entropy_core import (cycle, blowup, petersen, grotzsch, wagner,
                                 andrasfai, complete_bipartite, bip,
                                 bip_weighted, is_triangle_free,
                                 prgm_bruteforce)

    C5 = cycle(5)
    tests = [
        ("C5", C5, [1] * 5),
        ("C7", cycle(7), [1] * 7),
        ("K33", complete_bipartite(3, 3), [1] * 6),
        ("Wagner=And(3)", wagner(), [1] * 8),
        ("C5[2]", blowup(C5, [2] * 5), [1] * 10),
        ("C5[3,1,2,2,1]", blowup(C5, [3, 1, 2, 2, 1]), [1] * 9),
        ("C5[3,1,2,2,0]", blowup(C5, [3, 1, 2, 2, 0]), [1] * 8),
        ("Petersen", petersen(), [1] * 10),
        ("Grotzsch", grotzsch(), [1] * 11),
        ("And(4)", andrasfai(4), [1] * 11),
    ]
    print(f"{'graph':16s} {'n':>3s} {'|E|':>4s} {'tf':>3s} {'bip':>4s} "
          f"{'PRGM':>12s} {'target n^10/5^10':>18s} {'25*GM/n^2':>10s}  verdict")
    for name, g, a in tests:
        n, edges = g
        q = sum(a)
        val, phi = prgm_numpy(g, a)
        m = verify_phi(g, a, phi)
        assert np.prod(np.array(m, dtype=object)) == val
        b = bip_weighted(g, a)[0]
        tgt = q ** 10 / 5 ** 10
        gm = val ** 0.2
        ok = 5 ** 10 * val <= q ** 10
        print(f"{name:16s} {n:3d} {len(edges):4d} {str(is_triangle_free(g)):>3s} "
              f"{b:4d} {val:12d} {tgt:18.4f} {25 * gm / q ** 2:10.6f}  "
              f"{'OK' if ok else 'FAILS'}   m={m}")
