from collections import Counter, defaultdict
from fractions import Fraction
import sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp

for chart in [0]:
    target, gens, meta = lp.build_chart(chart)
    neg = {e:c for e,c in target.items() if c < 0}
    pos = {e:c for e,c in target.items() if c > 0}
    print('chart', chart)
    print('target_terms', len(target), 'neg', len(neg), 'pos', len(pos), 'min', min(target.values()), 'max', max(target.values()))
    cols = lp.repair_columns(target, gens, 'repair', None)
    by_g = Counter(c.gen_index for c in cols)
    print('repair_cols', len(cols))
    for i,g in enumerate(gens):
        neg_terms = sum(1 for c in g.terms.values() if c < 0)
        pos_terms = sum(1 for c in g.terms.values() if c > 0)
        print(i, g.name, 'deg', g.degree, 'terms', len(g.terms), 'neg_terms', neg_terms, 'pos_terms', pos_terms, 'repair_cols', by_g[i])
    cover = defaultdict(int)
    cover_by_g = defaultdict(Counter)
    for col in cols:
        g = gens[col.gen_index]
        for ge, gc in g.terms.items():
            if gc >= 0:
                continue
            te = tuple(a+b for a,b in zip(ge, col.beta))
            if te in neg:
                cover[te] += 1
                cover_by_g[te][col.gen_index] += 1
    uncovered = [e for e in neg if cover[e] == 0]
    print('uncovered_neg', len(uncovered))
    cov_vals = [cover[e] for e in neg]
    print('coverage min/median/max', min(cov_vals), sorted(cov_vals)[len(cov_vals)//2], max(cov_vals))
    hardest = sorted(neg, key=lambda e: (cover[e], neg[e]))[:10]
    for e in hardest:
        print('hard', e, 'coeff', neg[e], 'cover', cover[e], 'by_g', dict(cover_by_g[e]))
