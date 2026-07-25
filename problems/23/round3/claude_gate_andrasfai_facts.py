"""ROOT-AGENT GATE (Claude, round 3): the Andrasfai family, and a check of the min-degree
thresholds quoted in the inherited ledger.

Quoted in round1/CLAUDE_GATE_RESULTS.md section 3b:
    "the known theorem of Jin (triangle-free with min degree > 10N/29 admits a homomorphism to C5)"

That form is refutable by an explicit graph, with no reference to the literature at all:
And(4) is triangle-free, vertex-transitive, has delta = 4 > 10*11/29 = 3.79..., and is NOT
homomorphic to C5, because a homomorphism cannot increase the fractional chromatic number and
        chi_f(And(4)) = n/alpha = 11/4 = 2.75  >  5/2 = chi_f(C5).
(For a vertex-transitive graph chi_f = n/alpha exactly.)

Everything below is exact integer arithmetic: brute-force independence number, brute-force triangle
count, brute-force search for a homomorphism to C5.
"""
from itertools import combinations


def andrasfai(k):
    """And(k): circulant on Z_{3k-1} with connection set the residues = 1 mod 3."""
    m = 3 * k - 1
    S = [s for s in range(1, m) if s % 3 == 1]
    adj = [set() for _ in range(m)]
    for v in range(m):
        for s in S:
            adj[v].add((v + s) % m)
    # symmetry check: the connection set must satisfy S = -S
    assert all(v in adj[w] for w in range(m) for v in adj[w]), "connection set not symmetric"
    for v in range(m):
        assert v not in adj[v]
    return m, adj


def edges(m, adj):
    return sorted({(min(u, v), max(u, v)) for u in range(m) for v in adj[u]})


def ntriangles(m, adj):
    return sum(1 for a, b, c in combinations(range(m), 3)
               if b in adj[a] and c in adj[b] and c in adj[a])


def independence_number(m, adj):
    best = 0
    order = sorted(range(m), key=lambda v: -len(adj[v]))

    def rec(cand, cur):
        nonlocal best
        if cur + len(cand) <= best:
            return
        if not cand:
            best = max(best, cur)
            return
        v = cand[0]
        # branch: take v
        rec([w for w in cand[1:] if w not in adj[v]], cur + 1)
        # branch: drop v
        rec(cand[1:], cur)

    rec(order, 0)
    return best


def hom_to_C5(m, adj):
    """exact backtracking search for a homomorphism to C5 (edges must map to edges)"""
    col = [-1] * m

    def ok(v, c):
        return all(col[w] < 0 or abs(col[w] - c) % 5 in (1, 4) for w in adj[v])

    def rec(v):
        if v == m:
            return True
        lo, hi = (0, 1) if v == 0 else (0, 5)      # fix vertex 0 to colour 0 by symmetry
        for c in range(lo, hi):
            if ok(v, c):
                col[v] = c
                if rec(v + 1):
                    return True
                col[v] = -1
        return False

    return rec(0)


print(f"{'k':>2s} {'n':>3s} {'deg':>4s} {'|E|':>5s} {'tri':>4s} {'alpha':>6s} {'chi_f=n/alpha':>14s} "
      f"{'delta/n':>9s} {'>10/29?':>8s} {'>3/8?':>7s} {'hom->C5':>8s} {'N(v) max ind?':>14s}")
for k in range(2, 9):
    m, adj = andrasfai(k)
    E = edges(m, adj)
    deg = len(adj[0])
    a = independence_number(m, adj)
    nb_is_max_ind = (len(adj[0]) == a) and all(w not in adj[u] for u in adj[0] for w in adj[0])
    h = hom_to_C5(m, adj)
    print(f"{k:2d} {m:3d} {deg:4d} {len(E):5d} {ntriangles(m, adj):4d} {a:6d} "
          f"{str(m) + '/' + str(a):>14s} {deg / m:9.4f} "
          f"{str(deg / m > 10 / 29):>8s} {str(deg / m > 3 / 8):>7s} {str(h):>8s} {str(nb_is_max_ind):>14s}")

print()
m, adj = andrasfai(4)
print("REFUTATION of the quoted Jin form, on And(4):")
print("  n = 11, delta = 4, 10n/29 = %.4f, so delta > 10n/29 holds:" % (10 * 11 / 29),
      4 > 10 * 11 / 29)
print("  triangle-free:", ntriangles(m, adj) == 0)
print("  alpha =", independence_number(m, adj), "-> chi_f = 11/4 = 2.75 > 2.5 = chi_f(C5)")
print("  exhaustive homomorphism search to C5 succeeds:", hom_to_C5(m, adj))
print("  => 'delta > 10n/29 implies hom to C5' is FALSE.  The correct Jin 1995 statement is")
print("     3-COLOURABILITY, not a C5-homomorphism; the C5-homomorphism threshold is Haggkvist's")
print("     delta > 3n/8, which And(3) = Wagner (delta/n = 3/8 exactly) shows is best possible.")
