"""AUDIT G12: ALL extremal graphs at N = 13 (bip = 6 = a(13)), found by an exhaustive
sweep of the 19 425 052 connected triangle-free graphs on 13 vertices (audit_G12_scan).

The report asserts (bold, section 1 P1):
  "The extremal objects up to N = 13 are exactly the graphs on which the trivial
   uniform cover x = 1/5 is LP-optimal and integral"
and "Same phenomenon on the extremal graphs at N = 12 (both of them) and N = 13:
   there bip = nu* = |E|/5 exactly."
and frames the N = 14 graph as the extremal object on which the LP first fails.

Decision procedure, exact, no full odd-cycle enumeration needed:
  * G triangle-free  =>  every odd cycle has >= 5 edges  =>  x == 1/5 is a feasible
    fractional cover  =>  nu* = tau* <= |E|/5.   If 5*bip > |E|, that ALONE proves
    bip > nu*: an integrality gap.
  * otherwise: an exactly verified fractional packing using only 5-cycles gives
    nu* >= value; if value == bip then nu* = bip exactly (since nu* <= bip), i.e. tight.
"""
from fractions import Fraction as Fr
import audit_G12_core as A

G13 = ["L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
       "L?`DAboU`w@{hS", "L?`DAboUdIF_Bo", "L?`DAboUdIF_Bw", "L?`DE`gl@YJODg"]

print("all 8 connected triangle-free graphs on 13 vertices with bip = 6 = a(13):", flush=True)
print()
gaps, tight, undecided = [], [], []
for s in G13:
    n, E = A.g6(s)
    m = len(E)
    assert A.triangle_free(n, E)
    b = A.bip(n, E)
    assert b == 6, (s, b)
    d = sorted(A.degrees(n, E))
    print(f"{s}: |E|={m} degs={d}   bip = {b}   |E|/5 = {Fr(m,5)}", flush=True)
    if 5 * b > m:
        print(f"    5*bip = {5*b} > |E| = {m}  =>  bip > |E|/5 >= tau* = nu*")
        print(f"    ==> INTEGRALITY GAP on an EXTREMAL object: deficit >= {Fr(b)-Fr(m,5)},"
              f" gap >= {Fr(5*b,m)}")
        gaps.append((s, m, b, Fr(m, 5)))
    else:
        cols = [es for vs, es in A.simple_cycles(n, E, maxlen=5, only_odd=True) if len(vs) == 5]
        r = A.nu_star_certified(n, E, columns=cols, dual_check_cycles=[])
        v = r["lower"]
        print(f"    exact 5-cycle packing (feasibility re-checked) = {v}"
              f"   ({len(cols)} five-cycles)")
        if v == b:
            print(f"    ==> nu* = {b} = bip exactly (tight; uniform 1/5 cover need not be optimal)")
            tight.append(s)
        else:
            print(f"    ==> undecided by 5-cycles alone (packing {v} < bip {b})")
            undecided.append(s)
    print(flush=True)

print(f"RESULT: of the 8 extremal graphs at N = 13, {len(gaps)} have bip > nu* "
      f"(EXACT), {len(tight)} are tight, {len(undecided)} undecided by this test.")
for s, m, b, nu in gaps:
    print(f"    GAP  {s}: |E|={m}, bip={b}, nu* <= {nu}, deficit >= {Fr(b)-nu}, "
          f"gap >= {Fr(b)/nu} = {float(Fr(b)/nu):.5f}")
print()
print("report's HEADLINE at N = 14 (M?AE@bH{AYN_LgBs?): bip = 7, nu* = 32/5,")
print("    deficit 3/5 = 0.6, gap 35/32 = 1.09375  -- strictly weaker than the N = 13")
print("    extremal witnesses above (smaller N, larger deficit, larger gap).")
