"""H3: third, numpy-vectorised brute force (no pruning at all) for max_a bip(H[a]).
Exact integer arithmetic (int64 throughout, values are far below 2^63).
Independent of both H3_psi.cpp (branch and bound) and H3_verify.py (pure python loops).
"""
import sys
import numpy as np
from H3_verify import g6decode


def all_comps(n, q):
    """all compositions of q into n nonneg parts, as an (K,n) int64 array."""
    out = []
    cur = np.zeros(n, dtype=np.int64)

    def rec(d, r):
        if d == n - 1:
            cur[d] = r
            out.append(cur.copy())
            return
        for t in range(r + 1):
            cur[d] = t
            rec(d + 1, r - t)
        cur[d] = 0
    rec(0, q)
    return np.array(out, dtype=np.int64)


def maxbip(g6, q, chunk=20000):
    n, E = g6decode(g6)
    m = len(E)
    ncut = 1 << (n - 1)
    M = np.zeros((ncut, m), dtype=np.int64)
    S = np.arange(ncut, dtype=np.int64)
    for k, (i, j) in enumerate(E):
        M[:, k] = (((S >> i) & 1) == ((S >> j) & 1)).astype(np.int64)
    A = all_comps(n, q)
    ei = np.array([e[0] for e in E]); ej = np.array([e[1] for e in E])
    best = -1; arg = None
    for s in range(0, len(A), chunk):
        B = A[s:s + chunk]
        P = (B[:, ei] * B[:, ej]).T            # (m, k)
        vals = M @ P                            # (ncut, k)
        mn = vals.min(axis=0)
        t = int(mn.argmax())
        if mn[t] > best:
            best = int(mn[t]); arg = B[t].copy()
    return n, m, best, arg


if __name__ == '__main__':
    g6 = sys.argv[1]; q = int(sys.argv[2])
    n, m, b, a = maxbip(g6, q)
    print('n=%d m=%d q=%d maxbip=%d 25*maxbip=%d q^2=%d  %s' %
          (n, m, q, b, 25 * b, q * q, 'REFUTES' if 25 * b > q * q else '<=1/25'))
    print('argmax', list(a))
