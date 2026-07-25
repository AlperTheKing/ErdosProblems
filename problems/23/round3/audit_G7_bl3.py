"""
audit_G7_bl3.py -- exact (pure-Python integer / Fraction) verification of the
witnesses that bear on G7.md's BL3 claim

    "BL3 ... is NOT tight: the exhaustive degree-restricted search over all
     q <= 98 gives 25 Psi(Gamma_3,1/3) >= 1925/2116 ~ 0.9097 but nothing
     reaching 1, so BL3 has an apparent margin of about 9%."

A finite-q search bounds Psi from BELOW only.  Here are degree-feasible integer
weightings with a strictly larger ratio, verified from scratch.
"""
from fractions import Fraction as F
import itertools

G3 = (8, [(0, 3), (0, 4), (0, 5), (1, 4), (1, 5), (1, 6),
          (2, 5), (2, 6), (2, 7), (3, 6), (3, 7), (4, 7)])      # C8({3,4}) = Wagner


def bip(n, edges, a):
    """min over ALL 2^(n-1) cuts of the monochromatic weight (exact integers)"""
    best = None
    for S in range(1 << (n - 1)):
        s = 0
        for (u, v) in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                s += a[u] * a[v]
        if best is None or s < best:
            best = s
    return best


def maxcut_check(n, edges, a):
    """independent second route: bip = total weight - maxcut"""
    W = sum(a[u] * a[v] for (u, v) in edges)
    mc = 0
    for S in range(1 << (n - 1)):
        c = sum(a[u] * a[v] for (u, v) in edges if ((S >> u) & 1) != ((S >> v) & 1))
        mc = max(mc, c)
    return W - mc


def degrees(n, edges, a):
    d = [0] * n
    for (u, v) in edges:
        d[u] += a[v]; d[v] += a[u]
    return d


def report(tag, a, n=8, edges=G3[1]):
    q = sum(a)
    d = degrees(n, edges, a)
    ok = all(3 * x > q for x in d)
    b1 = bip(n, edges, a)
    b2 = maxcut_check(n, edges, a)
    r = F(25 * b1, q * q)
    print('%-22s q=%-6d bip=%-9d (2nd route %d, agree=%s)  3*(Aa)_v>q : %s'
          % (tag, q, b1, b2, b1 == b2, ok))
    print('   weighted degrees = %s   (need > q/3 = %s)' % (d, F(q, 3)))
    print('   25*bip/q^2 = %s = %.9f' % (r, float(r)))
    return r, ok


print('=== G7.md claimed degree-restricted optimum at q=92 ===')
r92, ok92 = report('q=92 (target claim)', [1, 16, 14, 6, 19, 6, 14, 16])
print('   equals 1925/2116 ?', r92 == F(1925, 2116))

print()
print('=== falsifying witnesses for the "~9% margin" claim ===')
best = r92
for tag, a in [('q=300',  [45, 53, 3, 53, 45, 20, 61, 20]),
               ('q=600',  [91, 107, 3, 107, 91, 39, 123, 39]),
               ('q=1200', [217, 3, 217, 181, 78, 245, 78, 181]),
               ('q=2400', [430, 368, 152, 497, 152, 368, 430, 3]),
               ('q=6000', [1237, 382, 915, 1083, 3, 1083, 915, 382])]:
    r, ok = report(tag, a)
    assert ok, tag
    if r > best:
        best = r
print()
print('best exact lower bound on 25*Psi(Gamma_3,1/3) found here: %s = %.9f'
      % (best, float(best)))
print('G7.md value                                            : %s = %.9f'
      % (F(1925, 2116), float(F(1925, 2116))))
print('so the true margin is at most %.4f%%, not "about 9%%"'
      % (100 * (1 - float(best))))

print()
print('=== the same finite-budget artefact in the "margin grows with the index" table ===')
print('G7.md compares Gamma_3 exhausted to q<=98 (0.9097) with Gamma_7 exhausted')
print('to q<=23 (0.7500).  At a COMMON budget q<=23 the Gamma_3 value is:')
tab = {8: 2, 11: 3, 14: 6, 16: 8, 17: 8, 19: 10, 20: 12, 22: 15, 23: 18}
print('   ', max((F(25 * m, q * q), q) for q, m in tab.items()))
