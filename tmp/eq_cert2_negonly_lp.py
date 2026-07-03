from scipy.optimize import linprog
from scipy.sparse import coo_matrix
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
rows=[i for i,j,v in entries]
cc=[j for i,j,v in entries]
data=[v/row_scale[i] for i,j,v in entries]
A=coo_matrix((data,(rows,cc)),shape=(len(neg_mons),len(cols))).tocsr()
b=[float(target[m])/row_scale[i] for i,m in enumerate(neg_mons)]
print('neg-only rows',len(neg_mons),'cols',len(cols),'nnz',len(data),flush=True)
res=linprog(c=[0.0]*len(cols), A_ub=A, b_ub=b, bounds=[(0,None)]*len(cols), method='highs', options={'time_limit':30})
print('status',res.status,res.message,'success',res.success,flush=True)
if res.success:
    print('nonzero',sum(1 for x in res.x if x>1e-9),'max',max(res.x),flush=True)
