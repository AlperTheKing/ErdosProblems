"""Lemma 3 (neighbourhood cut) and its density corollary, verified exhaustively.

Lemma 3.  G triangle-free, v any vertex  =>  bip(G) <= |E| - sum_{u in N(v)} deg(u).
Corollary. bip(G) <= |E| - 4|E|^2/N^2, hence bip(G) <= N^2/25 whenever |E| >= N^2/5 or |E| <= N^2/20
           (the roots of e - 4e^2 = 1/25 are e = 1/20 and e = 1/5), and bip(G) <= N^2/16 always.

Exhaustive check over ALL connected triangle-free graphs on <= 9 vertices via geng -t -c.
"""
import subprocess, os, sys
from fractions import Fraction as F
from beta import g6_decode, bip_bruteforce

GENG = os.environ.get("GENG", r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")

worst_gap = None
bad_lemma = bad_cor = bad_dense = 0
tot = 0
for n in range(3, 10):
    out = subprocess.run([GENG, "-t", "-c", "-q", str(n)], capture_output=True, text=True).stdout.split()
    for L in out:
        nn, E = g6_decode(L, n)
        deg = [0] * n
        adj = [[] for _ in range(n)]
        for u, v in E:
            deg[u] += 1; deg[v] += 1; adj[u].append(v); adj[v].append(u)
        b = bip_bruteforce(n, E) if E else 0
        tot += 1
        # Lemma 3
        best = min(len(E) - sum(deg[u] for u in adj[v]) for v in range(n))
        if b > best:
            bad_lemma += 1
            print("LEMMA3 FAIL", L, b, best)
        # Corollary (exact rational)
        cor = F(len(E)) - F(4 * len(E) ** 2, n * n)
        if F(b) > cor:
            bad_cor += 1
            print("COR FAIL", L, b, cor)
        # density claim
        if 25 * len(E) >= 5 * n * n or 20 * len(E) <= n * n:
            if 25 * b > n * n:
                bad_dense += 1
                print("DENSITY CLAIM FAIL", L, "N=", n, "|E|=", len(E), "bip=", b)
        # N^2/16
        if 16 * b > n * n:
            print("N^2/16 FAIL", L, n, b)
print("graphs checked: %d ; Lemma3 failures: %d ; Corollary failures: %d ; density-claim failures: %d"
      % (tot, bad_lemma, bad_cor, bad_dense))

# tightness at C5[n] and K_{m,m}
print("\ntightness of the corollary  bip <= |E| - 4|E|^2/N^2 :")
for n in (1, 2, 3, 10):
    N, Ee = 5 * n, 5 * n * n
    print("  C5[%d]:  N=%2d |E|=%3d  bound=%s  N^2/25=%s" % (n, N, Ee, F(Ee) - F(4 * Ee ** 2, N * N), F(N * N, 25)))
for m in (2, 5, 10):
    N, Ee = 2 * m, m * m
    print("  K_{%d,%d}: N=%2d |E|=%3d  bound=%s  (true bip=0)" % (m, m, N, Ee, F(Ee) - F(4 * Ee ** 2, N * N)))
