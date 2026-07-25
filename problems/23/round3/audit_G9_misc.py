"""audit_G9_misc.py -- independent checks of the remaining G9 claims:
  (a) the N=12,13,14 "extremal" table (graph6 decode, triangle-freeness, exact bip,
      degrees, per-vertex drops, Theorem A tightness);
  (b) Theorem B: L(N) = 2(floor(N^2/25)+1-floor((N-1)^2/25)) vs floor((4N-2)/25)+1;
  (c) the C5[n] baseline and the N[v]-peeling failure;
  (d) the "ceiling search" over C5 blow-ups (including ZERO part sizes, which the
      target's search excluded);
  (e) Theorem A corollaries as exact rational statements.
All exact.
"""
from fractions import Fraction
from itertools import product
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G9_core import (g6_decode, deg_list, edge_list, triangle_free,
                           maximal_triangle_free, bip_exhaustive, delete_vertex,
                           masks_of, C5, blowup_bip_exact)

print("=== (a) extremal graphs quoted in G9.md ===")
tbl = {"K?ABBBwerwBw": (12, 25, 5, 3, 1),
       "K?BD@g]Qvo^?": (12, 25, 5, 4, 1),
       "L??ED@_~?~^_Fw": (13, 30, 6, 4, 2),
       "M?AE@bH{AYN_LgBs?": (14, 32, 7, 4, 1)}
for g6, (eN, em, eb, ed, edrop) in tbl.items():
    n, M = g6_decode(g6)
    m = len(edge_list(n, M))
    deg = deg_list(n, M)
    b = bip_exhaustive(n, M)
    drops = []
    for v in range(n):
        n2, M2 = delete_vertex(n, M, v)
        drops.append(b - bip_exhaustive(n2, M2))
    volmax = max(sum(deg[w] for w in range(n) if M[v][w]) for v in range(n))
    print("%-20s N=%d m=%d bip=%d delta=%d mindrop=%d  tf=%s maxtf=%s  "
          "ThmA: %d <= %d-%d=%d (%s, tight=%s)  N^2/25=%s  25*bip<=N^2? %s"
          % (g6, n, m, b, min(deg), min(drops), triangle_free(n, M),
             maximal_triangle_free(n, M), b, m, volmax, m - volmax,
             b <= m - volmax, b == m - volmax, Fraction(n * n, 25), 25 * b <= n * n))
    print("     claimed (N,m,bip,delta,mindrop) = %s ; got %s ; MATCH=%s"
          % ((eN, em, eb, ed, edrop), (n, m, b, min(deg), min(drops)),
             (n, m, b, min(deg), min(drops)) == (eN, em, eb, ed, edrop)))
    print("     degrees=%s  drops=%s  delta>(4N-2)/25? %s  floor(delta/2)=%d  budget=%s"
          % (deg, drops, min(deg) > Fraction(4 * n - 2, 25), min(deg) // 2,
             Fraction(2 * n - 1, 25)))

print()
print("=== (b) Theorem B: L(N) vs the recorded bound ===")


