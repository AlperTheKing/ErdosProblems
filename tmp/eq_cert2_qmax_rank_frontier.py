import json, sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp
path = 'tmp/eq_cert2_chart0_rowgen_dyn_qmax32_replay_v1.json'
rows = {tuple(r) for r in json.load(open(path, encoding='utf-8'))['active_rows']}
_, generators, _ = lp.build_chart(0, extra_maxcut='all')
base_n = 15
stats = []
for gi, gen in enumerate(generators):
    if gi < base_n:
        continue
    beta_degree = lp.TARGET_DEGREE - gen.degree
    neg = [e for e, c in gen.terms.items() if c < 0]
    seen = set()
    hit_rows = 0
    for row in rows:
        row_hit = False
        for ge in neg:
            beta = lp.sub_exp(row, ge)
            if beta is not None and sum(beta) == beta_degree:
                seen.add(beta)
                row_hit = True
        if row_hit:
            hit_rows += 1
    stats.append((len(seen), hit_rows, gen.name, gi, len(neg), len(gen.terms)))
stats.sort(reverse=True)
print('rows', len(rows), 'qmax facets', len(stats))
for item in stats[:120]:
    print(item)
print('zero coverage', sum(1 for x in stats if x[0] == 0))
