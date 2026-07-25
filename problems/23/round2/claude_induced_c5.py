"""CORRECTION CHECK: does an induced C5 force max_x psi(H,x) >= 1/25 ?

Claim (elementary). If x is supported on S subset V(H), then for any cut (A,B) of H only the
monochromatic edges inside S contribute to sum_{uv mono} x_u x_v; and as the cut ranges over all
cuts of H its restriction to S ranges over ALL cuts of the induced subgraph H[S], because the
vertices outside S may be 2-coloured arbitrarily. Hence

        psi(H, x) = psi(H[S], x restricted to S)      for every x supported on S,

and therefore  max_x psi(H,x)  >=  max_y psi(H[S], y)  for every induced subgraph H[S].
Since max_y psi(C5,y) = 1/25 exactly (AM-GM, proved earlier), ANY triangle-free H containing an
INDUCED C5 satisfies max_x psi(H,x) >= 1/25.

If this is right, the psi values I recorded for Wagner (0.038652), Petersen (0.030879),
Grotzsch (0.037700), C13(1,5) (0.035170) and the Andrasfai family are all just poor local optima of
the hill-climb, and the true values are >= 1/25 in every case with odd girth 5. This script checks
the claim numerically and exactly: it finds an induced C5, puts weight 1/5 on each of its vertices,
and evaluates psi exactly over ALL cuts of the ambient graph.
"""

from fractions import Fraction
from itertools import combinations, permutations


def circulant(n, conn):
    E = set()
    for v in range(n):
        for d in conn:
            w = (v + d) % n
            E.add((min(v, w), max(v, w)))
    return n, sorted(E)


def petersen():
    o = [(i, (i + 1) % 5) for i in range(5)]
    s = [(i, 5 + i) for i in range(5)]
    inn = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, sorted({(min(a, b), max(a, b)) for a, b in o + s + inn})


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((10, 5 + i))
    return 11, sorted({(min(a, b), max(a, b)) for a, b in E})


def andrasfai(k):
    n = 3 * k - 1
    conn = [d for d in range(k, 2 * k)]
    return circulant(n, conn)


def adjacency(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj


def find_induced_c5(n, E):
    adj = adjacency(n, E)
    for vs in combinations(range(n), 5):
        # count edges inside; an induced C5 has exactly 5 and is a single cycle
        inside = [(a, b) for a, b in combinations(vs, 2) if b in adj[a]]
        if len(inside) != 5:
            continue
        deg = {v: 0 for v in vs}
        for a, b in inside:
            deg[a] += 1; deg[b] += 1
        if all(d == 2 for d in deg.values()):
            return list(vs)
    return None


def psi_exact_on_support(n, E, support):
    """psi(H, x) for x = 1/5 on `support`, 0 elsewhere; exact, over ALL 2^(n-1) cuts of H."""
    w = Fraction(1, len(support))
    S5 = set(support)
    best = None
    for mask in range(1 << (n - 1)):
        C = (mask << 1) | 1
        tot = Fraction(0)
        for (u, v) in E:
            if u in S5 and v in S5 and ((C >> u) & 1) == ((C >> v) & 1):
                tot += w * w
        if best is None or tot < best:
            best = tot
    return best


PATTERNS = [
    ("Wagner C8(1,4)", circulant(8, [1, 4]), 0.038652),
    ("Petersen", petersen(), 0.030879),
    ("Grotzsch", grotzsch(), 0.037700),
    ("C11(1,3)", circulant(11, [1, 3]), 0.036426),
    ("C13(1,5)", circulant(13, [1, 5]), 0.035170),
    ("And(4)", andrasfai(4), 0.034666),
    ("And(5)", andrasfai(5), 0.032746),
]

print("=" * 96)
print("does each pattern contain an INDUCED C5, and what does putting weight 1/5 on it give?")
print("=" * 96)
print(f"{'pattern':18s} {'n':>3} {'induced C5':>28} {'psi at that x (exact)':>22} {'my old recorded value':>22}")
for name, (n, E), old in PATTERNS:
    c5 = find_induced_c5(n, E)
    if c5 is None:
        print(f"{name:18s} {n:>3} {'NONE FOUND':>28} {'-':>22} {old:>22.6f}")
        continue
    val = psi_exact_on_support(n, E, c5)
    print(f"{name:18s} {n:>3} {str(c5):>28} {str(val) + ' = ' + format(float(val), '.6f'):>22} {old:>22.6f}")

print()
print("=" * 96)
print("""If the middle column reads 1/25 = 0.040000 while the right column is smaller, then every value I
recorded for these patterns was a poor local optimum of the hill-climb, the true maxima are >= 1/25,
and the statement "C5 is the unique maximiser among the patterns tested" is FALSE.""")
