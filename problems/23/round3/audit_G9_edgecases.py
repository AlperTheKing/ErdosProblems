"""audit_G9_edgecases.py -- Theorem A / Theorem B on the cases the G9 census excludes:
disconnected graphs, graphs with isolated vertices, N odd, N not divisible by 5,
and the Clebsch graph (accepted fact 8: bip = 8, N = 16).
Exact integers only.
"""
from fractions import Fraction
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G9_core import (bip_exhaustive, triangle_free, deg_list, edge_list,
                           build_blowup, C5)


def thmA(n, M, name):
    m = len(edge_list(n, M))
    deg = deg_list(n, M)
    volmax = max((sum(deg[w] for w in range(n) if M[v][w]) for v in range(n)), default=0)
    b = bip_exhaustive(n, M)
    strong = b <= m - volmax
    cs = b * n * n <= m * n * n - 4 * m * m if n else True
    print("  %-28s N=%2d m=%3d tf=%s bip=%2d | strong: %d<=%d-%d=%d %s | CS: %s | 25bip<=N^2: %s"
          % (name, n, m, triangle_free(n, M), b, b, m, volmax, m - volmax,
             "OK" if strong else "FAIL", "OK" if cs else "FAIL", 25 * b <= n * n))
    return strong and cs


ok = True
print("=== disconnected / isolated-vertex / odd-N cases ===")
# C5 plus k isolated vertices
for k in range(0, 4):
    n = 5 + k
    M = [[0] * n for _ in range(n)]
    for i in range(5):
        j = (i + 1) % 5
        M[i][j] = M[j][i] = 1
    ok &= thmA(n, M, "C5 + %d isolated" % k)
# two disjoint C5's, and C5 + C7
def cycle(off, L, M):
    for i in range(L):
        a, b = off + i, off + (i + 1) % L
        M[a][b] = M[b][a] = 1
for (L1, L2) in [(5, 5), (5, 7), (5, 4), (7, 7)]:
    n = L1 + L2
    M = [[0] * n for _ in range(n)]
    cycle(0, L1, M); cycle(L1, L2, M)
    ok &= thmA(n, M, "C%d + C%d (disconnected)" % (L1, L2))
# unbalanced C5 blow-ups with a zero part, and with N not divisible by 5
for a in [[3, 0, 2, 4, 1], [1, 2, 3, 4, 5], [2, 2, 2, 2, 1], [6, 1, 1, 1, 1], [0, 0, 3, 4, 0]]:
    n, M, off, part = build_blowup(5, C5, a)
    ok &= thmA(n, M, "C5%s" % a)

print()
print("=== Clebsch graph (folded 5-cube), N=16, accepted bip = 8 ===")
S = [1, 2, 4, 8, 15]
n = 16
M = [[0] * n for _ in range(n)]
for x in range(16):
    for y in range(16):
        if x != y and (x ^ y) in S:
            M[x][y] = 1
deg = deg_list(n, M)
b = bip_exhaustive(n, M)
m = len(edge_list(n, M))
volmax = max(sum(deg[w] for w in range(n) if M[v][w]) for v in range(n))
print("  N=16 m=%d degrees=%s triangle-free=%s  bip=%d (accepted: 8)  N^2/25=%s"
      % (m, sorted(set(deg)), triangle_free(n, M), b, Fraction(256, 25)))
print("  Theorem A: %d <= %d - %d = %d -> %s   (CS form: %d <= %s -> %s)"
      % (b, m, volmax, m - volmax, b <= m - volmax, b,
         Fraction(m * n * n - 4 * m * m, n * n), b * n * n <= m * n * n - 4 * m * m))
ok &= (b == 8) and (b <= m - volmax)

print()
print("ALL EDGE-CASE CHECKS PASSED" if ok else "SOME EDGE-CASE CHECKS FAILED")
