#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from fractions import Fraction
from pathlib import Path

sys.path.append(str(Path('problems/23/writeup')))
import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_source_solution_check as source_check

COLUMNS = Path('tmp/eq_odl1_rung2_hybrid_phase1_cg_k6_F6_targetactive_price1024_step3_cols_v1.json')
TARGET = Path('tmp/eq_odl1_rung2_hybrid_phase1_cg_k6_F6_targetactive_price1024_step3_target_beta_v1.json')
RAY = Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_support_v1.json')
OUT = Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_exact_replay_v1.json')
MAX_DEN = 10000

def fmt(q: Fraction) -> dict[str, int | str]:
    return {'num': q.numerator, 'den': q.denominator, 'str': str(q)}

def main():
    columns, row_count, meta = custom_check.read_columns_json(COLUMNS)
    target = source_check.read_target_beta(TARGET, row_count)
    ray_data = json.loads(RAY.read_text(encoding='utf-8'))
    support = ray_data['ray_summary']['support_top']
    y = {}
    for rec in support:
        q = Fraction(float(rec['value'])).limit_denominator(MAX_DEN)
        if q:
            y[int(rec['row'])] = q
    y_dot_b = sum(y.get(i, Fraction(0)) * target[i] for i in y)
    positive = []
    max_score = None
    min_score = None
    zero_count = 0
    neg_count = 0
    for j, col in enumerate(columns):
        score = sum(coeff * y.get(row, Fraction(0)) for row, coeff in col.terms)
        if max_score is None or score > max_score:
            max_score = score
        if min_score is None or score < min_score:
            min_score = score
        if score > 0:
            positive.append({
                'source_col': j,
                'score': fmt(score),
                'kind': col.kind,
                'side': col.side,
                'name': col.name,
                'multiplier_exp': list(col.multiplier_exp),
            })
        elif score == 0:
            zero_count += 1
        else:
            neg_count += 1
    ray_support = [
        {
            'row': int(row),
            'value': fmt(val),
            'target_beta': fmt(target[row]),
            'contribution_to_y_dot_b': fmt(val * target[row]),
        }
        for row, val in sorted(y.items())
    ]
    out = {
        'schema': 'eq_odl1_rung2_k6_F6_step3_farkas_exact_replay_v1',
        'columns_json': str(COLUMNS),
        'target_beta_json': str(TARGET),
        'float_ray_json': str(RAY),
        'row_count': row_count,
        'columns': len(columns),
        'support_count': len(y),
        'max_den': MAX_DEN,
        'y_dot_b': fmt(y_dot_b),
        'farkas_rhs_positive': y_dot_b > 0,
        'max_column_score': fmt(max_score or Fraction(0)),
        'min_column_score': fmt(min_score or Fraction(0)),
        'positive_column_score_count': len(positive),
        'zero_column_score_count': zero_count,
        'negative_column_score_count': neg_count,
        'positive_column_score_top': positive[:50],
        'ray_support': ray_support,
        'chart': meta.get('chart'),
        'dominant': meta.get('dominant'),
        'dominant_name': meta.get('dominant_name'),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({
        'out': str(OUT),
        'support_count': len(y),
        'y_dot_b': str(y_dot_b),
        'rhs_positive': y_dot_b > 0,
        'positive_column_score_count': len(positive),
        'max_column_score': str(max_score),
        'zero_column_score_count': zero_count,
    }, sort_keys=True))

if __name__ == '__main__':
    main()
