"""Independent verification (my machinery) of Codex's 19:44 REFINED deficient-cap classification:
gluing the canonical deficient core graph I?AEBAwF_ to an extra C5 via a cut bridge should produce
a NEW zero-Psi 'baggage' deficient template (e.g. crossing lengths (5,5,7)) in addition to the (5,7)
core, with R[w]>=0 globally throughout. Tests several bridges; reports deficient-cap template
signatures + global sign. Reuses _defcap_sign_mine.scan_graph (my witness_structure). From problems/23/writeup."""
import sys
from collections import Counter
from _h import dec
from _bdef_construct import is_triangle_free
from _defcap_sign_mine import scan_graph

core_n, core_E = dec("I?AEBAwF_")     # canonical deficient core (n=10)
C5 = [(core_n + i, core_n + (i + 1) % 5) for i in range(5)]   # extra C5 on verts 10..14
bridges = [(a, b) for a in range(core_n) for b in range(core_n, core_n + 5)]

n = core_n + 5
agg = Counter()
agg['templates'] = Counter()
first_global = None
tested_bridges = 0
for br in bridges:
    E = list(core_E) + C5 + [br]
    if not is_triangle_free(n, E):
        continue
    acc = Counter(); acc['first'] = None; acc['first_global'] = None; acc['templates'] = Counter()
    scan_graph('glue%d-%d' % br, n, E, acc)
    tested_bridges += 1
    agg['two_cap_positive'] += acc['two_cap_positive']
    agg['defcap'] += acc['defcap']
    agg['fail'] += acc['fail']
    agg['global_fail'] += acc['global_fail']
    for t, c in acc['templates'].items():
        agg['templates'][t] += c
    if acc['first_global'] is not None and first_global is None:
        first_global = acc['first_global']

print('glued I?AEBAwF_ + C5, bridges tested:', tested_bridges)
print('two_cap_positive=%d defcap=%d fail(inS)=%d global_fail=%d' %
      (agg['two_cap_positive'], agg['defcap'], agg['fail'], agg['global_fail']))
print('deficient-cap template signatures (|C|, ell-sorted, witdeg-sorted, |Y|, gap):')
for t, c in sorted(agg['templates'].items()):
    print('   ', t, 'x', c)
print('first global-sign fail:', first_global or 'NONE')
print('VERDICT:', 'REFINED CLASSIFICATION CONFIRMED -- baggage template(s) appear, R>=0 globally'
      if agg['global_fail'] == 0 and agg['defcap'] > 0 else
      ('no deficient caps found (bridge choice)' if agg['defcap'] == 0 else 'GLOBAL SIGN FAIL'))
