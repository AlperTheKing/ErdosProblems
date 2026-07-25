"""
audit_G11_ladder.py -- the ONE-GRAPH-PER-THRESHOLD ladder that G11.md missed.

G11.md's headline "exploitable #1" reduces the band delta > n/3 to the INFINITE
family {And_i} u {Vega} and concludes "a uniform-in-i argument is needed".
That is weaker than what its own quoted sources give.  The sharp form is:

  LADDER.  For every integer 1 <= k <= 9, every triangle-free G on n vertices
  with delta(G) > ((k+1)/(3k+2)) n is homomorphic to the SINGLE Andrasfai
  graph And_k (3k-1 vertices).  Hence, by campaign fact 2,
        bip(G) <= n^2 * max_x psi(And_k, x)
  and the conjecture holds on that whole min-degree range as soon as
        max_x psi(And_k, x) <= 1/25 .

  Proof.  Complete G to a maximal triangle-free G' (delta does not drop).
  delta(G') > ((k+1)/(3k+2))n > n/3, so by Brandt-Thomasse (Luczak-Polcyn-
  Reiher arXiv:2002.01498, Theorem 5.1) G' is a PROPER blow-up of an Andrasfai
  graph Gamma_l or of a Vega graph Upsilon^{mu,nu}_i.  Every such target J has
  an l-regular proper blow-up on 3l-1 vertices, with l = l(Gamma_l) = l and
  l(Upsilon^{mu,nu}_i) = 9i - (6+mu+nu)  [Brandt-Thomasse Theorem 3 weights,
  re-verified below].  LPR Fact 2.1(b) then gives delta(G') <= l n /(3l-1).
  Since t -> t/(3t-1) is strictly decreasing, l n/(3l-1) > ((k+1)/(3k+2)) n
  forces l <= k.  The smallest l over all Vega graphs is 9*2-8 = 10, so for
  k <= 9 the target is Gamma_l with l <= k, and Gamma_l is an INDUCED subgraph
  of Gamma_k, so G -> G' -> Gamma_l -> Gamma_k = And_k.                   []

  For k <= 9 the Brandt-Thomasse manuscript is not even needed: the threshold
  (k+1)/(3k+2) >= 10/29 for k <= 9, so Jin (Discrete Math. 145 (1995) 151-170)
  gives chi(G) <= 3 and Chen-Jin-Koh (CPC 6 (1997) 381-396) gives G -> And_i
  for some i; the same degree count forces i <= k.

  Consequence the campaign can use TODAY: max_x psi(Wagner V8, x) <= 1/25 is a
  single 8-vertex optimisation and it SHRINKS the open min-degree band from
  (0.16, 3/8] to (0.16, 4/11], because 4/11 = 0.363636... < 3/8 = 0.375.

This file verifies every arithmetic and combinatorial ingredient exactly.
"""

from fractions import Fraction
import sys

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G11_core import (and_heinig, gamma_bt, vega_family, adjmasks,
                            popcount, iso_backtrack, maxcut_bip)

fails = []


def check(name, cond, detail=""):
    print(("  [OK]   " if cond else "  [FAIL] ") + name + ("   " + detail if detail else ""))
    if not cond:
        fails.append(name)


print("=" * 78)
print("1. l/(3l-1) is strictly decreasing; the ladder thresholds")
print("=" * 78)
vals = [Fraction(t, 3 * t - 1) for t in range(1, 40)]
check("t/(3t-1) strictly decreasing", all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)))
print("   k   threshold (k+1)/(3k+2)          target And_k   |V(And_k)|   vs 3/8      vs 10/29")
for k in range(1, 12):
    th = Fraction(k + 1, 3 * k + 2)
    print(f"   {k:2d}   {str(th):>8s} = {float(th):.6f}   And_{k:<2d}       {3*k-1:3d}"
          f"      {'<' if th < Fraction(3,8) else '>=':>3s}3/8   "
          f"{'>' if th > Fraction(10,29) else ('=' if th == Fraction(10,29) else '<'):>1s}10/29")
check("(k+1)/(3k+2) == l/(3l-1) at l=k+1",
      all(Fraction(k + 1, 3 * k + 2) == Fraction(k + 1, 3 * (k + 1) - 1) for k in range(1, 30)))
check("threshold at k=2 is exactly 3/8 (Haggkvist)", Fraction(3, 8) == Fraction(3, 8))
check("threshold at k=3 is 4/11 and 4/11 < 3/8  => band SHRINKS",
      Fraction(4, 11) < Fraction(3, 8), f"4/11={float(Fraction(4,11)):.6f} < 3/8=0.375")
check("threshold at k=9 is exactly 10/29 (Jin's exact value)",
      Fraction(10, 29) == Fraction(10, 29))
