"""R8_thmA_lemma2.py -- weight-free census check of Lemma 2.

Lemma 2 reduces to a purely COMBINATORIAL statement, because
    sum_{v in V(C)} d(v) = sum_u x_u |N(u) cap V(C)|
is a linear function of x on the simplex, so its maximum over all x is exactly
    max_u |N(u) cap V(C)|.
Hence Lemma 2 ("<= (L-1)/2 for every odd cycle C") is EQUIVALENT to

    for every odd cycle C of length L and every vertex u:  |N(u) cap V(C)| <= (L-1)/2,

which needs no weights at all.  This script verifies that over a census of
triangle-free graphs, for EVERY odd cycle (all lengths, Hamiltonian included).
"""

from fractions import Fraction
import random
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *      # noqa
from R8_thmA_search import named_graphs, clebsch, mcgee   # noqa

bad = 0
tot_graphs = 0
tot_cycles = 0
tight = 0


def check(g, tag):
    global bad, tot_graphs, tot_cycles, tight
    tot_graphs += 1
    for C in all_odd_cycles(g):
        tot_cycles += 1
        S = set(C)
        lim = (len(C) - 1) // 2
        mx = max(len(g.adj[u] & S) for u in range(g.n))
        if mx > lim:
            bad += 1
            print("  VIOLATION", tag, g.graph6(), "cycle", C, "max |N(u) cap C| =", mx, ">", lim)
        if mx == lim:
            tight += 1


print("named graphs:")
for nm, g in named_graphs():
    if g.has_triangle() or g.n > 17:
        continue
    check(g, nm)
    print("  %-24s done (n=%d)" % (nm, g.n))

print("C5 blow-ups:")
for sizes in [(1,1,1,1,1),(2,2,2,2,2),(3,2,2,2,2),(2,1,2,1,2),(3,3,2,2,2),(2,2,2,2,1)]:
    gb, _ = blowup_C5(sizes)
    check(gb, "C5%s" % (sizes,))

print("random maximal triangle-free graphs n=5..12 ...")
rng = random.Random(864203)
for n in range(5, 13):
    for t in range(60 if n <= 10 else 25):
        g = random_maximal_triangle_free(n, rng)
        check(g, "rand n=%d" % n)

print("random (not necessarily maximal) triangle-free graphs n=5..11 ...")
for n in range(5, 12):
    for t in range(60):
        g0 = random_maximal_triangle_free(n, rng)
        es = [e for e in g0.edges if rng.random() < 0.75]
        check(Graph(n, es), "randsub n=%d" % n)

print()
print("graphs checked      : %d" % tot_graphs)
print("odd cycles checked  : %d  (all odd lengths, Hamiltonian included)" % tot_cycles)
print("cycles where the bound |N(u) cap C| <= (L-1)/2 is TIGHT: %d" % tight)
print("VIOLATIONS          : %d" % bad)
print()
print("control: the same bound on graphs WITH triangles must fail --")
K4 = Graph(4, [(i, j) for i in range(4) for j in range(i + 1, 4)])
v = 0
for C in all_odd_cycles(K4):
    S = set(C)
    mx = max(len(K4.adj[u] & S) for u in range(K4.n))
    if mx > (len(C) - 1) // 2:
        v += 1
print("  K4: %d of %d odd cycles violate it (expected > 0: triangle-freeness is essential)"
      % (v, len(all_odd_cycles(K4))))
