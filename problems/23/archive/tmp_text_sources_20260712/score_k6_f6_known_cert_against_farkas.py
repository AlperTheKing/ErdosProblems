#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.append(str(Path('problems/23/writeup')))
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check

SOLUTION = Path('tmp/eq_odl1_rung2_source_solution_k6_F6_near_exact_active_face_split_patch3_rowgen2_hardspill_v1.jsonl')
RAY_EXACT = Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_exact_replay_v1.json')
OUT = Path('tmp/eq_odl1_rung2_k6_F6_known_cert_vs_step3_farkas_ray_v1.json')

def parse_frac(rec):
    return Fraction(int(rec['num']), int(rec['den']))

def fmt(q: Fraction):
    return {'num': q.numerator, 'den': q.denominator, 'str': str(q)}

def main():
    ray = json.loads(RAY_EXACT.read_text(encoding='utf-8'))
    y = {int(r['row']): parse_frac(r['value']) for r in ray['ray_support']}
    vals = source_check.read_source_solution(SOLUTION)
    prepared, columns, _mat, _b_ub = probe.build_lp(6, 5, 'near_2s_minus_1', 'negative')
    rows = []
    by_family = defaultdict(lambda: {'count': 0, 'solution_weight': Fraction(0), 'score_sum': Fraction(0), 'positive_count': 0, 'max_score': None})
    total_solution_score = Fraction(0)
    for source_col, val in sorted(vals.items()):
        col = columns[source_col]
        score = sum(coeff * y.get(row, Fraction(0)) for row, coeff in col.terms)
        contrib = val * score
        total_solution_score += contrib
        family = f'{col.kind}:{col.name}'
        g = by_family[family]
        g['count'] += 1
        g['solution_weight'] += val
        g['score_sum'] += contrib
        if score > 0:
            g['positive_count'] += 1
        if g['max_score'] is None or score > g['max_score']:
            g['max_score'] = score
        rows.append({
            'source_col': source_col,
            'family': family,
            'kind': col.kind,
            'name': col.name,
            'multiplier_exp': list(col.multiplier_exp),
            'value': fmt(val),
            'ray_score': fmt(score),
            'weighted_score': fmt(contrib),
        })
    fams = []
    for fam, g in by_family.items():
        fams.append({
            'family': fam,
            'count': g['count'],
            'positive_count': g['positive_count'],
            'solution_weight': fmt(g['solution_weight']),
            'score_sum': fmt(g['score_sum']),
            'max_score': fmt(g['max_score'] or Fraction(0)),
        })
    fams.sort(key=lambda r: parse_frac(r['score_sum']), reverse=True)
    rows.sort(key=lambda r: parse_frac(r['weighted_score']), reverse=True)
    out = {
        'schema': 'eq_odl1_rung2_k6_F6_known_cert_vs_step3_farkas_ray_v1',
        'solution_jsonl': str(SOLUTION),
        'farkas_exact_replay': str(RAY_EXACT),
        'source_columns': len(columns),
        'nonzero_solution_columns': len(vals),
        'ray_support_count': len(y),
        'y_dot_known_solution': fmt(total_solution_score),
        'families_by_weighted_score': fams,
        'positive_weighted_columns_top': rows[:200],
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({
        'out': str(OUT),
        'nonzero_solution_columns': len(vals),
        'families': len(fams),
        'y_dot_known_solution': str(total_solution_score),
        'top_families': [(f['family'], f['score_sum']['str'], f['count']) for f in fams[:8]],
    }, sort_keys=True))

if __name__ == '__main__':
    main()
