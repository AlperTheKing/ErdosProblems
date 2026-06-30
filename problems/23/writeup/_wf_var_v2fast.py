import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _bdef_construct import mycielski, Cn
import _wf_var_reduce as W

agg={}; firsts={}
for nn in range(7,10):
    outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); W.gate_run(g6,n,E,agg,firsts)
    print('done census',nn,flush=True)
bl=W.blowup
extra=[('M(C7)',)+mycielski(7,Cn(7)),('M(C9)',)+mycielski(9,Cn(9)),('M(C11)',)+mycielski(11,Cn(11)),
       ('Grotzsch',)+mycielski(5,Cn(5)),('M(Grotzsch)N23',)+mycielski(*mycielski(5,Cn(5))),
       ('C5[2]',)+bl([2,2,2,2,2]),('C5[3]',)+bl([3,3,3,3,3]),('C5[4]',)+bl([4,4,4,4,4]),
       ('C5unbal',)+bl([1,5,2,2,5]),('C7unbal',)+bl([1,4,2,4,2,4,2]),('C5[1,6,2,2,6]',)+bl([1,6,2,2,6]),
       ('C5[1,48,6,8,48]',)+bl([1,48,6,8,48])]
for it in extra:
    W.gate_run(it[0],it[1],it[2],agg,firsts); print('done',it[0],flush=True)
print('=== AGG ===')
for k in ['BD_thm','BD_TARGET','FINAL_var','S1_M_le_N','S2_llspread_le_N','S3_upper','S4_meanm_le_N']:
    print(' ',k,agg.get(k), ('FF '+str(firsts[k]) if firsts.get(k) else ''))
