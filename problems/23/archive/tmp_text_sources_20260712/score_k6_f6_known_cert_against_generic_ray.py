#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
sys.path.append(str(Path('problems/23/writeup')))
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check

def parse_frac(rec): return Fraction(int(rec['num']), int(rec['den']))
def fmt(q: Fraction): return {'num': q.numerator, 'den': q.denominator, 'str': str(q)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ray-exact', type=Path, required=True)
    ap.add_argument('--solution', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args=ap.parse_args()
    ray=json.loads(args.ray_exact.read_text(encoding='utf-8'))
    y={int(r['row']):parse_frac(r['value']) for r in ray['ray_support']}
    vals=source_check.read_source_solution(args.solution)
    prepared,columns,_mat,_b_ub=probe.build_lp(6,5,'near_2s_minus_1','negative')
    by=defaultdict(lambda:{'count':0,'solution_weight':Fraction(0),'score_sum':Fraction(0),'positive_count':0,'max_score':None})
    positives=[]; total=Fraction(0)
    for source_col,val in sorted(vals.items()):
        col=columns[source_col]
        score=sum(coeff*y.get(row,Fraction(0)) for row,coeff in col.terms)
        contrib=val*score; total+=contrib
        fam=f'{col.kind}:{col.name}'
        g=by[fam]; g['count']+=1; g['solution_weight']+=val; g['score_sum']+=contrib
        if score>0:
            g['positive_count']+=1
            positives.append({'source_col':source_col,'family':fam,'ray_score':fmt(score),'value':fmt(val),'weighted_score':fmt(contrib),'multiplier_exp':list(col.multiplier_exp)})
        if g['max_score'] is None or score>g['max_score']: g['max_score']=score
    fams=[]
    for fam,g in by.items():
        fams.append({'family':fam,'count':g['count'],'positive_count':g['positive_count'],'solution_weight':fmt(g['solution_weight']),'score_sum':fmt(g['score_sum']),'max_score':fmt(g['max_score'] or Fraction(0))})
    fams.sort(key=lambda r:(r['positive_count'], parse_frac(r['max_score'])), reverse=True)
    positives.sort(key=lambda r:parse_frac(r['ray_score']), reverse=True)
    out={'schema':'eq_odl1_rung2_k6_F6_known_cert_vs_generic_farkas_ray_v1','ray_exact':str(args.ray_exact),'solution_jsonl':str(args.solution),'source_columns':len(columns),'nonzero_solution_columns':len(vals),'ray_support_count':len(y),'y_dot_known_solution':fmt(total),'families':fams,'positive_columns':positives}
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'out':str(args.out),'families':len(fams),'positive_families':[(f['family'],f['positive_count'],f['max_score']['str']) for f in fams if f['positive_count']>0],'positive_columns':len(positives)}, sort_keys=True))
if __name__=='__main__': main()
