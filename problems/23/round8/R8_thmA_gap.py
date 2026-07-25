"""R8_thmA_gap.py -- how much weaker is Lambda than psi?

Theorem A bounds the LP value Lambda.  Since Lambda <= psi, a proof of
"Lambda <= 1/25" says NOTHING about psi unless the LP is integral for the
instance at hand.  This script measures the gap exactly, so that any consumer
of Theorem A can see how far it is from the Erdos statement.
"""

from fractions import Fraction
import random
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *      # noqa
from R8_thmA_search import named_graphs, clebsch, mcgee   # noqa

print("%-26s %4s %6s  %-14s %-14s %-10s" % ("graph (uniform x)", "n", "m", "Lambda", "psi", "psi/Lambda"))
print("-" * 84)
rows = []
for nm, g in named_graphs():
    if g.has_triangle() or g.n > 18:
        continue
    x = [Fraction(1, g.n)] * g.n
    lam = exact_lambda(g, x).value
    ps, _ = exact_psi(g, x)
    ratio = float(ps / lam) if lam else float("nan")
    print("%-26s %4d %6d  %-14s %-14s %.6f" % (nm, g.n, g.m, lam, ps, ratio))
    rows.append((nm, lam, ps))

for sizes in [(1,1,1,1,1),(2,2,2,2,2),(3,2,2,2,2),(2,1,2,1,2),(3,3,3,3,3)]:
    gb, _ = blowup_C5(sizes)
    x = [Fraction(1, gb.n)] * gb.n
    lam = exact_lambda(gb, x).value
    ps, _ = exact_psi(gb, x)
    print("%-26s %4d %6d  %-14s %-14s %.6f" % ("C5%s" % (sizes,), gb.n, gb.m, lam, ps, float(ps / lam)))

print()
print("random maximal triangle-free graphs, uniform x, hunting for the largest gap:")
rng = random.Random(31337)
best = (1.0, None)
for n in range(6, 15):
    bn = (1.0, None)
    for t in range(160):
        g = random_maximal_triangle_free(n, rng)
        if g.is_bipartite():
            continue
        x = [Fraction(1, n)] * n
        lam = exact_lambda(g, x).value
        if lam == 0:
            continue
        ps, _ = exact_psi(g, x)
        r = float(ps / lam)
        if r > bn[0]:
            bn = (r, (g.graph6(), str(lam), str(ps)))
    print("  n=%2d  max psi/Lambda = %.6f  %s" % (n, bn[0], bn[1]))
    if bn[0] > best[0]:
        best = bn
print("\nlargest integrality gap found: psi/Lambda = %.6f at %s" % best)
print("(1/25 = %.6f)" % (1 / 25))
