"""Validate S2 + S3' (the two-step proof of BD-TARGET) on the KNOWN finite-depth killers:
iterated Mycielskian M(Grotzsch)=N23, M(C11)=N23, plus bridges. EXACT."""
from fractions import Fraction as F
from _bdef_construct import mycielski, Cn, union_disjoint
import _wf_var_reduce as W

def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

agg={}; firsts={}
extra=[('M(C11)N23',)+mycielski(11,Cn(11)),
       ('M(Grotzsch)N23',)+mycielski(*mycielski(5,Cn(5))),
       ('C7|brg|Grotzsch',)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)]
for it in extra:
    W.gate_run(it[0],it[1],it[2],agg,firsts); print('done',it[0],flush=True)
print('=== AGG (N23 killers) ===')
for k in ['BD_thm','BD_TARGET','FINAL_var','S2_llspread_le_N','S3p_upperdef','S5b_lowerdef','S6_strong']:
    print(' ',k,agg.get(k), ('FF '+str(firsts[k]) if firsts.get(k) else ''))