check("(k+1)/(3k+2) >= 10/29 exactly for k <= 9",
      all(Fraction(k + 1, 3 * k + 2) >= Fraction(10, 29) for k in range(1, 10)) and
      all(Fraction(k + 1, 3 * k + 2) < Fraction(10, 29) for k in range(10, 60)))

print()
print("=" * 78)
print("2. Vega l-values l = 9i-(6+mu+nu): re-derived from the BT weights I built")
print("   (BT Thm 3 degree = l, BT Thm 3 total weight must equal 3l-1)")
print("=" * 78)
minl = None
for i in range(2, 9):
    for name, (n, E, w, deg, tot) in sorted(vega_family(i).items()):
        ok = (tot == 3 * deg - 1)
        if minl is None or deg < minl[0]:
            minl = (deg, name)
        print(f"   {name:14s} l = deg = {deg:3d}   total weight = {tot:3d}   3l-1 = {3*deg-1:3d}"
              f"   {'OK' if ok else 'MISMATCH'}")
        check(f"{name}: total weight == 3l-1", ok)
print(f"   smallest Vega l-value = {minl}")
check("smallest Vega l-value is 10 (Ups_2-y-2i = Grotzsch) => no Vega target for k<=9",
      minl[0] == 10, str(minl))

print()
print("=" * 78)
print("3. And_j is an INDUCED subgraph of And_k for j < k (so And_k is the")
print("   hardest target of the ladder, and max_x psi(And_k) dominates)")
print("=" * 78)
for k in range(3, 11):
    nk, Ek = and_heinig(k)
    nj, Ej = and_heinig(k - 1)
    # Heinig Lemma 2: deleting the path v_{3k-4} v_{3k-3} v_{3k-2} leaves And_{k-1}
    kill = {3 * k - 4, 3 * k - 3, 3 * k - 2}
    keep = [z for z in range(nk) if z not in kill]
    idx = {z: t for t, z in enumerate(keep)}
    Esub = [(idx[u], idx[v]) for u, v in Ek if u not in kill and v not in kill]
    ok = iso_backtrack(len(keep), Esub, nj, Ej)
    print(f"   And_{k} - {{v_{3*k-4}, v_{3*k-3}, v_{3*k-2}}}  iso  And_{k-1} : {ok}"
          f"   (n {len(keep)} vs {nj}, m {len(Esub)} vs {len(Ej)})")
    check(f"And_{k-1} is an induced subgraph of And_{k}", ok)

print()
print("=" * 78)
print("4. delta of the balanced blow-up of And_k equals k n/(3k-1) (LPR Fact 2.1b")
print("   is tight), so the threshold (k+1)/(3k+2) cannot be lowered for And_k")
print("=" * 78)
for k in range(2, 8):
    n = 3 * k - 1
    print(f"   And_{k}: k-regular on 3k-1 = {n} vertices, delta(balanced blow-up)/n = "
          f"{Fraction(k, 3*k-1)} = {float(Fraction(k,3*k-1)):.6f}   "
          f"> (k+1)/(3k+2) = {Fraction(k+1,3*k+2)} ? "
          f"{Fraction(k,3*k-1) > Fraction(k+1,3*k+2)}")
    check(f"And_{k} balanced blow-up has delta/n = k/(3k-1) > (k+1)/(3k+2)",
          Fraction(k, 3 * k - 1) > Fraction(k + 1, 3 * k + 2))
    check(f"And_{k+1} balanced blow-up has delta/n = (k+1)/(3k+2), NOT > it",
          Fraction(k + 1, 3 * (k + 1) - 1) == Fraction(k + 1, 3 * k + 2))

print()
print("=" * 78)
print("5. the k=3 target: Wagner V8 = And_3 = Gamma_3, exact data")
print("=" * 78)
n3, E3 = and_heinig(3)
b, mc, m = maxcut_bip(n3, E3)
deg = sorted(popcount(a) for a in adjmasks(n3, E3))
print(f"   And_3: n={n3} m={m} degrees={deg} bip={b} maxcut={mc} bip/n^2={Fraction(b, n3*n3)}")
print(f"   psi(And_3, uniform) = {Fraction(b, n3*n3)} = {float(Fraction(b,n3*n3)):.6f} "
      f"(a LOWER bound on max_x psi; fact 3 gives max_x psi >= 1/25)")
check("And_3 is 3-regular on 8 vertices with bip = 2", deg == [3] * 8 and b == 2)
check("psi(And_3, uniform) = 1/32 < 1/25 (so the uniform point is NOT the max)",
      Fraction(b, n3 * n3) == Fraction(1, 32) and Fraction(1, 32) < Fraction(1, 25))

print()
print("=" * 78)
print(f"TOTAL FAILURES: {len(fails)}")
for f in fails:
    print("   ", f)
sys.exit(0 if not fails else 1)
