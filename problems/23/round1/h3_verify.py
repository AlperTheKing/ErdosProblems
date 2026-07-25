"""Independent re-verification of every graph reported by the H3 family.

Deliberately written NOT to share code with h3_engine.cpp: its own graph6 decoder, its own
maximum-cut loop (plain subset enumeration over the 2^(n-1) bipartitions with a from-scratch
recount, no Gray code, no incremental arithmetic), its own triangle test and its own
independence-number routine.  Pure Python ints throughout.

Usage:  python h3_verify.py G6 [G6 ...]     (or graph6 strings on stdin, one per line)
"""
import sys
from itertools import combinations


def decode(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]:
                E.append((i, j))
            p += 1
    return n, E


def maxcut_bruteforce(n, E):
    """No Gray code, no deltas: recount the cut from scratch for every one of the 2^(n-1) sides."""
    best = 0
    for mask in range(1 << (n - 1)):
        side = mask << 1            # vertex 0 always on side 0
        c = 0
        for (u, v) in E:
            if ((side >> u) ^ (side >> v)) & 1:
                c += 1
        if c > best:
            best = c
    return best


def triangle_free(n, E):
    S = set(map(tuple, E))
    for a, b, c in combinations(range(n), 3):
        if (a, b) in S and (a, c) in S and (b, c) in S:
            return False
    return True


def independence_number(n, E):
    nb = [set() for _ in range(n)]
    for u, v in E:
        nb[u].add(v)
        nb[v].add(u)
    best = 0

    def rec(cand, cur):
        nonlocal best
        if len(cur) + len(cand) <= best:
            return
        if not cand:
            best = max(best, len(cur))
            return
        v = max(cand, key=lambda w: len(nb[w] & cand))
        rec(cand - nb[v] - {v}, cur | {v})
        rec(cand - {v}, cur)

    rec(set(range(n)), set())
    return best


def report(s):
    n, E = decode(s)
    m = len(E)
    mc = maxcut_bruteforce(n, E)
    bip = m - mc
    tf = triangle_free(n, E)
    a = independence_number(n, E)
    verdict = "*** VIOLATION ***" if 25 * bip > n * n else "consistent"
    print(f"{s}  n={n} m={m} maxcut={mc} bip={bip} trianglefree={tf} alpha={a} "
          f"25*bip={25*bip} N^2={n*n}  {verdict}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        for s in args:
            report(s)
    else:
        for line in sys.stdin:
            line = line.strip()
            if line:
                report(line.split()[0])
