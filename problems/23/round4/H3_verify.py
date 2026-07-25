"""H3: INDEPENDENT second implementation (pure Python, no pruning, exact integers)
of max_a bip(H[a]) over all integer a >= 0 with sum a = q.  Used to cross-check H3_psi.exe.

Also: exact evaluation of psi at a given rational weight vector, and bip of an explicit
blow-up graph computed twice (cut enumeration on the blow-up itself, and via the
weighted formula) -- the verification demanded for any value above 1/25.
"""
import sys, itertools
from fractions import Fraction


def g6decode(s):
    if ord(s[0]) == 126:
        n = ((ord(s[1]) - 63) << 12) | ((ord(s[2]) - 63) << 6) | (ord(s[3]) - 63)
        p = 4
    else:
        n = ord(s[0]) - 63
        p = 1
    bits = []
    for ch in s[p:]:
        v = ord(ch) - 63
        for b in range(5, -1, -1):
            bits.append((v >> b) & 1)
    E = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                E.append((i, j))
            idx += 1
    return n, E


def bip_weighted(n, E, a):
    """min over all 2^(n-1) cuts of sum_{uv mono} a_u a_v.  Exact."""
    best = None
    for S in range(1 << (n - 1)):
        tot = 0
        for (i, j) in E:
            if ((S >> i) & 1) == ((S >> j) & 1):
                tot += a[i] * a[j]
        if best is None or tot < best:
            best = tot
            if best == 0:
                break
    return best


def compositions(n, q):
    if n == 1:
        yield (q,)
        return
    for t in range(q + 1):
        for rest in compositions(n - 1, q - t):
            yield (t,) + rest


def maxbip(n, E, q):
    best = -1
    arg = None
    for a in compositions(n, q):
        v = bip_weighted(n, E, a)
        if v > best:
            best = v
            arg = a
    return best, arg


def blowup(n, E, a):
    """explicit blow-up graph: vertex v replaced by a[v] twins."""
    off = [0] * (n + 1)
    for v in range(n):
        off[v + 1] = off[v] + a[v]
    N = off[n]
    EE = []
    for (i, j) in E:
        for p in range(off[i], off[i + 1]):
            for r in range(off[j], off[j + 1]):
                EE.append((p, r))
    return N, EE


def bip_explicit(N, EE):
    """bip of an explicit graph by full cut enumeration (N <= ~24)."""
    best = None
    for S in range(1 << (N - 1)):
        tot = 0
        for (i, j) in EE:
            if ((S >> i) & 1) == ((S >> j) & 1):
                tot += 1
        if best is None or tot < best:
            best = tot
    return best


def psi_exact(n, E, x):
    """psi(H,x) for a list x of Fractions summing to 1."""
    best = None
    for S in range(1 << (n - 1)):
        tot = Fraction(0)
        for (i, j) in E:
            if ((S >> i) & 1) == ((S >> j) & 1):
                tot += x[i] * x[j]
        if best is None or tot < best:
            best = tot
    return best


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'max':
        g6, q = sys.argv[2], int(sys.argv[3])
        n, E = g6decode(g6)
        b, a = maxbip(n, E, q)
        print('n=%d m=%d q=%d maxbip=%d 25*maxbip=%d q^2=%d  %s' %
              (n, len(E), q, b, 25 * b, q * q,
               'REFUTES' if 25 * b > q * q else '<=1/25'))
        print('argmax', a)
    elif mode == 'point':
        g6 = sys.argv[2]
        a = [int(t) for t in sys.argv[3].split(',')]
        n, E = g6decode(g6)
        q = sum(a)
        b = bip_weighted(n, E, a)
        print('a=%s q=%d bip=%d psi=%s  vs 1/25=%s' %
              (a, q, b, Fraction(b, q * q), Fraction(1, 25)))
        N, EE = blowup(n, E, a)
        if N <= 24:
            b2 = bip_explicit(N, EE)
            print('explicit blow-up N=%d |E|=%d bip=%d  (agrees: %s)' % (N, len(EE), b2, b2 == b))
