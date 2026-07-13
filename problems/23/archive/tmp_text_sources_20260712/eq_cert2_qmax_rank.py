import json, sys
from collections import Counter
sys.path.insert(0,'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp

rows={tuple(r) for r in json.load(open('tmp/eq_cert2_chart0_iter3_rows.json'))['rows']}
t,g,m=lp.build_chart(0, extra_maxcut='all')
base_n=15
stats=[]
for gi,gen in enumerate(g):
    beta_degree=lp.TARGET_DEGREE-gen.degree
    neg=[e for e,c in gen.terms.items() if c<0]
    seen=set()
    for row in rows:
        for ge in neg:
            beta=lp.sub_exp(row, ge)
            if beta is not None and sum(beta)==beta_degree:
                seen.add(beta)
    if gi>=base_n:
        stats.append((len(seen), gen.name, gi, len(neg), len(gen.terms)))
stats.sort(reverse=True)
print('qmax facets',len(stats))
for item in stats[:60]:
    print(item)
print('zero coverage',sum(1 for x in stats if x[0]==0))
