import subprocess, sys
from _h import dec, GENG, loads
from _schur_spec import test
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
nt=0; fails=0; sing=0; minmargin=None
for g6 in out:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    nt+=1
    st,d=test(info)
    if st=='SINGULAR_AQQ': sing+=1; print(f"SINGULAR @ {g6}",flush=True)
    elif st=='FAIL': fails+=1; print(f"FAIL @ {g6}: {d['fails']} minrow={float(d['minrow'])}",flush=True)
    elif st=='ok':
        if minmargin is None or d['minrow']<minmargin: minmargin=d['minrow']
    if nt%8000==0: print(f"  ...{nt} done, fails={fails} sing={sing} min E-rowsum={float(minmargin) if minmargin is not None else 'na'}",flush=True)
print(f"FULL N=11 DONE: tested={nt} | FAILS={fails} | singular={sing} | min E-rowsum margin={float(minmargin) if minmargin is not None else 'na'}",flush=True)
