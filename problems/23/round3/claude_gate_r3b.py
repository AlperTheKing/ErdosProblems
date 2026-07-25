"""Root-agent (Claude) exact gate, Round 3 wave B.

Two independent checks, exact integer arithmetic only, no floats on any
acceptance path, nothing imported from the agents' own modules.

GATE 1  Kill the independent-set covering ceiling.
        For every independent set I, putting I on one side and V-I on the
        other shows  bip(G) <= e(G - I),  so  M2(G) := min_I e(G - I)  is an
        upper bound for bip.  The G12 agent reports M2 exceeding N^2/25 on
        the Clebsch graph.  If true, no mechanism of the form "delete an
        independent set / a neighbourhood / a BFS layer" can ever prove the
        conjecture.  Verified here from graphs I construct myself.

GATE 2  Audit the G10 named corpus for triangles.
        G10_named.txt is consumed as a corpus of triangle-free graphs.  Any
        entry containing a triangle voids every conclusion drawn from it.
"""
from fractions import Fraction
from itertools import combinations


# ---------------------------------------------------------------- graph basics

def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        assert u != v, "loop"
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def triangles(n, adj):
    """Return a triangle as a sorted tuple, or None."""
    for u in range(n):
        for v in range(u + 1, n):
            if not (adj[u] >> v) & 1:
                continue
            common = adj[u] & adj[v]
            if common:
                w = (common & -common).bit_length() - 1
                return (u, v, w)
    return None


def independent_sets(n, adj):
    """Every independent set, as a bitmask. Exhaustive, 2^n."""
    for S in range(1 << n):
        T, ok = S, True
        while T:
            v = (T & -T).bit_length() - 1
            if adj[v] & S:
                ok = False
                break
            T &= T - 1
        if ok:
            yield S


def edges_outside(edges, S):
    return sum(1 for (u, v) in edges if not (S >> u) & 1 and not (S >> v) & 1)


def bip_bruteforce(n, edges):
    """min over bipartitions of the number of monochromatic edges."""
    best = len(edges)
    for S in range(1 << (n - 1)):          # vertex n-1 pinned to side 0
        m = 0
        for (u, v) in edges:
            if ((S >> u) & 1 if u < n - 1 else 0) == ((S >> v) & 1 if v < n - 1 else 0):
                m += 1
                if m >= best:
                    break
        best = min(best, m)
    return best


# ------------------------------------------------------------- my own builders

def clebsch():
    """Clebsch graph = Cayley graph on (F_2)^4 with S = {e1,e2,e3,e4,1111}.
    16 vertices, 5-regular, triangle-free."""
    gens = [1, 2, 4, 8, 15]
    edges = sorted({tuple(sorted((x, x ^ g))) for x in range(16) for g in gens})
    return 16, edges


def andrasfai(k):
    """And(k) = circulant on Z_{3k-1} with connection set {i : i = 1 mod 3}.
    And(2) = C5, And(3) = Wagner."""
    n = 3 * k - 1
    gens = [i for i in range(1, n) if i % 3 == 1]
    edges = sorted({tuple(sorted((x, (x + g) % n))) for x in range(n) for g in gens})
    return n, edges


def c5_blowup(t):
    parts = [[5 * 0 + i for i in range(t)]] * 0  # placeholder, built below
    parts = [list(range(p * t, (p + 1) * t)) for p in range(5)]
    edges = []
    for p in range(5):
        for a in parts[p]:
            for b in parts[(p + 1) % 5]:
                edges.append(tuple(sorted((a, b))))
    return 5 * t, sorted(set(edges))


# ------------------------------------------------------------------ GATE 1

print("=" * 78)
print("GATE 1  independent-set covering ceiling  M2(G) = min_I e(G-I)  vs  N^2/25")
print("=" * 78)

cases = [("Clebsch(folded 5-cube)", clebsch()),
         ("And(5)", andrasfai(5)),
         ("And(4)", andrasfai(4)),
         ("And(3)=Wagner", andrasfai(3)),
         ("And(2)=C5", andrasfai(2)),
         ("C5[2]", c5_blowup(2)),
         ("C5[3]", c5_blowup(3))]

verdicts = []
for name, (n, edges) in cases:
    tri = triangles(n, adj_from_edges(n, edges))
    adj = adj_from_edges(n, edges)
    m2 = min(edges_outside(edges, S) for S in independent_sets(n, adj))
    alpha = max(bin(S).count("1") for S in independent_sets(n, adj))
    bound = Fraction(n * n, 25)
    bip = bip_bruteforce(n, edges) if n <= 20 else None
    breaks = m2 > bound
    verdicts.append((name, breaks))
    print(f"{name:24s} N={n:3d} |E|={len(edges):4d} alpha={alpha:2d} "
          f"triangle={tri}  bip={bip}  M2={m2}  N^2/25={bound} "
          f"({float(bound):.4f})  {'BREAKS' if breaks else 'ok'}")
    assert tri is None, f"{name} is NOT triangle-free: {tri}"
    if bip is not None:
        assert bip <= m2, f"{name}: bip {bip} > M2 {m2}, the bound direction is wrong"
        assert bip <= bound, f"{name}: CONJECTURE VIOLATED, bip {bip} > {bound}"

killed = [n for n, b in verdicts if b]
print()
print("GATE 1 VERDICT:", "REFUTED on " + ", ".join(killed) if killed else "not refuted")
print("  (bip <= M2 held everywhere, and bip <= N^2/25 held everywhere:")
print("   the mechanism is dead, the conjecture is untouched.)")

# ------------------------------------------------------------------ GATE 2

print()
print("=" * 78)
print("GATE 2  triangle audit of the G10 named corpus")
print("=" * 78)

bad, total = [], 0
with open("G10_named.txt") as fh:
    for line in fh:
        parts = line.split()
        if not parts:
            continue
        name, n, m = parts[0], int(parts[1]), int(parts[2])
        flat = [int(x) for x in parts[3:]]
        assert len(flat) == 2 * m, f"{name}: declared {m} edges, got {len(flat) // 2}"
        edges = list(zip(flat[0::2], flat[1::2]))
        total += 1
        tri = triangles(n, adj_from_edges(n, edges))
        if tri is not None:
            bad.append((name, n, m, tri))

print(f"corpus entries: {total}")
print(f"entries WITH a triangle: {len(bad)}")
for name, n, m, tri in bad:
    print(f"  CONTAMINATED  {name}  N={n} |E|={m}  triangle {tri}")
print()
print("GATE 2 VERDICT:", "CORPUS CONTAMINATED" if bad else "all entries triangle-free")
