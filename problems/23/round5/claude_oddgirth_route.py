"""ROOT-AGENT (Claude): can piece (i) -- pentagon-free triangle-free graphs -- be closed by W/g_odd?

R3-C41's corrected reduction leaves two open pieces, the softer being

        (i) every PENTAGON-FREE triangle-free G has max_x psi <= 1/25.

The natural attack: prove  psi(G,x) <= W(x)/g_odd(G),  W = sum over edges of x_u x_v. That would
SUFFICE, because Motzkin-Straus caps W <= 1/4 on triangle-free graphs, so odd girth >= 7 gives
psi <= 1/28 = 0.0357 < 1/25.

It is attractive because it is TIGHT where it should be: at uniform x on C_g we get W = 1/g and
psi = 1/g^2 = W/g exactly. It also matches my proved R3-C29 lemma at k = 2, where
ARCBOUND(And(2)) <= (k-1)W/(3k-1) = W/5 on C5.

The fractional form is trivial (y = 1/g_odd on every edge covers every odd cycle), so the whole
content is integrality -- which is exactly where this campaign keeps losing. Two witnesses are
already on the record that ought to be checked FIRST:

  * odd girth 5: the N = 14 extremal graph M?AE@bH{AYN_LgBs? has bip = 7 and |E| = 32, and
    32/5 = 6.4 < 7. So the bound is false at g = 5 -- this is registry A5's witness.
  * odd girth 9: twice-subdivided K5 has bip = 4 and |E| = 30, and 30/9 = 3.33 < 4.

If the second holds, the bound dies at HIGH odd girth too and cannot close piece (i).
"""
from fractions import Fraction as F

import numpy as np


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for x in b[1:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def subdivide_twice(n0, E0):
    """replace every edge by a path of length 3; odd cycles map to odd cycles of 3x the length"""
    V = list(range(n0))
    E, nxt = [], n0
    for (u, v) in E0:
        a, b = nxt, nxt + 1
        nxt += 2
        E += [(u, a), (a, b), (b, v)]
    return nxt, [tuple(sorted(e)) for e in E]


def odd_girth(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    best = None
    for s in range(n):
        dist = {s: 0}
        par = {s: None}
        dq = [s]
        while dq:
            u = dq.pop(0)
            for v in A[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    par[v] = u
                    dq.append(v)
                elif dist[v] == dist[u] and v != par[u]:
                    L = dist[u] + dist[v] + 1
                    if L % 2 == 1 and (best is None or L < best):
                        best = L
    return best


def bip_exact(n, E):
    if n > 26:
        return None
    best = None
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    CH = 1 << 20
    total = 1 << (n - 1)
    for s in range(0, total, CH):
        mm = np.arange(s, min(s + CH, total), dtype=np.int64)
        S = (mm << 1) | 1
        mono = np.zeros(len(mm), dtype=np.int32)
        for k in range(len(E)):
            mono += (((S >> int(ue[k])) & 1) == ((S >> int(ve[k])) & 1)).astype(np.int32)
        v = int(mono.min())
        if best is None or v < best:
            best = v
    return best


K5 = [(u, v) for u in range(5) for v in range(u + 1, 5)]
cases = [
    ("C5", 5, [(i, (i + 1) % 5) for i in range(5)]),
    ("C7", 7, [(i, (i + 1) % 7) for i in range(7)]),
    ("C9", 9, [(i, (i + 1) % 9) for i in range(9)]),
    ("Petersen", 10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
     + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]),
    ("N=14 extremal", *g6("M?AE@bH{AYN_LgBs?")),
    ("twice-subdivided K5", *subdivide_twice(5, K5)),
    ("twice-subdivided K4", *subdivide_twice(4, [(u, v) for u in range(4) for v in range(u + 1, 4)])),
]

print(f"{'graph':22s} {'n':>4s} {'|E|':>5s} {'odd girth':>10s} {'bip':>5s} "
      f"{'|E|/g':>9s} {'bip <= |E|/g ?':>16s}")
for name, n, E in cases:
    E = [tuple(sorted(e)) for e in E]
    g = odd_girth(n, E)
    b = bip_exact(n, E)
    if b is None or g is None:
        print(f"{name:22s} {n:4d} {len(E):5d} {str(g):>10s} {'-':>5s} {'-':>9s} {'skipped':>16s}")
        continue
    r = F(len(E), g)
    ok = F(b) <= r
    print(f"{name:22s} {n:4d} {len(E):5d} {g:10d} {b:5d} {str(r):>9s} "
          f"{('holds' if ok else 'VIOLATED'):>16s}")
    if not ok:
        print(f"      psi at uniform = {F(b, n*n)} = {float(F(b, n*n)):.6f}, "
              f"W/g = {F(len(E), n*n*g)} = {float(F(len(E), n*n*g)):.6f}, "
              f"and 1/25 = 0.04  -> conjecture itself safe: {F(b, n*n) <= F(1,25)}")

print("\nIf the bound fails at odd girth 9, then psi <= W/g_odd cannot close piece (i), and the")
print("pentagon-free case needs a different mechanism -- the same subdivision phenomenon that")
print("registry A28 used to kill gap quantification.")
