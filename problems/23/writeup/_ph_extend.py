"""Extend PH max-flow test to N=10,11 + ROBUSTNESS: strict shadow (only eta>0 defect-carrying cycles contribute).
If PH stays feasible with the STRICT shadow, the result isn't an artifact of permissive (eta<=0) shadows."""
import subprocess
from census_GPI import dec, GENG
import _ph_maxflow_test as P

def ph_strict(info):
    # monkeypatch: shadow only from eta>0 cycles
    orig=P.shadow
    def strict_shadow(inf,f,C,j):
        sh,eta=orig(inf,f,C,j)
        return (sh if eta>0 else set()), eta
    P.shadow=strict_shadow
    st,mf,dem,uo=P.ph_test(info)
    P.shadow=orig
    return st,mf,dem

for nn in (10,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    inf=triv=nt=infS=0
    for g6 in out:
        n,E=dec(g6); info=P.loads_atoms(n,E)
        if info is None: continue
        nt+=1
        st,_,_,_=P.ph_test(info)
        if st=='trivial': triv+=1
        elif st=='INFEASIBLE': inf+=1
        sts,_,_=ph_strict(info)
        if sts=='INFEASIBLE': infS+=1
    print(f"N={nn}: configs={nt} | PH-infeasible(permissive)={inf} | PH-infeasible(STRICT eta>0)={infS} | trivial={triv}",flush=True)
print("Both columns 0 => PH 2-to-1 transport feasible census N<=11 under BOTH shadow readings (robust).")
