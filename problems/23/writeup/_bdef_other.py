"""Focus on OTHER components (proper, loaded, Q-only = disjoint from O). For each:
 - is O empty or nonempty? (cond(1) only cares about O nonempty)
 - deficit, dB, slack = deficit-dB, bd_ok
 - is it CRITICAL (deficit==0, i.e. T==N on all of C)?
Report: any bd violation; min slack overall; min slack among O-nonempty; any critical proper comp;
and whether ANY OTHER comp occurs with O nonempty at all."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def scan(Nmin,Nmax):
    glob_minslack=None; glob_minslack_Ononempty=None
    n_other=0; n_other_Ononempty=0; n_bdfail=0; n_critical=0
    crit_witness=None; bdfail_witness=None; Ononempty_witness=None
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']
            comps=components(K,n)
            for C in comps:
                Cs=set(C)
                if Cs&O: continue
                if len(C)==n: continue   # FULL
                if len(C)==1 and T[C[0]]==0: continue  # ISO0
                # OTHER: proper loaded Q-only
                d=analyze_one(B,C)
                n_other+=1
                slack=d['deficit']-d['dB']
                if glob_minslack is None or slack<glob_minslack:
                    glob_minslack=slack
                    if slack<0: bdfail_witness=(g6,tuple(C),float(d['deficit']),d['dB'])
                if not d['bd_ok']:
                    n_bdfail+=1
                    if bdfail_witness is None: bdfail_witness=(g6,tuple(C),float(d['deficit']),d['dB'])
                crit=(d['deficit']==0)
                if crit:
                    n_critical+=1
                    if crit_witness is None: crit_witness=(g6,tuple(C),d['dB'])
                if O:
                    n_other_Ononempty+=1
                    if Ononempty_witness is None: Ononempty_witness=(g6,tuple(C),float(d['deficit']),d['dB'],sorted(O))
                    if glob_minslack_Ononempty is None or slack<glob_minslack_Ononempty:
                        glob_minslack_Ononempty=slack
        print(f"  N={nn}: OTHER={n_other} (O-nonempty={n_other_Ononempty}) bdFAIL={n_bdfail} critical={n_critical} minslack={float(glob_minslack) if glob_minslack is not None else None}",flush=True)
    print("=== SUMMARY ===")
    print(f"OTHER total={n_other}, with O nonempty={n_other_Ononempty}")
    print(f"bd violations={n_bdfail}  witness={bdfail_witness}")
    print(f"CRITICAL (deficit=0 proper loaded) count={n_critical} witness={crit_witness}")
    print(f"global min slack(deficit-dB)={float(glob_minslack) if glob_minslack is not None else None}")
    print(f"min slack among O-nonempty OTHER={float(glob_minslack_Ononempty) if glob_minslack_Ononempty is not None else 'NONE EXIST'}")
    print(f"first O-nonempty OTHER witness={Ononempty_witness}")

if __name__=="__main__":
    scan(5,11)
