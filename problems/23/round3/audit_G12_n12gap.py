"""AUDIT G12 / step 2: the N=12 integrality-gap witnesses that the report left
unresolved ("the N=12 sweep ... is the only unresolved arithmetic in this report"),
plus the exact M1 ceiling.

Everything exact.  A witness is certified two independent ways:
  (i)  cheap exact certificate: G triangle-free => every odd cycle has >= 5 edges
       => x == 1/5 is a feasible fractional cover => nu* = tau* <= |E|/5.
       So 5*bip > |E| already proves bip > nu*.
  (ii) full LP over ALL odd cycles with an exactly verified primal/dual pair.
"""
from fractions import Fraction as Fr
import audit_G12_core as A

WIT = ["K??E@_qi?]Ia", "K??EDbGIaYAe", "K?AAD?WNBHCs"]
M1MAX12 = "K??FEb_F?wD_"
M2MAX12 = "K?`FE`wl?{Dg"


def main():
    print("=" * 76)
    print("A. N=12 exact integrality-gap witnesses  (report claimed min witness in {12,13,14})")
    print("=" * 76)
    for s in WIT:
        n, E = A.g6(s)
        m = len(E)
        tf = A.triangle_free(n, E)
        b = A.bip(n, E)
        odd = [es for _, es in A.simple_cycles(n, E, only_odd=True)]
        unif_ok = A.check_cover(n, E, [Fr(1, 5)] * m, odd)
        r = A.nu_star_certified(n, E)
        d = sorted(A.degrees(n, E))
        print(f"{s}: N={n} |E|={m} tri-free={tf} girth={A.girth(n,E)} degs={d}")
        print(f"   bip = {b} (exhaustive cuts)   |E|/5 = {Fr(m,5)}   5*bip = {5*b} > |E| = {m}: "
              f"{5*b > m}")
        print(f"   uniform 1/5 cover feasible on all {len(odd)} odd cycles: {unif_ok}"
              f"  => nu* <= {Fr(m,5)}")
        print(f"   exact LP over all odd cycles: nu* = tau* = {r['value']}"
              f"   bip - nu* = {Fr(b) - r['value']}   gap = {Fr(b)/r['value']}")
        print(f"   bip/N^2 = {Fr(b, n*n)} vs 1/25 (no threat to the conjecture)")
        print()

    print("=" * 76)
    print("B. the exact ceiling of the neighbourhood-cut mechanism M1")
    print("=" * 76)
    for s in (M1MAX12, M2MAX12):
        n, E = A.g6(s)
        m = len(E)
        d = A.degrees(n, E)
        a = [set() for _ in range(n)]
        for u, v in E:
            a[u].add(v)
            a[v].add(u)
        M1 = min(sum(1 for (p, q) in E if p not in a[v] and q not in a[v]) for v in range(n))
        best = 0
        for S in range(1 << n):
            vs = [i for i in range(n) if (S >> i) & 1]
            if all(q not in a[p] for i, p in enumerate(vs) for q in vs[i + 1:]):
                best = max(best, sum(d[i] for i in vs))
        M2 = m - best
        M4 = Fr(m) - Fr(sum(x * x for x in d), n)
        print(f"{s}: N={n} |E|={m} degrees={sorted(d)} bipartite={A.is_bipartite(n,E)} "
              f"bip={A.bip(n,E)}")
        print(f"   M1 = {M1} = {Fr(M1, n*n)} N^2 = {float(Fr(M1,n*n)):.6f} N^2   "
              f"(N^2/16 = {Fr(n*n,16)}, N^2/25 = {Fr(n*n,25)})")
        print(f"   M2 = {M2} = {Fr(M2, n*n)} N^2     M4 = {M4} = {Fr(M4, n*n)} N^2")
        print(f"   M1 == N^2/16 exactly: {Fr(M1) == Fr(n*n,16)}")
        print()
    print("Every 3-regular triangle-free graph on 12 vertices has")
    print("   M1 = m - 3*3 = 18 - 9 = 9 = 144/16 = N^2/16 exactly,")
    print("so sup_G M1(G)/N^2 = 1/16 is ATTAINED, not merely a limit;")
    print("the report's 'worst ratio found 5/81 = 0.061728' is not the worst (1/16 = 0.0625).")


if __name__ == "__main__":
    main()
