"""audit_G10_corpus.py -- INDEPENDENT re-verification of the corpora and of every
optimum reported by the G10 hunter.

For each (corpus, output) pair:
  * re-check triangle-freeness and (where claimed) maximality with my own routines;
  * recompute bip(H[a]) = min over ALL 2^(h-1) cuts of sum_{mono} a_u a_v from scratch
    in exact int64 arithmetic (numpy integer matrix product; no floats anywhere);
  * compare with the reported bestF, check sum(a) == bestQ,
  * report every pattern with 25*bestF - bestQ^2 > 0 (a counterexample would show here),
  * and print the exact rational value bestF/bestQ^2 histogram.

Usage: python audit_G10_corpus.py corpus.txt out.txt [--maximal]
"""
import sys
from fractions import Fraction
from collections import Counter
import numpy as np

sys.path.insert(0, '.')
from audit_G10_lib import is_tf, is_maximal_tf, adjlist, odd_girth


def load_corpus(path):
    G = {}
    order = []
    for L in open(path):
        p = L.split()
        if not p:
            continue
        nm, h, E = p[0], int(p[1]), int(p[2])
        e = [(int(p[3 + 2 * k]), int(p[4 + 2 * k])) for k in range(E)]
        G[nm] = (h, e)
        order.append(nm)
    return G, order


def mono_matrix(h, e):
    """(NC x E) 0/1 matrix: entry 1 iff edge k is monochromatic in cut c.  int64."""
    NC = 1 << (h - 1)
    M = np.zeros((NC, len(e)), dtype=np.int64)
    for c in range(NC):
        m = c << 1
        for k, (u, v) in enumerate(e):
            if ((m >> u) & 1) == ((m >> v) & 1):
                M[c, k] = 1
    return M


def bip_exact(h, e, a, cache={}):
    key = (h, tuple(e))
    if key not in cache:
        if len(cache) > 400:
            cache.clear()
        cache[key] = mono_matrix(h, e)
    M = cache[key]
    a = np.array(a, dtype=np.int64)
    prod = np.array([a[u] * a[v] for (u, v) in e], dtype=np.int64)
    return int((M @ prod).min())


def main():
    corpus, out = sys.argv[1], sys.argv[2]
    want_max = '--maximal' in sys.argv
    G, order = load_corpus(corpus)
    hcount = Counter()
    nottf = []
    notmax = []
    for nm in order:
        h, e = G[nm]
        hcount[h] += 1
        if not is_tf(h, e):
            nottf.append(nm)
        if want_max and not is_maximal_tf(h, e):
            notmax.append(nm)
    print('corpus %s : %d patterns, by h: %s' % (corpus, len(order), dict(sorted(hcount.items()))))
    print('  not triangle-free: %d %s' % (len(nottf), nottf[:5]))
    if want_max:
        print('  not maximal tf   : %d %s' % (len(notmax), notmax[:5]))

    vals = Counter()
    mismatch = []
    above = []
    worst = Fraction(0)
    nlines = 0
    for L in open(out):
        p = L.split(':')
        head = p[0].split()
        nm = head[0]
        F = int(head[2]); Q = int(head[3]); delta = int(head[4])
        a = [int(z) for z in p[1].split()]
        h, e = G[nm]
        nlines += 1
        if sum(a) != Q or len(a) != h:
            mismatch.append((nm, 'sum(a)=%d vs Q=%d len=%d vs h=%d' % (sum(a), Q, len(a), h)))
            continue
        F2 = bip_exact(h, e, a)
        if F2 != F:
            mismatch.append((nm, 'reported F=%d recomputed %d' % (F, F2)))
        if 25 * F2 - Q * Q != delta:
            mismatch.append((nm, 'delta field wrong'))
        v = Fraction(F2, Q * Q)
        vals[v] += 1
        if v > Fraction(1, 25):
            above.append((nm, v))
        if v > worst:
            worst = v
    print('  output lines: %d   value histogram (exact rationals):' % nlines)
    for v, c in sorted(vals.items(), reverse=True):
        print('     %-14s = %.10f  x%d' % (v, float(v), c))
    print('  recomputation mismatches: %d %s' % (len(mismatch), mismatch[:8]))
    print('  STRICTLY ABOVE 1/25: %d %s' % (len(above), above[:5]))
    print('  corpus max = %s = %.10f' % (worst, float(worst)))


if __name__ == '__main__':
    main()
