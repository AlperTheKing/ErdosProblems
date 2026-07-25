"""audit_Q2_c_switch.py -- exact minimum improving switch of W*(u,r), independent
engine, u = 1..40 and the r-range claim.  Exact integers.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_b_wstar import (wstar_min_switch_counts, wstar_delta_counts,
                              check_all_families)

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


say("=" * 78)
say("C1.  MINIMUM IMPROVING SWITCH of W*(u,u)  --  own engine, u = 1..40")
say("=" * 78)
q2 = {1: 5, 2: 9, 3: 12, 4: 16, 5: 19, 6: 23, 7: 26, 8: 30, 9: 33}
say("   u    N   min|S|  ceil((7u+3)/2)  |S|/N        Q2.md   witness s=(c0,c1,c2,c3a,R,c4)")
mism = []
for u in list(range(1, 21)) + [25, 30, 40]:
    k, s = wstar_min_switch_counts(u, u)
    N = 12 * u
    pred = -(-(7 * u + 3) // 2)
    tag = ""
    if u in q2:
        tag = f"{q2[u]}" + ("" if q2[u] == k else "  <<< MISMATCH")
        if q2[u] != k:
            mism.append((u, k, q2[u]))
    say(f"  {u:3d} {N:5d} {k:7d} {pred:13d}    {str(F(k,N)):>9s} = {float(F(k,N)):.5f}  "
        f"{tag:>10s}   {s}   [formula {'ok' if pred == k else 'BREAKS'}]")
say()
say(f"  Q2.md table u=1..9 : {'CONFIRMED' if not mism else 'MISMATCHES ' + str(mism)}")
say(f"  min over u<=9 of |S|/N = {min(F(wstar_min_switch_counts(u,u)[0], 12*u) for u in range(1,10))} "
    f"= {float(min(F(wstar_min_switch_counts(u,u)[0], 12*u) for u in range(1,10))):.5f}  "
    f"(Q2.md claims >= 0.3055 for N<=108)")
say(f"  limit of ceil((7u+3)/2)/(12u) = 7/24 = {float(F(7,24)):.6f}")

say()
say("=" * 78)
say("C2.  Is 7/24 really the INFIMUM?  exact min|S|/N for large u")
say("=" * 78)
for u in (40, 60, 100):
    k, s = wstar_min_switch_counts(u, u)
    say(f"   u={u:4d} N={12*u:5d} min|S|={k:5d}  |S|/N = {float(F(k,12*u)):.6f}  "
        f"pred ceil((7u+3)/2) = {-(-(7*u+3)//2)}   s={s}")
say("   analytic witness family:  s = (0, 1, floor(5u/2)+1, 0, u, 0)")
say("   Delta = -(5u*1 + 2u*k) + 2(1*k + k*u) = 2k - 5u  > 0  iff  k >= floor(5u/2)+1,")
say("   so |S| = 1 + u + floor(5u/2)+1 = ceil((7u+3)/2)  -- an exact PROOF of the upper")
say("   bound on min|S| for every u (the enumeration supplies the matching lower bound).")
for u in (3, 7, 11, 40, 100):
    k = (5 * u) // 2 + 1
    s = (0, 1, k, 0, u, 0)
    say(f"     u={u:4d}: s={s}  Delta={wstar_delta_counts(u,u,s)}  |S|={sum(s)}  "
        f"ceil((7u+3)/2)={-(-(7*u+3)//2)}")

say()
say("=" * 78)
say("C3.  the r-range claim of Q2.md section 5")
say("=" * 78)
q2range = {1: (1, 1), 2: (1, 3), 3: (1, 5), 4: (2, 6), 5: (2, 8), 6: (2, 10), 7: (3, 11)}
for u in range(1, 8):
    good = []
    for r in range(0, 2 * u + 1):
        res = check_all_families(u, r)
        ok = (res['sigma>=0'] and res['switch-star'] and res['(*)max'][0] <= 0
              and res['SUPmax'][0] <= 0 and res['NBRUmax'][0] <= 0 and res['PAIRNBRmax'][0] <= 0)
        if ok:
            good.append(r)
    lo, hi = q2range[u]
    claim = list(range(lo, hi + 1))
    say(f"  u={u}: r with sigma>=0 & star & (*) & SUP & NBRU & PAIRNBR all satisfied = {good}"
        f"    Q2.md claims {claim}   {'MATCH' if good == claim else '<<< MISMATCH'}")

open(r"E:\Projects\ErdosProblems\problems\23\round7\audit_Q2_c_out.txt", "w").write("\n".join(OUT))
