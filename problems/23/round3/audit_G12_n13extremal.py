"""AUDIT G12: ALL extremal graphs at N = 13 (bip = 6 = a(13)), found by an exhaustive
sweep of the 19 425 052 connected triangle-free graphs on 13 vertices.

The report asserts (bold, section 1 P1):
  "The extremal objects up to N = 13 are exactly the graphs on which the trivial
   uniform cover x = 1/5 is LP-optimal and integral"
and "Same phenomenon on the extremal graphs at N = 12 (both of them) and N = 13:
   there bip = nu* = |E|/5 exactly."
It also frames the N = 14 graph as the first extremal object with an integrality gap.

This script tests that on ALL 8 extremal graphs at N = 13, exactly.
"""
from fractions import Fraction as Fr
import audit_G12_core as A

G13 = ["L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
       "L?`DAboU`w@{hS", "L?`DAboUdIF_Bo", "L?`DAboUdIF_Bw", "L?`DE`gl@YJODg"]

print("all 8 connected triangle-free graphs on 13 vertices with bip = 6 = a(13):")
print()
gaps = []
for s in G13:
    n, E = A.g6(s)
    m = len(E)
    assert A.triangle_free(n, E)
    b = A.bip(n, E)
    assert b == 6
    odd = [es for _, es in A.simple_cycles(n, E, only_odd=True)]
    unif = A.check_cover(n, E, [Fr(1, 5)] * m, odd)
    assert unif, "uniform 1/5 cover must be feasible for a triangle-free graph"
    cols = [es for vs, es in A.simple_cycles(n, E, maxlen=5, only_odd=True) if len(vs) == 5]
    r = A.nu_star_certified(n, E, columns=cols, dual_check_cycles=odd)
    if r["lower"] == Fr(m, 5):
        nu = Fr(m, 5)
        how = "5-cycle packing = uniform cover"
    else:
        r2 = A.nu_star_certified(n, E)
        nu = r2["value"]
        how = f"full LP over {len(odd)} odd cycles"
    d = sorted(A.degrees(n, E))
    print(f"{s}: |E|={m} degs={d}")
    print(f"    bip = {b}   |E|/5 = {Fr(m,5)}   nu* = tau* = {nu}   [{how}]")
    print(f"    bip - nu* = {Fr(b) - nu}    gap bip/nu* = {Fr(b)/nu}"
          f"    {'<<< INTEGRALITY GAP on an EXTREMAL object' if nu < b else 'tight'}")
    if nu < b:
        gaps.append((s, m, b, nu))
    print()

print(f"{len(gaps)} of the 8 extremal graphs at N = 13 have bip > nu*.")
for s, m, b, nu in gaps:
    print(f"    {s}: bip={b}, nu*={nu}, deficit={Fr(b)-nu}, gap={Fr(b)/nu}")
print()
print("Compare the report's HEADLINE at N = 14 (M?AE@bH{AYN_LgBs?):")
print("    bip = 7, nu* = 32/5, deficit 3/5, gap 35/32 = 1.09375")
if gaps:
    bs, bm, bb, bn = max(gaps, key=lambda t: Fr(t[2]) / t[3])
    print(f"    beaten at N = 13 by {bs}: deficit {Fr(bb)-bn}, gap {Fr(bb)/bn} "
          f"= {float(Fr(bb)/bn):.5f}  (smaller N, larger gap, larger deficit)")
