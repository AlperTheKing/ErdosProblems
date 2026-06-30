"""Just the Mycielskian/blowup battery (no slow census) to get the S3 verdict fast + tightness."""
from fractions import Fraction as F
from _bdef_construct import mycielski, Cn
import _wf_var_reduce as W

agg={}; firsts={}
bl=W.blowup
extra=[('M(C7)',)+mycielski(7,Cn(7)),('M(C9)',)+mycielski(9,Cn(9)),
       ('Grotzsch',)+mycielski(5,Cn(5)),
       ('C5[2]',)+bl([2,2,2,2,2]),('C5[3]',)+bl([3,3,3,3,3]),
       ('C5unbal',)+bl([1,5,2,2,5]),('C7unbal',)+bl([1,4,2,4,2,4,2]),('C5[1,6,2,2,6]',)+bl([1,6,2,2,6])]
for it in extra:
    W.gate_run(it[0],it[1],it[2],agg,firsts); print('done',it[0],flush=True)
print('=== AGG (Myc/blowup battery only) ===')
for k in ['BD_thm','BD_TARGET','FINAL_var','S1_M_le_N','S2_llspread_le_N','S3_upper','S4_meanm_le_N','S3p_upperdef','S5a_llupper_leN','S5b_lowerdef','S6_strong']:
    print(' ',k,agg.get(k), ('FF '+str(firsts[k]) if firsts.get(k) else ''))
