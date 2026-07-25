"""Q3 round 7 -- INDEPENDENT exact re-verification of the engine's numbers.

Different language, different algorithms:
  * bip: explicit enumeration over all 2^(n-1) cuts using the edge list and Python ints
         (the engine uses a subset DP over 2^n with incremental weighted neighbour sums).
  * dist: FULL enumeration of all 5^(n-1) colourings, vectorised with numpy int64
         (the engine uses depth-first branch and bound with an admissible bound).
Every arithmetic operation is on exact integers.

usage:
  python Q3_verify.py named            re-verify all named graphs (bip and dist)
  python Q3_verify.py corpus <file>    re-verify bip for every graph in a graph6 file
  python Q3_verify.py one <g6> [w]     one graph, optional comma weights
"""
import sys
import numpy as np
from itertools import combinations


def parse_g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    i = 1
    if n == 63:
        n = (b[1] << 12) | (b[2] << 6) | b[3]
        i = 4
    bits = []
    for x in b[i:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E = []
    p = 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def bip_exact(n, E, w=None):
    """min over cuts of the monochromatic weight; pure python ints, vertex 0 fixed to side A."""
    if w is None:
        w = [1] * n
    best = None
    for T in range(1 << (n - 1)):
        S = (T << 1) | 1
        tot = 0
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += w[u] * w[v]
        if best is None or tot < best:
            best = tot
    return best


def dist_exact(n, E, w=None, chunk=1 << 20):
    """min over all colourings phi:V->Z5 of the weighted edit distance to the blow-up template.
       Full enumeration with phi(0)=0 fixed (rotation), vectorised."""
    if w is None:
        w = [1] * n
    adj = [[False] * n for _ in range(n)]
    for (u, v) in E:
        adj[u][v] = adj[v][u] = True
    total = 5 ** (n - 1)
    best = None
    bestphi = None
    for start in range(0, total, chunk):
        stop = min(start + chunk, total)
        idx = np.arange(start, stop, dtype=np.int64)
        col = np.zeros((stop - start, n), dtype=np.int8)
        t = idx.copy()
        for v in range(1, n):
            col[:, v] = (t % 5).astype(np.int8)
            t //= 5
        cost = np.zeros(stop - start, dtype=np.int64)
        for u in range(n):
            for v in range(u + 1, n):
                d = np.abs(col[:, u].astype(np.int16) - col[:, v].astype(np.int16))
                req = (d == 1) | (d == 4)
                mism = req != adj[u][v]
                cost += mism * (w[u] * w[v])
        k = int(np.argmin(cost))
        if best is None or cost[k] < best:
            best = int(cost[k])
            bestphi = ''.join(str(int(c)) for c in col[k])
    return best, bestphi


def main():
    mode = sys.argv[1]
    if mode == 'named':
        import Q3_named as NM
        for name, (n, E) in NM.NAMED.items():
            if n > 11:
                print('%-10s n=%2d  (skipped: 5^%d colourings too many for the exhaustive check)' % (name, n, n - 1))
                continue
            EE = sorted(set((min(a, b), max(a, b)) for (a, b) in E))
            b = bip_exact(n, EE)
            d, phi = dist_exact(n, EE)
            print('%-10s n=%2d m=%3d bip=%d dist=%d phi=%s   psi=%d/%d  d=%d/%d'
                  % (name, n, len(EE), b, d, phi, b, n * n, d, n * n))
    elif mode == 'corpus':
        path = sys.argv[2]
        hist = {}
        top = []
        with open(path) as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                n, E = parse_g6(s)
                b = bip_exact(n, E)
                hist[b] = hist.get(b, 0) + 1
                if b * 25 >= n * n:
                    top.append((s, n, b))
        print('bip histogram for %s: %s' % (path, sorted(hist.items())))
        print('graphs with 25*bip >= n^2: %s' % top)
    elif mode == 'one':
        s = sys.argv[2]
        n, E = parse_g6(s)
        w = None
        if len(sys.argv) > 3:
            w = [int(t) for t in sys.argv[3].split(',')]
        b = bip_exact(n, E, w)
        d, phi = dist_exact(n, E, w)
        Q = sum(w) if w else n
        print('%s n=%d m=%d Q=%d bip=%d dist=%d phi=%s  psi=%d/%d d=%d/%d'
              % (s, n, len(E), Q, b, d, phi, b, Q * Q, d, Q * Q))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
