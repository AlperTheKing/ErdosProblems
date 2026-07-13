#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.append(str(Path('problems/23/writeup')))

import _codex_eq_odl1_rung2_hybrid_cg as cg
import _codex_eq_odl1_rung2_charts as charts
import _codex_eq_odl1_rung2_face_split_quotient_probe as quotient
import _codex_eq_odl1_rung2_source_solution_check as source_check

try:
    import highspy
except ImportError as exc:
    raise SystemExit(f'highspy unavailable: {exc}')


def frac_rec(q: Fraction) -> dict[str, int]:
    return {'num': q.numerator, 'den': q.denominator}


def solve_ray(mat, target_beta, *, threads: int, time_limit: float, presolve: str, verbose: bool):
    csc = mat.tocsc()
    row_count, col_count = mat.shape
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = int(col_count)
    lp.num_row_ = int(row_count)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [0.0] * int(col_count)
    lp.col_lower_ = [0.0] * int(col_count)
    lp.col_upper_ = [inf] * int(col_count)
    lp.row_lower_ = [-inf] * int(row_count)
    lp.row_upper_ = [float(x) for x in target_beta]

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = int(col_count)
    a.num_row_ = int(row_count)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue('output_flag', bool(verbose))
    highs.setOptionValue('solver', 'simplex')
    highs.setOptionValue('threads', int(threads))
    highs.setOptionValue('time_limit', float(time_limit))
    highs.setOptionValue('presolve', presolve)
    pass_status = highs.passModel(lp)
    if pass_status != highspy.HighsStatus.kOk:
        return {'pass_status': int(pass_status), 'message': f'passModel failed: {pass_status}', '_ray': None}
    t0 = time.monotonic()
    run_status = highs.run()
    model_status = highs.getModelStatus()
    info = highs.getInfo()
    out = {
        'pass_status': int(pass_status),
        'run_status': int(run_status),
        'model_status': int(model_status),
        'message': highs.modelStatusToString(model_status),
        'simplex_iteration_count': int(getattr(info, 'simplex_iteration_count', -1)),
        'seconds': time.monotonic() - t0,
        'presolve': presolve,
    }
    ray_arr = None
    if model_status == highspy.HighsModelStatus.kInfeasible:
        ray_status, ray_exists, ray = highs.getDualRay()
        out['dual_ray_status'] = int(ray_status)
        out['dual_ray_exists'] = bool(ray_exists)
        if ray_exists:
            ray_arr = np.array(ray, dtype=float)
    out['_ray'] = ray_arr
    return out


def summarize_ray(ray_arr, mat, target_beta, betas, top: int, tol: float):
    target_float = np.array([float(x) for x in target_beta], dtype=float)
    scores = mat.tocsc().T.dot(ray_arr)
    nz = np.flatnonzero(np.abs(ray_arr) > tol)
    top_rows = sorted(nz, key=lambda i: abs(float(ray_arr[i])), reverse=True)[:top]
    return {
        'ray_min': float(ray_arr.min()) if len(ray_arr) else 0.0,
        'ray_max': float(ray_arr.max()) if len(ray_arr) else 0.0,
        'ray_nonzero': int(len(nz)),
        'ray_positive_count': int(np.sum(ray_arr > tol)),
        'ray_negative_count': int(np.sum(ray_arr < -tol)),
        'ray_dot_rhs': float(np.dot(ray_arr, target_float)),
        'seed_score_min': float(scores.min()) if len(scores) else 0.0,
        'seed_score_max': float(scores.max()) if len(scores) else 0.0,
        'seed_positive_score_count': int(np.sum(scores > tol)),
        'seed_negative_score_count': int(np.sum(scores < -tol)),
        'support_top': [
            {
                'row': int(i),
                'beta': list(betas[int(i)]),
                'value': float(ray_arr[i]),
                'abs_value': float(abs(ray_arr[i])),
                'target_beta': frac_rec(target_beta[int(i)]),
                'target_beta_float': float(target_beta[int(i)]),
            }
            for i in top_rows
        ],
    }


