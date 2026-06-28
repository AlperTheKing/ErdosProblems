"""GPT's NEW route (bypasses the broken HV_B link II). Gamma<=N^2 reduces to:
  (SM)       sum_v T(v)^2 <= N * sum_v T(v) = N*Gamma.           [via Cauchy-Schwarz or X-intermediate]
  (Cycle-SM) per bad edge f:  sum_v p_f(v) T(v) <= N*ell(f).     [=> (SM), since sumT^2=sum_f ell(f) sum_v p_f T]
DECISIVE: must hold on the blow-up J???E?pNu\\?[2] (N=22) where link II FAILED, + census N<=11 + random.
All exact rational."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def sm_quants(info):
    n=info['n']; T=info['T']; N=n; M=info['M']; cyc=info['cyc']; ell=info['ell']
    ST=sum(T); ST2=sum(t*t for t in T)
    SM_ok = ST2 <= N*ST            # (SM)
    SM_slack = N*ST - ST2
    # per-edge cycle-SM
    worst=None; wf=None
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        # sum_v p_f(v) T(v) = (1/nf) sum_P sum_{v in P} T(v)
        s=F(0)
        for P in Ps:
            s+=sum(T[v] for v in P)
        val=s/nf                   # sum_v p_f(v) T(v)
        slack=N*ell[f]-val         # >=0 desired
        if worst is None or slack<worst: worst=slack; wf=f
    return SM_ok,SM_slack,worst,wf

def blowup(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

def one(label,n,E):
    info=loads(n,E)
    if info is None: print(f"  {label}: skip"); return
    ok,sl,cyc_slack,wf=sm_quants(info)
    print(f"  {label:20} N={n} G={info['G']} | (SM) sumT2<=N*G: {ok} (slack={float(sl):+.3f}) | (Cycle-SM) min slack={float(cyc_slack):+.4f} @f={wf} {'<<<CYCLE-SM FAILS' if cyc_slack<0 else ''}")

def run_census(Nmax,Nmin=5):
    print("--- (SM) and (Cycle-SM) census ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; SMbad=0; CYbad=0; sm_min=None; cy_min=None; cyg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; ok,sl,cyc_slack,wf=sm_quants(info)
            if not ok: SMbad+=1
            if cyc_slack<0: CYbad+=1
            if sm_min is None or sl<sm_min: sm_min=sl
            if cy_min is None or cyc_slack<cy_min: cy_min=cyc_slack; cyg=g6
        print(f"  N={nn}: cfg={nt} | (SM) viol:{SMbad} (min slack={float(sm_min):+.3f}) | (Cycle-SM) viol:{CYbad} (min slack={float(cy_min):+.4f}@{cyg})",flush=True)

if __name__=="__main__":
    print("=== DECISIVE: the blow-up where link II FAILED ===")
    n,E=dec("J???E?pNu\\?"); one("J???E?pNu\\?[1]",n,E)
    nn,EE=blowup(n,E,2); one("J???E?pNu\\?[2]",nn,EE)
    n,E=dec("H?AFBo]"); nn,EE=blowup(n,E,2); one("H?AFBo][2]",nn,EE)
    run_census(11,5)
