#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from fractions import Fraction
from pathlib import Path
sys.path.append(str(Path('problems/23/writeup')))
import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_source_solution_check as source_check

def fmt(q: Fraction) -> dict[str, int | str]:
    return {'num': q.numerator, 'den': q.denominator, 'str': str(q)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--columns-json', type=Path, required=True)
    ap.add_argument('--target-beta-json', type=Path, required=True)
    ap.add_argument('--ray-json', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--max-den', type=int, default=10000)
    args=ap.parse_args()
    columns,row_count,meta=custom_check.read_columns_json(args.columns_json)
    target=source_check.read_target_beta(args.target_beta_json,row_count)
    ray_data=json.loads(args.ray_json.read_text(encoding='utf-8'))
    support=ray_data['ray_summary']['support_top']
    y={}
    for rec in support:
        q=Fraction(float(rec['value'])).limit_denominator(args.max_den)
        if q:
            y[int(rec['row'])]=q
    y_dot_b=sum(y.get(i,Fraction(0))*target[i] for i in y)
    positive=[]; zero=0; neg=0; max_score=None; min_score=None
    for j,col in enumerate(columns):
        score=sum(coeff*y.get(row,Fraction(0)) for row,coeff in col.terms)
        if max_score is None or score>max_score: max_score=score
        if min_score is None or score<min_score: min_score=score
        if score>0:
            positive.append({'source_col':j,'score':fmt(score),'kind':col.kind,'side':col.side,'name':col.name,'multiplier_exp':list(col.multiplier_exp)})
        elif score==0: zero+=1
        else: neg+=1
    out={
        'schema':'eq_odl1_rung2_generic_farkas_exact_replay_v1',
        'columns_json':str(args.columns_json),
        'target_beta_json':str(args.target_beta_json),
        'float_ray_json':str(args.ray_json),
        'row_count':row_count,
        'columns':len(columns),
        'support_count':len(y),
        'max_den':args.max_den,
        'y_dot_b':fmt(y_dot_b),
        'farkas_rhs_positive': y_dot_b>0,
        'max_column_score':fmt(max_score or Fraction(0)),
        'min_column_score':fmt(min_score or Fraction(0)),
        'positive_column_score_count':len(positive),
        'zero_column_score_count':zero,
        'negative_column_score_count':neg,
        'positive_column_score_top':positive[:50],
        'ray_support':[{'row':row,'value':fmt(val),'target_beta':fmt(target[row]),'contribution_to_y_dot_b':fmt(val*target[row])} for row,val in sorted(y.items())],
        'chart':meta.get('chart'), 'dominant':meta.get('dominant'), 'dominant_name':meta.get('dominant_name')
    }
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'out':str(args.out),'support_count':len(y),'y_dot_b':str(y_dot_b),'rhs_positive':y_dot_b>0,'positive_column_score_count':len(positive),'max_column_score':str(max_score),'zero_column_score_count':zero}, sort_keys=True))
if __name__=='__main__': main()
