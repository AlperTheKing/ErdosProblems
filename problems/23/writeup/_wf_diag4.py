"""Characterize WHY the 3-row core is unreachable: dGamma absent? product-slack zero? maxcut sign?"""
from _wf_deficit_farkas import collect_rows, NGEN, GEN_LABELS
from fractions import Fraction as F
from _h import dec

core_specs = [('ECxo', (3, 0, 4, 1, 5)), ('F?bBo', (4, 0, 5, 1, 6)), ('F?bBo', (0, 4, 6, 1, 5))]
allrows = {}
for g6 in set(s[0] for s in core_specs):
    n, E = dec(g6)
    for r in collect_rows('cen'+g6, n, E):
        allrows[(g6, r['P'])] = r

for g6, P in core_specs:
    r = allrows[(g6, P)]
    g = r['g']
    def grp(prefix):
        return [g[i] for i, l in enumerate(GEN_LABELS) if l.startswith(prefix)]
    A = grp('A.'); B = grp('B.'); C = grp('C.'); D = grp('D.'); E = grp('E.'); Fl = grp('F.'); G = grp('G.')
    print('ROW %-7s P=%s  b=%s (=%.3f)' % (g6, P, r['b'], float(r['b'])))
    print('   dGamma A all-zero? %s   B all-zero? %s   C all-zero? %s'
          % (all(x == 0 for x in A), all(x == 0 for x in B), all(x == 0 for x in C)))
    print('   maxcut D values:', [int(x) for x in D])
    print('   product-slack G:', [str(x) for x in G], ' all-zero? %s' % all(x == 0 for x in G))
    print('   loads h:', [str(x) for x in r['h']], ' q=', r['q'], ' S=', r['S'])
    # max positive contribution achievable: only nonneg gens can raise; here all gens >=0?
    negs = [GEN_LABELS[i] for i in range(NGEN) if g[i] < 0]
    print('   generators that are NEGATIVE (would need to be unused since coeff>=0):', negs)
    # sum of all generator MAX (if we could set lambda huge) -- but uniform coupling is the real issue
    print()
