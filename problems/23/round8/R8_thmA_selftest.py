"""R8_thmA_selftest.py -- validate the enumerator, the separation oracle and the
exact LP against each other and against hand-computable counts."""

from fractions import Fraction
import random
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *   # noqa

FAIL = []


def check(name, got, want):
    ok = (got == want)
    print(("PASS " if ok else "FAIL ") + name + ": got %s want %s" % (got, want))
    if not ok:
        FAIL.append(name)


# ---------------------------------------------------------------- enumerator
K5 = Graph(5, [(i, j) for i in range(5) for j in range(i + 1, 5)])
cy = all_cycles(K5)
check("K5 total cycles (10 tri + 15 C4 + 12 C5)", len(cy), 37)
check("K5 odd cycles (10 tri + 12 C5)", len(all_odd_cycles(K5)), 22)
check("K5 C5-count (Hamiltonian, 4!/2)", sum(1 for c in cy if len(c) == 5), 12)

C5 = cycle_graph(5)
check("C5 odd cycles", len(all_odd_cycles(C5)), 1)

K33 = Graph(6, [(i, 3 + j) for i in range(3) for j in range(3)])
cy = all_cycles(K33)
check("K33 total cycles (9 C4 + 6 C6)", len(cy), 15)
check("K33 odd cycles", len(all_odd_cycles(K33)), 0)
check("K33 C6-count (Hamiltonian, 3!2!/2)", sum(1 for c in cy if len(c) == 6), 6)

P = petersen()
cy = all_cycles(P)
cnt = {}
for c in cy:
    cnt[len(c)] = cnt.get(len(c), 0) + 1
check("Petersen cycle spectrum {5:12,6:10,8:15,9:20}", cnt, {5: 12, 6: 10, 8: 15, 9: 20})
check("Petersen odd cycles 12+20", len(all_odd_cycles(P)), 32)

G11 = circle_graph(11, 11)
check("Gamma_11 n,m", (G11.n, G11.m), (11, 22))
oc11 = all_odd_cycles(G11)
check("Gamma_11 odd cycles (prompt: 596)", len(oc11), 596)
check("Gamma_11 odd Hamiltonian cycles (prompt: 145)",
      sum(1 for c in oc11 if len(c) == 11), 145)

# K6 sanity: number of Hamiltonian cycles 5!/2 = 60
K6 = Graph(6, [(i, j) for i in range(6) for j in range(i + 1, 6)])
check("K6 Hamiltonian cycles 5!/2", sum(1 for c in all_cycles(K6) if len(c) == 6), 60)


# ------------------------------------------- separation oracle vs enumeration
rng = random.Random(20260726)
bad = 0
for trial in range(60):
    n = rng.randint(5, 9)
    g = random_maximal_triangle_free(n, rng)
    if g.is_bipartite():
        continue
    oc = all_odd_cycles(g)
    y = [Fraction(rng.randint(0, 20), rng.randint(1, 9)) for _ in range(g.m)]
    brute = min(sum(y[g.eidx[e]] for e in cycle_edges(c)) for c in oc)
    L, C = shortest_odd_cycle(g, y)
    if L != brute:
        bad += 1
        print("  MISMATCH n=%d %s: dijkstra=%s brute=%s" % (n, g.graph6(), L, brute))
    if len(C) % 2 == 0:
        bad += 1
        print("  EVEN CYCLE RETURNED")
check("separation oracle == brute force shortest odd cycle (60 random graphs)", bad, 0)

# odd girth cross-check
bad = 0
for trial in range(40):
    n = rng.randint(5, 10)
    g = random_maximal_triangle_free(n, rng)
    oc = all_odd_cycles(g)
    og = g.odd_girth()
    want = min((len(c) for c in oc), default=None)
    if og != want:
        bad += 1
check("odd_girth == min odd cycle length (40 random graphs)", bad, 0)


# ------------------------------------------------------ exact LP cross-checks
def lambda_by_full_enumeration(g, x):
    """Same LP but with EVERY odd cycle listed explicitly; exact simplex."""
    keep = [v for v in range(g.n) if x[v] > 0]
    h, idx = g.subgraph(keep)
    xs = [x[v] for v in keep]
    w = [xs[u] * xs[v] for (u, v) in h.edges]
    oc = all_odd_cycles(h)
    if not oc:
        return Fraction(0)
    A = [[Fraction(0)] * len(oc) for _ in range(h.m)]
    for j, C in enumerate(oc):
        for e in cycle_edges(C):
            A[h.eidx[e]][j] = Fraction(1)
    val, z, u = simplex_max(A, w, [Fraction(1)] * len(oc))
    return val


x5 = [Fraction(1, 5)] * 5
r = exact_lambda(C5, x5)
v = r.verify()
check("C5 uniform Lambda == 1/25", r.value, Fraction(1, 25))
check("C5 certificate verifies", (v["primal_feasible"], v["dual_feasible"], v["match"]),
      (True, True, True))
check("C5 full-enumeration LP agrees", lambda_by_full_enumeration(C5, x5), Fraction(1, 25))

bad = 0
for trial in range(30):
    n = rng.randint(5, 9)
    g = random_maximal_triangle_free(n, rng)
    if g.is_bipartite():
        continue
    x = [Fraction(rng.randint(0, 6)) for _ in range(n)]
    s = sum(x)
    if s == 0:
        continue
    x = [xi / s for xi in x]
    a = exact_lambda(g, x)
    va = a.verify()
    b = lambda_by_full_enumeration(g, x)
    if a.value != b or not (va["primal_feasible"] and va["dual_feasible"] and va["match"]):
        bad += 1
        print("  LP MISMATCH %s x=%s cut=%s full=%s %s" % (g.graph6(), x, a.value, b, va))
check("cutting-plane LP == full-enumeration LP (30 random weighted graphs)", bad, 0)

# Lambda <= psi always
bad = 0
for trial in range(20):
    n = rng.randint(5, 8)
    g = random_maximal_triangle_free(n, rng)
    x = [Fraction(rng.randint(1, 5)) for _ in range(n)]
    s = sum(x)
    x = [xi / s for xi in x]
    lam = exact_lambda(g, x).value
    ps, _ = exact_psi(g, x)
    if lam > ps:
        bad += 1
        print("  Lambda > psi !!", g.graph6(), x, lam, ps)
check("Lambda <= psi (20 random weighted graphs)", bad, 0)

print()
print("FAILURES:", FAIL if FAIL else "none")
