"""Focused HARD stress: t=2 blow-ups of ALL overloaded census graphs N=8,9,10 (->16,18,20),
t=3 of N=8 overloaded (->24), and a SAMPLE of N=11 overloaded (->22 via t=2).
Exact-test all conditions + k2. Print every overloaded blow-up result; flag any fail.
Incremental output so partial results survive timeout."""
import sys
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _audit_stress import full_test, blow, report

def overloaded(nn,stride=1):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    ov=[]
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        if any(t>n for t in info['T']): ov.append(g6)
    return ov

def stress_blowups(base_list, t, cap):
    tested=0; fails=0; sing=0; wm=None; wk=None; noO=0
    for g6 in base_list:
        nbase,_=dec(g6); N=nbase*t
        if N>cap: continue
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info is None: continue
        res=full_test(info)
        if res['status']=='noO': noO+=1; continue
        tested+=1
        if res['status']=='SINGULAR_AQQ': sing+=1; print(" "+report(f"{g6}[{t}]",nn,res),flush=True)
        elif res['status']=='FAIL': fails+=1; print(" "+report(f"{g6}[{t}]",nn,res),flush=True)
        else:
            if wm is None or res['minrow']<wm: wm=res['minrow']
            if wk is None or res['mink2']<wk: wk=res['mink2']
    print(f"  t={t} cap={cap}: tested {tested} overloaded blow-ups, {noO} lost-overload, FAILS={fails} SING={sing}"
          f" | worst E-rowsum={float(wm) if wm is not None else 'na'} worst k2={float(wk) if wk is not None else 'na'}",flush=True)
    return fails,sing

if __name__=="__main__":
    which=sys.argv[1] if len(sys.argv)>1 else "all"
    if which in ("8","all"):
        print("=== N=8 overloaded ===",flush=True)
        ov8=overloaded(8); print(f"  {len(ov8)} overloaded",flush=True)
        stress_blowups(ov8,2,16)   # ->16
        stress_blowups(ov8,3,24)   # ->24
    if which in ("9","all"):
        print("=== N=9 overloaded -> t=2 (N=18) ===",flush=True)
        ov9=overloaded(9); print(f"  {len(ov9)} overloaded",flush=True)
        stress_blowups(ov9,2,18)
    if which in ("10","all"):
        print("=== N=10 overloaded -> t=2 (N=20) ===",flush=True)
        ov10=overloaded(10); print(f"  {len(ov10)} overloaded",flush=True)
        stress_blowups(ov10,2,20)
    if which.startswith("11"):
        stride=int(which.split(":")[1]) if ":" in which else 20
        print(f"=== N=11 overloaded (stride {stride}) -> t=2 (N=22) ===",flush=True)
        ov11=overloaded(11,stride); print(f"  {len(ov11)} overloaded sampled",flush=True)
        stress_blowups(ov11,2,22)
