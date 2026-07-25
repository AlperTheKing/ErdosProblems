"""Q3 round 7 -- the perfect-stability constant.

PST call a problem PERFECTLY B-stable if  dist(G, blow-ups of B) <= C * (deficit).
Here, in the psi normalisation,   d(H,x) <= C * (1/25 - psi(H,x)).
So the relevant statistic of every exact data point with d > 0 is the ratio

        R = d / (1/25 - psi)      (perfect stability <=> sup R < infinity)

and its reciprocal c = 1/R is the largest constant in  psi <= 1/25 - c*d.
This script prints the worst (largest R) exact data points of every input file.

usage: python Q3_ratio.py <tsv files ...>
"""
import sys
from fractions import Fraction as F


def rows(path):
    with open(path) as f:
        head = f.readline().rstrip('\n').split('\t')
        ix = {k: i for i, k in enumerate(head)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < 4:
                continue
            g6 = p[ix['g6']]
            Q = int(p[ix['Q']]) if 'Q' in ix else int(p[ix['n']])
            bip = int(p[ix['bip']])
            dist = int(p[ix['dist']])
            w = p[ix['w']] if 'w' in ix else ''
            yield (path, g6, Q, bip, dist, w)


def main():
    out = []
    for path in sys.argv[1:]:
        for (pa, g6, Q, bip, dist, w) in rows(path):
            if Q == 0 or dist == 0:
                continue
            psi = F(bip, Q * Q)
            d = F(dist, Q * Q)
            defi = F(1, 25) - psi
            if defi <= 0:
                print('*** VIOLATION psi >= 1/25 with d>0: %s %s Q=%d bip=%d dist=%d' % (pa, g6, Q, bip, dist))
                continue
            out.append((d / defi, pa, g6, Q, bip, dist, psi, defi, w))
    out.sort(reverse=True)
    print('%-10s %-12s %-12s %-12s %s' % ('R=d/deficit', 'psi', 'd', 'deficit', 'witness'))
    seen = set()
    shown = 0
    for (R, pa, g6, Q, bip, dist, psi, defi, w) in out:
        key = (g6, Q)
        if key in seen:
            continue
        seen.add(key)
        print('%-10.4f %-12s %-12s %-12s %s Q=%d bip=%d dist=%d %s'
              % (float(R), '%d/%d' % (psi.numerator, psi.denominator),
                 '%d/%d' % (F(dist, Q * Q).numerator, F(dist, Q * Q).denominator),
                 '%d/%d' % (defi.numerator, defi.denominator), g6, Q, bip, dist, w))
        shown += 1
        if shown >= 20:
            break
    if out:
        print('worst (largest) R over %d points with d>0 : %s = %.4f' % (len(out), out[0][0], float(out[0][0])))
        print('so every point satisfies  psi <= 1/25 - c*d  with c = %.6f' % (1.0 / float(out[0][0])))


if __name__ == '__main__':
    main()
