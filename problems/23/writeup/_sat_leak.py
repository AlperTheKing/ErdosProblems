"""Test a CLEAN candidate lemma that would directly kill criticality:
   (SAT-LEAK)  every SATURATED vertex q in Q (T[q]=N) has leak[q] > 0.
If true, then no q can have both T[q]=N and leak[q]=0, so NO critical component (needs all-saturated
& all-leak0). This is a per-VERTEX statement (much cleaner than per-component).
We exact-check over census whether any saturated (T=N) underloaded vertex has leak=0.
Also test the near-version: among q with T[q] close to N, what is min leak?
And: is there ALWAYS at least one q in Q with T[q]=N? (probably not; saturation is rare.)
Also test the broader candidate:
   (DIAG-DOM-row) for q in Q: K[q,q] + leak[q] >= something? to get strict.
Report: #saturated-underloaded vertices, min leak among them, any with leak=0."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K

def check(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    sat=[q for q in Q if T[q]==F(N)]
    sat_leak0=[q for q in sat if sum(K[q][o] for o in O)==0]
    min_leak_sat=None
    for q in sat:
        lk=sum(K[q][o] for o in O)
        if min_leak_sat is None or lk<min_leak_sat: min_leak_sat=lk
    return dict(N=N,nsat=len(sat),sat_leak0=len(sat_leak0),
                min_leak_sat=min_leak_sat, sat_leak0_verts=sat_leak0)

if __name__=="__main__":
    print("=== (SAT-LEAK) every saturated underloaded vertex has leak>0 ? ===")
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot_sat=0; tot_leak0=0; gwith_sat=0; minleak=None; ex=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=check(info)
            if d is None: continue
            if d['nsat']>0: gwith_sat+=1
            tot_sat+=d['nsat']; tot_leak0+=d['sat_leak0']
            if d['sat_leak0']>0 and ex is None: ex=(g6,d['sat_leak0_verts'])
            if d['min_leak_sat'] is not None:
                if minleak is None or d['min_leak_sat']<minleak: minleak=d['min_leak_sat']
        print(f"  N={nn}: graphs-with-saturated-Q-vertex={gwith_sat} | total saturated Q-verts={tot_sat} | "
              f"with leak=0 (VIOLATION)={tot_leak0}{(' ex='+str(ex)) if ex else ''} | min leak among saturated={float(minleak) if minleak is not None else 'na'}",flush=True)
