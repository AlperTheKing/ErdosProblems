"""S1: exact sanity checks for the extremal-induction lens on Erdos #23.
All arithmetic exact (ints / fractions). Brute-force maxcut over all 2^N cuts (numpy, chunked).
Also usable as a library: maxcut_exact, beta, c5_blowup, ck_blowup, is_triangle_free, induced_subgraph.
"""
import numpy as np
from fractions import Fraction
import sys

def maxcut_exact(n, edges):
    """Exact maxcut by enumerating all 2^n masks, chunked. Returns int."""
    assert n <= 26
    best = 0
    E = list(edges)
    total = 1 << n
    chunk = 1 << 20
    for start in range(0, total, chunk):
        m = np.arange(start, min(start + chunk, total), dtype=np.uint32)
        cut = np.zeros(m.shape, dtype=np.uint16)
        for (i, j) in E:
            bi = (m >> np.uint32(i)) & np.uint32(1)
            bj = (m >> np.uint32(j)) & np.uint32(1)
            cut += (bi ^ bj).astype(np.uint16)
        b = int(cut.max())
        if b > best:
            best = b
    return best

def beta(n, edges):
    return len(edges) - maxcut_exact(n, edges)

def is_triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for i, j in edges:
        adj[i].add(j); adj[j].add(i)
    for i, j in edges:
        if adj[i] & adj[j]:
            return False
    return True

def induced_subgraph(n, edges, keep):
    keep = sorted(keep)
    pos = {v: i for i, v in enumerate(keep)}
    E2 = [(pos[i], pos[j]) for (i, j) in edges if i in pos and j in pos]
    return len(keep), E2

def petersen():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))
        E.append((5 + i, 5 + (i + 2) % 5))
        E.append((i, i + 5))
    return 10, E

def ck_blowup(k, sizes):
    n = sum(sizes)
    idx = []
    s = 0
    for t in sizes:
        idx.append(list(range(s, s + t))); s += t
    E = []
    for c in range(k):
        for u in idx[c]:
            for v in idx[(c + 1) % k]:
                E.append((u, v))
    return n, E

def c5_blowup(sizes):
    return ck_blowup(5, list(sizes))

def main():
    ok = True
    n, E = petersen()
    assert is_triangle_free(n, E)
    mc = maxcut_exact(n, E)
    b = len(E) - mc
    print(f"Petersen: N={n} e={len(E)} maxcut={mc} beta={b} budget=N^2/25={Fraction(n*n,25)}")
    ok &= (len(E) == 15 and mc == 12 and b == 3 and Fraction(b) <= Fraction(n * n, 25))

    for t in range(1, 5):
        n, E = c5_blowup([t] * 5)
        assert is_triangle_free(n, E)
        b = beta(n, E)
        tight = (Fraction(b) == Fraction(n * n, 25))
        print(f"C5[{t}] balanced: N={n} e={len(E)} beta={b} vs N^2/25={Fraction(n*n,25)} TIGHT={tight}")
        ok &= tight and b == t * t

    for sizes in [(3, 2, 2, 2, 2), (4, 1, 2, 3, 2), (1, 1, 1, 1, 4), (2, 4, 2, 4, 2), (5, 1, 1, 1, 1)]:
        n, E = c5_blowup(list(sizes))
        b = beta(n, E)
        pred = min(sizes[i] * sizes[(i + 1) % 5] for i in range(5))
        print(f"C5{sizes}: N={n} beta={b} min-consec-product={pred} match={b==pred} <=(N/5)^2={Fraction(b)<=Fraction(n*n,25)}")
        ok &= (b == pred) and Fraction(b) <= Fraction(n * n, 25)

    for k, sizes in [(7, [1] * 7), (7, [2] * 7)]:
        n, E = ck_blowup(k, sizes)
        assert is_triangle_free(n, E)
        b = beta(n, E)
        print(f"C7 blowup sizes={sizes}: N={n} beta={b} vs N^2/25={Fraction(n*n,25)} holds={Fraction(b)<=Fraction(n*n,25)}")
        ok &= Fraction(b) <= Fraction(n * n, 25)

    print("S1 ALL OK" if ok else "S1 FAILURE")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
