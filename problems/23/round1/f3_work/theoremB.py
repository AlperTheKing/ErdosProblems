"""Exact verification of Theorem B:
      bip(G) <= ( |E| + 4*e0(phi) + 2*e2(phi) ) / 5     for every phi: V -> Z5,
and of its exact scope (min over phi equals n^2 on C5[n] and m^2/5 on K_{m,m}).
Uses Fractions, and brute-force bip over all 2^(N-1) bipartitions.
"""
from fractions import Fraction as F
import itertools, random
from beta import bip_bruteforce, explicit_blowup

def stats(N, E, phi):
    e0 = e2 = 0
    for u, v in E:
        d = (phi[u] - phi[v]) % 5
        if d == 0: e0 += 1
        elif d in (2, 3): e2 += 1
    return e0, e2

def bound(N, E, phi):
    e0, e2 = stats(N, E, phi)
    return F(len(E) + 4 * e0 + 2 * e2, 5)

rng = random.Random(0)
print("--- (1) bip <= bound for random graphs and random phi ---")
bad = 0
for trial in range(150):
    N = rng.randint(4, 9)
    E = [(u, v) for u in range(N) for v in range(u + 1, N) if rng.random() < 0.4]
    if not E: continue
    b = bip_bruteforce(N, E)
    phi = [rng.randrange(5) for _ in range(N)]
    if not (b <= bound(N, E, phi)):
        bad += 1; print("  VIOLATION", N, E, phi, b, bound(N, E, phi))
print("  violations:", bad)

print("--- (2) min over ALL phi of the bound ---")
def minbound(N, E):
    best = None
    for phi in itertools.product(range(5), repeat=N - 1):
        p = (0,) + phi
        v = bound(N, E, p)
        if best is None or v < best: best = v
    return best

C5 = [(0,1),(1,2),(2,3),(3,4),(4,0)]
for n in (1, 2):
    N, E = explicit_blowup(5, C5, [n]*5)
    mb = minbound(N, E); b = bip_bruteforce(N, E)
    print("  C5[%d]: N=%2d |E|=%2d  min bound=%s  bip=%d  N^2/25=%s   tight: %s"
          % (n, N, len(E), mb, b, F(N*N,25), mb == F(N*N,25)))
for m in (2, 3, 4):
    N = 2*m; E = [(i, m+j) for i in range(m) for j in range(m)]
    mb = minbound(N, E); b = bip_bruteforce(N, E)
    print("  K_{%d,%d}: N=%d |E|=%2d  min bound=%s = m^2/5,  bip=%d,  N^2/25=%s  -> mechanism %s"
          % (m, m, N, len(E), mb, b, F(N*N,25), "FAILS" if mb > F(N*N,25) else "ok"))