def L(N):
    return 2 * (N * N // 25 + 1 - (N - 1) * (N - 1) // 25)


def L0(N):
    return (4 * N - 2) // 25 + 1


gains = {}
bad = []
for N in range(2, 100001):
    g = L(N) - L0(N)
    gains[g] = gains.get(g, 0) + 1
    if g < 0:
        bad.append(N)
print("  gain distribution over 2<=N<=100000:", dict(sorted(gains.items())))
print("  N with L(N) < L0(N):", bad[:10], "count", len(bad))
print("  L(25t) for t=1..8:", [L(25 * t) for t in range(1, 9)],
      " 4N/25+2 =", [4 * t + 2 for t in range(1, 9)])
print("  L(N) - 4N/25 asymptotics: L(N) <= 4N/25 + 4 for all N<=100000?",
      all(25 * L(N) <= 4 * N + 100 for N in range(2, 100001)))
# is L(N) ever >= 2 + 4N/25 + something growing?  check L(N)*25 - 4N
mx = max(25 * L(N) - 4 * N for N in range(2, 100001))
mn = min(25 * L(N) - 4 * N for N in range(2, 100001))
print("  min/max of 25*L(N) - 4N over 2<=N<=100000: %d / %d  (so L(N) = 4N/25 + O(1))" % (mn, mx))

print()
print("=== (c) C5[n] baseline and N[v]-peeling ===")
for nn in range(1, 9):
    a = [nn] * 5
    N = 5 * nn
    b = blowup_bip_exact(5, C5, a)
    b1 = blowup_bip_exact(5, C5, [nn - 1, nn, nn, nn, nn])
    peel = blowup_bip_exact(5, C5, [nn - 1, 0, nn, nn, 0])
    k = 2 * nn + 1
    print("  n=%d N=%d bip=%d (=n^2? %s) drop_1v=%d floor(d/2)=%d budget=%s | "
          "N[v]-peel: bip(G-N[v])=%d drop=%d budget=%s fires=%s"
          % (nn, N, b, b == nn * nn, b - b1, nn, Fraction(2 * N - 1, 25), peel, b - peel,
             Fraction(N * N - (N - k) ** 2, 25), b - peel <= Fraction(N * N - (N - k) ** 2, 25)))

print()
print("=== (d) ceiling search over ALL C5 blow-ups with N<=60, zero parts INCLUDED ===")


def defeats(a):
    N = sum(a)
    if N == 0:
        return False
    b = blowup_bip_exact(5, C5, a)
    bud = Fraction(2 * N - 1, 25)
    for i in range(5):
        if a[i] == 0:
            continue
        a2 = list(a); a2[i] -= 1
        if b - blowup_bip_exact(5, C5, a2) <= bud:
            return False
    return True


def delta_of(a):
    return min(a[(i - 1) % 5] + a[(i + 1) % 5] for i in range(5) if a[i] > 0)


best = None
nzero_defeat = 0
LIM = 60
for a0 in range(0, LIM + 1):
    for a1 in range(0, LIM + 1 - a0):
        for a2 in range(0, LIM + 1 - a0 - a1):
            for a3 in range(0, LIM + 1 - a0 - a1 - a2):
                for a4 in range(0, LIM + 1 - a0 - a1 - a2 - a3):
                    a = (a0, a1, a2, a3, a4)
                    if sum(a) == 0:
                        continue
                    if min(a) == 0:
                        # blow-up with a zero part = blow-up of P4 -> bipartite -> bip=0
                        if defeats(a):
                            nzero_defeat += 1
                        continue
                    r = Fraction(delta_of(a), sum(a))
                    if best is not None and r > best[0]:
                        continue
                    if defeats(a):
                        if best is None or r < best[0]:
                            best = (r, [a])
                        elif r == best[0]:
                            best[1].append(a)
print("  blow-ups with a ZERO part that defeat the single-vertex mechanism:", nzero_defeat)
print("  smallest delta/N among defeating blow-ups, N<=60: ratio=%s = %s"
      % (best[0], float(best[0])))
print("  attaining part vectors (first 10):", best[1][:10])
print("  4/25 =", Fraction(4, 25))

print()
print("=== (e) Theorem A corollaries as exact statements ===")
print("  mu - 4mu^2 <= 1/25  <=>  4mu^2 - mu + 1/25 >= 0  <=> mu<=1/20 or mu>=1/5")
for mu in [Fraction(1, 20), Fraction(1, 5), Fraction(2, 25), Fraction(1, 8), Fraction(1, 4)]:
    val = mu - 4 * mu * mu
    print("     mu=%s : mu-4mu^2 = %s  (<=1/25? %s)" % (mu, val, val <= Fraction(1, 25)))
print("  C5[n]: mu = 5n^2/(25n^2) = 1/5, bound = N^2(1/5-4/25) = N^2/25 -> tight")
print("  K_{N/2,N/2}: mu = 1/4, bound = N^2(1/4-1/4) = 0 -> tight")
