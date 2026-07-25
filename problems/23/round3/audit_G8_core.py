"""AUDIT of G8: independent re-implementation of the basic invariants.

Own data structures: adjacency BITMASKS (not boolean matrices), maxcut by
numpy-vectorised exhaustive enumeration over all 2^n side-vectors, exact
Fraction arithmetic for psi.

Builds And(k) TWO ways and checks they agree:
  (a) circulant on Z_{3k-1} with connection set {i : i = 1 mod 3}      (report's def)
  (b) circular complete K_{p/k}: i~j iff k <= (i-j) mod p <= p-k       (report's claim 1)
and checks the multiplier map v -> k*v mod p is an isomorphism (a)->(b).
"""
import sys
from fractions import Fraction
from itertools import combinations
import numpy as np


def and_circulant(k):
    """(a) circulant Z_{3k-1}, connection {i : i % 3 == 1}."""
    n = 3 * k - 1
    adjm = [0] * n
    for v in range(n):
        for c in range(1, n):
            if c % 3 == 1:
                u = (v + c) % n
                adjm[v] |= 1 << u
                adjm[u] |= 1 << v
    return n, adjm


def and_circular_complete(k):
    """(b) K_{(3k-1)/k}."""
    p = 3 * k - 1
    adjm = [0] * p
    for i in range(p):
        for j in range(p):
            if i == j:
                continue
            d = (i - j) % p
            if k <= d <= p - k:
                adjm[i] |= 1 << j
    return p, adjm


def edges_of(n, adjm):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adjm[u] >> v) & 1]


def is_triangle_free(n, adjm):
    for u in range(n):
        for v in range(u + 1, n):
            if (adjm[u] >> v) & 1:
                if adjm[u] & adjm[v]:
                    return False, (u, v, (adjm[u] & adjm[v]).bit_length() - 1)
    return True, None


def odd_girth(n, adjm):
    """shortest odd closed walk length == shortest odd cycle length; BFS on (v,parity)."""
    from collections import deque
    best = None
    for s in range(n):
        dist = {(s, 0): 0}
        dq = deque([(s, 0)])
        while dq:
            v, p = dq.popleft()
            d = dist[(v, p)]
            m = adjm[v]
            while m:
                b = m & -m
                u = b.bit_length() - 1
                m ^= b
                st = (u, 1 - p)
                if st not in dist:
                    dist[st] = d + 1
                    dq.append(st)
        if (s, 1) in dist and (best is None or dist[(s, 1)] < best):
            best = dist[(s, 1)]
    return best


def alpha(n, adjm):
    """independence number, exact, simple recursion on bitmask of candidates."""
    from functools import lru_cache
    full = (1 << n) - 1

    def rec(cand):
        if cand == 0:
            return 0
        # pick lowest vertex
        b = cand & -cand
        v = b.bit_length() - 1
        # branch: take v, or drop v
        take = 1 + rec(cand & ~(adjm[v] | b))
        drop = rec(cand ^ b)
        return take if take > drop else drop

    sys.setrecursionlimit(10000)
    return rec(full)


def maxcut_exhaustive(n, edges):
    """exact maximum cut by full enumeration over all 2^n side-vectors (numpy)."""
    masks = np.arange(1 << n, dtype=np.uint32)
    bits = [((masks >> u) & 1).astype(np.uint8) for u in range(n)]
    cut = np.zeros(1 << n, dtype=np.int16)
    for (u, v) in edges:
        cut += (bits[u] ^ bits[v]).astype(np.int16)
    mc = int(cut.max())
    arg = int(masks[int(np.argmax(cut))])
    return mc, arg


def all_cut_monos(n, edges):
    """mono-edge lists for all 2^(n-1) cuts (vertex 0 fixed on side 0)."""
    out = []
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        out.append((mask, tuple((u, v) for (u, v) in edges if side[u] == side[v])))
    return out


def psi_exact(monos, x):
    return min(sum(x[u] * x[v] for (u, v) in mono) for _, mono in monos)


if __name__ == "__main__":
    print("k  n  |E|  deg  tri-free  odd-girth  alpha  maxcut  bip  bip/n^2   floor(k^2/4)")
    for k in range(2, 8):
        n, adjm = and_circulant(k)
        p, adjc = and_circular_complete(k)
        assert n == p
        # multiplier isomorphism check
        iso_ok = all(((adjm[u] >> v) & 1) == ((adjc[(k * u) % n] >> ((k * v) % n)) & 1)
                     for u in range(n) for v in range(n) if u != v)
        E = edges_of(n, adjm)
        tf, wit = is_triangle_free(n, adjm)
        og = odd_girth(n, adjm)
        al = alpha(n, adjm)
        deg = set(bin(m).count("1") for m in adjm)
        mc, arg = maxcut_exhaustive(n, E)
        bip = len(E) - mc
        print(f"{k}  {n}  {len(E)}  {sorted(deg)}  {tf}  {og}  {al}  {mc}  {bip}  "
              f"{Fraction(bip, n*n)}  {k*k//4}   iso_to_K_{{{n}/{k}}}={iso_ok}")
        assert iso_ok, k
        assert tf
    print()
    # psi at the uniform point, exact
    for k in range(2, 6):
        n, adjm = and_circulant(k)
        E = edges_of(n, adjm)
        monos = all_cut_monos(n, E)
        x = [Fraction(1, n)] * n
        v = psi_exact(monos, x)
        print(f"And({k}): psi(uniform) = {v} = {float(v):.8f}   (1/25 = 0.04)")
