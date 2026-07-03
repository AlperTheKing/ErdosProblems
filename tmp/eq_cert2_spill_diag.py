from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from collections import Counter
import sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp

chart=0
target, gens, meta = lp.build_chart(chart)
cols = lp.repair_columns(target, gens, 'repair', None)
term_maps = [lp.column_terms(c, gens[c.gen_index]) for c in cols]
neg_mons = sorted([e for e,c in target.items() if c < 0])
row_index={m:i for i,m in enumerate(neg_mons)}
row_scale=[max(1.0, abs(float(target[m]))) for m in neg_mons]
entries=[]
for j,mp in enumerate(term_maps):
    for mon,coeff in mp.items():
        if mon in row_index:
            i=row_index[mon]
            val=float(coeff)
            row_scale[i]=max(row_scale[i], abs(val))
            entries.append((i,j,val))
A=coo_matrix(([v/row_scale[i] for i,j,v in entries],([i for i,j,v in entries],[j for i,j,v in entries])),shape=(len(neg_mons),len(cols))).tocsr()
b=[float(target[m])/row_scale[i] for i,m in enumerate(neg_mons)]
res=linprog(c=[0.0]*len(cols), A_ub=A, b_ub=b, bounds=[(0,None)]*len(cols), method='highs', options={'time_limit':30})
print('success',res.success)
resid={m:float(c) for m,c in target.items()}
for x,mp in zip(res.x, term_maps):
    if x <= 1e-9: continue
    for mon,coeff in mp.items():
        resid[mon]=resid.get(mon,0.0)-x*float(coeff)
viol=[(v,m) for m,v in resid.items() if v < -1e-6]
viol.sort()
print('violations',len(viol),'worst',viol[:10])
print('viol degree counts',Counter(sum(m) for v,m in viol))
print('viol s-power counts',Counter(m[0] for v,m in viol).most_common(20))
print('target sign among viol',Counter('neg' if target.get(m,0)<0 else 'pos' if target.get(m,0)>0 else 'zero' for v,m in viol))
