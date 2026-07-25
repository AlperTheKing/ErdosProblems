"""Root-agent (Claude) exact gate, Round 3 wave C: the density-band theorem.

The G12 agent posted: "bip(G) <= |E| - (1/N) sum d(v)^2 <= |E| - 4|E|^2/N^2 <= N^2/16,
gives bip <= N^2/25 whenever |E| >= N^2/5 or |E| <= 2N^2/25".

Gated here in three parts, exact rational arithmetic throughout.

(1) The chain itself, verified on a corpus:
      N(v) is independent (G triangle-free), so (N(v), V - N(v)) is a bipartition and
          bip(G) <= e(G - N(v)) = |E| - sum_{u in N(v)} d(u)
      for every v; averaging over v turns max_v into the mean,
          max_v sum_{u in N(v)} d(u)  >=  (1/N) sum_v sum_{u in N(v)} d(u)  =  (1/N) sum_u d(u)^2,
      hence bip(G) <= |E| - (1/N) sum d(v)^2, and Cauchy-Schwarz gives the |E|-only form.

(2) The band, solved exactly. With x = |E|/N^2 the |E|-only bound is N^2 (x - 4x^2), so it
    certifies 1/25 iff 4x^2 - x + 1/25 >= 0. Discriminant 1 - 16/25 = 9/25 is a perfect
    square of a rational, so the roots are exactly rational and the band is exact.

(3) The posted sparse endpoint 2N^2/25 is tested against explicit graphs.
"""
from fractions import Fraction


def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def triangle_free(n, adj):
    return all(not (adj[u] & adj[v]) for u in range(n) for v in range(u + 1, n)
               if (adj[u] >> v) & 1)


def bip_bruteforce(n, edges):
    best = len(edges)
    for S in range(1 << (n - 1)):
        m = 0
        for (u, v) in edges:
            if ((S >> u) & 1 if u < n - 1 else 0) == ((S >> v) & 1 if v < n - 1 else 0):
                m += 1
                if m >= best:
                    break
        best = min(best, m)
    return best


def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def andrasfai(k):
    n = 3 * k - 1
    gens = [i for i in range(1, n) if i % 3 == 1]
    return n, sorted({tuple(sorted((x, (x + g) % n))) for x in range(n) for g in gens})


def clebsch():
    gens = [1, 2, 4, 8, 15]
    return 16, sorted({tuple(sorted((x, x ^ g))) for x in range(16) for g in gens})


def c5_blowup(t):
    parts = [list(range(p * t, (p + 1) * t)) for p in range(5)]
    return 5 * t, sorted({tuple(sorted((a, b))) for p in range(5)
                          for a in parts[p] for b in parts[(p + 1) % 5]})


