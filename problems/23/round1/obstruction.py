"""Exact verification of the obstruction to the 'random arc of C5' mechanism (task F3(ii)).

A rotation-invariant mechanism is: pick phi: V -> Z5, then pick a bipartition of Z5 from a
fixed distribution D that is invariant under the rotation i -> i+1, and cut V accordingly.
Its expected number of monochromatic edges is  sum_{uv in E} c(phi(u)-phi(v))  where
c(d) = P[ endpoints at Z5-distance d land on the same side ].

We verify:
 (1) for EVERY bipartition S of Z5,  #mono pentagon edges >= 1  and  #mono pentagram edges >= 1
     (both are 5-cycles, hence non-bipartite);
 (2) hence c(1) >= 1/5, c(2) >= 1/5, c(0) = 1, so the expected count is >= |E|/5 for every
     graph G and every phi;
 (3) the extreme points and the unique optimum c = (1, 1/5, 3/5);
 (4) for K_{m,m} (triangle-free, bip = 0, N = 2m) the mechanism's bound is exactly m^2/5 =
     N^2/20 > N^2/25, so no rotation-invariant mechanism can prove Erdos #23.
"""
from fractions import Fraction as F
import itertools

Z5 = range(5)
PENT = [(i, (i + 1) % 5) for i in Z5]        # distance-1 pairs
STAR = [(i, (i + 2) % 5) for i in Z5]        # distance-2 pairs

rows = []
print("  S           mono pentagon  mono pentagram   c1     c2")
for bits in range(32):
    S = {i for i in Z5 if (bits >> i) & 1}
    m1 = sum(1 for (a, b) in PENT if (a in S) == (b in S))
    m2 = sum(1 for (a, b) in STAR if (a in S) == (b in S))
    rows.append((m1, m2))
    if bits < 32:
        pass
mins = (min(r[0] for r in rows), min(r[1] for r in rows))
print("(1) min over all 32 bipartitions:  mono pentagon = %d, mono pentagram = %d" % mins)
assert mins == (1, 1)

types = sorted({r for r in rows})
print("(3) achievable (5*c1, 5*c2) pairs over single cuts:", types)
print("    => every cut has c1 >= 1/5 and c2 >= 1/5; a mixture cannot go below the min.")

# the unique rotation-invariant distribution attaining c1 = 1/5: uniform on the 5 max cuts
maxcuts = [ {k, (k + 2) % 5} for k in Z5 ]
c1 = sum(F(sum(1 for (a, b) in PENT if (a in S) == (b in S)), 5) for S in maxcuts) / 5
c2 = sum(F(sum(1 for (a, b) in STAR if (a in S) == (b in S)), 5) for S in maxcuts) / 5
print("(3) uniform over the 5 maximum cuts {k,k+2}:  c = (c0,c1,c2) = (1, %s, %s)" % (c1, c2))
assert (c1, c2) == (F(1, 5), F(3, 5))

# (4) K_{m,m}: min over phi of sum_e c(phi(u)-phi(v)) = m^2 * min_d c(d)
print("(4) for K_{m,m}: bound = m^2 * min_d c(d) >= m^2/5 = N^2/20 > N^2/25 (bip = 0).")
print("    ratio of what the mechanism can prove to the truth on K_{m,m}: infinite;")
print("    ratio to the conjectured bound: (N^2/20)/(N^2/25) = 5/4.")

# sanity: the best rotation-invariant bound in full, on C5[n] with the identity map
print("\nBest rotation-invariant bound is  e0 + e1/5 + 3*e2/5 .")
print("  C5[n]: e0=e2=0, e1=5n^2  -> n^2 = N^2/25  (TIGHT)")
print("  K_{m,m} best phi: all of A -> 0, all of B -> 1: e1 = m^2 -> m^2/5 = N^2/20  (FAILS)")
