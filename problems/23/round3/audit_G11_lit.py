"""
audit_G11_lit.py -- exhaustive independent tests of the LITERATURE
inequalities that round3/G11.md imports and calls "free" / "usable".

  (1) Norin-Sun Thm 4 restricted to triangle-free G:   m + bip <= n^2/4,
      and the claim that equality forces G = K_{n/2,n/2}.
  (2) EFPS 1988 Theorem 1, second term:   bip <= m - 4m^2/n^2.
  (3) EFPS 1988 Theorem 1, first term:    bip <= m/2 - 2m(2m^2-n^3)/(n^2(n^2-2m)).
  (4) Odd girth of every Vega graph (needed for G11 section 0.2: max psi >= 1/25
      requires an INDUCED C5, i.e. odd girth exactly 5).
  (5) The odd-cycle edge-packing observation of G11 section (f) on C5[2]:
      nu_odd(C5[2]) = bip(C5[2]) = 4.

All over ALL connected triangle-free graphs on n <= 10 vertices from nauty geng
(plus all disconnected ones are covered because both sides are additive/monotone
-- we also run geng without -c for n <= 9 to be safe).

EXACT Fraction arithmetic only.
"""

import subprocess
import sys
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G11_core import (maxcut_bip, triangle_free, adjmasks, popcount,
                            is_bipartite, vega_family, mindeg)

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def g6_decode(line):
    """Own graph6 decoder."""
    s = line.strip()
    if not s:
        return None
    b = [ord(ch) - 63 for ch in s]
    if b[0] == 63:
        raise ValueError("large graph6 not supported")
    n = b[0]
    bits = []
    for x in b[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    E = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]:
                E.append((i, j))
            p += 1
    return n, E


def geng(n, extra=()):
    cmd = [GENG, "-t", "-q", str(n)] + list(extra)
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.strip():
            yield g6_decode(line)


def odd_girth(n, E):
    """Length of the shortest odd cycle (None if bipartite). BFS bipartite-double."""
    adj = [[] for _ in range(n)]
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    best = None
    for s in range(n):
        dist = [[-1, -1] for _ in range(n)]
        dist[s][0] = 0
        q = [(s, 0)]
        head = 0
        while head < len(q):
            x, p = q[head]
            head += 1
            for y in adj[x]:
                if dist[y][1 - p] < 0:
                    dist[y][1 - p] = dist[x][p] + 1
                    q.append((y, 1 - p))
        if dist[s][1] >= 0:
            if best is None or dist[s][1] < best:
                best = dist[s][1]
    return best


def has_induced_C5(n, E):
    adj = adjmasks(n, E)
    for c in combinations(range(n), 5):
        sub = [(a, b) for a, b in combinations(c, 2) if (adj[a] >> b) & 1]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in c}
        for a, b in sub:
            deg[a] += 1
            deg[b] += 1
        if all(d == 2 for d in deg.values()):
            # 5 vertices, 5 edges, all degrees 2 => a single 5-cycle
            return True
    return False


