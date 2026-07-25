"""ROOT-AGENT GATE on the weighted-pattern claim.

By the blow-up identity (R1-C7) the conjecture is exactly:  for every triangle-free H,
    max over x >= 0, sum x = 1  of  psi(H,x) := min over cuts S of H of
                                              sum over uv monochromatic of x_u x_v
is at most 1/25.  Round-1 family F8 claimed max_x psi(H,x) = 1/25 for all 573 reduced patterns on
5..15 vertices, attained only by C5 blow-ups.  NO VERIFIER AGENT EVER RAN (session quota), so that
claim is unaccepted.  This is my own independent partial gate.

What is checked here, all with my own code:
  1. psi(C5, uniform) = 1/25 exactly, and max_x psi(C5,x) = 1/25 with a complete proof
     (psi(C5,x) = min_i x_i x_{i+1} <= (prod x_i)^{2/5} <= 5^{-2}, AM-GM twice).
  2. For a list of named triangle-free patterns, max_x psi is estimated by multi-start projected
     local search and the best point is then re-evaluated in EXACT rational arithmetic.
     Any value strictly above 1/25 would be a counterexample to the conjecture and is reported
     loudly; the point of the gate is to see whether the claimed ceiling 1/25 is real.
  3. Sanity: psi(K_{m,m}, x) must be 0 (bipartite), psi(C7, uniform) = 1/49.
"""

from fractions import Fraction
from itertools import combinations
import random


def psi_exact(n, edges, x):
    """min over all 2^(n-1) cuts of sum_{uv monochromatic} x_u x_v, x a list of Fractions."""
    best = None
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        tot = Fraction(0)
        for u, v in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += x[u] * x[v]
        if best is None or tot < best:
            best = tot
    return best


def psi_float(n, edges, x):
    best = None
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        tot = 0.0
        for u, v in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += x[u] * x[v]
        if best is None or tot < best:
            best = tot
    return best


def maximize_psi(n, edges, restarts=40, iters=3000, seed=1):
    """multi-start coordinate hill-climb on the simplex; float search, exact re-check after."""
    rnd = random.Random(seed)
    best_val, best_x = -1.0, None
    for r in range(restarts):
        x = [rnd.random() + 1e-3 for _ in range(n)]
        s = sum(x)
        x = [v / s for v in x]
        cur = psi_float(n, edges, x)
        step = 0.08
        for it in range(iters):
            i = rnd.randrange(n)
            j = rnd.randrange(n)
            if i == j:
                continue
            d = step * rnd.random() * x[i]
            if x[i] - d <= 0:
                continue
            y = list(x)
            y[i] -= d
            y[j] += d
            v = psi_float(n, edges, y)
            if v > cur:
                x, cur = y, v
            if it % 600 == 599:
                step *= 0.6
        if cur > best_val:
            best_val, best_x = cur, x
    return best_val, best_x


def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def complete_bipartite(a, b):
    n = a + b
    return n, [(i, a + j) for i in range(a) for j in range(b)]


def petersen():
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, 5 + i) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner


def grotzsch():
    # Mycielskian of C5: vertices 0..4 (C5), 5..9 (copies), 10 (apex)
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((10, 5 + i))
    return 11, E


def circulant(n, conn):
    E = set()
    for v in range(n):
        for d in conn:
            w = (v + d) % n
            E.add((min(v, w), max(v, w)))
    return n, sorted(E)


def is_triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u, v in edges)


LIMIT = Fraction(1, 25)

print("=" * 74)
print("1. C5 exact")
n, E = cycle(5)
x = [Fraction(1, 5)] * 5
val = psi_exact(n, E, x)
print(f"   psi(C5, uniform) = {val} = 1/{1//val if val else 0}   equals 1/25: {val == LIMIT}")
print("   max_x psi(C5,x) = 1/25 PROVED: psi = min_i x_i x_{i+1} <= (prod x_i)^{2/5} <= 5^-2 (AM-GM twice)")

print()
print("=" * 74)
print("2. named triangle-free patterns: local-search max, then EXACT re-evaluation")
print("=" * 74)
PATTERNS = [
    ("C5", cycle(5)),
    ("C7", cycle(7)),
    ("C9", cycle(9)),
    ("K_{3,3}", complete_bipartite(3, 3)),
    ("K_{4,4}", complete_bipartite(4, 4)),
    ("Petersen", petersen()),
    ("Grotzsch", grotzsch()),
    ("C13(1,5) = (3,5)-Ramsey", circulant(13, [1, 5])),
    ("C11(1,3)", circulant(11, [1, 3])),
    ("Wagner C8(1,4)", circulant(8, [1, 4])),
]
worst = None
for name, (n, E) in PATTERNS:
    tf = is_triangle_free(n, E)
    v, xf = maximize_psi(n, E, restarts=25, iters=2500, seed=7)
    # exact re-evaluation at a rational rounding of the best point
    den = 2520
    xr = [Fraction(max(1, round(t * den)), den) for t in xf]
    s = sum(xr)
    xr = [t / s for t in xr]
    ve = psi_exact(n, E, xr)
    flag = "*** ABOVE 1/25 ***" if ve > LIMIT else ""
    print(f"   {name:26s} n={n:2d} tri-free={str(tf):5s} "
          f"search={v:.6f}  exact_at_best={float(ve):.6f} = {ve}  {flag}")
    if worst is None or ve > worst[1]:
        worst = (name, ve)
print()
print(f"   highest EXACT value found: {worst[0]} at {worst[1]} = {float(worst[1]):.6f}")
print(f"   1/25 = {float(LIMIT):.6f}")
print(f"   any pattern above 1/25 ? {'YES -- COUNTEREXAMPLE' if worst[1] > LIMIT else 'no'}")
print()
print("   NOTE: the local search only gives LOWER bounds on max_x psi, so this gate can refute")
print("   the ceiling but cannot confirm it. It is recorded as a partial, one-sided check.")
