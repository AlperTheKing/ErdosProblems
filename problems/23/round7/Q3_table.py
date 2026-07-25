"""Q3 round 7 -- build the empirical trade-off table from engine output (exact rationals).

Input: TSV files produced by Q3_engine.exe / Q3_wsweep.exe with columns
       g6 n m Q bip dist ... (engine)   or   g6 n Q bip dist w phi (wsweep)
Output: for each distance band [t1,t2) of d = dist/Q^2, the maximum psi = bip/Q^2 observed,
        printed as an exact rational and as a decimal, with the witness.

usage: python Q3_table.py <file1> [file2 ...]
"""
import sys
from fractions import Fraction as F

BANDS = [F(0), F(1, 1000), F(1, 100), F(2, 100), F(3, 100), F(4, 100), F(5, 100),
         F(6, 100), F(8, 100), F(10, 100), F(15, 100), F(1)]


def load(path):
    rows = []
    with open(path) as f:
        head = f.readline().rstrip('\n').split('\t')
        ix = {k: i for i, k in enumerate(head)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < 5:
                continue
            g6 = p[ix['g6']]
            Q = int(p[ix['Q']]) if 'Q' in ix else int(p[ix['n']])
            bip = int(p[ix['bip']])
            dist = int(p[ix['dist']])
            n = int(p[ix['n']]) if 'n' in ix else 0
            m = int(p[ix['m']]) if 'm' in ix else -1
            w = p[ix['w']] if 'w' in ix else ''
            rows.append((g6, n, m, Q, bip, dist, w))
    return rows


def main():
    rows = []
    for path in sys.argv[1:]:
        rows += load(path)
    print('rows: %d' % len(rows))
    best = {}
    for (g6, n, m, Q, bip, dist, w) in rows:
        if Q == 0:
            continue
        d = F(dist, Q * Q)
        psi = F(bip, Q * Q)
        for i in range(len(BANDS) - 1):
            lo, hi = BANDS[i], BANDS[i + 1]
            inband = (d == 0) if i == 0 else (lo < d <= hi if i > 0 else False)
            if i == 0:
                inband = (d == 0)
            else:
                inband = (BANDS[i - 1] < d <= hi) if False else (lo < d <= hi)
            if inband:
                cur = best.get(i)
                if cur is None or psi > cur[0]:
                    best[i] = (psi, d, g6, n, Q, bip, dist, w)
                break
    print('%-18s %-14s %-10s %-9s %s' % ('distance band', 'max psi', 'decimal', 'deficit', 'witness'))
    for i in range(len(BANDS) - 1):
        lo, hi = BANDS[i], BANDS[i + 1]
        lab = 'd = 0' if i == 0 else '%.4f < d <= %.4f' % (float(lo), float(hi))
        if i not in best:
            print('%-18s %-14s' % (lab, '(empty)'))
            continue
        psi, d, g6, n, Q, bip, dist, w = best[i]
        print('%-18s %-14s %-10.6f %-9.6f  %s n=%d Q=%d bip=%d dist=%d d=%s w=%s'
              % (lab, '%d/%d' % (psi.numerator, psi.denominator), float(psi),
                 float(F(1, 25) - psi), g6, n, Q, bip, dist, str(d), w))


if __name__ == '__main__':
    main()
