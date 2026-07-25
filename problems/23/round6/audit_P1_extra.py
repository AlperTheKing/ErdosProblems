"""Two side questions that decide how much P1.md's pentagon lemma is worth.

(1) Is "pentagonal" (cyclic 5-block) strictly weaker than "admits a homomorphism to C5"?
    If the two coincide on circle configurations then the pentagon lemma covers exactly the
    class for which the CONJECTURE is already trivial (G -> C5 implies psi(G,x) <=
    psi(C5, pushforward x) <= 1/25 by pulling any cut back along the homomorphism), and the
    lemma's only content is that the certifying cut can be taken to be an ARC.
    Exhaustive over supports S subset Z_q, q <= 16, |S| <= 8, rotation fixed; pentagonality is
    only tested when a C5-homomorphism exists (pentagonal => hom, so no mismatch is possible
    otherwise).

(2) max_x psi(V8) over the simplex -- the report only computes psi at the uniform weighting
    (1/32).  V8 contains an induced C5, so max_x psi should be exactly 1/25; check by exact
    integer enumeration of all weightings with denominator 20 and 30.
"""
import functools
from fractions import Fraction as F
from itertools import combinations
print = functools.partial(print, flush=True)
from audit_P1_engine import M, TARGET

print("=== (1) pentagonal vs hom-to-C5 on circle supports ===")
mismatch = []
tot = homs = 0
for q in range(5, 17):
    for size in range(5, min(q, 8) + 1):
        for S in combinations(range(1, q), size - 1):
            S = (0,) + S
            mu = M(q, [(k, 1) for k in S])
            if not mu.E:
                continue
            tot += 1
            if not mu.hom_C5():
                continue                       # then it cannot be pentagonal either
            homs += 1
            if mu.pentagon() is None:
                mismatch.append((q, S))
    print(f"   ...q={q} done: tested {tot}, hom-to-C5 {homs}, mismatches {len(mismatch)}")
print(f"   supports tested: {tot}   hom-to-C5: {homs}   hom but NOT pentagonal: {len(mismatch)}")
for t in mismatch[:12]:
    print("     ", t)

print()
print("=== (2) max_x psi for the Wagner graph V8 (integer enumeration, exact) ===")
POS = (0, 1, 6, 7, 12, 13, 14, 19)
CEs = M(20, [(k, 1) for k in POS])
E = CEs.E
print(f"   uniform weighting: psi = {CEs.psi()} = {float(CEs.psi()):.6f}")
c5corner = M(20, [(k, 1) for k in (0, 1, 7, 12, 14)])
print(f"   induced C5 {{0,1,7,12,14}}, uniform: psi = {c5corner.psi()}  (= 1/25: "
      f"{c5corner.psi() == TARGET})")
masks = [[(i, j) for (i, j) in E if ((mk >> i) & 1) == ((mk >> j) & 1)]
         for mk in range(1 << 7)]
for den in (20, 30):
    best = (0, None)
    for w in combinations(range(1, den), 7):
        p = [w[0]] + [w[i + 1] - w[i] for i in range(6)] + [den - w[6]]
        v = min(sum(p[i] * p[j] for (i, j) in mk) for mk in masks)
        if v > best[0]:
            best = (v, p)
    val = F(best[0], den * den)
    print(f"   all integer weightings summing to {den}: max psi = {best[0]}/{den*den} = {val} "
          f"= {float(val):.6f} at {best[1]}   (25*psi <= 1: {25 * val <= 1})")
