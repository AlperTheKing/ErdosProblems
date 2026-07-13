from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_rowgen.py')
s = p.read_text(encoding='utf-8')
s = s.replace('import clarabel\nimport numpy as np\n', 'import clarabel\nimport highspy\nimport numpy as np\n')
s = s.replace('    if oracle == "clarabel":\n        return solve_lp_clarabel(matrix, rhs, objective, time_limit, threads)\n', '    if oracle == "clarabel":\n        return solve_lp_clarabel(matrix, rhs, objective, time_limit, threads)\n    if oracle == "highspy":\n        return solve_lp_highspy(matrix, rhs, objective, method, time_limit, threads)\n')
insert = r'''

def solve_lp_highspy(matrix, rhs, objective, method, time_limit, threads):
    csc = matrix.tocsc()
    n = matrix.shape[1]
    m = matrix.shape[0]
    lp = highspy.HighsLp()
    lp.num_col_ = n
    lp.num_row_ = m
    lp.col_cost_ = [0.0 if objective == "zero" else 1.0] * n
    lp.col_lower_ = [0.0] * n
    lp.col_upper_ = [highspy.kHighsInf] * n
    lp.row_lower_ = [-highspy.kHighsInf] * m
    lp.row_upper_ = list(rhs)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = n
    lp.a_matrix_.num_row_ = m
    lp.a_matrix_.start_ = list(map(int, csc.indptr[:-1]))
    lp.a_matrix_.p_end_ = list(map(int, csc.indptr[1:]))
    lp.a_matrix_.index_ = list(map(int, csc.indices))
    lp.a_matrix_.value_ = list(map(float, csc.data))

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", False)
    if time_limit > 0:
        highs.setOptionValue("time_limit", float(time_limit))
    if threads > 0:
        highs.setOptionValue("threads", int(threads))
    if method in {"highs-ds", "simplex"}:
        highs.setOptionValue("solver", "simplex")
        highs.setOptionValue("simplex_strategy", 1)
    elif method in {"highs-ipm", "ipm"}:
        highs.setOptionValue("solver", "ipm")
    highs.passModel(lp)
    highs.run()
    status = highs.getModelStatus()
    status_text = highs.modelStatusToString(status)

    class Result:
        pass

    res = Result()
    res.status = 0 if status == highspy.HighsModelStatus.kOptimal else (2 if status == highspy.HighsModelStatus.kInfeasible else 1)
    res.message = status_text
    res.success = res.status == 0
    if res.success:
        res.x = np.array(highs.getSolution().col_value, dtype=float)
    else:
        res.x = np.zeros(n, dtype=float)
    return res
'''
if 'def solve_lp_highspy' not in s:
    s = s.replace('\ndef solve_lp_clarabel', insert + '\ndef solve_lp_clarabel')
s = s.replace('    ap.add_argument("--oracle", choices=["scipy", "clarabel"], default="scipy")', '    ap.add_argument("--oracle", choices=["scipy", "clarabel", "highspy"], default="scipy")')
p.write_text(s, encoding='utf-8')
