"""ROOT-AGENT GATE: exact bip of the Gewirtz graph — the last of the four strongly-regular claims.

The Gewirtz graph is srg(56, 10, 0, 2): take the Steiner system S(3,6,22), fix a point p, and let
the vertices be the 77 - 21 = 56 blocks that avoid p, two blocks adjacent iff they are disjoint.
Triangle-free (lambda = 0), 280 edges, spectrum 10, 2, -4.

Same two-sided recipe as for Hoffman-Singleton and Higman-Sims:
  maxcut <= (n/4)(d - lambda_min) = (56/4)(10+4) = 196  =>  bip >= 280 - 196 = 84,
then exhibit a bipartition with exactly 196 crossing edges, recounted independently.

The S(3,6,22) is rebuilt here from the extended binary Golay code, and re-verified.
"""

import random
from itertools import combinations
from fractions import Fraction


def golay24():
    g = 0
    for e in (11, 9, 7, 6, 5, 1, 0):
        g |= 1 << e

    def mulmod(a, b):
        r = 0
        for i in range(12):
            if (a >> i) & 1:
                r ^= b << i
        while r >> 23:
            hi = r >> 23
            r = (r & ((1 << 23) - 1)) ^ hi
        return r

    out = []
    for m in range(1 << 12):
        c = mulmod(m, g)
        if bin(c).count("1") % 2:
            c |= 1 << 23
        out.append(c)
    return out


code = golay24()
wd = {}
for w in code:
    k = bin(w).count("1")
    wd[k] = wd.get(k, 0) + 1
assert wd == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}, wd
octads = [w for w in code if bin(w).count("1") == 8]
blocks = [frozenset(i for i in range(22) if (w >> i) & 1)
          for w in octads if (w >> 22) & 1 and (w >> 23) & 1]
assert len(blocks) == 77 and all(len(b) == 6 for b in blocks)
tc = {}
for b in blocks:
    for t in combinations(sorted(b), 3):
        tc[t] = tc.get(t, 0) + 1
assert all(tc.get(t, 0) == 1 for t in combinations(range(22), 3))
print("S(3,6,22) rebuilt and re-verified: 77 blocks, every triple covered exactly once")

P = 0                                            # the point to avoid
V = [b for b in blocks if P not in b]
n = len(V)
adj = [0] * n
for i in range(n):
    for j in range(i + 1, n):
        if not (V[i] & V[j]):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
E = [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]
degs = sorted(bin(a).count("1") for a in adj)
tri_free = all(not (adj[u] & adj[v]) for (u, v) in E)

print("=" * 74)
print(f"   vertices {n} (expect 56), edges {len(E)} (expect 280), "
      f"degrees {degs[0]}..{degs[-1]} (expect 10,10), triangle-free {tri_free}")

ok = True
for u in range(n):
    for v in range(n):
        a2 = bin(adj[u] & adj[v]).count("1")
        a_uv = (adj[u] >> v) & 1
        want = (10 if u == v else 0) + 2 * (1 - (1 if u == v else 0) - a_uv)
        if a2 != want:
            ok = False
print(f"   SRG identity A^2 = 10I + 2(J - I - A) holds exactly: {ok}")
print("   => spectrum 10 and the roots of x^2 + 2x - 8 = 0, i.e. 2 and -4; lambda_min = -4")
assert tri_free and ok and n == 56 and len(E) == 280 and degs[0] == degs[-1] == 10

bound = Fraction(n, 4) * (10 + 4)
print(f"   maxcut <= (n/4)(d - lambda_min) = {bound}  =>  bip >= {len(E)} - {bound} = {len(E) - bound}")

rnd = random.Random(20260725)
FULL = (1 << n) - 1
best, bestS = 0, 0
for _ in range(2000):
    S = rnd.getrandbits(n)
    improved = True
    while improved:
        improved = False
        order = list(range(n))
        rnd.shuffle(order)
        for v in order:
            inS = (S >> v) & 1
            nin = bin(adj[v] & S).count("1")
            nout = bin(adj[v] & ~S & FULL).count("1")
            gain = (nin - nout) if inS else (nout - nin)
            if gain > 0:
                S ^= (1 << v)
                improved = True
    val = sum(1 for (u, v) in E if ((S >> u) & 1) != ((S >> v) & 1))
    if val > best:
        best, bestS = val, S
        if best >= int(bound):
            break

recount = sum(1 for (u, v) in E if ((bestS >> u) & 1) != ((bestS >> v) & 1))
side = bin(bestS).count("1")
print(f"   best cut {best}, independent recount {recount}, parts {side}/{n - side}")
print("=" * 74)
if recount == int(bound):
    b = len(E) - recount
    print(f"   RESULT: maxcut(Gewirtz) = {recount}, bip = {b}")
    print(f"   claim bip = 84 : {'CONFIRMED' if b == 84 else 'REFUTED'}")
    print(f"   ratio bip/N^2 = {Fraction(b, n*n)} = {float(Fraction(b, n*n)):.6f}  vs 1/25 = 0.040000")
else:
    print(f"   bounds not met: bip >= {len(E) - bound}, bip <= {len(E) - recount}")
print("=" * 74)
