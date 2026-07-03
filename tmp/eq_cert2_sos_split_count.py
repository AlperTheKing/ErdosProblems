import sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,'problems/23/writeup')
import _codex_eq_cert2_chart_sos as sos
import _codex_eq_cert2_chart_lp as lp

target11,_,_=lp.build_chart(0)
target12=sos.mul_linear(target11)
all_deg6=list(sos.weak_compositions(6, lp.SX_DIM))
seed=(6,)+(0,)*(lp.SX_DIM-1)
neg=[e for e,c in target12.items() if c<0]
counts=[]
total=0
with_pos=0
for row in neg:
    cands=[]
    poscands=[]
    for a in all_deg6:
        b=sos.sub_exp(row,a)
        if b is None or sum(b)!=6 or a>b or a==seed or b==seed:
            continue
        cands.append((a,b))
        if target12.get(tuple(2*x for x in a), Fraction(0))>0 and target12.get(tuple(2*x for x in b), Fraction(0))>0:
            poscands.append((a,b))
    counts.append((len(cands),len(poscands),row,target12[row]))
    total += len(cands)
    with_pos += len(poscands)
print('neg_rows',len(neg),'all_pair_splits',total,'positive_diag_splits',with_pos)
print('rows_with_any',sum(1 for a,b,_,__ in counts if a),'rows_with_posdiag',sum(1 for a,b,_,__ in counts if b))
print('max',max(counts)[:2],'min',min(counts)[:2])
print('top_pos', sorted(counts, reverse=True)[:10])
