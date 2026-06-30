from _wf_deficit_farkas import families, collect_rows, NGEN, GEN_LABELS
from fractions import Fraction as F
import collections

rows = []
for (name, n, E) in families():
    try:
        rows += collect_rows(name, n, E)
    except Exception:
        pass
print('total', len(rows))

zero_b = [r for r in rows if all(x == 0 for x in r['g']) and r['b'] != 0]
hard = [r for r in rows if r['b'] > 0 and all(x <= 0 for x in r['g'])]
print('all-gen-zero with b!=0:', len(zero_b))
print('b>0 but all gens <=0 (UNREACHABLE):', len(hard))

cnt = collections.Counter(r['name'] for r in hard)
print('hard-row families:', cnt.most_common(15))
for r in hard[:4]:
    print('  HARD', r['name'], 'N=', r['N'], 'b=', float(r['b']), 'P=', r['P'])
    nz = [(GEN_LABELS[i], float(g)) for i, g in enumerate(r['g']) if g != 0]
    print('   nonzero gens:', nz)

# also: how many rows have b<0 ? (those are over-satisfied; identity must still hold exactly)
neg_b = [r for r in rows if r['b'] < 0]
print('rows with b<0:', len(neg_b))
# is glue row hard?
gl = [r for r in rows if 'glue' in r['name']]
glhard = [r for r in gl if r['b'] > 0 and all(x <= 0 for x in r['g'])]
print('glue rows:', len(gl), 'of which UNREACHABLE:', len(glhard))
