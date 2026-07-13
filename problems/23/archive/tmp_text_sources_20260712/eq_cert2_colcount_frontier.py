import json, sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_rowgen as rg
seed='tmp/eq_cert2_chart0_rowgen_dyn_qmax32_replay_v1.json'
rows={tuple(r) for r in json.load(open(seed, encoding='utf-8'))['active_rows']}
for mode, masks in [('all', None), ('tight', None)]:
    _, gens, _ = lp.build_chart(0, extra_maxcut=mode)
    cols = rg.repair_columns_for_rows(rows, gens, None)
    term_nnz = sum(len(lp.column_terms(col, gens[col.gen_index])) for col in cols)
    print(mode, 'gens', len(gens), 'rows', len(rows), 'cols', len(cols), 'term_nnz', term_nnz)
