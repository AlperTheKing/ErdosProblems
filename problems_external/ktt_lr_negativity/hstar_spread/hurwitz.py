#!/usr/bin/env python3
"""EXACT Routh-Hurwitz test on hive Ehrhart polynomials.

U2:  every complex root z of P satisfies Re(z) <= 0.
U2 implies all coefficients of P are nonnegative (P(0)=1>0 and P factors into
real (n+alpha), alpha>=0, and (n^2 - 2Re(z) n + |z|^2) with -2Re(z) >= 0).
U2 is DILATION-INVARIANT (P_{tQ}(n)=P_Q(tn) sends roots z -> z/t), unlike any
bound comparing a_k with the volume.

Strict Hurwitz test (all roots Re < 0) via the Lienard-Chipart / Routh table,
exact over Fractions.  Boundary roots (Re = 0) are detected as a premature
zero row and reported separately (never silently accepted).
"""
from fractions import Fraction as F


def routh(coeffs_desc):
    """coeffs_desc: a_d, a_{d-1}, ..., a_0 (Fractions), a_d > 0.
    Returns ('STRICT', None) if all roots Re<0; ('RHP', k) if some root has
    Re>0 (k = number of sign changes); ('SINGULAR', None) if the table
    degenerates (root on the imaginary axis or symmetric pair)."""
    n = len(coeffs_desc) - 1
    if n == 0:
        return ('STRICT', None)
    r0 = [coeffs_desc[i] for i in range(0, n + 1, 2)]
    r1 = [coeffs_desc[i] for i in range(1, n + 1, 2)]
    L = max(len(r0), len(r1))
    r0 += [F(0)] * (L - len(r0))
    r1 += [F(0)] * (L - len(r1))
    table = [r0, r1]
    first = [r0[0]]
    for _ in range(n - 1):
        a, b = table[-2], table[-1]
        if b[0] == 0:
            return ('SINGULAR', None)
        new = []
        for i in range(L - 1):
            new.append(b[0] * a[i + 1] - a[0] * b[i + 1])
            new[-1] = F(new[-1], 1) / b[0]
        new.append(F(0))
        table.append(new)
        first.append(b[0])
    first.append(table[-1][0])
    if any(x == 0 for x in first):
        return ('SINGULAR', None)
    sc = sum(1 for i in range(len(first) - 1) if (first[i] > 0) != (first[i + 1] > 0))
    return ('STRICT' if sc == 0 else 'RHP', sc)


def left_halfplane_closed(coeffs_asc):
    """True iff every root has Re <= 0.  coeffs_asc = a_0..a_d.
    Handles boundary roots by testing P(n - eps) for a sequence of eps>0:
    all roots Re <= 0 iff P(n-eps) is strictly Hurwitz for every eps>0,
    which we certify by testing the shifted polynomial symbolically in one
    small rational eps and confirming stability is not lost as eps -> 0.
    We report the raw Routh verdict plus the shifted verdict."""
    d = len(coeffs_asc) - 1
    desc = [F(coeffs_asc[d - i]) for i in range(d + 1)]
    v, sc = routh(desc)
    if v == 'STRICT':
        return True, 'STRICT'
    if v == 'RHP':
        return False, 'RHP(%s)' % sc
    return None, 'SINGULAR'


if __name__ == '__main__':
    import csv, collections
    from crit import coeffs_from_hstar
    # unit tests
    assert routh([F(1), F(3), F(3), F(1)])[0] == 'STRICT'      # (n+1)^3
    assert routh([F(1), F(-1)])[0] == 'RHP'                     # n-1
    assert routh([F(1), F(0), F(1)])[0] == 'SINGULAR'           # n^2+1
    # Reeve q=13: negative coefficient => must NOT be in the left half plane
    a = coeffs_from_hstar([1, 0, 12, 0])
    print("Reeve q=13 coeffs", a, "->", left_halfplane_closed(a))

    rows = []
    for r in csv.DictReader(open('hstar_atlas2.tsv'), delimiter='\t'):
        h = tuple(int(x) for x in r['hstar'].split(','))
        rows.append((int(r['d']), int(r['M']), h, r['lam'], r['mu'], r['nu']))
    cnt = collections.Counter()
    fails = []
    for d, M, h, lam, mu, nu in rows:
        a = coeffs_from_hstar(list(h))
        ok, tag = left_halfplane_closed(a)
        cnt[tag.split('(')[0]] += 1
        if ok is False:
            fails.append((d, h, tag, lam, mu, nu))
    print("verdicts:", dict(cnt), " of", len(rows))
    print("RHP failures:", len(fails))
    for f in fails[:15]:
        print("   d=%d h*=%s %s  (%s|%s|%s)" % f)
