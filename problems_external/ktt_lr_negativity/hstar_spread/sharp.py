#!/usr/bin/env python3
"""How sharp is the half-plane lemma?  Numeric root search (search only; every
verdict already certified exactly by hurwitz.py).  Reports, over the corpus:
  maxRe          = max over roots of Re(z)                (dilation-covariant)
  maxCos         = max over roots of Re(z)/|z| = cos(arg) (dilation-INVARIANT)
  real-rooted?   = are all roots real?
Also runs an exact strip test: is Re(z) <= -1/2 always?  (shift n -> n-1/2)
"""
import csv, collections
import numpy as np
from fractions import Fraction as F
from crit import coeffs_from_hstar
from hurwitz import routh

rows = []
for r in csv.DictReader(open('hstar_atlas2.tsv'), delimiter='\t'):
    h = tuple(int(x) for x in r['hstar'].split(','))
    rows.append((int(r['d']), int(r['M']), h, r['lam'], r['mu'], r['nu']))


def shift(coeffs_asc, c):
    """coefficients of P(n + c), ascending, exact."""
    d = len(coeffs_asc) - 1
    out = [F(0)] * (d + 1)
    from math import comb
    for i, a in enumerate(coeffs_asc):
        for t in range(i + 1):
            out[t] += a * comb(i, t) * F(c) ** (i - t)
    return out


bestRe = (-99, None)
bestCos = (-99, None)
nreal = 0
strip = collections.Counter()
for d, M, h, lam, mu, nu in rows:
    a = coeffs_from_hstar(list(h))
    rts = np.roots([float(x) for x in reversed(a)])
    if len(rts) == 0:
        continue
    mre = max(z.real for z in rts)
    mcos = max(z.real / abs(z) for z in rts if abs(z) > 0)
    if mre > bestRe[0]:
        bestRe = (mre, (d, h, lam, mu, nu))
    if mcos > bestCos[0]:
        bestCos = (mcos, (d, h, lam, mu, nu))
    if all(abs(z.imag) < 1e-9 for z in rts):
        nreal += 1
    # exact: is Re(z) <= -1/2 ?  test P(n - 1/2) strictly Hurwitz
    b = shift(a, F(-1, 2))
    dd = len(b) - 1
    v, _ = routh([b[dd - i] for i in range(dd + 1)])
    strip[v] += 1

print("corpus size %d" % len(rows))
print("max Re(root)        = %+0.6f   at d=%d h*=%s (%s|%s|%s)" % ((bestRe[0],) + bestRe[1]))
print("max Re(root)/|root| = %+0.6f   at d=%d h*=%s (%s|%s|%s)" % ((bestCos[0],) + bestCos[1]))
print("all-real-rooted: %d / %d" % (nreal, len(rows)))
print("exact test Re(z) <= -1/2 for all roots:", dict(strip))
