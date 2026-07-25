"""
G7_psi_verify.py -- INDEPENDENT second implementation of

    M(H,q) = max_{a in Z_{>=0}^n, sum a = q} bip(H[a]),
    bip(H[a]) = min over cuts S of sum_{uv monochromatic} a_u a_v.

Written from scratch with a *different* algorithm from G7_psi_search.cpp:
  * cuts are the OUTER loop (all 2^(n-1) monochromatic edge lists precomputed),
  * weightings are enumerated by itertools compositions with NO pruning,
  * min over cuts is taken directly on the monochromatic edge lists
    (no W - maxcut identity, no Gray code, no branch and bound).
Pure Python integers => exact.  Only for small n, q (used as a cross-check).

Also builds the explicit blow-up graph and recomputes bip by a third route
(networkx-free, brute-force over 2^(N-1) cuts of the blow-up) for the
argmax weightings, so a claimed violation would be checked three ways.
"""
import itertools, sys, os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def compositions(q, n):
    """all a in Z_{>=0}^n with sum a = q  (ZEROS ALLOWED)."""
    if n == 1:
        yield (q,)
        return
    for t in range(q + 1):
        for rest in compositions(q - t, n - 1):
            yield (t,) + rest


def mono_lists(n, edges):
    """for every cut S (bit v = side of v), the list of monochromatic edges"""
    out = []
    for S in range(1 << (n - 1)):
        L = [(u, v) for (u, v) in edges if ((S >> u) & 1) == ((S >> v) & 1)]
        out.append(L)
    return out


def bip_weighted(n, monos, a):
    best = None
    for L in monos:
        s = 0
        for (u, v) in L:
            s += a[u] * a[v]
            if best is not None and s >= best:
                break
        if best is None or s < best:
            best = s
    return best


def M_exact(n, edges, q):
    monos = mono_lists(n, edges)
    best, arg = -1, None
    for a in compositions(q, n):
        m = bip_weighted(n, monos, a)
        if m > best:
            best, arg = m, a
    return best, arg


def bip_blowup_bruteforce(n, edges, a):
    """build H[a] explicitly and brute-force its bipartition number"""
    parts, idx = [], 0
    for v in range(n):
        parts.append(list(range(idx, idx + a[v])))
        idx += a[v]
    N = idx
    E = []
    for (u, v) in edges:
        for p in parts[u]:
            for r in parts[v]:
                E.append((p, r))
    if N == 0:
        return 0
    best = None
    for S in range(1 << (N - 1)):
        c = 0
        for (p, r) in E:
            if ((S >> p) & 1) == ((S >> r) & 1):
                c += 1
                if best is not None and c >= best:
                    break
        if best is None or c < best:
            best = c
    return best


C5 = (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])

if __name__ == '__main__':
    print('== C5 calibration (exact, second implementation) ==')
    for q in range(0, 21):
        m, a = M_exact(C5[0], C5[1], q)
        print('  q=%2d  M=%3d  25M=%4d  q^2=%4d  25M/q^2=%s  argmax=%s'
              % (q, m, 25 * m, q * q, Fraction(25 * m, q * q) if q else '-', a))
    print()
    print('== C5: blow-up cross-check (third route, explicit graph) ==')
    for a in [(1, 1, 1, 1, 1), (2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (2, 1, 2, 1, 2),
              (3, 2, 3, 2, 2), (0, 3, 3, 3, 3)]:
        monos = mono_lists(5, C5[1])
        print('  a=%s  psi-route=%d  explicit-blow-up=%d'
              % (str(a), bip_weighted(5, monos, a), bip_blowup_bruteforce(5, C5[1], a)))


# ---------------------------------------------------------------------------
# DEGREE-RESTRICTED variant (independent check of the 'maxdeg' engine mode):
#   maximise bip(H[a]) over a >= 0, sum a = q, subject to 3*(A a)_v > q for all v
#   (this is the exact set of weightings that can arise from a triangle-free G
#    with delta(G) > N/3 via the twin quotient, with q = N).
def M_exact_deg(n, edges, q):
    monos = mono_lists(n, edges)
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v); adj[v].append(u)
    best, arg = -1, None
    for a in compositions(q, n):
        if any(3 * sum(a[u] for u in adj[v]) <= q for v in range(n)):
            continue
        m = bip_weighted(n, monos, a)
        if m > best:
            best, arg = m, a
    return best, arg


def _selftest_deg():
    from fractions import Fraction as F
    print()
    print('== degree-restricted cross-check (independent implementation) ==')
    W = (8, [(0, 3), (0, 4), (0, 5), (1, 4), (1, 5), (1, 6), (2, 5), (2, 6),
             (2, 7), (3, 6), (3, 7), (4, 7)])
    for q in range(5, 21):
        m, a = M_exact(*C5, q)
        md, ad = M_exact_deg(*C5, q)
        print('  C5      q=%2d  M=%3d  Mdeg=%3d  25Mdeg/q^2=%-10s argmax_deg=%s'
              % (q, m, md, F(25 * md, q * q), ad))
    for q in range(8, 21):
        md, ad = M_exact_deg(*W, q)
        print('  Wagner  q=%2d  Mdeg=%3d  25Mdeg/q^2=%-10s argmax_deg=%s'
              % (q, md, F(25 * md, q * q), ad))


if __name__ == '__main__' and '--deg' in sys.argv:
    _selftest_deg()
