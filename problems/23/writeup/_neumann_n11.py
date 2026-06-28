import subprocess
from _h import dec, GENG, loads
from _schur_neumann import test
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
nt=0; fail=0; mn=None
for g6 in out:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    st,o=test(info,kmax=2)
    if st=='noO': continue
    nt+=1
    if o[2]<0: fail+=1; print(f"k2 FAIL @ {g6}: {float(o[2])}",flush=True)
    if mn is None or o[2]<mn: mn=o[2]
    if nt%4000==0: print(f"  ...{nt} overloaded done, k2-fail={fail} min={float(mn)}",flush=True)
print(f"FULL N=11 k=2 DONE: overloaded graphs={nt} | k2 FAILS={fail} | min k2 residual={float(mn) if mn is not None else 'na'}",flush=True)
