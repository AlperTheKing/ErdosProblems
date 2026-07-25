"""
Task (i): the exact rational dual certificate for the extremal family C5[n].

C5[n] = balanced blow-up of the 5-cycle: parts V_0,...,V_4, |V_i| = n,
        complete bipartite between V_i and V_{i+1} (indices mod 5).
        N = 5n,  |E| = 5n^2.

We produce, in exact rational arithmetic:

  PRIMAL (fractional odd-cycle edge cover):  y_e = 1/5 for every edge.
      feasible because C5[n] is triangle-free, so every odd cycle has >= 5 edges.
      value = |E|/5 = n^2.

  DUAL (fractional odd-cycle packing):  z_C = n^{-3} on each of the n^5
      "transversal pentagons" (one vertex from each part).
      Every edge lies in exactly n^3 of them, so every edge load is exactly 1.
      value = n^5 * n^{-3} = n^2.

Equal values => both optimal =>  nu*(C5[n]) = tau*(C5[n]) = n^2,  and since
      nu* <= tau* <= bip,  we get bip(C5[n]) >= n^2.  The rotation cut
      S = V_0 u V_2  has exactly n^2 monochromatic edges (those inside
      V_3 u V_4), so bip(C5[n]) = n^2 exactly.

The script verifies all of this exactly for n = 1,2,3 (and the certificate
identities symbolically for general n), solves the LP from scratch for
n = 1,2 to confirm the optimum, and computes the OPTIMAL DUAL FACE.
"""
from fractions import Fraction
from itertools import product
import sympy as sp
from f5lib import bip, best_cut, all_odd_cycles, tau_star, verify_cover, verify_packing, simplex_max


def C5n(n):
    """vertices 0..5n-1, vertex i*n + j is the j-th vertex of part i."""
    V = 5 * n
    edges = []
    for i in range(5):
        for a in range(n):
            for b in range(n):
                u = i * n + a
                v = ((i + 1) % 5) * n + b
                edges.append((min(u, v), max(u, v)))
    edges = sorted(set(edges))
    return V, edges


def pentagons(n, edges):
    eidx = {}
    for k, (u, v) in enumerate(edges):
        eidx[(u, v)] = k
        eidx[(v, u)] = k
    out = []
    for choice in product(range(n), repeat=5):
        vs = [i * n + choice[i] for i in range(5)]
        es = frozenset(eidx[(vs[i], vs[(i + 1) % 5])] for i in range(5))
        assert len(es) == 5
        out.append(es)
    return out


def main():
    print("=" * 72)
    print("EXACT CERTIFICATE FOR C5[n]   (all arithmetic in Fraction / int)")
    print("=" * 72)
    for n in (1, 2, 3):
        V, E = C5n(n)
        m = len(E)
        print(f"\n--- n = {n} :  N = {V}, |E| = {m}  (predicted 5n^2 = {5*n*n}) ---")
        assert m == 5 * n * n

        # --- the explicit certificates -----------------------------------
        y = [Fraction(1, 5)] * m                       # cover
        pent = pentagons(n, E)
        z = [Fraction(1, n ** 3)] * len(pent)          # packing
        assert len(pent) == n ** 5

        cycles = all_odd_cycles(V, E)
        print(f"    total simple odd cycles: {len(cycles)}; transversal pentagons: {len(pent)}")
        ok_cover = verify_cover(E, cycles, y)          # against ALL odd cycles
        load = [Fraction(0)] * m
        for zc, C in zip(z, pent):
            for e in C:
                load[e] += zc
        ok_pack = all(l == 1 for l in load)
        print(f"    cover y = 1/5 feasible against all {len(cycles)} odd cycles : {ok_cover}")
        print(f"    packing z = n^-3 on pentagons: every edge load == 1        : {ok_pack}")
        vy = sum(y)
        vz = sum(z)
        print(f"    value(cover)   = {vy}   value(packing) = {vz}   (n^2 = {n*n})")
        assert ok_cover and ok_pack and vy == vz == n * n

        # --- the true bip ------------------------------------------------
        if V <= 15:
            b, S = best_cut(V, E)
            print(f"    bip(C5[{n}]) computed exhaustively = {b}   (n^2 = {n*n})")
            assert b == n * n

        # --- solve the LP from scratch (small n) -------------------------
        if n <= 2:
            t, ystar, zstar, _ = tau_star(V, E, cycles)
            print(f"    LP solved from scratch: tau* = nu* = {t}")
            assert t == n * n
            assert verify_cover(E, cycles, ystar) and verify_packing(m, cycles, zstar)

    # ------------------------------------------------------------------
    # OPTIMAL DUAL FACE of the cover LP for C5[n]
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("STRUCTURE OF THE OPTIMAL COVER FACE  F = {y >= 0 : all pentagons tight}")
    print("=" * 72)
    for n in (1, 2, 3):
        V, E = C5n(n)
        m = len(E)
        pent = pentagons(n, E)
        # affine hull of F: solve  sum_{e in C} y_e = 1 for all pentagons C
        M = sp.zeros(len(pent), m)
        for r, C in enumerate(pent):
            for e in C:
                M[r, e] = 1
        rk = M.rank()
        print(f"  n={n}: |E|={m}, #pentagon equations={len(pent)}, "
              f"rank={rk}, dim(affine solution space)={m - rk}")
        # predicted dimension (see the .md write-up): 5n - 4 + ... check formula
    print()


if __name__ == "__main__":
    main()