def family_summary(columns, ray_arr, top: int):
    groups: dict[str, dict[str, float | int]] = {}
    for col in columns:
        score = 0.0
        for row, coeff in col.terms:
            score += float(coeff) * float(ray_arr[row])
        key = f'{col.side}:{col.kind}:{col.name}'
        g = groups.setdefault(key, {'count': 0, 'score_max': -math.inf, 'score_min': math.inf, 'positive': 0})
        g['count'] = int(g['count']) + 1
        g['score_max'] = max(float(g['score_max']), score)
        g['score_min'] = min(float(g['score_min']), score)
        if score > 1e-10:
            g['positive'] = int(g['positive']) + 1
    rows = [dict(family=k, **v) for k, v in groups.items()]
    rows.sort(key=lambda r: (float(r['score_max']), int(r['positive'])), reverse=True)
    return rows[:top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--columns-json', type=Path, required=True)
    ap.add_argument('--target-beta-json', type=Path, required=True)
    ap.add_argument('--chart', type=int, default=6)
    ap.add_argument('--threads', type=int, default=48)
    ap.add_argument('--time-limit', type=float, default=900.0)
    ap.add_argument('--top', type=int, default=500)
    ap.add_argument('--tol', type=float, default=1e-10)
    ap.add_argument('--summary', type=Path, required=True)
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    t0 = time.monotonic()
    target_raw = json.loads(args.target_beta_json.read_text(encoding='utf-8'))
    row_count = int(target_raw['row_count'])
    target_beta = source_check.read_target_beta(args.target_beta_json, row_count)
    columns, col_meta = cg.read_seed_columns_json(args.columns_json, row_count)
    mat = cg.build_matrix(columns, row_count)
    chart = charts.build_chart(args.chart)
    betas = charts.all_exps(len(chart.variables), quotient.TARGET_DEGREE)
    if len(betas) != row_count:
        raise RuntimeError(f'beta count {len(betas)} != row_count {row_count}')

    solve = solve_ray(mat, target_beta, threads=args.threads, time_limit=args.time_limit, presolve='on', verbose=args.verbose)
    ray_arr = solve.pop('_ray', None)
    if ray_arr is None and solve.get('message') == 'Infeasible':
        retry = solve_ray(mat, target_beta, threads=args.threads, time_limit=args.time_limit, presolve='off', verbose=args.verbose)
        ray_arr = retry.pop('_ray', None)
        solve = {'initial': solve, 'retry': retry, 'message': retry.get('message'), 'dual_ray_exists': retry.get('dual_ray_exists', False)}

    out = {
        'schema': 'eq_odl1_rung2_k6_F6_step3_highspy_ray_support_v1',
        'columns_json': str(args.columns_json),
        'target_beta_json': str(args.target_beta_json),
        'chart': int(args.chart),
        'dominant': col_meta.get('dominant'),
        'dominant_name': col_meta.get('dominant_name'),
        'columns': len(columns),
        'row_count': row_count,
        'nnz': int(mat.nnz),
        'threads': args.threads,
        'solve': solve,
        'seconds_total': time.monotonic() - t0,
    }
    if ray_arr is not None:
        out['ray_summary'] = summarize_ray(ray_arr, mat, target_beta, betas, args.top, args.tol)
        out['seed_family_score_top'] = family_summary(columns, ray_arr, top=100)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({
        'summary': str(args.summary),
        'message': out['solve'].get('message'),
        'dual_ray_exists': out['solve'].get('dual_ray_exists'),
        'ray_nonzero': (out.get('ray_summary') or {}).get('ray_nonzero'),
        'ray_dot_rhs': (out.get('ray_summary') or {}).get('ray_dot_rhs'),
        'seed_score_max': (out.get('ray_summary') or {}).get('seed_score_max'),
    }, sort_keys=True))


if __name__ == '__main__':
    main()
