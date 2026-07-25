"""R8: the UNWEIGHTED (edit-distance) form of stability, tested at N = 14.

A removal/stability lemma of the shape "bip(G) close to N^2/25  =>  G close in edit distance
to a C5 blow-up" needs, at the very least, the MAXIMISERS of bip to be blow-ups.  They are not.
Here we re-derive, independently and exactly, the N = 14 witness recorded in the project's
approach registry, and measure its edit distance to the blow-up family.
"""
import sys, os, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import Graph, from_g6, blowup_C5

G6 = "M?AE@bH{AYN_LgBs?"


def bip(g):
    """|E| - maxcut, by exhaustive enumeration of the 2^(n-1) bipartitions."""
    n, E = g.n, g.edges
    best = len(E) + 1
    for S in range(1 << (n - 1)):
        Sm = (S << 1) | 1
        c = 0
        for (u, v) in E:
            if ((Sm >> u) & 1) == ((Sm >> v) & 1):
                c += 1
                if c >= best:
                    break
        if c < best:
            best = c
    return best


def edit_distance_to_blowups(g6):
    """Exact min over all C5-blow-up structures of |E(G) triangle E(blowup)|.
    Delegated to R8_stability_editdist.exe (branch-and-bound over the 5^(n-1) class maps)."""
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    exe = os.path.join(here, "R8_stability_editdist.exe")
    return subprocess.run([exe, g6], capture_output=True, text=True).stdout


if __name__ == "__main__":
    g = from_g6(G6)
    print(f"graph6 {G6}:  n = {g.n},  |E| = {len(g.edges)},  triangle-free = {g.is_triangle_free()}")
    b = bip(g)
    print(f"  bip(G) = {b}   (25*bip = {25*b}  vs  N^2 = {g.n**2})   -> conjecture holds: {25*b <= g.n**2}")
    print(f"  N^2/25 = {F(g.n**2,25)} = {float(F(g.n**2,25)):.4f},  floor = {g.n**2//25}")
    print(f"  induced C5 count = {len(g.induced_C5s())}")
    print("  --- every C5 blow-up on 14 vertices ---")
    bestb, arg = 0, None
    for c in itertools.combinations_with_replacement(range(15), 5):
        for p in set(itertools.permutations(c)):
            if sum(p) != 14:
                continue
            val = min(p[i] * p[(i + 1) % 5] for i in range(5))
            if val > bestb:
                bestb, arg = val, p
    print(f"  max over C5 blow-ups on 14 vertices: bip = min_i n_i n_(i+1) = {bestb} at {arg}")
    print(f"  => the maximiser of bip at N = 14 BEATS every blow-up: {b} > {bestb}")
    print("  " + edit_distance_to_blowups(G6).replace("\n", "\n  "))
    # sanity: an actual blow-up
    h = blowup_C5([3, 3, 3, 3, 2])
    print(f"  sanity: bip(C5[3,3,3,3,2]) = {bip(h)} (formula min_i n_i n_(i+1) = "
          f"{min([3,3,3,3,2][i]*[3,3,3,3,2][(i+1)%5] for i in range(5))})")
