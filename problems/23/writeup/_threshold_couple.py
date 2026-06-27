"""GPT's DECISIVE per-edge threshold-coarea test. For each bad edge f, lambda_f(z)=phi_f(z)/T(z) (f's posterior
load-share at z), phi_f(z)=ell_f p_f(z). Threshold set A_t(f)={z: lambda_f(z)>=t}. POINTWISE THRESHOLD-COUPLE:
   K_t(f) := u(A_t)-o(A_t) = sum_{z in A_t}(N-T(z))  >= 0   for ALL f and ALL thresholds t.
[since (N-T)_+ - (T-N)_+ = N-T exactly.] If K_t>=0 always => PF follows by layer-cake (PF = integral of [u(A_t)>=o(A_t)]dt)
=> COUPLE => delta=0, with NO further CD needed beyond what shapes the threshold sets. A single K_t<0 => this clean
route is DEAD on real graphs (since CD makes delta_B(A)-delta_M(A)>=0 for ALL A, the Threshold-CD lemma cannot
produce a CD-violating shore) => PF would need the harder integrated form. THE decisive diagnostic."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, GENG
from _ph_mincut import loads
from _pf_lsc import phi

def min_Kt(info):
    n=info['n']; T=info['T']; M=info['M']; N=n; ph=phi(info)
    worst=None; wf=None
    for f in M:
        lam={z: ph[f][z]/T[z] for z in ph[f]}     # lambda_f(z)
        ts=sorted(set(lam.values()))
        for t in ts:
            A=[z for z in lam if lam[z]>=t]
            Kt=sum((N-T[z]) for z in A)            # = u(A)-o(A)
            if worst is None or Kt<worst: worst=Kt; wf=(f,float(t))
    return worst, wf

def run_named():
    fails=["I?BD@g]Qo","J?AADagROl?","J??CE?{{?]?","J?BD@g]Qvo?"]
    print("=== pointwise threshold-couple min_t K_t(f) (>=0 => clean PF via layer-cake) ===")
    for g6 in fails:
        n,E=dec(g6); info=loads(n,E)
        w,wf=min_Kt(info)
        print(f"  {g6:13} N={n} | min_t K_t = {float(w):+.4f} ({'HOLDS' if w>=0 else 'FAILS at '+str(wf)})")

def run_census(Nmax,Nmin=8):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=viol=0; worst=None; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; w,wf=min_Kt(info)
            if worst is None or w<worst: worst=w; wg=g6
            if w<0: viol+=1
        print(f"  N={nn}: configs={nt} | threshold-couple K_t<0 violations={viol} | global min K_t={float(worst):+.4f} ({wg})",flush=True)

if __name__=="__main__":
    run_named()
    run_census(11,8)
