# Exact uniform beta of Andrasfai graphs And_k (n=3k-1, circulant, differences ≡ 1 mod 3)
# to measure whether the reduced-family interior values approach 1/25 = 0.04.
from fractions import Fraction

def andrasfai(k):
    n = 3 * k - 1
    D = set()
    for d in range(1, 3 * k - 1):
        if d % 3 == 1:
            D.add(d)
            D.add(n - d)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) in D]
    return n, edges

def frustration(n, edges):
    nbr = [0] * n
    for u, v in edges:
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u
    full = (1 << n) - 1
    e = len(edges)
    best = None
    for S in range(1 << (n - 1)):
        comp = full & ~S
        cut = 0
        t = S
        while t:
            v = (t & -t).bit_length() - 1
            cut += bin(nbr[v] & comp).count('1')
            t &= t - 1
        mono = e - cut
        if best is None or mono < best:
            best = mono
    return best

for k in (2, 3, 4, 5, 6, 7):
    n, E = andrasfai(k)
    f = frustration(n, E)
    b = Fraction(f, n * n)
    print("And_%d: n=%d e=%d frustration=%d uniform beta=%s = %.6f (1/25=0.04)"
          % (k, n, len(E), f, b, float(b)), flush=True)
