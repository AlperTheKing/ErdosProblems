"""Characterize the EXACT equality cases of (Cycle-SM) (Oell)_f = N*ell(f) [slack 0].
A sharp proof must be tight exactly there. For census N<=11, find graphs with min-slack 0 and report
Gamma vs N^2, whether T is constant (==N), and the T-profile. Exact rational."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def min_cycle_sm_slack(info):
    n=info['n']; T=info['T']; N=n; M=info['M']; cyc=info['cyc']; ell=info['ell']
    worst=None; wf=None
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        s=sum(sum(T[v] for v in P) for P in Ps)
        val=F(s,nf)            # sum_v p_f(v)T(v)
        slack=N*ell[f]-val
        if worst is None or slack<worst: worst=slack; wf=f
    return worst,wf

def run(Nmax,Nmin=7):
    print("--- EXACT tight (Cycle-SM) graphs: structure of the equality case ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tight=[]; nt=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; sl,wf=min_cycle_sm_slack(info)
            if sl==0: tight.append((g6,info))
        # summarize tight graphs
        gam_eq=0; Tconst=0
        for g6,info in tight:
            if info['G']==nn*nn: gam_eq+=1
            if len(set(info['T']))==1: Tconst+=1
        print(f"  N={nn}: cfg={nt} | tight(slack=0) graphs:{len(tight)} | of those Gamma==N^2:{gam_eq} | T constant(==N):{Tconst}")
        # show up to 3 examples
        for g6,info in tight[:3]:
            Tset=sorted(set(float(t) for t in info['T']))
            print(f"      {g6}: Gamma={info['G']} (N^2={nn*nn}) T-values={Tset}")

if __name__=="__main__":
    run(11,8)
