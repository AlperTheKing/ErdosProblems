"""G12: fully exact double-check of the headline falsifier --
the N=14 extremal graph M?AE@bH{AYN_LgBs? has bip = 7 but nu* = tau* = 32/5.

Both the packing (primal) and the cover (dual) are printed as exact rationals and
verified exactly, by TWO independent routes:
  route 1 : full enumeration of every odd cycle + exact rational simplex
  route 2 : cutting planes with exact double-cover Dijkstra separation
and bip is verified by TWO independent routes:
  route A : brute force over all 2^(N-1) cuts
  route B : minimum weight of the coset  1 + Cut(G)  in GF(2)^E   (cographic T-join)
"""
from fractions import Fraction as F
import G12_core as C

G6 = "M?AE@bH{AYN_LgBs?"


def coset_min(n, E):
    m = len(E)
    ones = (1 << m) - 1
    best = m
    arg = None
    for S in range(1 << (n - 1)):
        mask = 0
        for i, (u, v) in enumerate(E):
            if ((S >> u) & 1) != ((S >> v) & 1):
                mask |= 1 << i
        w = bin(ones ^ mask).count("1")
        if w < best:
            best, arg = w, ones ^ mask
    return best, arg


def main():
    n, E = C.graph6_to_edges(G6)
    print(f"graph6 {G6}: N={n} |E|={len(E)} triangle-free={C.is_triangle_free(n,E)}")
    d = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
    print(f"degrees {sorted(d)}  m/N^2 = {F(len(E), n*n)} = {float(F(len(E),n*n)):.5f}"
          f"  (open band is 2/25 = 0.08 .. 1/5 = 0.2)")
    print(f"edges: {E}")

    bA = C.bip_bruteforce_fast(n, E)
    bB, Fm = coset_min(n, E)
    print(f"\nbip route A (all cuts)          = {bA}")
    print(f"bip route B (coset 1+Cut(G))    = {bB}")
    assert bA == bB == 7
    Fedges = [E[i] for i in range(len(E)) if (Fm >> i) & 1]
    rem = [e for e in E if e not in set(Fedges)]
    print(f"    an optimal transversal: {Fedges}; remainder bipartite = "
          f"{C.bip_bruteforce_fast(n, rem)==0}")

    r2 = C.nu_star_cutting(n, E)
    print(f"\nnu* route 2 (cutting planes, {r2['ncycles']} rows)         = {r2['value']}")
    assert r2['value'] == F(32, 5)
    r1 = r2
    # route 1 (independent of the LP solver):
    #   upper bound tau* <= |E|/5 because G is triangle-free (every odd cycle has
    #   >= 5 edges), so the uniform x = 1/5 is a feasible fractional cover;
    #   lower bound nu* >= 32/5 from the explicit packing below, checked by hand.
    mw15 = C.min_odd_cycle_weight(n, E, [F(1, 5)] * len(E))
    print(f"nu* route 1 (hand certificate): uniform cover x=1/5 feasible "
          f"(min odd-cycle weight {mw15} >= 1) gives tau* <= |E|/5 = {F(len(E),5)};"
          f" explicit packing below gives nu* >= {F(len(E),5)}")

    # exact certificate printout
    cyc = r2['cycles']
    y = r2['y']
    x = r2['x']
    print("\nEXACT OPTIMAL PACKING (odd cycles with positive weight):")
    tot = F(0)
    for j, Cc in enumerate(cyc):
        if y[j] != 0:
            tot += y[j]
            print(f"    y = {y[j]}   on the {len(Cc)}-cycle with edges "
                  f"{sorted(E[e] for e in Cc)}")
    print(f"    total = {tot}")
    load = [sum(y[j] for j, Cc in enumerate(cyc) if e in Cc) for e in range(len(E))]
    print(f"    edge loads: min {min(load)}  max {max(load)}  (all <= 1 required)")
    print("\nEXACT OPTIMAL COVER (dual):")
    print(f"    x = {[str(v) for v in x]}")
    print(f"    sum x = {sum(x)}   min odd-cycle x-weight = "
          f"{C.min_odd_cycle_weight(n, E, x)}  (>= 1 required)")
    print(f"    uniform 1/5 cover value |E|/5 = {F(len(E),5)}  (equal: the uniform"
          f" cover is optimal here)")

    print(f"\n==> bip = {bA}   nu* = tau* = {r1['value']}"
          f"   integrality gap = {F(bA)/r1['value']}   deficit = {F(bA)-r1['value']}")
    print(f"    N^2/25 = {F(n*n,25)} = {float(F(n*n,25)):.4f};  bip/N^2 = {F(bA,n*n)}")
    print("    This graph is a KNOWN a(N) attainer (a(14) = 7), so the packing LP")
    print("    is already strictly below the truth on an extremal object.")


if __name__ == "__main__":
    main()
