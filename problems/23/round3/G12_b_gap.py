"""G12: integrality gap of the odd-cycle edge cover/packing LP on TRIANGLE-FREE graphs.

Constructs and certifies exactly the witness  OK5  =  the odd-K5 subdivision
obtained from K5 by subdividing a maximum non-triangle-free edge set into paths
of length 3:  N = 13, |E| = 18, girth 5, triangle-free,
      bip(OK5) = 4,   nu*(OK5) = tau*(OK5) = 10/3,   gap = 6/5 > 1.
Also does the 3-subdivision S3(K5) (N = 25) for comparison.
"""
from fractions import Fraction as F
import G12_core as C


def subdivide(n, edges, subdiv):
    """Replace each edge in `subdiv` (given as a set of indices) by a path of
    length 3 (2 new vertices).  Returns (N, E)."""
    E = []
    nxt = n
    for i, (u, v) in enumerate(edges):
        if i in subdiv:
            a, b = nxt, nxt + 1
            nxt += 2
            E += [(u, a), (a, b), (b, v)]
        else:
            E.append((u, v))
    return nxt, E


def K5():
    e = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    return 5, e


def report(name, n, E, bip=None):
    tf = C.is_triangle_free(n, E)
    if bip is None:
        bip = C.bip_bruteforce_fast(n, E)
    r1 = C.nu_star_enumerate(n, E)
    r2 = C.nu_star_cutting(n, E)
    assert r1['value'] == r2['value'], (r1['value'], r2['value'])
    nu = r1['value']
    print(f"{name}: N={n} |E|={len(E)} triangle-free={tf}")
    print(f"    bip = {bip}   nu* = tau* = {nu}   gap = {F(bip)/nu}   bip-nu* = {F(bip)-nu}")
    print(f"    odd cycles enumerated = {r1['ncycles']}, cutting-plane rows = {r2['ncycles']}")
    print(f"    exact certificate: primal feasible={r1['primal_ok']}, dual feasible={r1['dual_ok']}")
    return bip, nu


def main():
    print("=" * 78)
    print("K5 itself (NOT triangle-free) -- the source of the gap")
    print("=" * 78)
    n, e = K5()
    report("K5", n, e)

    print()
    print("=" * 78)
    print("OK5 = K5 with the 4 edges {01,23,24,34} subdivided into paths of length 3")
    print("      (the 6 remaining edges form K_{2,3}: {0,1} x {2,3,4})")
    print("=" * 78)
    n, e = K5()
    idx = {ed: i for i, ed in enumerate(e)}
    sub = {idx[(0, 1)], idx[(2, 3)], idx[(2, 4)], idx[(3, 4)]}
    N, E = subdivide(n, e, sub)
    print("    vertex map: 0..4 = branch vertices of K5, 5..12 = subdivision vertices")
    print("    edges:", E)
    bip, nu = report("OK5", N, E)
    # explicit transversal of size 4 exhibited independently
    # optimal cut of K5: S={0,1}; monochromatic K5-edges = 01,23,24,34 -> all subdivided
    print("    explicit size-4 transversal: one edge from each subdivided path,")
    print("      i.e. the middle edges of the paths replacing 01,23,24,34")
    mids = [E[i] for i in range(len(E)) if E[i][0] >= 5 and E[i][1] >= 5]
    print("      =", mids)
    rem = [ed for ed in E if ed not in mids]
    print("      remaining graph bipartite:", C.bip_bruteforce_fast(N, rem) == 0)
    assert len(mids) == 4 and C.bip_bruteforce_fast(N, rem) == 0
    assert bip == 4 and nu == F(10, 3)
    print(f"    ==> CERTIFIED gap = {F(4)/F(10,3)} on a triangle-free graph, N=13")
    print(f"    bip/N^2 = {F(4, 169)} = {float(F(4,169)):.6f} vs 1/25 = 0.04  (no threat to the conjecture)")

    print()
    print("=" * 78)
    print("S3(K5) = every edge of K5 subdivided into a path of length 3 (N=25)")
    print("=" * 78)
    n, e = K5()
    N, E = subdivide(n, e, set(range(10)))
    # bip by the reduction, certified: nu* <= bip <= explicit transversal
    r1 = C.nu_star_enumerate(N, E)
    nu = r1['value']
    mids = [ed for ed in E if ed[0] >= 5 and ed[1] >= 5]
    # take the 4 middle edges of the paths for K5-edges 01,23,24,34
    idx = {ed: i for i, ed in enumerate(e)}
    order = list(range(10))
    want = {idx[(0, 1)], idx[(2, 3)], idx[(2, 4)], idx[(3, 4)]}
    # in subdivide, K5-edge i (all subdivided) occupies E[3i:3i+3], middle = E[3i+1]
    Fset = [E[3 * i + 1] for i in sorted(want)]
    rem = [ed for ed in E if ed not in Fset]
    ok = C.bip_bruteforce_fast(N, rem) == 0
    print(f"    N={N} |E|={len(E)} triangle-free={C.is_triangle_free(N,E)} girth 9")
    print(f"    nu* = {nu}  (so bip >= ceil({nu}) = {-(-nu.numerator // nu.denominator)})")
    print(f"    explicit transversal of size {len(Fset)} = {Fset}; remainder bipartite = {ok}")
    assert ok and nu == F(10, 3)
    print(f"    ==> bip = 4 exactly, gap = {F(4)/nu} = 6/5")


if __name__ == "__main__":
    main()
