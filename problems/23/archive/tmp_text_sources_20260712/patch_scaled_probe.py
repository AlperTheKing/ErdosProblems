from pathlib import Path
p=Path('tmp/probe_k8_g3_repair_lp_scaled.py')
s=p.read_text()
old='''def solve_active(columns, residual, active_rows, candidate_cols):
    row_index = {r: i for i, r in enumerate(active_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    A = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                A[i, j] = float(coeff)
    b = np.array([float(residual[r]) for r in active_rows], dtype=float)
    cvec = np.ones(len(candidate_cols), dtype=float)
    return linprog(cvec, A_ub=A.tocsr(), b_ub=b, bounds=(0, None), method="highs")
'''
new='''def solve_active(columns, residual, active_rows, candidate_cols):
    row_index = {r: i for i, r in enumerate(active_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    A = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    scales = []
    for r in active_rows:
        rr = residual[r]
        scales.append(float(-rr) if rr < 0 else 1.0)
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                A[i, j] = float(coeff) / scales[i]
    b = np.array([float(residual[r]) / scales[i] for i, r in enumerate(active_rows)], dtype=float)
    cvec = np.ones(len(candidate_cols), dtype=float)
    return linprog(cvec, A_ub=A.tocsr(), b_ub=b, bounds=(0, None), method="highs")
'''
if old not in s:
    raise SystemExit('pattern not found')
p.write_text(s.replace(old,new))