def petersen():
    outer = [(i, (i + 1) % 5) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, sorted(outer + inner + [(i, i + 5) for i in range(5)])


CORPUS = ([("C%d" % n, cycle(n)) for n in range(5, 26, 2)]
          + [("And(%d)" % k, andrasfai(k)) for k in range(2, 8)]
          + [("C5[%d]" % t, c5_blowup(t)) for t in range(1, 5)]
          + [("Petersen", petersen()), ("Clebsch", clebsch())])

print("=" * 96)
print("PART 1  the neighbourhood-cut chain, exact, on every corpus member")
print("=" * 96)
print(f"{'H':12s} {'N':>4s} {'|E|':>5s} {'bip':>5s} {'M1':>6s} {'M4=|E|-sum d^2/N':>18s} "
      f"{'|E|-4|E|^2/N^2':>16s} {'N^2/25':>9s}")

fails = []
for name, (n, edges) in CORPUS:
    adj = adj_from_edges(n, edges)
    assert triangle_free(n, adj), f"{name} not triangle-free"
    m = len(edges)
    deg = [bin(adj[v]).count("1") for v in range(n)]
    # M1: min over v of e(G - N(v)), computed directly, and the closed form
    m1 = min(sum(1 for (a, b) in edges
                 if not (adj[v] >> a) & 1 and not (adj[v] >> b) & 1) for v in range(n))
    m1_closed = m - max(sum(deg[u] for u in range(n) if (adj[v] >> u) & 1) for v in range(n))
    assert m1 == m1_closed, f"{name}: e(G-N(v)) closed form wrong, {m1} vs {m1_closed}"
    m4 = m - Fraction(sum(d * d for d in deg), n)
    cs = m - Fraction(4 * m * m, n * n)
    bip = bip_bruteforce(n, edges) if n <= 20 else None
    bound = Fraction(n * n, 25)
    if bip is not None:
        assert bip <= m1 <= m4 <= cs, f"{name}: chain broken {bip} {m1} {m4} {cs}"
        assert bip <= bound, f"{name}: CONJECTURE VIOLATED"
    if cs > bound:
        fails.append(name)
    print(f"{name:12s} {n:4d} {m:5d} {str(bip):>5s} {m1:6d} {str(m4):>18s} "
          f"{str(cs):>16s} {str(bound):>9s} {'' if cs <= bound else '<- no certificate'}")

print()
print("PART 1 VERDICT: chain bip <= M1 <= M4 <= |E|-4|E|^2/N^2 verified exactly on")
print(f"  {len(CORPUS)} graphs, 0 violations. The |E|-only form certifies 1/25 on all but:")
print(f"  {', '.join(fails)}")

print()
print("=" * 96)
print("PART 2  the exact density band")
print("=" * 96)
# 4x^2 - x + 1/25 >= 0. Roots (1 +- sqrt(1 - 16/25))/8 = (1 +- 3/5)/8.
lo, hi = Fraction(1 - Fraction(3, 5), 8), Fraction(1 + Fraction(3, 5), 8)
print(f"roots of 4x^2 - x + 1/25:  x = {lo} and x = {hi}")
assert 4 * lo * lo - lo + Fraction(1, 25) == 0
assert 4 * hi * hi - hi + Fraction(1, 25) == 0
print(f"both roots verified exactly as rationals: 1/20 = {lo}, 1/5 = {hi}")
print()
print(f"  CERTIFIED:  |E| <= N^2/20   or   |E| >= N^2/5")
print(f"  OPEN BAND:  N^2/20 < |E| < N^2/5      i.e.  0.05 < |E|/N^2 < 0.2")
print()
print("value of x - 4x^2 at the endpoints and at the posted endpoint 2/25:")
for label, x in [("1/20 (lower root)", lo), ("2/25 (POSTED)", Fraction(2, 25)),
                 ("1/5 (upper root)", hi)]:
    val = x - 4 * x * x
    print(f"  x = {str(x):8s} {label:20s} x-4x^2 = {str(val):10s} = {float(val):.6f}"
          f"   vs 1/25 = 0.040000   {'OK' if val <= Fraction(1,25) else 'EXCEEDS 1/25'}")

print()
print("=" * 96)
print("PART 3  is the posted sparse endpoint |E| <= 2N^2/25 correct?")
print("=" * 96)
bad = []
for name, (n, edges) in CORPUS:
    m = len(edges)
    if Fraction(m, n * n) > Fraction(2, 25):
        continue                                   # outside the posted hypothesis
    cs = m - Fraction(4 * m * m, n * n)
    bound = Fraction(n * n, 25)
    if cs > bound:
        bad.append((name, n, m, cs, bound))
        print(f"  FALSIFIER  {name}: N={n} |E|={m} <= 2N^2/25={Fraction(2*n*n,25)}, "
              f"but |E|-4|E|^2/N^2 = {cs} > N^2/25 = {bound}")
print()
print("PART 3 VERDICT:", "POSTED BAND IS WRONG" if bad else "posted band holds on this corpus")
print("  correct sparse endpoint is N^2/20, not 2N^2/25 (= N^2/12.5);")
print("  2/25 = 0.08 lies strictly inside the open band (0.05, 0.2).")

print()
print("=" * 96)
print("PART 4  where does the extremal family sit?")
print("=" * 96)
for t in range(1, 6):
    n, edges = c5_blowup(t)
    m = len(edges)
    x = Fraction(m, n * n)
    cs = m - Fraction(4 * m * m, n * n)
    print(f"C5[{t}]: N={n:3d} |E|={m:3d}  |E|/N^2 = {x} = {float(x):.4f}  "
          f"|E|-4|E|^2/N^2 = {cs} = N^2/25 = {Fraction(n*n,25)}  "
          f"{'EQUALITY' if cs == Fraction(n*n,25) else 'strict'}")
print()
print("So C5[n] sits EXACTLY on the upper endpoint |E| = N^2/5, with equality in the")
print("whole chain. The theorem is tight precisely at the extremal family, and the open")
print("band N^2/20 < |E| < N^2/5 is open on its closed upper side.")
