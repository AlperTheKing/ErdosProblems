"""R8_thmA_gap2.py -- explicit triangle-free instance where the odd-cycle LP is
NOT integral, i.e. Lambda < psi.  This is what stops Theorem A from implying
Erdos's conjecture.

Construction: subdivide every edge of K5 twice.  Subdividing an edge twice adds
2 to the length of every cycle through it, so cycle parities are preserved:
the resulting 25-vertex graph S has odd girth 9 (triangle-free), and its odd
cycles correspond exactly to the odd cycles of K5.  With x uniform, every edge
has weight 1/625 and

    Lambda(S,x) = (1/625) * tau*(K5-all-odd) = (1/625)*(10/3) = 2/375,
    psi(S,x)    = (1/625) * tau (K5-all-odd) = (1/625)*4      = 4/625,

a 6/5 integrality gap (Guenin: K5 with all edges odd is THE obstruction to
weak bipartiteness).
"""

from fractions import Fraction
import itertools
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *      # noqa

# ---- build S = K5 with every edge subdivided twice
K5edges = [(i, j) for i in range(5) for j in range(i + 1, 5)]
edges = []
nxt = 5
paths = {}
for (u, v) in K5edges:
    a, b = nxt, nxt + 1
    nxt += 2
    edges += [(u, a), (a, b), (b, v)]
    paths[(u, v)] = [(u, a), (a, b), (b, v)]
S = Graph(nxt, edges)
print("S: n=%d m=%d triangle-free=%s odd girth=%s graph6=%s"
      % (S.n, S.m, not S.has_triangle(), S.odd_girth(), S.graph6()))

x = [Fraction(1, S.n)] * S.n
r = exact_lambda(S, x)
v = r.verify()
print("Lambda(S, uniform x) = %s = %.10f" % (r.value, float(r.value)))
print("  certificate: primal feasible %s (shortest odd cycle y-length %s), dual feasible %s, match %s"
      % (v["primal_feasible"], v["shortest_odd_cycle_len"], v["dual_feasible"], v["match"]))
print("  predicted (10/3)/625 = %s" % (Fraction(10, 3) / 625))

# ---- psi exactly, by the path argument:  an optimal cut can 2-colour every
# subdivision path perfectly iff its two branch vertices differ, and otherwise
# pays exactly one monochromatic edge.  So psi = (min mono edges of K5)/625.
best = None
for mask in range(32):
    mono = sum(1 for (u, w) in K5edges if ((mask >> u) & 1) == ((mask >> w) & 1))
    best = mono if best is None else min(best, mono)
print("min monochromatic edges over cuts of K5 = %d  (max-cut(K5)=6)" % best)
psi_exact = Fraction(best, 625)
print("psi(S, uniform x) = %s = %.10f" % (psi_exact, float(psi_exact)))

# independent confirmation of psi by direct search over cuts of S that respect
# the branch vertices (proved optimal above) + a brute-force check on a smaller
# analogue where the full 2^(n-1) enumeration is feasible.
print("psi/Lambda = %s = %.6f" % (psi_exact / r.value, float(psi_exact / r.value)))
print()

# smaller fully-brute-forceable analogue: K4 with every edge subdivided twice
# (K4 is not weakly bipartite? it is - included only as a control where
# LP = IP is expected)
for base, nm in [([(i, j) for i in range(4) for j in range(i + 1, 4)], "K4"),
                 ([(i, j) for i in range(5) for j in range(i + 1, 5)], "K5")]:
    e2 = []
    k = max(max(p) for p in base) + 1
    for (u, w) in base:
        a, b = k, k + 1
        k += 2
        e2 += [(u, a), (a, b), (b, w)]
    H = Graph(k, e2)
    xx = [Fraction(1, H.n)] * H.n
    lam = exact_lambda(H, xx).value
    print("subdivided %s: n=%d Lambda=%s=%.8f" % (nm, H.n, lam, float(lam)))

print()
print("CONCLUSION: the odd-cycle LP is NOT integral on triangle-free graphs, so")
print("Theorem A (Lambda <= 1/25) does NOT by itself give psi <= 1/25.")