def main():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append((name, detail))
            print("  [FAIL]", name, detail)

    print("=" * 78)
    print("(1)-(3)  exhaustive over triangle-free graphs from geng")
    print("=" * 78)
    worst_ns = None
    worst_efps = None
    ns_eq = []
    for n in range(2, 11):
        cnt = 0
        for n_, E in geng(n):
            cnt += 1
            m = len(E)
            b, mc, _ = maxcut_bip(n_, E)
            # (1) Norin-Sun
            lhs = Fraction(m + b)
            rhs = Fraction(n * n, 4)
            if lhs > rhs:
                check(f"Norin-Sun m+bip<=n^2/4 (n={n})", False, f"E={E} m={m} bip={b}")
            slack = rhs - lhs
            if worst_ns is None or slack < worst_ns[0]:
                worst_ns = (slack, n, m, b, tuple(E))
            if lhs == rhs:
                ns_eq.append((n, m, b, tuple(E)))
            # (2) EFPS second term  bip <= m - 4m^2/n^2
            r2 = Fraction(m) - Fraction(4 * m * m, n * n)
            if Fraction(b) > r2:
                check(f"EFPS Thm1 second term (n={n})", False,
                      f"E={E} m={m} bip={b} bound={r2}")
            s2 = r2 - b
            if worst_efps is None or s2 < worst_efps[0]:
                worst_efps = (s2, n, m, b, tuple(E))
            # (3) EFPS first term  m/2 - 2m(2m^2-n^3)/(n^2(n^2-2m))
            if n * n != 2 * m:
                r1 = (Fraction(m, 2)
                      - Fraction(2 * m * (2 * m * m - n ** 3),
                                 n * n * (n * n - 2 * m)))
                if Fraction(b) > r1 and n * n - 2 * m > 0:
                    check(f"EFPS Thm1 FIRST term (n={n})", False,
                          f"E={E} m={m} bip={b} bound={r1}")
        print(f"  n={n:2d}: {cnt} triangle-free graphs checked")
    print(f"  tightest Norin-Sun slack  n^2/4-(m+bip): {worst_ns}")
    print(f"  tightest EFPS-2 slack     (m-4m^2/n^2)-bip: {worst_efps}")
    print(f"  Norin-Sun EQUALITY cases among triangle-free graphs n<=10: {len(ns_eq)}")
    for e in ns_eq:
        n, m, b, E = e
        print(f"     n={n} m={m} bip={b}  bipartite={is_bipartite(n, list(E))} "
              f"degseq={sorted(popcount(a) for a in adjmasks(n, list(E)))}")

    print()
    print("=" * 78)
    print("(4) odd girth / induced C5 of every Vega graph (G11 section 0.2 relies on it)")
    print("=" * 78)
    for i in range(2, 7):
        for name, (n, E, w, dd, tt) in sorted(vega_family(i).items()):
            og = odd_girth(n, E)
            ic5 = has_induced_C5(n, E) if n <= 26 else None
            print(f"   {name:14s} n={n:3d} odd girth = {og}  induced C5 = {ic5}")
            check(f"{name} has odd girth 5", og == 5, str(og))
            check(f"{name} has an induced C5", ic5 is True)

    print()
    print("=" * 78)
    print("(5) odd-cycle edge packing in C5[2] (G11 section (f) observation)")
    print("=" * 78)
    # C5[2]: parts {0,1},{2,3},{4,5},{6,7},{8,9}
    parts = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    E = []
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i + 1) % 5]:
                E.append((min(a, b), max(a, b)))
    n = 10
    b, mc, m = maxcut_bip(n, E)
    print(f"   C5[2]: n={n} m={m} bip={b}")
    # explicit pentagon decomposition: a_t = alpha_t*s + beta_t*t over GF(2)
    vecs = [(1, 0), (0, 1), (1, 1), (1, 0), (0, 1)]
    pent = []
    for s in range(2):
        for t in range(2):
            cyc = []
            for idx in range(5):
                al, be = vecs[idx]
                cyc.append(parts[idx][(al * s + be * t) % 2])
            pent.append(cyc)
    used = set()
    ok = True
    for cyc in pent:
        for idx in range(5):
            e = (min(cyc[idx], cyc[(idx + 1) % 5]), max(cyc[idx], cyc[(idx + 1) % 5]))
            if e in used or e not in set(E):
                ok = False
            used.add(e)
    print(f"   4 pentagons pairwise edge-disjoint and inside C5[2]: {ok}; "
          f"edges used = {len(used)} of {m}")
    check("nu_odd(C5[2]) >= 4 = bip(C5[2])", ok and b == 4, f"bip={b}")

    print()
    print("=" * 78)
    print(f"TOTAL FAILURES: {len(fails)}")
    for f in fails:
        print("   ", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
