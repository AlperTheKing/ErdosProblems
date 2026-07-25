"""audit_P3_build.py -- audit of P3.md claims (a) and (b): construction and properties.

Independent build; then compare with P3_vega.g6 line by line (exact edge-set match on the
declared vertex order, NOT just isomorphism), and re-check every predicate.
"""
import sys
from fractions import Fraction as F
from audit_P3_core import (vega_family, edges, triangle_free, maximal_tf, twin_free, chrom,
                           odd_girth, has_induced_c5, g6_decode, SPECIALS)

IMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 8

g6lines = []
with open('P3_vega.g6') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line.strip():
            continue
        code, meta = line.split('\t')
        g6lines.append((code, meta))

print('P3_vega.g6 has %d lines' % len(g6lines))

rows = []
k = 0
fails = []
for i in range(2, IMAX + 1):
    for (name, adj, order, w) in vega_family(i):
        n = len(order)
        m = sum(len(adj[t]) for t in order) // 2
        tf = triangle_free(adj)
        mtf = maximal_tf(adj)
        twf = twin_free(adj)
        chi = chrom(adj)
        og = odd_girth(adj)
        degs = {t: sum(w[s] for s in adj[t]) for t in order}
        tot = sum(w.values())
        dmin, dmax = min(degs.values()), max(degs.values())
        delta = F(dmin, tot)
        ic5 = has_induced_c5(adj)
        # --- compare with the g6 file
        code, meta = g6lines[k]
        k += 1
        gn, gE = g6_decode(code)
        declared = meta.split('order=')[1].strip()
        dorder = [t if t in SPECIALS else int(t) for t in declared.split(',')]
        idx = {t: j for j, t in enumerate(dorder)}
        myE = set()
        for p in order:
            for q in adj[p]:
                a, b = idx[p], idx[q]
                myE.add((min(a, b), max(a, b)))
        match = (meta.split()[0] == name) and (gn == n) and (gE == myE) and (dorder == order)
        # closed-form checks
        variant = name.split('-', 1)[1] if '-' in name else ''
        exp = {'': (9 * i - 6, 27 * i - 19, 3 * i + 7),
               'y': (9 * i - 7, 27 * i - 22, 3 * i + 6),
               '2i': (9 * i - 7, 27 * i - 22, 3 * i + 6),
               'y-2i': (9 * i - 8, 27 * i - 25, 3 * i + 5)}[variant]
        formula_ok = (dmin, tot, n) == exp
        ok = tf and mtf and twf and chi == 4 and og == 5 and dmin == dmax and delta > F(1, 3) \
            and ic5 and match and formula_ok
        rows.append((name, n, m, tf, mtf, twf, chi, og, dmin == dmax, dmin, tot, str(delta),
                     ic5, match, formula_ok, ok))
        if not ok:
            fails.append((name, dict(tf=tf, mtf=mtf, twf=twf, chi=chi, og=og,
                                     reg=dmin == dmax, delta=str(delta), ic5=ic5,
                                     g6match=match, formula=formula_ok)))

hdr = '%-13s %3s %4s %5s %5s %5s %4s %3s %4s %5s %6s %-9s %5s %6s %5s %s'
print(hdr % ('name', 'n', 'm', 'tf', 'mtf', 'twf', 'chi', 'og', 'reg', 'wdeg', 'wtot',
             'delta', 'indC5', 'g6==', 'form', 'OK'))
for r in rows:
    print(hdr % r)
print('rows=%d  FAILURES=%d' % (len(rows), len(fails)))
for f_ in fails:
    print('  FAIL', f_)
print('g6 lines consumed: %d of %d' % (k, len(g6lines)))
