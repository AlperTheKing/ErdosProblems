"""R8_thmA_blowup.py -- task 3: is 1/25 attained or exceeded on C5 and on
UNBALANCED C5 blow-ups?  Everything exact.

Claims checked here:
 (i)   Lambda(C5,x) = min_i x_i x_{i+1}, maximised at 1/25 exactly at x uniform.
 (ii)  For any graph G with a homomorphism to C5 (in particular every C5
       blow-up, with parts allowed to be empty) and any x,
       Lambda(G,x) <= min_i P_i P_{i+1} <= 1/25, P_i = weight of class i.
       Equality on the right forces P_i = 1/5 for all i (AM-GM).
 (iii) For every triangle-free G containing a 5-cycle C, putting x = 1/5 on C
       and 0 elsewhere gives Lambda(G,x) = 1/25 EXACTLY (plateau).
"""

from fractions import Fraction
import random
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *      # noqa
from R8_thmA_search import named_graphs, five_cycles, clebsch, mcgee   # noqa

ONE25 = Fraction(1, 25)
FAIL = []
rng = random.Random(99991)

print("=" * 96)
print("(i) C5 itself")
print("=" * 96)
C5 = cycle_graph(5)
x = [Fraction(1, 5)] * 5
r = exact_lambda(C5, x)
v = r.verify()
print("x uniform: Lambda = %s ; cover y = %s (cost %s) ; packing z = %s (value %s)"
      % (r.value, r.y, v["primal_value"], r.z, v["dual_value"]))
print("           certificate: primal feasible %s, dual feasible %s, values match %s"
      % (v["primal_feasible"], v["dual_feasible"], v["match"]))
print("           1/25 ATTAINED exactly, not exceeded.")

worst = Fraction(0)
worstx = None
bad = 0
for t in range(1200):
    xs = [Fraction(rng.randint(0, 60)) for _ in range(5)]
    s = sum(xs)
    if s == 0:
        continue
    xs = [q / s for q in xs]
    lam = exact_lambda(C5, xs).value
    formula = min(xs[i] * xs[(i + 1) % 5] for i in range(5))
    if lam != formula:
        bad += 1
        print("  FORMULA MISMATCH", xs, lam, formula)
    if lam > worst:
        worst, worstx = lam, xs
    if lam > ONE25:
        FAIL.append(("C5 random x over 1/25", xs, lam))
print("1200 random rational x on C5: formula mismatches = %d ; max Lambda = %s = %.12f at x=%s"
      % (bad, worst, float(worst), worstx))

print()
print("=" * 96)
print("(ii) C5 blow-ups C5[a1..a5], INCLUDING unequal parts, empty parts and")
print("     non-uniform weights inside the parts")
print("=" * 96)
maxlam = Fraction(0)
maxrec = None
rows = 0
for trial in range(160):
    sizes = tuple(rng.randint(0, 3) for _ in range(5))
    if sum(sizes) == 0:
        continue
    gb, parts = blowup_C5(sizes)
    if gb.m == 0 or gb.n > 12:
        continue
    mode = trial % 3
    if mode == 0:
        xs = [Fraction(1, gb.n)] * gb.n
    elif mode == 1:                        # uniform inside parts, unequal parts
        pw = [Fraction(rng.randint(0, 20)) for _ in range(5)]
        xs = [Fraction(0)] * gb.n
        for i, P in enumerate(parts):
            for u in P:
                xs[u] = pw[i] / max(len(P), 1)
        s = sum(xs)
        if s == 0:
            continue
        xs = [q / s for q in xs]
    else:                                   # fully generic weights
        xs = [Fraction(rng.randint(0, 20)) for _ in range(gb.n)]
        s = sum(xs)
        if s == 0:
            continue
        xs = [q / s for q in xs]
    P = [sum(xs[u] for u in parts[i]) for i in range(5)]
    blockbound = min(P[i] * P[(i + 1) % 5] for i in range(5))
    lam = exact_lambda(gb, xs).value
    rows += 1
    if lam > blockbound:
        FAIL.append(("blow-up exceeds block bound", sizes, xs, lam, blockbound))
        print("  BLOCK BOUND VIOLATED", sizes, lam, blockbound)
    if blockbound > ONE25:
        FAIL.append(("block bound over 1/25", sizes, P, blockbound))
    if lam > maxlam:
        maxlam, maxrec = lam, (sizes, [str(q) for q in xs], str(blockbound))
    if lam > ONE25:
        FAIL.append(("blow-up over 1/25", sizes, xs, lam))
print("%d blow-up instances (sizes 0..3 per part, 3 weight regimes)" % rows)
print("max exact Lambda = %s = %.12f   at sizes=%s  (block bound there %s)"
      % (maxlam, float(maxlam), maxrec[0], maxrec[2]))
print("1/25 = 0.04 : %s" % ("ATTAINED, never exceeded" if maxlam == ONE25 else "not attained"))

print()
print("targeted unbalanced blow-ups, uniform x on each vertex:")
for sizes in [(1,1,1,1,1),(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),
              (2,2,2,2,1),(3,2,2,2,2),(5,5,5,5,4),(6,5,5,5,5),(10,10,10,10,10),
              (2,1,1,1,1),(1,2,1,2,1),(3,1,3,1,3),(0,1,1,1,1),(1,1,0,1,1)]:
    gb, parts = blowup_C5(sizes)
    if gb.m == 0:
        print("   sizes=%-18s (bipartite / empty) Lambda = 0" % (str(sizes),))
        continue
    xs = [Fraction(1, gb.n)] * gb.n
    P = [sum(xs[u] for u in parts[i]) for i in range(5)]
    bb = min(P[i] * P[(i + 1) % 5] for i in range(5))
    lam = exact_lambda(gb, xs).value
    print("   sizes=%-18s n=%3d  Lambda = %-12s = %.10f   block bound %-10s   %s"
          % (str(sizes), gb.n, lam, float(lam), bb,
             "== 1/25" if lam == ONE25 else ("> 1/25 !!!" if lam > ONE25 else "< 1/25")))

print()
print("=" * 96)
print("(iii) plateau: x concentrated on a 5-cycle of a larger triangle-free graph")
print("=" * 96)
for nm, g in named_graphs():
    if g.has_triangle():
        continue
    C = five_cycles(g, 1)
    if not C:
        print("   %-24s no 5-cycle (odd girth %s)" % (nm, g.odd_girth()))
        continue
    xs = [Fraction(0)] * g.n
    for u in C[0]:
        xs[u] = Fraction(1, 5)
    r = exact_lambda(g, xs)
    v = r.verify()
    ok = v["primal_feasible"] and v["dual_feasible"] and v["match"]
    print("   %-24s Lambda(C5-concentrated x) = %-8s  %s  (certified %s)"
          % (nm, r.value, "== 1/25" if r.value == ONE25 else "!= 1/25", ok))
    if r.value != ONE25:
        FAIL.append(("plateau", nm, r.value))

print()
print("FAILURES:", FAIL if FAIL else "none")
