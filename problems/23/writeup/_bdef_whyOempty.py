"""WHY do OTHER (proper loaded Q-only) components only occur with O empty?
For each OTHER component C, characterize R = V \ C:
  - is R entirely T=0 (load-free)?  (then all load is in C, sum T = mass(C) <= N|C| <= N^2 trivially, O empty)
  - if R has load, where does it sit? does R itself contain overload?
Also: examine the tight slack=4 witnesses (deficit - dB = 4): what makes slack exactly 4?
And: relationship of dB(C) to (N - max geodesic reach) / structure."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def scan(Nmin,Nmax):
    R_allT0=0; R_hasload=0; tot=0
    tight_witness=[]
    R_load_witness=None
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
                if len(C)==n: continue
                if len(C)==1 and T[C[0]]==0: continue
                d=analyze_one(B,C)
                tot+=1
                R=[v for v in range(n) if v not in Cs]
                R_load=[v for v in R if T[v]>0]
                if not R_load:
                    R_allT0+=1
                else:
                    R_hasload+=1
                    if R_load_witness is None:
                        R_load_witness=(g6,tuple(C),[(v,float(T[v])) for v in R_load],sorted(O))
                slack=d['deficit']-d['dB']
                if slack==4 and len(tight_witness)<6:
                    tight_witness.append((g6,tuple(C),float(d['deficit']),d['dB'],
                                          [float(T[v]) for v in C]))
        print(f"  N={nn}: OTHER tot={tot} R_allT0={R_allT0} R_hasLOAD={R_hasload}",flush=True)
    print("=== SUMMARY (OTHER comps, R = complement) ===")
    print(f"R entirely T=0: {R_allT0}   R has some load: {R_hasload}")
    print(f"R-has-load witness: {R_load_witness}")
    print("tight slack=4 witnesses:")
    for w in tight_witness: print("  ",w)

if __name__=="__main__":
    scan(6,11)
