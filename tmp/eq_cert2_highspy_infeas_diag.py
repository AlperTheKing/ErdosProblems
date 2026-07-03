import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, 'problems/23/writeup')
import highspy
import _codex_eq_cert2_chart_lp as base
import _codex_eq_cert2_chart_rowgen as rg

target, gens, meta = base.build_chart(0)
rows_data = json.load(open('tmp/eq_cert2_chart0_iter3_rows.json'))['rows']
row_set = {tuple(r) for r in rows_data}
cols = rg.repair_columns_for_rows(row_set, gens, None)
term_maps = [base.column_terms(c, gens[c.gen_index]) for c in cols]
row_mons = sorted(row_set)
mat, rhs = rg.build_scaled_matrix(row_mons, cols, term_maps, target)
csc = mat.tocsc()
n = mat.shape[1]
m = mat.shape[0]
lp = highspy.HighsLp()
lp.num_col_ = n
lp.num_row_ = m
lp.col_cost_ = [0.0]*n
lp.col_lower_ = [0.0]*n
lp.col_upper_ = [highspy.kHighsInf]*n
lp.row_lower_ = [-highspy.kHighsInf]*m
lp.row_upper_ = list(rhs)
lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
lp.a_matrix_.num_col_ = n
lp.a_matrix_.num_row_ = m
lp.a_matrix_.start_ = list(map(int,csc.indptr[:-1]))
lp.a_matrix_.p_end_ = list(map(int,csc.indptr[1:]))
lp.a_matrix_.index_ = list(map(int,csc.indices))
lp.a_matrix_.value_ = list(map(float,csc.data))
h = highspy.Highs()
h.setOptionValue('output_flag', False)
h.setOptionValue('time_limit', 180.0)
h.setOptionValue('threads', 64)
h.setOptionValue('solver','simplex')
h.passModel(lp)
h.run()
status = h.getModelStatus()
print('status', h.modelStatusToString(status), 'rows', m, 'cols', n, 'nnz', mat.nnz)
print('dualray exist', h.getDualRayExist())
try:
    dr = h.getDualRay()
    print('dualray tuple', dr[0], dr[1], 'len', len(dr[2]))
    ray = np.asarray(dr[2], dtype=float)
    nz = np.where(np.abs(ray)>1e-9)[0]
    print('ray nz', len(nz), 'min', ray.min() if len(ray) else None, 'max', ray.max() if len(ray) else None)
    top = sorted(nz, key=lambda i: -abs(ray[i]))[:40]
    for i in top:
        print('raytop', i, ray[i], row_mons[i], 'target', target.get(row_mons[i],0))
except Exception as e:
    print('dualray error', repr(e))
try:
    st, iis = h.getIis()
    print('iis status', st, iis)
except Exception as e:
    print('iis error', repr(e))
